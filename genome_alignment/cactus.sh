#!/bin/sh
#SBATCH --nodes=1
# allow use of all the memory on the node
#SBATCH --mem=0
# request all CPU cores on the node
#SBATCH --exclusive
# Customize --time --partition as appropriate
#SBATCH --time=96:00:00
#SBATCH --partition=holy-info,shared

set -o nounset -o errexit -o xtrace

########################################
# parameters
########################################
readonly CACTUS_IMAGE=/n/singularity_images/informatics/cactus/cactus_v1.2.3.sif
readonly JOBSTORE_IMAGE=jobStore.img # cactus jobStore; will be created if it doesn't exist
readonly SEQFILE=4butterflies_genomes_cactus.txt
readonly OUTPUTHAL=4butterflies_cactus_brchlen1_treewancs_2020.12.06.hal

########################################
# ... don't modify below here ...

readonly CACTUS_SCRATCH=/scratch/cactus-${SLURM_JOB_ID}

if [ ! -e "${JOBSTORE_IMAGE}" ]
then
  restart=''
  mkdir -p -m 777 ${CACTUS_SCRATCH}/upper ${CACTUS_SCRATCH}/work
  truncate -s 2T "${JOBSTORE_IMAGE}"
  singularity exec ${CACTUS_IMAGE} mkfs.ext3 -d ${CACTUS_SCRATCH} "${JOBSTORE_IMAGE}"
else
  restart='--restart'
fi

# Use empty /tmp directory in the container
mkdir -m 700 -p ${CACTUS_SCRATCH}/tmp

# the toil workDir must be on the same file system as the cactus jobStore
singularity exec --overlay ${JOBSTORE_IMAGE} ${CACTUS_IMAGE} mkdir -p /cactus/workDir
srun -n 1 /usr/bin/time -v singularity exec --cleanenv \
                           --overlay ${JOBSTORE_IMAGE} \
                           --bind ${CACTUS_SCRATCH}/tmp:/tmp \
                           --env PYTHONNOUSERSITE=1 \
                           ${CACTUS_IMAGE} \
  cactus ${CACTUS_OPTIONS-} ${restart-} --workDir=/cactus/workDir --binariesMode local /cactus/jobStore "${SEQFILE}" "${OUTPUTHAL}"

# /tmp would eventually be purged, but just in case the
# next job to run on this node needs lots of /space...

rm -rf ${CACTUS_SCRATCH} jobStore.img
