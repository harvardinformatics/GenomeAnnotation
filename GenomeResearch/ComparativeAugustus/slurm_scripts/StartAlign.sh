#!/bin/sh
#SBATCH --partition=holy-info,holy-cow,holy-smokes,shared
#SBATCH -n 12
#SBATCH -N 1
#SBATCH --mem=24000
#SBATCH -J startlalign
#SBATCH --time=03:00:00

module load python
source activate genomethreader

/PATH/TO/startAlign.pl --genome=${1} --prot=${2} --CPU=12 --prg=gth
