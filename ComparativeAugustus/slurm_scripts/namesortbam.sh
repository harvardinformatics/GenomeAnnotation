#!/bin/sh
#SBATCH -p holy-info,shared
#SBATCH -n 16
#SBATCH -N 1
#SBATCH --mem=24000
#SBATCH --time=23:00:00
#SBATCH -e namesort_%A.e
#SBATCH -o namesort_%A.o
#SBATCH -J namesort

module purge
module load python
source activate samtools

samtools sort -@ 16 -n -o namesorted_${1} -T tmp/ $1
