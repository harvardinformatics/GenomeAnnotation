#!/bin/sh
# Customize --time and --partition as appropriate.
# --exclusive --mem=0 allocates all CPUs and memory on the node.
#SBATCH --partition=serial_requeue,shared,holy-smokes
#SBATCH -N 1
#SBATCH -n 24
#SBATCH --mem=24000
#SBATCH --time=48:00:00
#SBATCH -e genemarkES_%A.err
#SBATCH -o genemarkES_%A.out
#SBATCH -J genemarkES

MAKER_IMAGE=/n/singularity_images/informatics/maker/maker_3.01.03--pl5262h8f1cd36_2-repbase.sif
genomefasta=$1
singularity exec --no-home --home /opt/gm_key --cleanenv ${MAKER_IMAGE} gmes_petap.pl --cores 24 --ES --sequence $genomefasta 
