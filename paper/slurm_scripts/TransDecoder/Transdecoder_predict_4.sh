#!/bin/bash
#SBATCH -n 1
#SBATCH --mem 15000
#SBATCH -p serial_requeue,shared
#SBATCH -o tdecoder_predict_%A.out
#SBATCH -e tdecoder_predict_%A.err
#SBATCH -t 16:00:00
#SBATCH -J tdpred


module purge
module load python
source activate transdecoder_5.5.0

transcriptomefasta=$1
blastphits=$2
TransDecoder.Predict -t $transcriptomefasta --single_best_only --retain_blastp_hits $blastphits


