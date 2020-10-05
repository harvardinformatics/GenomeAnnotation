# GenomeAnnotation
The objective of this project is to evaluate the performance of alternative pipelines for performing genome annotation, with an end goal of providing best practice workflows for those seeking to annotate novel genomes, or update annotations to those that already have a draft annotation. We evaluate both methods that directly use comparative information summarized in whole-genome alignments, as well as single-genome annotation tools that employ some combination of homology information obtained from protein sequences, splice hints obtained from RNA-seq data, and ab initio prediction.  

## Data
We perform annotation for 3 heliconine butterflies, *Heliconius erato*, *Bombyx mori*, and *Danaus plexippus*. We use the genome (and annotation) for *Heliconius melpomene* as a high-quality reference genome, and the anchor for the whole genome alignment used by some tools. We downloaded the cactus hal file for heliconines published by [Edelman *et al.* (2019)](https://science.sciencemag.org/content/366/6465/594). We extracted the four heliconine genomes from the hal file with hal2maf version 2.1, using the following cmd:
   
```bash
   hal2maf finalAssemblies_highQual_1kbFilter_161101.hal 4speciesset_finalAssemblies_highQual_1kbFilter_161101.hal --refGenome HmelRef --noAncestors --noDupes --targetGenomes HmelRef,Bmor,HeraRef,Dple 
```

Some tools and pipelines presented here integrate RNA-seq data, either as splice site hints, ESTs or transcript models directly inferred from read alignments. Thus,for each species we downloaded paired-end RNA-seq data from the [NCBI Sequence Read Archive (SRA)](https://www.ncbi.nlm.nih.gov/sra).

## Objectives and strategy
Our objectives are to:
* Compare the performance of purportedly full annotation pipelines
    * [Maker2](https://www.yandell-lab.org/software/maker.html)
    * [Braker2](https://github.com/Gaius-Augustus/BRAKER)
    * [Funannotate](https://github.com/nextgenusfs/funannotate)
    * [Comparative Augustus](https://github.com/Gaius-Augustus/Augustus)
    * [Comparative Annotation Toolkit (CAT)](https://github.com/ComparativeGenomicsToolkit/Comparative-Annotation-Toolkit)

* Assess benefits of integrating RNA-seq data
* Assess the relative performance of standard pipelines (above) with integrators that take inputs from multiple sources
    * [Mikado](https://github.com/EI-CoreBioinformatics/mikado)
    * [EvidenceModeler](https://evidencemodeler.github.io/)

* Assess whether transferring annotation information from another genome improves genome annotation
    * Add annotation transfers from [CESAR](https://github.com/hillerlab/CESAR) to pipelines and integrators 

* Enhance reproducibility and ease of deployment on HPC clusters of top performing pipelines by providing
    * Snakemake pipelines
    * Singularity containers

## Methods
### QC and pre-processing
Prior to aligning RNA-seq paired-end reads to their respective genomes, we first do a quick quality check on libraries with [fastqc](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/), v. 0.11.8. We then strip residual adapter sequences from reads with [Trim Galore!](https://www.bioinformatics.babraham.ac.uk/projects/trim_galore/) v. 0.6.4, which is used to wrap [cutadapt](https://cutadapt.readthedocs.io/en/stable/) v. 2.10. A second run of fastqc is then peroformed to confirm success in removing residual adapter sequences. A generic example of our Trim Galore! command line is as follows:

```bash
trim_galore --path_to_cutadapt /FULL/PATH/TO/cutadapt --paired --retain_unpaired --phred33 --output_dir $(pwd)/trimmed_reads --length 35 -q 0 --stringency 5 -e 0.1 SRAId_R1.fastq SraId_R2.fastq
```
We do not trim on a base quality threshold (*-q 0*), and require a minimum read length of 35 bases. Trimmed reads < 35bp are discarded leading to unpaired "orphan" reads. While in our command line we keep unpaired reads, we do not use these reads subsequently for downstream analysis. The *stringency* and *-e* arguments influence the stringency of criteria for matching to hypothetical adapter sequences; see the *Trim Galore!* or *cutadapt* documentation for more details.

### Short read alignment
We align the adapter-trimmed RNA-seq reads to their respective reference genomes with two different aligners: [HISAT2](https://daehwankimlab.github.io/hisat2/) v. 2.2.1 and [STAR](https://github.com/alexdobin/STAR) v. 2.7.5c. 

For HISAT2, we first build an index:

```bash
hisat2-build -p 6 /PATH/TO/GENOME/genome.fasta IndexBaseName
```
where IndexBaseName is simply the name you assign as the prefix for the various index files, and -p indicates the number of threads.

Then, run HISAT2:
```
hisat2 -p 12 -x /PATH/TO/HISAT2/INDEX/IndexBaseName -q --phred33 --min-intronlen 20 --max-intronlen 500000 -1 SRAId_adaptertrimmed_R1.fq SRAId_adaptertrimmed_R2.fq -S SRAId_hisat2.sam
```

The intron length arguments reflect defaults.


## Performance evaluation
  - NCBI genome and annotation benchmarks
  - Sensitivity to method choice
    - best combination of tools
    - quality trimming RNA-seq reads
    - peformance gains with integration methosd 
  - Evaluation metrics
    - annotation BUSCO score / genome BUSCO score
    - percenttranscripts recovered as function of percent correct bases threshold
    - recall
    - precision
    - F1 score
    - false negative rate
    - expression correlations with benchmark genes
    - comparison of DE testing to benchmark
    - conditional on same orthologous gene symbol assignment
