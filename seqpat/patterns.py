import re
from typing import Any, Callable, List, Optional, Tuple, Union

import importlib.metadata

__version__: str = "0.0.0-unknown"
try:
    if __package__:
        if v := importlib.metadata.version(__package__):
            __version__ = v
except importlib.metadata.PackageNotFoundError:
    pass
except ValueError:
    pass


class Pattern:
    """
    Base class for all patterns. Provides the common interface for parsing sequences.

    All subclasses must implement the `parse` method to define their parsing behavior.
    """

    def parse(self, seq: List[str], row: int = 0) -> Optional[Tuple[List, int]]:
        """
        Parse a sequence starting from the given row.
        Must be implemented by subclasses.

        Args:
            seq (List[str]): The sequence of strings to parse.
            row (int): The row index to start parsing from.

        Returns:
            Optional[Tuple[List, int]]: The parsed result and the next row index, or None if parsing fails.
        """
        raise NotImplementedError()

    def __or__(self, other: "Pattern") -> "Pattern":
        """
        Combine this pattern with another using a logical OR (alternative).

        Args:
            other (Pattern): The other pattern to combine with.

        Returns:
            Pattern: A new Choice pattern representing the logical OR.
        """
        return Choice(self, other)

    def __add__(self, other: "Pattern") -> "Pattern":
        """
        Combine this pattern with another using a logical AND (sequence).

        Args:
            other (Pattern): The other pattern to combine with.

        Returns:
            Pattern: A new Sequence pattern representing the logical AND.
        """
        return Sequence(self, other)

    def __mul__(self, count: Union[int, Tuple[int, Optional[int]]]) -> "Pattern":
        """
        Repeat this pattern a specified number of times.

        Args:
            count (Union[int, Tuple[int, Optional[int]]]): The number of repetitions, or a range (min, max).

        Returns:
            Pattern: A new Repeat pattern.
        """
        return Repeat(self, count=count)


class Sequence(Pattern):
    """
    A pattern representing a sequence of other patterns or strings.
    """

    def __init__(
        self,
        *contents: Union[Pattern, str],
        repl: Optional[List] = None,
        fmt: Optional[Callable[[Tuple[Any, ...]], List]] = None,
    ):
        """
        Initialize the Sequence pattern.

        Args:
            contents (Union[Pattern, str]): A list of patterns or strings to be parsed in sequence.
            repl (List, optional): A replacement list to return instead of the parsed result, if provided.
            fmt (Callable[[Tuple[Any, ...]], List], optional): A formatting function to apply to the parsed result.
        """
        fmt_count = sum((1 if f is not None else 0) for f in (repl, fmt))
        assert fmt_count <= 1, "repl, fmt are mutually exclusive"
        assert repl is None or isinstance(repl, list)

        self.contents = []
        for c in contents:
            if isinstance(c, Sequence):
                # If the content is another Sequence, extend the sequence
                self.contents.extend(c.contents)
            else:
                self.contents.append(c)

        self.repl = repl
        self.fmt = fmt

    def parse(self, seq: List[str], row: int = 0) -> Optional[Tuple[List, int]]:
        """
        Parse the sequence by attempting to match each pattern in the sequence.

        Args:
            seq (List[str]): The sequence of strings to parse.
            row (int): The row index to start parsing from.

        Returns:
            Optional[Tuple[List, int]]: The parsed result and the next row index, or None if any pattern fails.
        """
        result = []
        for content in self.contents:
            if isinstance(content, str):
                # If the content is a string, append it directly to the result
                result.append(content)
            else:
                # Parse the content
                r = content.parse(seq, row)
                if r is None:
                    return None
                parsed, next_row = r
                assert next_row >= row
                result.extend(parsed)
                row = next_row

        if self.repl is not None:
            return self.repl, row
        elif self.fmt is not None:
            replaced = self.fmt(*result)
            assert isinstance(replaced, list)
            return replaced, row
        else:
            return result, row


class Choice(Pattern):
    """
    A pattern representing an alternative between multiple patterns.
    """

    def __init__(self, *contents: Pattern):
        """
        Initialize the Choice pattern.

        Args:
            contents (Pattern): A list of patterns to choose from.
        """
        self.contents = []
        for c in contents:
            if isinstance(c, Choice):
                # If the content is another Choice, extend the alternatives
                self.contents.extend(c.contents)
            else:
                self.contents.append(c)

    def parse(self, seq: List[str], row: int = 0) -> Optional[Tuple[List, int]]:
        """
        Parse the sequence by attempting to match one of the alternative patterns.

        Args:
            seq (List[str]): The sequence of strings to parse.
            row (int): The row index to start parsing from.

        Returns:
            Optional[Tuple[List, int]]: The parsed result and the next row index, or None if no pattern matches.
        """
        for content in self.contents:
            r = content.parse(seq, row)
            if r is not None:
                return r
        return None


