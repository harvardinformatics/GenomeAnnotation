#!/bin/sh
#SBATCH -N 1
#SBATCH -n 16
#SBATCH -t 03:00:00  #Runtime in minutes
#SBATCH -e taco_%A.e
#SBATCH -o taco_%A.o
#SBATCH -J taco
#SBATCH -p holy-info,shared  #Partition to submit to
#SBATCH --mem=32000 #Memory per node in MB

module purge
module load Anaconda3/2020.11
source activate taco
$output_prefix

ls *gtf > gtflist.txt

taco_run -p 16 --gtf-expr-attr RPKM -o $output_prefix gtflist.txt

