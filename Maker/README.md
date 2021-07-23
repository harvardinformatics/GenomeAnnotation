# Maker3
The current version of Maker gives one the option of running [EVidenceModeler](https://evidencemodeler.github.io/), i.e. EVM, under the hood to use its scoring scheme for filtering and selection final transcripts. We implemented Maker in four different ways in order to examine the impact of EVM and the inclusion of external evidence provided in the form of RNA-seq derived transcript assemblies:
* Protein evidence, without EVM
* Protein evidence, with EVM
* Protein  and RNA-seq evidence, without EVM
* Protein and RNA-seq evidence, with EVM

More generally, and especially in light of scientific literature and firsthand reports indicating poor performance by Maker, we sought to run as robust a pipeline as possible. For example, we did not simply run Maker once with a single selected Augustus species parameter set. Instead, we largely adopted a two-pass approach, modified from a detailed protocol provided by [Daren Card](https://gist.github.com/darencard/bb1001ac1532dd4225b030cf0cd61ce2). Outputs from the first pass are used as the basis for training two *ab initio* prediction tools: Augustus, SNAP. The second pass uses parameters learned from the first pass for Augustus and SNAP. As an extension of Daren Card's protocol, we also provide Hidden Markov Model parameters for a third predictor, [Genemark-ES](http://exon.gatech.edu/GeneMark/gmes_instructions.html). 

## Genemark-ES
When one wishes to include Genemark predictions in the Maker pipeline, there are a few different versions of the Genemark algorithm to consider. We use GenemarkES because Maker was designed to support this version [see this thread](https://groups.google.com/g/maker-devel/c/CFmls8P3FAY/m/py3xLniPCAAJ), and we are unaware of extensive testing using other approaches such as Genemark-ET (using RNA-seq data) or Genemark-EP, which is used by Braker2 and incorporates evidence from protein data. Genemark-ES takes as its only input the genome sequence. An example job script for running Genemark on the Harvard Cannon cluster is [genemarkES.sh](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/Maker/slurm_scripts/genemarkES.sh), and can be run as follows:

```bash
sbatch genemarkES.sh genome.fa
```
## Maker: round1
For a particular dataset, and depending upon whether annotation is performed only with external protein evidence or also with RNA-seq evidence, in the maker_opts.ctl file we specify the protein fasta and the transcript assembly gff3 files, respectively. For the latter, we use a Stringtie assembly merged across samples and based upon spliced RNA-seq read alignments generated with STAR. Generic control files are provided [here](https://github.com/harvardinformatics/GenomeAnnotation/tree/master/Maker/control_files), with run-specific maker_opts.ctl files located in the opts directory. The first round is executed with [maker.sh](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/Maker/slurm_scripts/maker.sh) from the same directory where the control files for the analysis run are stored:

```bash
sbatch maker.sh
```

### Summarizing outputs
After Maker completes, we do some quick bookkeeping by way of generating a transcript fasta and gff3 file from all of the genomic intervals with results. This can be done either as a slurm script or in an interactive session in which you setup an environment using a singularity image, for example:

```bash
MAKER_IMAGE=/n/singularity_images/informatics/maker/maker:3.01.03-repbase.sif
singularity exec --cleanenv ${MAKER_IMAGE} /bin/bash
gff3_merge -s -d $datastore_index > ${YOUR_ANALYSIS_NAME}_round1_maker_all.gff3
fasta_merge -d $datastore_index
gff3_merge -n -s -d $datastore_index > ${YOUR_ANALYSIS_NAME}_round1_maker_all.gff3
```

These three commands generate a gff3 file including the predicted transcript sequences appended in the footer, a transcript fasta, and a gff3 without the fasta sequences in the footer, respectively.

For more details regarding the singularity implementation of Maker3 on Harvard's FASRC cluster, see the following Informatics Group [webpage](https://informatics.fas.harvard.edu/maker-on-the-fasrc-cluster.html). 


## SNAP training
To train SNAP for *ab initio* prediction in round2, we first create a directory for our training data, and run the maker2zff executable from within that directory, providing as a command line argument the maker master_datastore_index.log file included as output from round1 by Maker. A generic call of maker2zff is as follows:

```bash
maker2zff -n -d $datatore_index
```

where datastore_index is the full path to the datastore_index.log file. 

Following guidance from the Maker developers, we perform no filtering with this command (that would typically be implemented with -x and -l arguments) by using the -n switch, as filtering can lead to zero-sized output files, i.e. no useable results. This is particularly the case when using protein data. To make analyses comparable, we use -n even when we supply RNA-seq transcript assemblies as evidence. See [this thread](http://yandell-lab.org/pipermail/maker-devel_yandell-lab.org/2013-December/004663.html) for more details. 


We run it using [maker-snap-training.sh](https://github.com/harvardinformatics/GenomeAnnotation/tree/master/Maker/slurm_scripts/maker-snap-training.sh):

```bash
sbatch maker-snap-training.sh $datastore_index
```

Once this job has finished, from within the same directory, we launch an interactive session, and create a new environment using the Maker3 singularity image, and run fathom and forge:

```bash
MAKER_IMAGE=/n/singularity_images/informatics/maker/maker:3.01.03-repbase.sif
singularity exec --cleanenv ${MAKER_IMAGE} /bin/bash
fathom genome.ann genome.dna -gene-stats > gene-stats.log 2>&1
fathom genome.ann genome.dna -validate > validate.log 2>&1
fathom genome.ann genome.dna -categorize 1000 > categorize.log 2>&1
fathom uni.ann uni.dna -export 1000 -plus > uni-plus.log 2>&1

mkdir params
cd params
forge ../export.ann ../export.dna > ../forge.log 2>&1
cd ..
hmm-assembler.pl genome params > ${YOUR_ANALYSIS_NAME}_rnd1.zff.hmm
```
The \.hmm file will be specified in the second round of annotation.
