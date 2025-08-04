#!/bin/bash

infile=$1
outfile=$2

sum_mu=0
sum_nu=0
count=0
line_num=0

while read -r line;do
	second_column=$(echo "$line" | awk '{print $2}')
	sum_mu=$(echo "$sum_mu+$second_column" | bc)
    
    fourth_column=$(echo "$line" | awk '{print $4}')
    sum_nu=$(echo "$sum_nu+$fourth_column" | bc)
	((count++))

	if ((count == 5)); then
		average_mu=$(echo "$sum_mu/5" | bc -l)
		average_nu=$(echo "$sum_nu/5" | bc -l)
        prop=$(echo "$line" | awk '{print $1}')
		echo "$prop $average_mu $average_nu" >> $outfile
		
		sum_mu=0
        sum_nu=0
		count=0
	fi

	((line_num++))
done < "$infile"
