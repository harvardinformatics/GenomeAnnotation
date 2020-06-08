# GenomeAnnotation
Best practices and workflow for genome annotation

## Project Outline
1. Base Strategies
  1. RNAseq based transcript assembly
    * Splice aligners
      1. STAR
      2. Hisat2
    * Assemblers
      1. Class2
      2. Stringtie
      3. Scallop
  2. RNAseq plus *ab initio* trainining
    1. MAKER2
    2. BRAKER2
  3. Genome alignment-based
      1. CESAR
      2. ComparativeAugustus (CGP)

2. Method integration
  * Mikado
  * EvidenceModeler (?)

3. Performance Evaluation
  1. NCBI genome and annotation benchmarks
    * human
    * mouse
    * fly
    * zebrafish

  2. Method effects
    * best combination of methods
    * effect of quality trimming reads
    
    
  3. Evaluation metrics
    1. Annotation BUSCO score / genome BUSCO score
    2. % transcripts recovered as function of percent correct bases threshold
    3. recall
    4. precision
    5. false negative rate
    6. expression correlations with benchmark genes
    7. comparison of DE testing to benchmark
      * conditional on same orthologous gene symbol assignment
