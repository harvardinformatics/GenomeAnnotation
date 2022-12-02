#!/bin/bash
#SBATCH -J repeatstats
#SBATCH -n 1                  
#SBATCH -t 00:20:00              
#SBATCH -p serial_requeue,shared      
#SBATCH --mem=4000            
#SBATCH -o repeatstats.%A.out  
#SBATCH -e repeatstats.%A.err  

module purge
module load python

gff3=$1
genome=$2
outprefix=$3

conda run -n gffread gffread $gff3 -g $genome -x ${outprefix}_CDS.fasta

conda run -n biopython1.78 python /n/home_rc/afreedman/workspace/GenomeAnnotation/PerformanceMetrics/utilities/WriteRepeatFractionTableFromTranscriptomeFasta.py ${outprefix}_CDS.fasta


