#!/bin/sh
#SBATCH -p holy-info,shared
#SBATCH -n 16
#SBATCH -N 1
#SBATCH --mem=24000
#SBATCH --time=23:00:00
#SBATCH -e bamcoordsort_%A.e
#SBATCH -o bamcoordsort_%A.o
#SBATCH -J bamsort

module purge
module load python
source activate samtools

samtools sort -@ 16 -o coordresort_${1} -T tmp/ $1
