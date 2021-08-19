#!/bin/sh
#SBATCH -n 8
#SBATCH -N 1
#SBATCH -t 360  #Runtime in minutes
#SBATCH -e stie_merge_%A.e
#SBATCH -o stie_merge_%A.o
#SBATCH -J stmerge
#SBATCH -p shared,holy-smokes,holy-cow  #Partition to submit to
#SBATCH --mem=20000 #Memory per node in MB
module purge
module load python
source activate stringtie
speciesname=$1
aligner=$2
gtflist=$(ls *gtf)

stringtie -p 8 --merge $gtflist -o ${speciesname}_${aligner}_stringtie_merged.gtf
