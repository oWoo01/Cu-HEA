#!/bin/bash

temp_file="merged_columns.txt"
c=$1

> "$temp_file"

first_file=true
ls dump/gsf_${c}_*.dump | while read -r file; do
    step=$(echo "$file" | cut -d_ -f3 | cut -d. -f1)
    echo "$step ${file}"
done | sort -n | awk '{print $2}' | while read -r file; do
    if $first_file; then
        column=$(tail -n +10 "$file" | awk '{print $1, $3, $4, $5, $6, $NF}')
	echo "$column" > "$temp_file"
        first_file=false
    else
    	column=$(tail -n +10 "$file" | awk '{print $NF}')
        paste "$temp_file" <(echo "$column") > temp_file && mv temp_file "$temp_file"
    fi
done

awk '{$1=$1}1' "$temp_file" > "gsfe/gsfe_atom_${c}.txt" 

