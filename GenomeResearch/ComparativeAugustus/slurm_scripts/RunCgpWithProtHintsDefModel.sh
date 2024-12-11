#!/bin/sh
#SBATCH -p serial_requeue,shared
#SBATCH -n 1
#SBATCH --mem=8000
#SBATCH --time=08:00:00
#SBATCH --array=1-2123
#SBATCH -e logs/cgpprot_%A_%a.e
#SBATCH -o logs/cgpprot_%A_%a.o
#SBATCH -J cgp

augustus_species=$1
tree=$2
genomes_tbl=$3
sqldb=$4

AUGUSTUS_IMAGE="/n/singularity_images/informatics/augustus/augustus_3.4.0-afreedman-build.sif"
singularity exec --cleanenv ${AUGUSTUS_IMAGE} augustus --species=${augustus_species} --softmasking=1 --treefile=${tree} --alnfile=../maflinks/${SLURM_ARRAY_TASK_ID}.maf --dbaccess=${sqldb} --speciesfilenames=${genomes_tbl} --alternatives-from-evidence=0 --dbhints=1 --extrinsicCfgFile=extrinsic.M.RM.E.W.P.cfg --/CompPred/outdir=preds/pred${SLURM_ARRAY_TASK_ID} 


