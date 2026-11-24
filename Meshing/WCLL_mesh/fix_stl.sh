#!/bin/bash

file="$1"

if [ ! -f "$file" ]; then
    echo "File not found: $file"
    exit 1
fi

name=$(basename "$file" .stl)

tmp=$(mktemp)

# Remove all internal endsolid/solid pairs
sed '/^endsolid[[:space:]].*/{
N
/^endsolid[[:space:]].*\nsolid[[:space:]].*/d
}' "$file" > "$tmp"

# Fix first and last lines
sed -i "1s|.*|solid $name|" "$tmp"
sed -i "\$s|.*|endsolid $name|" "$tmp"

mv "$tmp" "$file"

echo "Fixed $file" 
