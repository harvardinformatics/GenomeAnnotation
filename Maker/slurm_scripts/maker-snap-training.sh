#!/bin/sh
## Customize --time and --partition as appropriate.
## --exclusive --mem=0 allocates all CPUs and memory on the node.

#SBATCH --partition=holy-info,holy-smokes,holy-cow,shared
#SBATCH -n 1
#SBATCH --mem=6000
#SBATCH --time=08:00:00
#SBATCH -J snaptrain
#SBATCH -e snaptrain_%A.err
#SBATCH -o snaptrain_%A.out

MAKER_IMAGE=/n/singularity_images/informatics/maker/maker:3.01.03-repbase.sif

# Submit this job script from the directory with the MAKER control files

# RepeatMasker setup (if not using RepeatMasker, optionally comment-out these three lines)
#export SINGULARITYENV_LIBDIR=${PWD}/LIBDIR
#mkdir -p LIBDIR
#singularity exec ${MAKER_IMAGE} sh -c 'ln -sf /usr/local/share/RepeatMasker/Libraries/* LIBDIR'

# singularity options:
# * --cleanenv : don't pass environment variables to container (except those specified in --env option-arguments)
# * --no-home : don't mount home directory (if not current working directory) to avoid any application/language startup files
# Add any MAKER options after the "maker" command
# * -nodatastore is suggested for Lustre, as it reduces the number of directories created
# * -fix_nucleotides needed for hsap_contig.fasta example data
#singularity exec --no-home --cleanenv ${MAKER_IMAGE} mpiexec -n $((SLURM_CPUS_ON_NODE*3/4)) maker -fix_nucleotides -nodatastore
datatore_index=$1

singularity exec --cleanenv ${MAKER_IMAGE} maker2zff -n -d $datatore_index
#singularity exec --cleanenv ${MAKER_IMAGE} maker2zff -n -x 0.25 -l 50 -d $datatore_index
