#!/bin/bash
#SBATCH -J BUSCO
#SBATCH -N 1                   
#SBATCH -n 16                  
#SBATCH -t 48:00:00              
#SBATCH -p holy-info,holy-smokes,holy-cow,shared      
#SBATCH --mem=16000            
#SBATCH -o BUSCO.%A.out  
#SBATCH -e BUSCO.%A.err  

module purge
#module load Anaconda3/2020.11
module load python
source activate busco_5.1.2
tscriptsfa=$1
outstring=`echo $tscriptsfa |sed 's/.fasta//g'`

busco -c 16 -m genome --long --augustus --augustus_species heliconius_melpomene1 --augustus_parameters='--progress=true' -o busco_${outstring} -i $tscriptsfa -l /n/holyscratch01/external_repos/INFORMATICS/BUSCO/lepidoptera_odb10


