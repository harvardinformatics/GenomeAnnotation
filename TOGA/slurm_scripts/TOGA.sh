#!/bin/bash
#SBATCH -J toga
#SBATCH -n 1                  
#SBATCH -t 12:00:00              
#SBATCH -p shared      
#SBATCH --mem=3000           
#SBATCH -o toga.%A.out  
#SBATCH -e toga.%A.err  

module purge
module load python
soure activate TOGA

chainfile=$1
targetCDSbed=$2
target2bit=$3
source2bit=$4
outname=$5
isoforms=$6 # tsv file with CDS gene and transcript id as columns

/n/home_rc/afreedman/software/TOGA/toga.py $chainfile $targetCDSbed $target2bit $source2bit --kt --pn $outname -i $isoforms  --nc /n/home_rc/afreedman/software/TOGA/my_nextflow_config_files --cb 10,100 --cjn 750 
