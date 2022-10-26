#!/bin/sh
#SBATCH --partition=serial_requeue,shared
#SBATCH -n 1
#SBATCH --mem=6000
#SBATCH --time=08:00:00
#SBATCH -J snaptrain
#SBATCH -e snaptrain_%A.err
#SBATCH -o snaptrain_%A.out

MAKER_IMAGE=/n/singularity_images/informatics/maker/maker_3.01.03--pl5262h8f1cd36_2-repbase.sif
datatore_index=$1
singularity exec --cleanenv ${MAKER_IMAGE} maker2zff -n -d $datatore_index
