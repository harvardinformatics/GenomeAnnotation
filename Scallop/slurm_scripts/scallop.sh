#!/bin/sh
#SBATCH -n 1
#SBATCH -t 420  #Runtime in minutes
#SBATCH -e scallop_%A.e
#SBATCH -o scallop_%A.o
#SBATCH -J scallop
#SBATCH -p shared,holy-cow,holy-smokes  #Partition to submit to
#SBATCH --mem=32000 #Memory per node in MB
module purge
module load python
source activate scallop

echo "the sorted bamfile is $1"
fileprefix=`echo $1 |sed 's/.bam//g'`
scallop -i $1 -o ${fileprefix}_scallop.gtf
