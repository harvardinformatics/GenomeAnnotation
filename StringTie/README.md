# StringTie

[Stringtie](https://github.com/gpertea/stringtie) assembles transcripts from spliced alignments of RNA-seq reads to a genome, and is able to assemble alternative splice isoforms. One first assembles a set of transcripts for each sample separately, then merges those sample-specific assemblies in a subsequent step. StringTie does not distinguish CDS from UTR sequence, providing as output a gtf annotation file containing transcript and exon-level features, as well as gene names specified in the attribute data (9th column) of the gtf file. Because Stringtie doesn't predict CDS, to obtain putative CDS and protein sequences, one must run a CDS prediction pipeline. For this purpose, we use [TransDecoder](https://github.com/TransDecoder/TransDecoder/wiki). In addition, a typically small fraction of features annotated by StringTie has ambiguous strand information. For practical purposes such as expression analysis, such entries are not accepted by commonly used expression estimation tools such as [RSEM](https://github.com/deweylab/RSEM), so we filter these entries out. 

We run stringtie built in a conda environment. We build this environment by loading a Python 3 module on the Cannon HPC cluster, which is an Anaconda distribution of python, then create the environment as follows:

```bash
module load python
conda create -n stringtie -c bioconda stringtie
```

For our study, to evaluate the effects of spliced-alignment method on annotation quality, for each set of samples in a dataset, we assemble transcripts using either STAR or HISAT2, sorting and converting to bam format the output of these aligners prior to transcript assembly. We then run StringTie for each sample, using the generic [stringtie.sh](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/StringTie/slurm_scripts/stringtie.sh) script as follows:

```bash
sbatch stringtie.sh $sorted.bam
```

where $sorted.bam is the name of the input bam file.

Once we have generated gtf files for each of a set of samples run with either HISAT2 or STAR, we can then run the stringtie merge function using a second script [stringtie_merge.sh](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/StringTie/slurm_scripts/stringtie_merge.sh). The gtf files must all be in the directory from which you launch the script, as its first step is to create a list of the sample-specific gtf files output by your first set of jobs. One then can simply run the merge script, by providing a species name and aligner (so you can figure out where the alignments came from) as consecutive command line arguments:

```bash
sbatch stringtie_merge.sh bigfoot STAR
```
  
