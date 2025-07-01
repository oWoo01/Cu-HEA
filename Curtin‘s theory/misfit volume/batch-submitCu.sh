#!/usr/bin/bash
c_array=($(seq 10 10 90))
ran_array=(48291 97294 34582 83472 56921)
for a in ${c_array[@]}; do
	for random in ${ran_array[@]}; do
		cat > submit.sh <<EOF
#!/bin/bash
#SBATCH -J lc-$a 
#SBATCH -p tyhcnormal 
#SBATCH -N 1 # num of nodes 
#SBATCH --ntasks-per-node=16
#SBATCH -o log/log.$a

module purge
source /work/home/jyzhang/apprepo/lammps/stable.29Aug2024-intelmpi2021/scripts/env.sh
export UCX_IB_ADDR_TYPE=ib_global
export I_MPI_PMI_LIBRARY=/opt/gridview/slurm/lib/libpmi.so

srun --mpi=pmix_v3 lmp_mpi -var random ${random} -var a ${a} -in in.lc_Cu

EOF
		sbatch submit.sh
	done
done
