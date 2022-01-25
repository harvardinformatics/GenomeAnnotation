# GenomeAnnotation
## Objectives and strategy
The objective of this project is to evaluate the performance of alternative pipelines for performing genome annotation, with an end goal of providing best practice workflows for those seeking to annotate novel genomes, or update annotations to those that already have a draft annotation. We evaluate both methods that directly use comparative information summarized in whole-genome alignments, as well as single-genome annotation tools that employ some combination of homology information obtained from protein sequences, splice hints obtained from RNA-seq data, and ab initio prediction.

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
        * [PsiCLASS](https://github.com/splicebox/PsiCLASS)
* Assess impact of RNA-seq integration on annotation quality
    * Maker3,Braker, Comparative Augustus
* Assess impact on annotation quality of integrating multiple annotation sources
    * [Mikado](https://github.com/EI-CoreBioinformatics/mikado)
    * [EvidenceModeler](https://evidencemodeler.github.io/)
* Enhance reproducibility and ease of deployment on HPC clusters of top performing pipelines by providing
    * Snakemake pipelines
    * Singularity containers

## Data
Some tools and pipelines presented here integrate RNA-seq data, either as splice site hints, ESTs or transcript models directly inferred from read alignments. Thus,for each species we downloaded paired-end RNA-seq data from the [NCBI Sequence Read Archive (SRA)](https://www.ncbi.nlm.nih.gov/sra).
### Butterflies
We perform annotation for 3 heliconine butterflies, *Heliconius erato demophoon*, *Bombyx mori*, and *Danaus plexippus*. We use the genome (and annotation) for *Heliconius melpomene* as a high-quality reference genome, and the anchor for the whole genome alignment used by some tools. We used soft-masked versions of these genomes published in [Edelman *et al.* (2019)](https://science.sciencemag.org/content/366/6465/594), that were filtered such that the minimum scaffold size was 1kb.Whole-genome alignment was based upon the relationships depicted in [tree.nwk](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/genome_alignment/tree.nwk). We aligned the four genomes using [cactus](https://github.com/ComparativeGenomicsToolkit/cactus), executing the script in a SLURM script on Harvard's Cannon HPC with [cactus.sh](https://github.com/harvardinformatics/GenomeAnnotation/tree/master/genome_alignment/cactus.sh). To serve as a source of annotation and protein information for the reference species, *H. melponene*, we downloaded the "renamed" protein fasta and gff3 files from [lepbase](http://download.lepbase.org/v4/provider/). SRA RNA-seq accessions are listed [here](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/RNA-seq/butterfly_SRA_accession_ids.tsv).

### Human
We annotate the human genome with RNA-seq data generated for a study of gene expression in human and four non-human primate species, in eight brain regions [Xu et al. 2018](https://genome.cshlp.org/content/early/2018/06/13/gr.231357.117). 
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
