#!/bin/sh
# Customize --time and --partition as appropriate.
# --exclusive --mem=0 allocates all CPUs and memory on the node.
#SBATCH --partition=holy-info,holy-smokes,holy-cow
#SBATCH -n 1
#SBATCH --mem 6000
#SBATCH -e aln2hints_%A.e
#SBATCH -o aln2hints_%A.o
#SBATCH -J aln2hints
#SBATCH --time=06:00:00

SINGULARITY_IMAGE="/n/singularity_images/informatics/braker/braker_2021-06-14.sif"
singularity exec --cleanenv ${SINGULARITY_IMAGE} align2hints.pl --in align_gth/gth.concat.aln --out=prot.hints --prg=gth
