#!/bin/sh
# Customize --time and --partition as appropriate.
# --exclusive --mem=0 allocates all CPUs and memory on the node.
#SBATCH --partition=shared
#SBATCH --nodes=1
#SBATCH -n 24
#SBATCH --mem=75000
#SBATCH -J brakrnaseq
#SBATCH --time=23:00:00

singularity exec --cleanenv /n/singularity_images/informatics/braker/braker_2021-06-14.sif cp -Rs /opt/augustus/config augustus_config
singularity exec --no-home \
                 --home /opt/gm_key \
                 --cleanenv \
                 --env AUGUSTUS_CONFIG_PATH=${PWD}/augustus_config\
                 /n/singularity_images/informatics/braker/braker_2021-06-14.sif braker.pl --cores 24 \
                 --bam=dple_hisat-star_merged.bam \
                 --species=danaus_plexippus --genome=dple.fa \
                 --softmasking 
