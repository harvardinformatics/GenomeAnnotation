#!/bin/sh
#SBATCH -p holy-info,shared
#SBATCH -n 1
#SBATCH --mem=12000
#SBATCH --time=96:00:00
#SBATCH -e bam2wig_%A.e
#SBATCH -o bam2wig_%A.o
#SBATCH -J bam2wig

#set -o errexit -o nounset -o xtrace
inbam=$1
echo "inbam is $inbam"

bamprefix=`echo $inbam |sed 's/.bam//g'`
echo "bamprefix is $bamprefix"

AUGUSTUS_IMAGE="/n/singularity_images/informatics/augustus/augustus_3.4.0-afreedman-build.sif"
singularity exec --cleanenv ${AUGUSTUS_IMAGE} bam2wig $1 > ${bamprefix}.wig 

