#!/bin/sh
#SBATCH -p shared,serial_requeue
#SBATCH -n 1
#SBATCH --mem=24000
#SBATCH --time=36:00:00
#SBATCH -e filterbam_%A.e
#SBATCH -o filterbam_%A.o
#SBATCH -J filerbam

#set -o errexit -o nounset -o xtrace
# $1 == namesorted pe bam

AUGUSTUS_IMAGE="/n/singularity_images/informatics/augustus/augustus_3.4.0-afreedman-build.sif"
singularity exec --cleanenv ${AUGUSTUS_IMAGE} filterBam --in $1 --out filtered_${1} --uniq --paired --pairwiseAlignment 

