#!/bin/bash
#SBATCH -n 1
#SBATCH --mem 5000
#SBATCH -p serial_requeue,shared
#SBATCH -o tdec_gtf2gff3_%A.out
#SBATCH -e tdec_gtf2gff3_%A.err
#SBATCH -t 01:00:00
#SBATCH -J gtf2gff3

module purge
module load python
source activate transdecoder_5.5.0

gtfin=$1
gtfprefix=`echo $gtfin |sed 's/gtf//g'`
echo "params: $gtfin"

gtf_to_alignment_gff3.pl $gtfin > ${gtfprefix}gff3
