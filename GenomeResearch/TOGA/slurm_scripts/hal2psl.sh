#!/bin/bash
#SBATCH -J hal2psl
#SBATCH -n 1                  
#SBATCH -t 23:00:00              
#SBATCH -p shared,serial_requeue,holy-smokes      
#SBATCH --mem=15000           
#SBATCH -o hal2psl.%A.out  
#SBATCH -e hal2psl.%A.err  

module purge
module load hal/20160415-fasrc01
### halLiftover:  Map BED genome interval coordinates between two genomes ###

halfile=$1
querygenome=$2 # name of genome to be annotated in hal file
querybed=$3 # chrom length bed file of query genome
targetgenome=$4 # target is the reference genome to which one is lifting
pslout=$5

halLiftover --outPSL $halfile $querygenome $querybed $targetgenome $pslout 



