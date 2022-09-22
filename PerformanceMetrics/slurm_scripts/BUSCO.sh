#!/bin/bash
#SBATCH -J BUSCO
#SBATCH -N 1                   
#SBATCH -n 16                  
#SBATCH -t 12:00:00              
#SBATCH -p shared      
#SBATCH --mem=16000            
#SBATCH -o BUSCO.%A.out  
#SBATCH -e BUSCO.%A.err  

module purge
module load python
source activate busco_5.0.0
tscriptsfa=$1
outstring=`echo $tscriptsfa |sed 's/.fa//g' |sed 's/.fna//g'`

busco -c 16 -m transcriptome -o busco_${outstring} -i $tscriptsfa -l /n/holyscratch01/external_repos/INFORMATICS/BUSCO/arthropoda_odb10



