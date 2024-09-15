# seqpat

`seqpat` is a Python library designed for flexible and efficient sequence pattern matching, primarily aimed at converting microformats from various command-line tools into JSON Line format.

The motivation behind this project was the idea: *"Wouldn't it be great if we could perform operations on a sequence of strings (i.e., lines of text like in a text file) in the same way we use regular expressions on individual strings (i.e., a sequence of characters)?"*

## Features

- **Pattern Matching**: Match sequences of strings using customizable patterns.
- **Sequence Handling**: Process and parse structured text data efficiently.
- **Customizable Replacements**: Use pattern-based substitutions to transform the input as needed.

## Installation

You can install `seqpat` using `pip`:

```bash
pip install seqpat
```

## Patterns/Utility Functions

The core of `seqpat` is its ability to define and use flexible patterns for text matching. It provides:

- **R**: A pattern that matches regular expressions.
- **gsub**: A function for global substitution based on patterns.
- **split_by**: A function to split a sequence of strings by a delimiter pattern.

For detailed usage, please refer to the Docstrings, and for examples, see the `examples` directory.

## Related Projects

- **[`jc`](https://github.com/kellyjonbrazil/jc)**: A CLI tool and Python library that converts the output of popular command-line tools (e.g., `ls`, `ps`, `ifconfig`) to JSON or JSON Line for easier parsing and automation.

- **[`miller`](https://github.com/johnkerl/miller)**:  A CLI tool for manipulating CSV and JSON files. For example, you can convert a .csv file to .jsonl format with the following command: `$ mlr --icsv --ojsonl cat file.csv`

- **[`csvkit`](https://github.com/wireservice/csvkit)**: A CLI tool for converting CSV files to other formats. For instance, you can convert a .csv file to .jsonl format with `csvjson` command: `$ csvjson --stream file.csv`

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests on the [GitHub repository](https://github.com/tos-kamiya/seqpat).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.txt) file for details.