class Repeat(Pattern):
    """
    A pattern representing a repetition of another pattern.
    """

    def __init__(
        self,
        content: Pattern,
        count: Union[int, Tuple[int, Optional[int]]] = (0, None),
        repl: Optional[List] = None,
        fmt: Optional[Callable[[Tuple[Any, ...]], List]] = None,
        sep: Optional[str] = None,
    ):
        """
        Initialize the Repeat pattern.

        Args:
            content (Pattern): The pattern to repeat.
            count (Union[int, Tuple[int, Optional[int]]]): The number of repetitions, or a range (min, max).
            repl (List, optional): A replacement list to return instead of the parsed result, if provided.
            fmt (Callable[[Tuple[Any, ...]], List], optional): A formatting function to apply to the parsed result.
            sep (str, optional): A separator to insert between repetitions.
        """
        assert not isinstance(content, Repeat), "Repeat cannot contain another Repeat."
        if isinstance(count, int):
            assert count > 0, "Repetition count cannot be zero or negative."
            self.min_count, self.max_count = count, count  # Exactly n times
        else:
            min_count, max_count = count
            assert isinstance(min_count, int), "Invalid min count"
            assert isinstance(max_count, (int, type(None))), "Invalid max count"
            assert min_count >= 0, "Min count must be non-negative."
            assert max_count is None or max_count >= min_count, "Max count must be greater than or equal to min count."
            assert not (min_count == max_count == 0), "Min count and max count cannot both be 0."
            self.min_count, self.max_count = min_count, max_count
        fmt_count = sum((1 if f is not None else 0) for f in (repl, fmt))
        assert fmt_count <= 1, "repl, fmt are mutually exclusive"
        assert repl is None or isinstance(repl, list)

        self.content = content
        self.repl = repl
        self.fmt = fmt
        self.sep = sep

    def parse(self, seq: List[str], row: int = 0) -> Optional[Tuple[List, int]]:
        """
        Parse the sequence by repeating the pattern a specified number of times.

        Args:
            seq (List[str]): The sequence of strings to parse.
            row (int): The row index to start parsing from.

        Returns:
            Optional[Tuple[List, int]]: The parsed result and the next row index, or None if the minimum repetitions are not met.
        """
        count = 0
        result = []

        while self.max_count is None or count < self.max_count:
            r = self.content.parse(seq, row)
            if r is None:
                break
            parsed, next_row = r

            if self.sep is not None and count >= 1:
                # Add separator between repetitions if specified
                result.append(self.sep)

            consume_some = next_row > row

            result.extend(parsed)
            row = next_row
            count += 1

            # Stop parsing if no characters were consumed and min_count is satisfied
            if not consume_some and count >= self.min_count:
                break

        if count < self.min_count:
            return None
        if self.repl is not None:
            return self.repl, row
        elif self.fmt is not None:
            replaced = self.fmt(*result)
            assert isinstance(replaced, list)
            return replaced, row
        else:
            return result, row


class R(Pattern):
    """
    A pattern for matching regular expressions.
    """

    def __init__(
        self,
        regex_pattern: str,
        flags: Optional[re.RegexFlag] = None,
        repl: Optional[List] = None,
        fmt: Optional[Callable[[str], List]] = None,
        fmt_match: Optional[Callable[[re.Match], List]] = None,
        fmt_group: Optional[Callable[[Callable[[int], str]], List]] = None,
    ):
        """
        Initialize the R pattern.

        Args:
            regex_pattern (str): The regular expression pattern to match.
            flags (re.RegexFlag, optional): Optional flags for the regular expression.
            repl (List, optional): A replacement list to return instead of the parsed result, if provided.
            fmt (Callable[[str], List], optional): A formatting function that takes the matched string.
            fmt_match (Callable[[re.Match], List], optional): A formatting function that takes the Match object.
            fmt_group (Callable[[Callable[[int], str]], List], optional): A formatting function that takes a group accessor function.
        """
        self.flags = flags
        if self.flags is not None:
            self.regex = re.compile(regex_pattern, self.flags)
        else:
            self.regex = re.compile(regex_pattern)
        fmt_count = sum((1 if f is not None else 0) for f in (repl, fmt, fmt_match, fmt_group))
        assert fmt_count <= 1, "repl, fmt, fmt_match, fmt_group are mutually exclusive"
        assert repl is None or isinstance(repl, list)
        self.repl = repl
        self.fmt = fmt
        self.fmt_match = fmt_match
        self.fmt_group = fmt_group

    def parse(self, seq: List[str], row: int = 0) -> Optional[Tuple[List, int]]:
        """
        Parse the sequence by matching the regular expression.

        Args:
            seq (List[str]): The sequence of strings to parse.
            row (int): The row index to start parsing from.

        Returns:
            Optional[Tuple[List, int]]: The parsed result and the next row index, or None if the regular expression does not match.
        """
        if row >= len(seq):
            return None
        text = seq[row]
        m = self.regex.match(text)
        if m is None:
            return None

        if self.repl is not None:
            return self.repl, row + 1
        elif self.fmt is not None:
            replaced = self.fmt(text)
            assert isinstance(replaced, list)
            return replaced, row + 1
        elif self.fmt_match is not None:
            replaced = self.fmt_match(m)
            assert isinstance(replaced, list)
            return replaced, row + 1
        elif self.fmt_group is not None:
            replaced = self.fmt_group(m.group)
            assert isinstance(replaced, list)
            return replaced, row + 1
        else:
            return [text], row + 1


class T(Pattern):
    """
    A pattern for matching a specific string.
    """

    def __init__(
        self,
        text: str,
        repl: Optional[List] = None,
    ):
        """
        Initialize the T pattern.

        Args:
            text (str): The exact string to match.
            repl (List, optional): A replacement list to return instead of the parsed result, if provided.
        """
        self.text = text
        assert repl is None or isinstance(repl, list)
        self.repl = repl

    def parse(self, seq: List[str], row: int = 0) -> Optional[Tuple[List, int]]:
        """
        Parse the sequence by matching the exact string.

        Args:
            seq (List[str]): The sequence of strings to parse.
            row (int): The row index to start parsing from.

        Returns:
            Optional[Tuple[List, int]]: The parsed result and the next row index, or None if the string does not match.
        """
        if row >= len(seq):
            return None
        text = seq[row]
        if text != self.text:
            return None

        if self.repl is not None:
            return self.repl, row + 1
        else:
            return [text], row + 1
