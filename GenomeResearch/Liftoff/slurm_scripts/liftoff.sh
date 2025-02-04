#!/bin/bash
#SBATCH -J liftoff
#SBATCH -N 1                   
#SBATCH -n 24                  
#SBATCH -t 12:00:00              
#SBATCH -p # add your available partition name(s) here      
#SBATCH --mem=96000            
#SBATCH -o liftoff.%A.out  
#SBATCH -e liftoff.%A.err  

module purge
module load python
source activate liftoff

ref_genome=$1
ref_gff=$2
target_genome=$3

liftoff -p 24 -polish -g $ref_gff -o liftoff_flank0.2_d3.gff3 -flank 0.2 -d 3 $target_genome $ref_genome
