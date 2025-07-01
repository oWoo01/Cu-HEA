#!/usr/bin/bash

c_array=($(seq 10 10 90))
array=(0 1 2 3)
ele_array=(Fe Ni Cr Co)
mass_array=(55.847 58.690 51.960 58.933)
ran_array=(48291 97294 34582 83472 56921)
for i in ${!array[@]}; do
	E4=${ele_array[$i]}
	remaining=("${array[@]:0:$i}" "${array[@]:$((i+1))}")
	echo "$i ${remaining[@]}"
	E1=${ele_array[${remaining[0]}]}
	E2=${ele_array[${remaining[1]}]}
	E3=${ele_array[${remaining[2]}]}
	m1=(${mass_array[${remaining[0]}]}) 
	m2=(${mass_array[${remaining[1]}]})
	m3=(${mass_array[${remaining[2]}]})
	m4=(${mass_array[$i]})
	echo "${E1} ${E2} ${E3} ${E4} ${m[@]}"
	for a in ${c_array[@]}; do
		for random in ${ran_array[@]}; do
			cat > submit.sh <<EOF
#!/bin/bash
#SBATCH -J lc-$i-$a 
#SBATCH -p tyhcnormal 
#SBATCH -N 1 # num of nodes 
#SBATCH --ntasks-per-node=16
#SBATCH -o log/log.$i-$a

module purge
source /work/home/jyzhang/apprepo/lammps/stable.29Aug2024-intelmpi2021/scripts/env.sh
export UCX_IB_ADDR_TYPE=ib_global
export I_MPI_PMI_LIBRARY=/opt/gridview/slurm/lib/libpmi.so

srun --mpi=pmix_v3 lmp_mpi -var i $i -var random ${random} -var a ${a} -var E1 ${E1} -var E2 ${E2} -var E3 ${E3} -var E4 ${E4} -var m1 ${m1} -var m2 ${m2} -var m3 ${m3} -var m4 ${m4} -in in.lc

EOF
		sbatch submit.sh
		done
	done
done
