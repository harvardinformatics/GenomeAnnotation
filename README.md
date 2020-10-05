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
