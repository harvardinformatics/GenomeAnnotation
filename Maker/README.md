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
