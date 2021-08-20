#!/bin/sh
# Customize --time and --partition as appropriate.
# --exclusive --mem=0 allocates all CPUs and memory on the node.
#SBATCH --partition=holy-info,holy-smokes,holy-cow,shared
#SBATCH --nodes=1
#SBATCH --mem=0
#SBATCH --exclusive
#SBATCH -J brakrnaseq
#SBATCH --time=2-23:00


singularity exec --cleanenv /n/singularity_images/informatics/braker/braker_2021-06-14.sif cp -Rs /opt/augustus/config augustus_config
singularity exec --no-home \
                 --home /opt/gm_key \
                 --cleanenv \
                 --env AUGUSTUS_CONFIG_PATH=${PWD}/augustus_config\
                 /n/singularity_images/informatics/braker/braker_2021-06-14.sif braker.pl --cores 48 \
                 --species=danaus_plexippus --genome=dple.fa \
                 --prot_seq=/n/holyscratch01/informatics/genome_annotation_evaluation/heliconines/hmel_refdata/headcleaned_Hmel2_braker_20170203.proteins.renamed.Hm.faa \
                 --softmasking 
