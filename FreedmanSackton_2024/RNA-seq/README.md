# Snakemake workflows
In this directory we provide snakefiles, config files and slurm profiles for using [snakemake](https://snakemake.readthedocs.io/en/stable/index.html) to run the transcript assemblers and genome annotation tools we evaluate. For these workflows to be used in other settings, snakemake must be installed--preferrably in a conda environment--along with the implemented bioformatics tools and associated dependencies.

## RNA-seq
This snakemake workflow executes RNA-seq read alignment using [Hisat2](http://daehwankimlab.github.io/hisat2/) and [STAR](https://github.com/alexdobin/STAR). For the latter, a 2-pass alignment strategy is implemented, in which splice sites detected across all samples in the 1st pass are used to inform alignment of individual samples in the 2nd pass. Resulting *sam* files are then coordinated sorted and converted to *bam* format. Next, these bam files are passed to the RNA-seq transcript assemblers [Stringtie2](https://ccb.jhu.edu/software/stringtie/) and [Scallop](https://github.com/Kingsford-Group/scallop) to perform sample-level assemblies. Sample-level *Stringtie2* assemblies are then merged using the stringtie *--merge* argument, while sample-level assemblies generated with *Scallop* are merged using [TACO](http://tacorna.github.io/). A few important notes regarding the current workflow:
* Alignment and assembly are currently implemented in a strand-agnostic fashion, such that no strand-specific arguments have been employed. We did this to avoid spending an inordinate amount of time trying to confirm strand-confiuration for SRA accessions used in this study. 
* Users may want to customize other cmd line arguments in rnaseq.smk including:
    * intron minimum and maximum sizes in *Hisat2*
    * --sjdbOverhang in STAR to reflect median read size - 1, instead of the currently implemented default of 100
     

