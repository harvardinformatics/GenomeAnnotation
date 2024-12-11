#!/bin/sh
#SBATCH -p serial_requeue,shared
#SBATCH -n 16
#SBATCH -N 1
#SBATCH --mem=32000
#SBATCH --time=16:00:00
#SBATCH -e mafsplit_%A.e
#SBATCH -o mafsplit_%A.o
#SBATCH -J mafsplit

set -o errexit -o nounset -o xtrace

AUGUSTUS_IMAGE="/n/singularity_images/informatics/augustus/augustus_3.4.0-afreedman-build.sif"
CHUNKSIZE=2500000
OVERLAP=500000

halfile=$1
refspecies=$2
nosplitlist=$3

echo "halfile=${halfile}"
echo "refspecies=${refspecies}"
echo "nosplitlist=${nosplitlist}"

singularity exec --cleanenv ${AUGUSTUS_IMAGE} /root/augustus/scripts/hal2maf_split.pl --halfile $halfile --refGenome $refspecies --cpus 8 --chunksize $CHUNKSIZE --overlap $OVERLAP --no_split_list $nosplitlist --outdir mafs 
