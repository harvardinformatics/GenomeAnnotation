#!/bin/bash
#SBATCH -J faTo2bit
#SBATCH -n 1                  
#SBATCH -t 1:00:00              
#SBATCH -p shared,serial_requeue      
#SBATCH --mem=6000           
#SBATCH -o faTo2bit.%A.out  
#SBATCH -e faTo2bit.%A.err  

module purge
module load python
source activate faToTwoBit

fastain=$1
twobitout=$2
faToTwoBit $fastain $twobitout 
