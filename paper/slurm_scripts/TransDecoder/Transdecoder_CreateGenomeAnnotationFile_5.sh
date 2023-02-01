#!/bin/bash
#SBATCH -n 1
#SBATCH --mem 15000
#SBATCH -p serial_requeue,shared
#SBATCH -o tdecoder_ts2genome_%A.out
#SBATCH -e tdecoder_ts2genome_%A.err
#SBATCH -t 16:00:00
#SBATCH -J ts2genome


module purge
module load python
source activate transdecoder_5.5.0

transcriptomefasta=$1 # transcriptome fasta created with gtf_genome_to_cdna_fasta.pl == the fasta based upon the rna-seq transcript assembly 
transcriptsgff3=$2 # gff3 file created with gtf_to_alignment_gff3.pl, converted from the rna-seq transcript assembly gtf file (stringtie and scallop generate gtfs) 
cdna_alignment_orf_to_genome_orf.pl ${transcriptomefasta}.transdecoder.gff3 $transcriptsgff3 $transcriptomefasta > ${transcriptomefasta}.transdecoder.genome.gff3

