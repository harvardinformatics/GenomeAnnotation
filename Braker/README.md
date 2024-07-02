# BRAKER
This page provides a description of best practice for generating genome annotations with [BRAKER](https://github.com/Gaius-Augustus/BRAKER). BRAKER3 is the latest major release, which now includes options for running with protein evidence, RNA-seq evidence, or both. For details on how BRAKER3 (and particularly the integration of protein and RNA-seq evidence) works, see [Gabriel et al. 2024](https://genome.cshlp.org/content/early/2024/05/28/gr.278090.123.abstract). The basic "how tos" provided below follow closely instructions from the BRAKER GitHub repository, but we will be adding on additional recommendations for assessing the quality of and filtering the annotation in the near future.
 
## Obtaining and installing BRAKER
The easiest way to run BRAKER, and to avoid headaches involved with installing software dependencies is to run it via a singularity container. One first needs to download the latest BRAKER image:

```bash
singularity build braker3.sif docker://teambraker/braker3:latest
```
## Running BRAKER
### Protein-only
The BRAKER developers indicate that the preferred protein database to use is [OrthoDB](https://www.orthodb.org/). Some care should be taken in selecting a subset of the overall database that strikes a balance between maximizing the probability of representing the proteomic diversity likely to be found in the genome being annotated, and filtering out protein sequences for species that are so evolutionarily distant that robust alignments to the genome being annotated are unlikely. The easiest way to access taxonomically partitioned subsets of OrthoDB is to download them from University of Greifswald's [partitioned OrthoDB v.11](https://bioinf.uni-greifswald.de/bioinf/partitioned_odb11/) site. One will also need to decompress the downloaded file before running BRAKER. If you desire to use a more customized OrthoDB subset, one will need to download the complete OrthoDB fasta file as well as relevant tables from [here](https://data.orthodb.org/download/) and use taxonomic tabular information to select records of interest. 

Once the protein database has been downloaded, one can then launch BRAKER:

```bash
brakersif=$1 # e.g. path to your downloaded braker3.sif
myspecies=$2 # do NOT make this the same as an existing pre-computed AUGUSTUS species parameter set
genome=$3 # path to soft-masked genome fasta
proteindbase=$4 # path to orthodb fasta file

singularity exec --cleanenv $brakersif cp -Rs /opt/Augustus/config/ augustus_config

singularity exec --no-home \
                 --home /opt/gm_key \
                 --cleanenv \
                 --env AUGUSTUS_CONFIG_PATH=${PWD}/augustus_config \
                 $brakersif braker.pl \
		 --species=${myspecies} 
                 --genome=$genome \
                 --prot_seq=${proteindbase} \
                 --threads=48
```
The above command line assumes one has 48 cores available. The need for parallelization and associated memory likely will require access to a high-performance computing (HPC) cluster. The above command line can easily be wrapped in a job script for SLURM, SGE, or LSF. The first of the two *singuarity exec* commands copies *augustus_config* to a writeable location (which is the location to which the actual BRAKER run uses via the *--env* switch.
 
### RNA-seq only
                


