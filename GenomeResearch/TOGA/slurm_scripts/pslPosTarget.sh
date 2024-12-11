#!/bin/bash
#SBATCH -J pslPosTarget
#SBATCH -n 1                  
#SBATCH -t 3:00:00              
#SBATCH -p shared,serial_requeue,holy-smokes      
#SBATCH --mem=15000           
#SBATCH -o pslPosTarget.%A.out  
#SBATCH -e pslPosTarger.%A.err  

module purge
module load python
source activate pslPosTarget
inpsl=$1
outpsl=$2
pslPosTarget $1 $2 
