#!/bin/sh
#SBATCH -p holy-info,shared
#SBATCH -n 1
#SBATCH --mem=140000
#SBATCH --time=48:00:00
#SBATCH -e bam2hints_%A.e
#SBATCH -o bam2hints_%A.o
#SBATCH -J bam2hints

#set -o errexit -o nounset -o xtrace
inbam=$1
echo "inbam is $inbam"

bamprefix=`echo $inbam |sed 's/.bam//g'`
echo "bamprefix is $bamprefix"

/n/holyscratch01/informatics/nweeks/bam2hints --in $inbam --out ${bamprefix}.hints.gff 
