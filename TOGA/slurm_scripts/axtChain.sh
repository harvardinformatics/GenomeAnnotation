#!/bin/bash
#SBATCH -J axtChain
#SBATCH -n 1                  
#SBATCH -t 3:00:00              
#SBATCH -p shared,serial_requeue,holy-smokes      
#SBATCH --mem=15000           
#SBATCH -o axtChain.%A.out  
#SBATCH -e axtChain.%A.err  

module purge
module load python
source activate axtChain
pos_target_psl=$1
echo $pos_target_psl

target2bit=$2
echo $target2bit

source2bit=$3
echo $source2bit

chainout=$4
echo $chainout

axtChain -psl -verbose=0 -linearGap=medium $pos_target_psl $target2bit $source2bit $chainout
