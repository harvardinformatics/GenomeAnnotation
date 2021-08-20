#!/bin/sh
#SBATCH -p holy-info,shared
#SBATCH -n 1
#SBATCH --mem=175000
#SBATCH --time=6-23:00:00
#SBATCH -e filtbam_%A.e
#SBATCH -o filtbam_%A.o
#SBATCH -J filtbam

inbam=$1
echo "inbam is $inbam"

bamprefix=`echo $inbam |sed 's/.bam//g'`
echo "bamprefix is $bamprefix"

singularity exec --cleanenv /n/holyscratch01/informatics/genome_annotation_evaluation/heliconines/comparative_augustus/hints/oneapi-hpckit_2021.2-devel-centos8.sif /n/holyscratch01/informatics/genome_annotation_evaluation/heliconines/comparative_augustus/hints/filterBam-zlib-ng-2 --in $1 --out filtered_${1} --uniq --paired --pairwiseAlignment  
