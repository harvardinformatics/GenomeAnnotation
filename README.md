# GenomeAnnotation
The objective of this project is to evaluate the performance of alternative pipelines for performing genome annotation, with an end goal of providing best practice workflows for those seeking to annotate novel genomes, or update annotations to those that already have a draft annotation. We evaluate both methods that directly use comparative information summarized in whole-genome alignments, as well as single-genome annotation tools that employ some combination of homology information obtained from protein sequences, splice hints obtained from RNA-seq data, and ab initio prediction.  

## Data
We perform annotation for 3 heliconine butterflies, *Heliconius erato*, *Bombyx mori*, and *Danaus plexippus*. We use the genome (and annotation) for *Heliconius melpomene* as a high-quality reference genome, and the anchor for the whole genome alignment used by some tools. We downloaded the cactus hal file for heliconines published by [Edelman *et al.* (2019)](https://science.sciencemag.org/content/366/6465/594). We extracted the four heliconine genomes from the hal file with hal2maf version 2.1, using the following cmd:
   
```bash
   hal2maf finalAssemblies_highQual_1kbFilter_161101.hal 4speciesset_finalAssemblies_highQual_1kbFilter_161101.hal --refGenome HmelRef --noAncestors --noDupes --targetGenomes HmelRef,Bmor,HeraRef,Dple 
```

The annotation problem is broken down into two fundamental parts: 
1. transcript assembly
2. functional classification and gene symbol assignment

Both are crucial to producing an annotated set of transcript and gene models, and functional information is often used to inform transcript assembly.

- Base Strategies
- RNAseq based transcript assembly
  - Splice aligners
    - STAR
    - Hisat2
  - Assemblers
    - Class2
    - Stringtie
    - Scallop
  - RNAseq plus *ab initio* trainining
    - MAKER2
    - BRAKER2
  - Genome alignment-based
      - CESAR
      - ComparativeAugustus (CGP)
- Method integration
  - Mikado
  - EvidenceModeler
- Performance evaluation
  - NCBI genome and annotation benchmarks
    - human
    - mouse
    - fly
    - zebrafish
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
- Workflow architecture
  - singularity containers for difficult to build tools
    - Comparative Augustus (CGP)
    - Maker2
    - Braker2
    - Cesar2.0
  - Snakemake pipelines to pass inputs/outputs between tools
