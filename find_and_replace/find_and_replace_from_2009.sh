#!/usr/bin/env bash


while true

do
    read -p "Enter the word to find = " word
    read -p "Enter word to replace = " replace

    echo "$word -> $replace"

    for file in 2009.tex 2010.tex 2011.tex 2012.tex 2013.tex 2014.tex 2015.tex 2016.tex 2017.tex 2018.tex 2019.tex; do
    	perl -pi -e "s/(?<!\pL)${word}(?!\pL)/$replace/g" $file
    done

    read -p "Do you have further replacements? (y/n) " temp

    if [ "$temp" ="n" ]; then
        break
    fi

done
