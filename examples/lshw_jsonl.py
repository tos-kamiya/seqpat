# Extract some properties of `lshw` output entities and print them in JSON-line format.
# This script reads the output of the `lshw` command from stdin, extracts certain properties
# (description, product, vendor, logical name), and prints them in JSON format, one entity per line.
#
# Usage:
#   $ env LC_ALL=C lshw | python3 examples/lshw_jsonl.py
#   If using the `uv` package manager:
#   $ env LC_ALL=C lshw | uv run examples/lshw_jsonl.py

import json
import sys
from seqpat import R, gsub, split_by

# Define the pattern for detecting the start of a new hardware entity section.
# This pattern matches lines that start with zero or more spaces followed by "*-",
# which is how `lshw` indicates a new section.
delim_pat = R(r"^\s*\*-(.*)$")

# Define the pattern for extracting specific properties within each entity.
# This pattern matches lines that contain the following properties:
# - description: The description of the hardware component.
# - product: The product name or model.
# - vendor: The manufacturer or vendor.
# - logical name: The logical name of the device in the system.
# The pattern captures the property name and its value.
desc_pat = R(
    r"^\s*(description|product|vendor|logical[ ]name):\s+(.*)$",
    fmt_group=lambda g: [(g(1), g(2))],
)

# Read lines from stdin, removing any trailing newlines or carriage returns.
# This step ensures that the input is clean and ready for parsing.
lines = [line.rstrip("\r\n") for line in sys.stdin]

# Split the input into separate entities based on the delimiter pattern.
# Each entity represents a hardware component in the `lshw` output.
entities = split_by(delim_pat, lines)

# Process each entity one by one.
for entity in entities:
    # Use the description pattern to extract relevant properties from the entity.
    parsed = gsub(desc_pat, entity, drop=True)

    # Convert the parsed result (list of key-value pairs) into a dictionary.
    d = dict(parsed)

    # Only print the entity if it contains a "product" property.
    # This filters out entities that may not have enough useful information.
    if "product" in d:
        # Convert the dictionary to a JSON object and print it.
        # Each entity is printed as a separate JSON line.
        print(json.dumps(d))
