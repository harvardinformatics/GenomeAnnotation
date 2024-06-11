# Augustus: multi-species mode
For years, Augustus has been a key component of genome annotation pipelines, and has also been used as a stand-alone genome annotation tool. Augustus offers myriad options for implementing genome annotation. We focus on a small subset of these likely to be of use for most researchers wishing to annotate genomes of non-model organisms. In our study, we evaluate Augustus in comparative mode (aka CGP) to annotate multiple genomes at once,and to leverage gene model evidence across genomes. Although the Augustus developers recommending integrating outputs from single-genome and multi-species instances of Augustus to maximize sensitivity, single-species implementations of Augustus are now optimally implemented in Braker. Therefore, we consider the effectiveness of integrating these different approaches as part of our assessment of multi-method integration. 

As CGP uses a whole-genome alignment as its backbone, it will not annotate genomic intervals in the reference genome specified in the MAF file for which there is no alignment. In other words, if a species of interest has functional gene sequence that doesn't align to the reference, it will be missed. 

## Converting Cactus hal to MAF
To convert our Cactus whole-genome alignments to multiple alignment format (MAF) files for use with Augustus, we followed the [recommendations](http://bioinf.uni-greifswald.de/augustus/binaries/tutorial-cgp/cactus.html#hal2maf). We split the MAF file into smaller MAF files, such that their corresponding intervals did not split known gene boundaries in the reference species for each whole genome alignment. Reference species were set as *Homo sapiens*, *Drosophila melanogaster*, *Gallus gallus*, *Arabidopsis thaliana*, and *Heliconius melpomene*, for mammals, dipterans, birds, rosids, and monocots, respectively.

We ran the Augustus *hal2maf_split.pl* perl script with [mafsplit_fromhal_nosplits.sh](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/FreedmanSackton_2024/ComparativeAugustus/slurm_scripts/mafsplit_fromhal_nosplits.sh), where the "no split list" file is simply a tab-delimited file of chromosome, start and stop for gene boundaries from the annotation of the reference species used to anchor the MAF files.


## Protein-only 
### Hint creation
To generate splice hints from external protein sequence data, we use scripts that are part of the Augustus distribution to wrap protein alignment to the genome using [GenomeThreader](https://genomethreader.org/) and creation of hints from those alignments. 

We first create a genomethreader conda environment
```bash
module load python
conda create -n genomethreader -c bioconda genomethreader
```

Next we execute the Augustus startAlign.pl script using []():
```bash
sbatch StartAlign.sh $GenomeFasta $ProteinFasta
```
where $GenomeFasta and $ProteinFasta are the genome sequences for the species of interest, and the protein fasta from (ideally) closely related species.

We run the perl script from outside of the singularity container we use for running Augustus to avoid various path-related errors. This analysis will produce a directory with the name align_gth. Next, we convert the alignment to hits using [Align2hints.sh]() as follows:
```bash
sbatch Align2hints.sh
```
This script looks for the align_gth directory produced during the alignment step so run it from the same directory where the alignment is located.


 
 





## RNA-seq only
### Hint creation
To generate RNA-seq derived splice-site hints for Augustus is a multi-step process which present computational challenges. We have implemented changes to tools within the Augustus distribution in order for them to handle contemporary, increasingly large RNA-seq datasets in a time-efficient manner. 

After using samtools to merge the bamfiles of interest, one has to sort them bam-file by sequence name rather that coordinate order. In the directory where the merged bam is, first create a tmp directory:
```bash
mkdir tmp
```
Next, use samtools to namesort the bam file, using our script [namesortbam.sh]():
```bash
sbatch namesortbam.sh $mymergedbam
```

After name-sorting, the bam file needs to be filtered. We have modified the original [filterBam](https://github.com/nextgenusfs/augustus/tree/master/auxprogs/filterBam) code to [filterBam-zlib-ng-2:LINK NOT YET ADDED] in order to speed up filtering. We execute this updated version from within a singularity image,oneapi-hpckit_2021.2-devel-centos8.sif, available at: . To execute this step we use [filterbam_FAS_informatics_version.sh](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/ComparativeAugustus/slurm_scripts/filterbam_FAS_informatics_version.sh) run as follows:
```bash
sbatch filterbam_FAS_informatics_version.sh $mymergeddbam
```

After filtering the bam file, we then generate "intron part" hints by running the Augustus tool bam2hints with [bam2hints](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/ComparativeAugustus/slurm_scripts/bam2hints.sh):
```bash
sbatch bam2hints $myfilteredbam
``` 

To generate "exon part" hints, we then resort the filtered bam file back into coordinate order with [coordsortbam.sh](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/ComparativeAugustus/slurm_scripts/coordsortbam.sh):
```bash
mkdir tmp
sbatch coordsortbam.sh $myfilteredbam
```

Then, we convert the resorted bam to wig format with the Augustus tool bam2wig using [bam2wig.sh](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/ComparativeAugustus/slurm_scripts/bam2wig.sh):
```bash
sbatch bam2wig.sh $coordsorted_filtered_bam
```
Finally, we convert the wig file into a gff formatted hints file with wig2hints.pl via our slurm script [wig2hints.sh](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/ComparativeAugustus/slurm_scripts/wig2hints.sh)
```bash
sbatch wig2hints.sh $mywigfile
```
