# Genome annotation performance assessment
The information below describes the motivations and analyses found in our preprint on **bioRxiv**,[Building better genome annotations across the tree of life](https://www.biorxiv.org/content/10.1101/2024.04.12.589245v1.full).

## Objectives
Our objectives is to evaluate the performance of alternative pipelines for performing genome annotation, with an end goal of providing best practice workflows for those seeking to annotate novel genomes, or update annotations to those that already have a draft annotation. We evaluate both methods that directly use comparative information summarized in whole-genome alignments, as well as single-genome annotation tools that employ some combination of homology information obtained from protein sequences, splice hints obtained from RNA-seq data, and ab initio prediction.

With respect to testing of specific bioinformatics tools, our strategy is to first evaluate a broad set of avaialble tools using a dataset typical of a non-model organism study, for which genomes may be preliminary draft versions, and for which there are no high quality genome annotations. It is worth noting that standard tools for genome annotation are typically benchmarked with model organisms, such that published performance represents a best-case scenario. Secondly, in the absence of gold standard annotations, there is no "truth set" with which to compare predicted gene models in order to produce standard performance metrics (sensitivity, specificity, etc.). Our initial evaluation data set consists of four butterfly genomes, including a putative reference species (see below).

After identifying a set of top-performing methods, we then evaluate these in human for which there are highly quality annotations.  

Our specific objectives with respect to methods comparisons are to:
* Compare the performance of diverse annotation approaches
    * Annotation pipelines
        * [Maker3](https://www.yandell-lab.org/software/maker.html)
        * [Braker](https://github.com/Gaius-Augustus/BRAKER)
    * Genome-alignment driven gene prediction
        * [Comparative Augustus](https://github.com/Gaius-Augustus/Augustus)
    * Exon-aware annotation transfer from a reference genome
        * [TOGA](https://github.com/hillerlab/TOGA)
    * Transcript assembly from RNA-seq
        * [StringTie](https://ccb.jhu.edu/software/stringtie/)
        * [Scallop](https://github.com/Kingsford-Group/scallop)
* Assess impact of including RNA-seq integration on annotation quality
    * Maker3, Braker,Comparative Augustus
* Assess impact on annotation quality of integrating multiple annotation sources


## Target species and data
The standard approach for evaluating annotation tool performance has been to generation transcript predictions for a limited number of model organisms will high-quality well-curated annotations, such as human, *Caenorhabditis elegans*, and *Saccharomyces cerevisiae*. By generating annotations across a broader swath of the tree of life, we sought to make more general inferences about the performance of annotation tools, what types of genome features might impact annotation quality (and the optimal choice of method), and whether there are taxonomic effects on annotation quality. We generated annotations for 21 species spanning six broad taxonomic groups: heliconiine butterflies, drosophilids (Diptera), mammals, birds, rosids and monocots. With the exception of the heliconiine butterflies, genomes and annotations were obtained from NCBI. We treat NCBI annotations as the true annotations when evaluating outputs from annotation tools we tested. Information on the specific species, genome versions, and download links for genome fastas and annotation files are available [here](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/genomes.md). The species chosen had relatively high-quality genome assemblies, but for each group, we included one species with a genome known to be of extremely high quality and with an annotation unlikely to be missing any real CDS transcripts. These species were used as the "reference" species for whole genome alignments used with Comparative Augustus (CGP), and provided the annotations for the majority of annotations generated with TOGA. Furthermore, we perform a subset of performance assessments only using theses species where the results might be sensitive to the completeness of the real (NCBI annotation), e.g. estimating the frequency of intergenic predictions.  

Some tools and pipelines presented here integrate RNA-seq data, either as splice site hints, ESTs or transcript models directly inferred from read alignments. Thus,for each species we downloaded paired-end RNA-seq data from the [NCBI Sequence Read Archive (SRA)](https://www.ncbi.nlm.nih.gov/sra). The specific SRA Run and Bioproject ids we used can be found [here](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/paper/data/SRA/SRA_accession_ids.tsv). 

### Test data: heliconiine butterflies
We used the heliconine butterflies to test and optimize our implementation of annotation tools. Because the most recent genome releases are hosted by [lebpase](lepbase.org), and because annotations have been derived by tools other than the NCBI annotation pipeline, we did not treat these annotations as truth sets as we do with NCBI annotations. In particular, the annotation for  *Heliconius melpomene* was generated using BRAKER, one of the tools we evaluate, such that comparing our BRAKER predictions to a BRAKER predictions would lead to an inflation of performance metrics. We used soft-masked versions of these genomes published in [Edelman *et al.* (2019)](https://science.sciencemag.org/content/366/6465/594), that were filtered such that the minimum scaffold size was 1kb.

## Whole-genome alignments
CGP and TOGA require whole-genome alignment (WGA). WGAs for each taxonomic group were produced with[cactus](https://github.com/ComparativeGenomicsToolkit/cactus), using guide trees representing known phylogenetic relationships, that can be found here. Details on running the GPU version of cactus can be found [here](https://github.com/harvardinformatics/GenomeAnnotation-WholeGenomeAlignment).

## Performance evaluation
  - Evaluation metrics
    - BUSCO recovery
    - CDS length distributions
    - proportion intergenic (false positive) predictions
    - proportion of protein predictions with proper start and stop codons
    - proportion of genes representing bioinformatics-error gene fusions
    - RNA-seq read alignment rates
    - repeat and GC content
    - proportion of predicted open reading frames with BLAST hits
    - proportion of expressed, NCBI-annotated transcript with no overlapping prediction

    
     

