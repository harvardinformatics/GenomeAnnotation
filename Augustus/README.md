# Augustus
For years, [Augustus](https://github.com/Gaius-Augustus/Augustus) has been a key component of genome annotation pipelines, and has also been used as a stand-alone genome annotation tool. Augustus offers myriad options for implementing genome annotation. We focus on a small subset of these likely to be of use for most researchers wishing to annotate genomes of non-model organisms. In our study, we evaluate Augustus in comparative mode (aka CGP) to annotate multiple genomes at once,and to leverage gene model evidence across genomes. We also integrate single-genome instances of Augustus with outputs from CGP so as to maximize sensitivity. As CGP uses a whole-genome alignment as its backbone, it will not annotate genomic intervals in the reference genome specified in the MAF file for which there is no alignment. In other words, if a species of interest has functional gene sequence that doesn't align to the reference, it will be missed. Following guidance from the Augustus developers, we combine single-genome (SG)and CGP Augustus runs for each species. 

Current guidance also recommends performing separate Augustus runs for different forms of extrinsic evidence. We assume that there is always some form of extrinsic protein evidence available. Finally, we also consider the possibility that within the available Augustus species hidden markov model (hmm) parameter files, there may not be available a profile for a closely related species, and that, if there is, there may not be UTR parameters provided. Thus, we consider the option for generating new species profiles. Thus, the following annotation workflows (and associated analysis steps) are evaluated:

* Protein evidence only
    * generate Augustus species profile (for reference species in MAF)
        * protein2genome alignments with GenomeThreader
    * for each species, generate hints files from protein2genome alignment
    * run CGP with hints
    * run SG with hints
    * For each species, merge SG and CGP annotations
        * joingenes
* Protein and RNA-seq evidence
    * generate Augustus reference species profile
        * profile with UTR produced by BRAKER
    * for each species generate exon and intron part hints
        * STAR aligment of RNA-seq to genome
        * filterbam and bam2hints for intron hints
        * bam2wig and wig2hints for exon-part hints
        * concatenate hints 
        * run CGP with hints
            * include UTR prediction
        * run SG with hints
            * include UTR prediction
        * Merge SG and CGP annotations
            * joingenes

To simply the above pipelines, for SG analyses we use the Augustus parameters generated for the the reference species, under the assumption that the reference is close enough to the aligned target species for the reference species hmm parameters to perform well in the targets.
