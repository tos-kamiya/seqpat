# Converts `apt show <package>` output to JSON format.
# This script reads the output of the `apt show` command from stdin,
# parses it, and converts it into a JSON object. It handles continuation
# lines and removes empty lines during the parsing process.
#
# Usage:
#   $ apt show <package> | python3 examples/apt_show_json.py
#   If using the `uv` package manager:
#   $ apt show <package> | uv run examples/apt_show_json.py

import json
import sys
from seqpat import R, gsub

# Read lines from stdin, strip newlines
# This reads the input line by line and removes any carriage return or newline characters.
lines = [line.rstrip("\r\n") for line in sys.stdin]

# Define the pattern to match relevant lines
# The pattern consists of three parts:
# 1. A line with key-value pairs in the format `Key: Value`
#    where the key contains alphanumeric characters and hyphens.
# 2. A continuation line that starts with a space and continues the previous value.
# 3. An empty line, which will be ignored during parsing.
pattern = (
    R(r"^([A-Za-z0-9-]+): (.*)$", fmt_group=lambda g: [(g(1), g(2))])  # Key: Value lines
    | R(r"^ ( *[^ ].*)$", fmt=lambda s: [(" ", s)])  # Continuation lines (indented)
    | R(r"^\s*$", repl=[])  # Remove empty lines
)

# Parse the lines using the defined pattern
# The `gsub` function applies the pattern to the input lines, replacing matches
# according to the pattern's rules. If a line does not match, the `strict` flag
# ensures that an error is raised.
parsed = gsub(pattern, lines, strict=True)

# Build the dictionary data structure
# This loop processes the parsed result and builds a dictionary (`data`).
# If a continuation line is encountered (key is " "), it appends the value to
# the last key's value. Otherwise, it adds a new key-value pair to the dictionary.
data = {}
last_k = None
for k, v in parsed:
    if k == " ":  # Continuation line: append the value to the last key
        data[last_k] += "\n" + v
        continue
    data[k] = v  # Add new key-value pair
    last_k = k

# Output the result as JSON
# The final dictionary is converted to a JSON string with indentation for readability.
print(json.dumps(data, indent=4))
