#!/bin/bash

FILE="/temp/temp.c"
TMP_FILE=$(mktemp)

# Format the file and save the output to a temporary file
clang-format --style="{BasedOnStyle: LLVM, IndentWidth: 4, UseTab: Never}" $FILE > $TMP_FILE

# Compare the original file with the formatted file
if ! diff -u $FILE $TMP_FILE > /dev/null; then
    echo "Formatting error in $FILE:"
    diff -u $FILE $TMP_FILE
    rm $TMP_FILE
    exit 1
else
    echo "No formatting errors found."
    rm $TMP_FILE
    exit 0
fi