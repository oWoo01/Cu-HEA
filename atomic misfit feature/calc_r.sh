#!/usr/bin/bash

a_array=(0 10 11 12 13)

temp_file="merged_radius.txt"
> "$temp_file"

for i in ${a_array[@]}; do
    column=$(tail -n +10 "voro_${i}.dump" | awk '{volumn=$NF; radius=(3*volumn/4/3.1415926)^(1/3); print radius}')
    echo "$column" > "$temp_file"
    awk '{$1=$1}1' "$temp_file" > "radius_$i.txt"
done
rm $temp_file
