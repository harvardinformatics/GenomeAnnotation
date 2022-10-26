#!/bin/bash
#SBATCH -J BUSCOaugtrain
#SBATCH -N 1                   
#SBATCH -n 16                  
#SBATCH -t 48:00:00              
#SBATCH -p shared      
#SBATCH --mem=16000            
#SBATCH -o BUSCO_augustus_train.%A.out  
#SBATCH -e BUSCO_augustus_train.%A.err  

module purge
module load python
source activate busco_5.1.2
tscriptsfa=$1
outstring=`basename $tscriptsfa |sed 's/.fasta//g'`
speciesmodel=$2
lineage_database=$3


busco -c 16 -m genome --long --augustus --augustus_species $speciesmodel --augustus_parameters='--progress=true' -o busco_${outstring} -i $tscriptsfa -l $lineage_database


