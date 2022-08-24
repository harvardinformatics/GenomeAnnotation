# Genome alignment with [Cactus](https://github.com/ComparativeGenomicsToolkit/cactus)

This documents the snakemake workflow for genome alignments with the Cactus genome aligner (GPU version).

## Pre-requisites

This pipeline runs the various steps of the [Cactus](https://github.com/ComparativeGenomicsToolkit/cactus) genome alignment tool with [Snakemake](https://snakemake.readthedocs.io/en/stable/). It is configured to submit each step as a job on a [SLURM](https://slurm.schedmd.com/overview.html) configured cluster.

### 1. SLURM 

[SLURM](https://slurm.schedmd.com/overview.html) is job scheduling and resource management software for high-performance clusters. This should be set up by your server administrators.

Currently, SLURM is the only supported job scheduling software for this pipeline. But let us know which job scheduler you have and we can work to incorporate it into the pipeline!

### 2. Snakemake

[Snakemake](https://snakemake.readthedocs.io/en/stable/) is a workflow management tool. Since Cactus is comprised of several steps, we use Snakemake to make sure those steps are run automatically and efficiently.

You can [install Snakemake using conda](https://anaconda.org/bioconda/snakemake).

### 3. Cactus (Singularity image)

[Cactus](https://github.com/ComparativeGenomicsToolkit/cactus) is whole genome alignment software.

This pipeline was built around the Singularity image of the Cactus program optimized for GPU usage. Singularity is a program that containerizes and executes programs in an isolated environment, making them easier to use. 

You can [install Singularity using conda](https://anaconda.org/conda-forge/singularity).

With Singularity installed, you can create the image from [the Docker image provided with Cactus (GPU)](https://github.com/ComparativeGenomicsToolkit/cactus/releases) for the latest version (2.2.0 as of the writing of this file) as `cactus_v2.2.0-gpu.sif` with the following command:

```{bash}
singularity pull --disable-cache docker://quay.io/comparative-genomics-toolkit/cactus:v2.2.0-gpu
```

We chose the Singularity image over Docker for security reasons.

## What you will need (Inputs)

To run this pipeline you will need:

1. The location of the Cactus executable (e.g. the path to the Cactus Singularity image)
2. A phylogenetic tree of all species to align, with or without branch lengths
3. The genome FASTA files for each species

## Preparing the Cactus input file

The various Cactus commands depend on a single input file with information about the genomes to align. This file is a simple tab delmited file. The first line of the file contains the **rooted** input species tree in [Newick format](https://en.wikipedia.org/wiki/Newick_format) and nothing else. Each subsequent line contains in the first column one tip label and in the second column the path to the genome FASTA file for that species. **The genome fasta files must be uncompressed for Cactus to read them.**

For example, if I were running this pipeline on 5 species, A, B, C, D, and E, my input file may look something like this:

```
(((A,B),(C,D)),E)
A   seqdir/a.fa
B   seqdir/b.fa
C   seqdir/c.fa
D   seqdir/d.fa
E   seqdir/e.fa
```

## Running `cactus-prepare`

Next we need to run the `cactus-prepare` script, which importantly labels the internal nodes of the input tree according to Cactus' specifications and generates several more files needed to run subsequent steps.

Generally, it can be run as follows:

```{bash}
<cactus_path> cactus-prepare <INPUT FILE> --outDir <OUTPUT DIRECTORY> --jobStore <TEMP DIRECTORY> --gpu
```

Specifically, for the Singularity image, it can be run as:

```{bash}
singularity exec --cleanenv cactus_v2.2.0-gpu.sif cactus-prepare <INPUT FILE> --outDir <OUTPUT DIRECTORY> --jobStore <TEMP DIRECTORY> --gpu
```

You will have to specify the paths defined within <>.

| Name in command above | Description |
|-----------------------|-------------|
| INPUT FILE            | The file prepared above that contains the input species tree and input fasta sequences  |
| OUTPUT DIRECTORY      | Desired output directory for all Cactus config and sequence files |
| TEMP DIRECTORY        | A directory with plenty of storage space for temporary files generated during Cactus runs |

## Preparing the snakemake config file

Now we can set up the config file for the snakemake pipeline. An example template is provided in this repository: `cactus-gpu-snakemake/config-template.yaml`. This file contains the following parameters that will be used by snakemake to run Cactus:

```
working_dir: <working_dir>

cactus_path: <cactus_path>

input_file: <input_file>

output_dir: <output_dir>

final_hal: <final .hal file with all genomes appended>

tmp_dir: <tmp_dir>

use_gpu: True
```

Simply replace each path surrounded by <> with the path you used when running `cactus-prepare`, e.g.:

```
working_dir: /path/to/directory/in/which/to/run/cactus/

cactus_path: /path/to/my/cactus_v2.2.0-gpu.sif

input_file: /path/to/my/input/file.txt

output_dir: /path/to/my/output-directory/

final_hal: /desired/path/to/final/file.hal

tmp_dir: /path/to/my/tmp-directory/

use_gpu: True
```

Here, `working_dir` is whatever directory you want to be in when all the cactus commands to be run. I prefer this directory to be one level above my output directory. Snakemake will also create a folder here called `slurm-logs/` where all cluster log files will be stored.

The `final_hal` file will be the one with all aligned genomes appended to it. It starts as a copy of the .hal file at the root of the tree and then the `append` rule runs `halAppendSubtree` on each other node in the tree to ad them to this file.

`use_gpu` is a boolean (enter only `True` or `False` without quotes) that tells the workflow whether or not to expect the cactus GPU version to be provided in the `cactus_path`. If so, the partitions for the `mask` and `blast` rules should be GPU nodes. To use the non-GPU cactus version, provide that as the `cactus_path` and set `use_gpu: False`.

### Allocating resources for each step

The config file also has resource allocations for each step of the cactus pipeline, e.g. for the alignment step:

```
align_partition: "bigmem"
align_cpu: 24
align_mem: "450g"
align_time: "24:00:00"
```

Be sure to adjust these to your cluster and needs!

**But note that due to a [bug](https://github.com/ComparativeGenomicsToolkit/cactus/issues/709), the number of cpus assigned to the `mask` rule must be the total number of cpus on that node!**

## Getting email updates for jobs

If you wish to get emails when individual jobs submitted by snakemake END or FAIL, edit the file `cactus-gpu-snakemake/profiles/slurm_profile/config.yaml`. 

Uncomment lines 14 and 15 and insert your email address there:

```
  #--mail-type=END,FAIL
  #--mail-user=<YOUR EMAIL>
```

## Running Cactus with Snakemake

Now we are ready to run Cactus with snakemake!

```{bash}
snakemake -p -s cactus_gpu.smk --configfile <CONFIG FILE> --profile <SLURM PROFILE DIRECTORY> --dryrun
```

The `cactus_gpu.smk` script is located in the `cactus-gpu-snakemake`

For the other files, you will have to specify the paths defined within <>.

| Name in command above      | Description |
|----------------------------|-------------|
| CONFIG FILE                | The config file prepared above that contains the paths for Cactus files |
| SLURM PROFILE DIRECTORY    | The path to the **directory** containing the SLURM cluster configuration file called `config.yaml`. Relative to this file, this directory is `cactus-gpu-snakemake/profiles/slurm_profile/` |

With the `--dryrun` option, this command will run through the pipeline without executing any commands to make sure no errors occur with the pipeline itself. When you are satisfied that the pipeline will be run correctly, remove `--dryrun` to execute the pipeline.

We also recommend running the pipeline script itself using a [terminal multiplexer](https://en.wikipedia.org/wiki/Terminal_multiplexer) or submitting it as a job to your cluster so that it won't be interrupted.

