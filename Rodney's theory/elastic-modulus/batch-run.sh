#!/bin/bash

# x_w=(0.01 0.03 0.06 0.15 0.25 0.35 0.50)
x_w=($(seq 0.40 0.10 0.90))
ALLOY="quaternary"      # "binary" or "quaternary"

if [ "$ALLOY" == "binary" ]; then
    output="output2.txt"
    modulus="modulus2.txt"
    potential="potential2.mod"
    init="init2.mod"
    result="avg_modulus2.txt"
else
    output="output4.txt"
    modulus="modulus4.txt"
    potential="potential4.mod"
    init="init4.mod"
    result="avg_modulus4.txt"
fi

rm ${output} ${modulus} ${result}

seed=(61318 12532 84113 51347 98421)
for i in ${!x_w[@]}; do
	prop0=${x_w[$i]}
	for j in ${!seed[@]}; do
		random0=${seed[$j]}
        mpiexec.openmpi -np 8 lmp_g++_openmpi -var output ${output} -var modulus ${modulus} -var potential ${potential} -var init ${init} -var prop ${prop0} -var r ${random0} -in in.elastic
        rm *.data
    done
done

bash calc.sh ${modulus} ${result}
