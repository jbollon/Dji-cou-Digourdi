#!/usr/bin/env bash


while true; do
    read -p "Enter the word to find: " word
    read -p "Enter word to replace: " replace

    echo "$word -> $replace"

    for file in test.txt; do
        # Use Unicode character classes to match word boundaries
        perl -pi -e "s/(?<!\pL)${word}(?!\pL)/$replace/g" $file
    done

    read -p "Do you have further replacements? (y/n): " temp

    if [ "$temp" = "n" ]; then
        break
    fi
done

