#!/bin/sh
#SBATCH -n 1
#SBATCH -t 45 #Runtime in minutes
#SBATCH -e gfastats_%A.e
#SBATCH -o gfastats_%A.o
#SBATCH -J gfastats
#SBATCH -p serial_requeue,shared,holy-smokes  #Partition to submit to
#SBATCH --mem=12000 #Memory per node in MB
echo -n "Starting job on "
module purge
module load python
source activate gfastats
genomefasta=$1

echo "genome fasta == $genomefasta"

gfastats $genomefasta
