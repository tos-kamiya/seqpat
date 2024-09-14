from typing import List
from .patterns import Pattern


def gsub(pattern: Pattern, seq: List[str], drop: bool = False, strict: bool = False) -> List:
    """
    Perform a global substitution on the sequence using the provided pattern.

    This function attempts to match each element in the sequence with the given pattern.
    If a match is found, the matched elements are replaced according to the pattern's rules.
    If no match is found, the behavior depends on the `drop` and `strict` flags.

    Args:
        pattern (Pattern): The pattern to use for matching and substitution.
        seq (List[str]): The sequence of strings to process.
        drop (bool): If True, unmatched elements are dropped. If False, unmatched elements are kept in the result.
        strict (bool): If True, raises an exception if no match is found for any element.
                       If False, continues processing even if no match is found.

    Returns:
        List: The sequence with matched elements replaced according to the pattern.

    Raises:
        RuntimeError: If `strict` is True and a pattern does not match an element in the sequence.

    Note:
        The `drop` and `strict` options are mutually exclusive and cannot both be True.
    """
    assert not (drop and strict), "drop and strict are mutually exclusive."
    replaced_seq = []
    row = 0
    while row < len(seq):
        r = pattern.parse(seq, row)
        if r is None:
            if strict:
                raise RuntimeError(f"Pattern not matched at row {row}")
            if not drop:
                replaced_seq.extend(seq[row : row + 1])
            row += 1
        else:
            result, next_row = r
            assert next_row >= row

            replaced_seq.extend(result)

            if next_row == row:
                row += 1  # Ensure we move to the next row even if no match is found
            else:
                row = next_row
    return replaced_seq


def split_by(delimiter_pattern: Pattern, seq: List[str], keep_delimiters: bool = False) -> List[List]:
    """
    Split the sequence into sublists based on the delimiter pattern.

    This function splits the input sequence at points where the delimiter pattern matches.
    The sequence is split into sublists, and the behavior of the delimiter (whether it is kept or dropped)
    can be controlled using the `keep_delimiters` flag.

    Args:
        delimiter_pattern (Pattern): The pattern used to identify the delimiters in the sequence.
        seq (List[str]): The sequence of strings to split.
        keep_delimiters (bool): If True, the delimiters are included in the result.
                                If False, the delimiters are dropped.

    Returns:
        List[List]: A list of sublists, where the sequence has been split at the delimiter points.

    Raises:
        RuntimeError: If the delimiter pattern matches an empty sequence, indicating an invalid delimiter match.
    """
    splitted = []
    row = 0
    while row < len(seq):
        # Look for the delimiter pattern in the sequence
        for row_delimiter_found in range(row, len(seq)):
            r = delimiter_pattern.parse(seq, row_delimiter_found)
            if r is not None:
                break
        else:
            # No more delimiters found, append the remaining part of the sequence
            splitted.append(seq[row:])
            return splitted

        result, next_row = r
        if next_row == row_delimiter_found:
            raise RuntimeError(f"Delimiter pattern matched an empty sequence at row {row_delimiter_found}")

        assert next_row > row_delimiter_found >= row

        # Append the part of the sequence before the delimiter
        splitted.append(seq[row:row_delimiter_found])

        if keep_delimiters:
            # If keeping delimiters, append the delimiter result
            splitted.append(result)

        # Move to the next part of the sequence after the delimiter
        row = next_row

    # Ensure the last element is not a delimiter by appending an empty list at the end
    splitted.append([])  # ensure the last element is not a delimiter
    return splitted
