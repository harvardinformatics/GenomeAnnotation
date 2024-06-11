#!/bin/sh
#SBATCH -p shared,serial_requeue
#SBATCH -n 1
#SBATCH --mem=90000
#SBATCH --time=23:00:00
#SBATCH --array=1-2123 # range should cover total number of MAFs
#SBATCH -e logs/cgphints_%A_%a.e
#SBATCH -o logs/cgphints_%A_%a.o
#SBATCH -J cgp

augustus_species=$1
treefile=$2
genomes_table=$3
sqldb=$4

AUGUSTUS_IMAGE="/n/singularity_images/informatics/augustus/augustus_3.4.0-afreedman-build.sif"
singularity exec --cleanenv ${AUGUSTUS_IMAGE} augustus --species=${augustus_species} --softmasking=1 --treefile=${treefile} --alnfile=../maflinks/${SLURM_ARRAY_TASK_ID}.maf --dbaccess=${sqldb} --speciesfilenames=${genomes_table} --alternatives-from-evidence=0 --dbhints=1 --allow_hinted_splicesites=atac --/CompPred/liftover_all_ECs=on --UTR=0 --extrinsicCfgFile=extrinsic-rnaseq_mammals.cfg --/CompPred/outdir=preds_splice/pred${SLURM_ARRAY_TASK_ID} 


