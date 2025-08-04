#!/usr/bin/bash

alloy="quaternary"   # "binary" or "quaternary"
BINARY=("Nb" "W")
QUATERNARY=("Nb" "Mo" "Ta" "W")

# W_array=(0.01 0.03 0.06 0.15 0.25 0.35 0.50)
# W_array=($(seq 0.4 0.1 0.9))
W_array=0.4

DC=0.01     # disturbance

Ntotal=$(awk 'NR==3 {print $1}' "ini.lmp")    # total number of atoms in ini.lmp

OUTDIR="results"
mkdir -p "$OUTDIR"

if [ "$alloy" == "binary" ]; then
    elements=("${BINARY[@]}")
else
    elements=("${QUATERNARY[@]}")
fi

nelem=${#elements[@]}

for w in "${W_array[@]}"; do 
    echo "----> W = $w"

    if [ "$alloy" == "binary" ]; then
        c_Nb=$(echo "scale=4; 1 - $w" | bc)
        comps=($c_Nb $w)
    else
        base=$(echo "scale=4; (1 - $w)/3"| bc)
        comps=($base $base $base $w)
    fi

    basedir="$OUTDIR/${alloy}/W$(printf "%.2f" $w)"
    mkdir -p "$basedir"
    compfile="$basedir/lattice-constant.txt"

    for ((alpha=0; alpha<$nelem; alpha++)); do
        for delta in "pos" "neg"; do
            perturbed=("${comps[@]}")
            if [ "$delta" == "pos" ]; then
                sign=1
                dir="dc_pos"
                change=$DC
            else
                sign=-1
                dir="dc_neg"
                change="-$DC"
            fi

            perturbed[$alpha]=$(echo "scale=5; ${perturbed[$alpha]} + $change" | bc)

           if [ $alloy == "binary" ]; then
               newc=$(echo "scale=5; 1 - ${perturbed[$alpha]}" | bc)
           elif [ $alpha -eq $(($nelem-1)) ]; then
               newc=$(echo "scale=5; (1 - ${perturbed[$alpha]}) / ($nelem - 1)" | bc)
           else
               newc=$(echo "scale=5; (1 - $w - ${perturbed[$alpha]}) / ($nelem - 2)" | bc)
           fi

            for ((i=0; i<$(($nelem-1)); i++)); do
                if [ $i -ne $alpha ]; then
                    perturbed[$i]=$newc
                fi
            done

           name="${elements[$alpha]}_${delta}"
           echo "${name}" >> "$compfile"
           logfile="$basedir/log_${name}.lmp"

           N_array=()
           for ((i=0; i<$nelem; i++)); do
                Ni=$(printf "%.0f" "$(echo "${perturbed[$i]} * $Ntotal + 0.5" | bc -l)")
                N_array+=($Ni)
           done

           if [ "${alloy}" == "binary" ];  then 
               mpiexec.openmpi -np 8 lmp_g++_openmpi -var N2 ${N_array[0]} -var filename $compfile -in in.lc2 -log ${logfile}
           else
               mpiexec.openmpi -np 8 lmp_g++_openmpi -var N2 ${N_array[1]} -var N3 ${N_array[2]} -var N4 ${N_array[3]} -var filename $compfile -in in.lc4 -log ${logfile}
           fi

        done
    done
done


