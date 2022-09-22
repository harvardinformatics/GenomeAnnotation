#!/bin/bash
#SBATCH -J genoBUSCO
#SBATCH -N 1                   # Ensure that all cores are on one machine
#SBATCH -n 24                  # Use 16 cores for the job
#SBATCH -t 06:00:00              # Runtime in D-HH:MM
#SBATCH -p shared      # Partition to submit to
#SBATCH --mem=80000            # Memory pool for all cores (see also --mem-per-cpu)
#SBATCH -o BUSCOgeno.%A.out  # File to which STDOUT will be written
#SBATCH -e BUSCOgeno.%A.err  # File to which STDERR will be written

module purge
module load python
source activate busco_5.0.0

busco -c 24 -o ${1}_Genome -i $1 -l /n/holyscratch01/external_repos/INFORMATICS/BUSCO/arthropoda_odb10 --mode genome  

