# GenomeAnnotation
Best practices and workflow for genome annotation

## Project Outline
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
