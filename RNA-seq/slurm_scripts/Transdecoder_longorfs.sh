#!/bin/bash
#SBATCH -n 1
#SBATCH --mem 5000
#SBATCH -p serial_requeue,shared,holy-smokes
#SBATCH -o tdecod_longorfs_%A.out
#SBATCH -e tdecod_longorfs_%A.err
#SBATCH -t 23:00:00
#SBATCH -J tdeclongorfs

module purge
module load python
source activate transdecoder_5.5.0

transcriptfasta=$1
echo "params: $transcriptfasta"

TransDecoder.LongOrfs -t $transcriptfasta

## if your RNA-seq data is strand-specific use the below instead

# TransDecoder.LongOrfs -S -t $transcriptfasta
