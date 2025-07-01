#!/usr/bin/bash

a_array=(0 10 11 12 13)

temp_file1="merged_vol.txt"
temp_file2="merged_pe.txt"
> "$temp_file1"
> "$temp_file2"

for i in ${a_array[@]}; do
    c=$i
    first_file=true
    ls compress/compress_${c}_*.dump | while read -r file; do
        step=$(echo "$file" | cut -d_ -f3 | cut -d. -f1)
        echo "${step} ${file}"
    done | sort -n | awk '{print $2}' | while read -r file; do
        if $first_file; then
            column1=$(tail -n +10 "$file" | awk '{print $1, $(NF-1)}')
            column2=$(tail -n +10 "$file" | awk '{print $1, $NF}')
            echo "$column1" > "$temp_file1"
            echo "$column2" > "$temp_file2"
            first_file=false
        else
            column1=$(tail -n +10 "$file" | awk '{print $(NF-1)}') 
            column2=$(tail -n +10 "$file" | awk '{print $NF}') 
            paste "$temp_file1" <(echo "$column1") > temp_file && mv temp_file "$temp_file1"
            paste "$temp_file2" <(echo "$column2") > temp_file && mv temp_file "$temp_file2"
        fi
    done

    awk '{$1=$1}1' "$temp_file1" > "compress_vol_$c.txt"
    awk '{$1=$1}1' "$temp_file2" > "compress_pe_$c.txt"
done

