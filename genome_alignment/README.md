# Genome alignment with [Cactus](https://github.com/ComparativeGenomicsToolkit/cactus)

This documents the snakemake workflow for genome alignments with the cactus genome aligner (GPU version).

## Pre-requisites

This pipeline runs the various steps of the [Cactus](https://github.com/ComparativeGenomicsToolkit/cactus) genome alignment tool with [Snakemake](https://snakemake.readthedocs.io/en/stable/). It is configured to submit each step as a job on a [SLURM](https://slurm.schedmd.com/overview.html) configured cluster.

### 1. SLURM 

[SLURM](https://slurm.schedmd.com/overview.html) is job scheduling and resource management software for high-performance clusters. This should be set up by your server administrators.

Currently, SLURM is the only supported job scheduling software for this pipeline. But let us know which job scheduler you have and we can work to incorporate it into the pipeline!

### 2. Snakemake

[Snakemake](https://snakemake.readthedocs.io/en/stable/) is a workflow management tool. Since cactus is comprised of several steps, we use Snakemake to make sure those steps are run automatically and efficiently.

You can [install Snakemake using conda](https://anaconda.org/bioconda/snakemake).

### 3. Cactus

[Cactus](https://github.com/ComparativeGenomicsToolkit/cactus) is whole genome alignment software.

While any type of Cactus executable should work, this pipeline was built around the Singularity image of the cactus program optimized for GPU usage. Singularity is a program that containerizes and executes programs in an isolated environment, making them easier to use. 

You can [install Singularity using conda](https://anaconda.org/conda-forge/singularity).

The Singularity image for Cactus (GPU) is included in this repository in the `cactus-snakemake-gpu` folder as `cactus_v2.0.5-gpu.sif`. 


<details><summary>Click here to see how we built the Singularity image for cactus</summary>
<p>

This singularity image was built from [the Docker image provided with cactus](https://github.com/ComparativeGenomicsToolkit/cactus/releases) using the following command:

```{bash}
singularity pull --disable-cache docker://quay.io/comparative-genomics-toolkit/cactus:v2.0.5-gpu
```

We chose the Singularity image over Docker for security reasons.

</p>
</details>

## What you will need (Inputs)

To run this pipeline you will need:

1. The location of the Cactus executable (e.g. the path to the Cactus Singularity image)
2. A phylogenetic tree of all species to align, with or without branch lengths
3. The genome FASTA files for each species

## Preparing the Cactus input file

The various Cactus commands depend on a single input file with information about the genomes to align. This file is a simple tab delmited file. The first line of the file contains the **rooted** input species tree in [Newick format](https://en.wikipedia.org/wiki/Newick_format) and nothing else. Each subsequent line contains in the first column one tip label and in the second column the path to the genome FASTA file for that species. **The genome fasta files must be uncompressed for cactus to read them.**

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
singularity exec --cleanenv cactus_v2.0.5-gpu.sif cactus-prepare <INPUT FILE> --outDir <OUTPUT DIRECTORY> --jobStore <TEMP DIRECTORY> --gpu
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
cactus_path: <cactus_path>

input_file: <input_file>

output_dir: <output_dir>

tmp_dir: <tmp_dir>
```

Simply replace each path surrounded by <> with the path you used when running `cactus-prepare`, e.g.:

```
cactus_path: /path/to/my/cactus_v2.0.5-gpu.sif

input_file: /path/to/my/input/file.txt

output_dir: /path/to/my/output-directory/

tmp_dir: /path/to/my/tmp-directory/
```

## Running cactus with snakemake

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