#!/bin/sh
#SBATCH -n 8
#SBATCH -N 1
#SBATCH -t 420  #Runtime in minutes
#SBATCH -e stie_%A.e
#SBATCH -o stie_%A.o
#SBATCH -J stringtie
#SBATCH -p shared,holy-cow,holy-smokes  #Partition to submit to
#SBATCH --mem=48000 #Memory per node in MB
module purge
module load python
source activate stringtie
echo "the sorted bamfile is $1"
fileprefix=`echo $1 |sed 's/.bam//g'`
stringtie $1  -p 8 -o ${fileprefix}_stringtie.gtf
