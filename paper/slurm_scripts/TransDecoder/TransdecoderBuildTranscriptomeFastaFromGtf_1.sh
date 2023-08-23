#!/bin/bash
#SBATCH -n 1
#SBATCH --mem 5000
#SBATCH -p serial_requeue,shared
#SBATCH -o tdec_gtf2transcriptfasta_%A.out
#SBATCH -e tdec_gtf2transcriptfasta_%A.err
#SBATCH -t 01:00:00
#SBATCH -J gtf2fasta

module purge
module load python
source activate transdecoder_5.5.0

gtfin=$1
genomefasta=$2
tsfastaout=$3

echo "args: $gtfin $genomefasta $tsfastaout"
gtf_genome_to_cdna_fasta.pl $gtfin $genomefasta > $tsfastaout 
