# Augustus: multi-species mode
For years, Augustus has been a key component of genome annotation pipelines, and has also been used as a stand-alone genome annotation tool. Augustus offers myriad options for implementing genome annotation. We focus on a small subset of these likely to be of use for most researchers wishing to annotate genomes of non-model organisms. In our study, we evaluate Augustus in comparative mode (aka CGP) to annotate multiple genomes at once,and to leverage gene model evidence across genomes. Although the Augustus developers recommending integrating outputs from single-genome and multi-species instances of Augustus to maximize sensitivity, single-species implementations of Augustus are now optimally implemented in Braker. For the purposes of our study, we do not evaluate integration of single and multi-genome (comparative) Augustus, but evaluate separately CGP annotation with protein evidence, and that with RNA-seq evidence.

## Converting Cactus hal to MAF
To convert our Cactus whole-genome alignments to multiple alignment format (MAF) files for use with Augustus, we followed the [recommendations](http://bioinf.uni-greifswald.de/augustus/binaries/tutorial-cgp/cactus.html#hal2maf) of the Augustus developers. We split the MAF file into smaller MAF files, such that their corresponding intervals did not split known gene boundaries in the reference species for each whole genome alignment. Reference species were set as *Homo sapiens*, *Drosophila melanogaster*, *Gallus gallus*, *Arabidopsis thaliana*, and *Heliconius melpomene*, for mammals, dipterans, birds, rosids, and monocots, respectively.

We ran the Augustus *hal2maf_split.pl* perl script with [mafsplit_fromhal_nosplits.sh](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/FreedmanSackton_2024/ComparativeAugustus/slurm_scripts/mafsplit_fromhal_nosplits.sh), where the "no split list" file is simply a tab-delimited file of chromosome, start and stop for gene boundaries from the annotation of the reference species used to anchor the MAF files.

## CGP with protein evidence 
### Hint creation
To generate splice hints from external protein sequence data, we use scripts that are part of the Augustus distribution to wrap protein alignment to the genome using [GenomeThreader](https://genomethreader.org/) and creation of hints from those alignments. 

We first create a genomethreader conda environment
```bash
module load python
conda create -n genomethreader -c bioconda genomethreader
```

Next we execute the Augustus startAlign.pl script as follows:
```bash
#!/bin/sh
module load python
source activate genomethreader

genomefasta=$1
proteintargetfasta=$2

startAlign.pl --genome=${genomefasta} --prot=${proteintargetfasta} --CPU=12 --prg=gth
```

where $genomefasta and $proteintargetfasta are the genome sequences for the species of interest, and the protein fasta from (ideally) closely related species. For a large protein fasta, one can split the fasta file into smaller pieces, run aligngment on those pieces, and combine the alignment files afterwards before proceeding to the next step. The number of CPUs flag should be changed to reflect the available compute resources you have at your disposal. We ran the perl script from outside of the singularity container we use for running Augustus to avoid various path-related errors. This analysis will produce a directory with the name align_gth

We ran *startAlign.pl* with the [StartAlign.sh](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/FreedmanSackton_2024/ComparativeAugustus/slurm_scripts/StartAlign.sh) slurm script as follows:

```bash
sbatch StartAlign.sh $GenomeFasta $ProteinFasta
```
where $GenomeFasta and $ProteinFasta are the genome sequences for the species of interest, and the protein fasta to be aligned to the genome with GenomeThreader for the purpose of producing splice hints used to train Augustus.

Next, we converted the protein alignments to hints.To do this, we downloaded the BRAKER [align2hints.pl](https://github.com/Gaius-Augustus/BRAKER/blob/master/scripts/align2hints.pl) script. Then ran it as follows:
```bash
align2hints.pl --in align_gth/gth.concat.aln --out=prot.hints --prg=gth
```
This script looks for the align_gth directory produced during the alignment step so run it from the same directory in which align_gth is located. The file *gth.concat.aln* is the file containing all of the GenomeThreader alignments, i.e. if you ran alignments in parallel on many subsets of the protein fasta, they should be concatenated to produce *gth.concat.aln*. 

We wrapped this in a slurm script [Align2hints.sh](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/FreedmanSackton_2024/ComparativeAugustus/slurm_scripts/Align2hints.sh) as follows:
```bash
sbatch Align2hints.sh
```
This script looks for the align_gth directory produced during the alignment step so run it from the same directory where the alignment is located.

### Running CGP
We followed recommendations by the AUGUSTUS developers (see link above) whereby we split the alignment into chunks and converting it to maf ... leading to a number of smaller, more tractable MAF files, such that their boundaries did not intersect known gene coordinates for the reference species. Following this procedure, for ease of iterating over individual MAFs, we create a directory for symlinks to the MAF files, changing the link names such that they have integers in those names that range from 1 to the total number of MAFs. We then modified [extrinsic.M.RM.E.W.P.cfg](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/FreedmanSackton_2024/ComparativeAugustus/misc/extrinsic.M.RM.E.W.P.cfg), the configuration file recommended by the AUGUSTUS developers for analysis with protein-derived hints. Specifically, we edited the entires in the GROUP block to reflect the names of your species as they are represented in the whole-genome alignment. We ran CGP with protein evidence using an singularity container, that we execute via a slurm script [RunCgpWithProtHintsDefModel.sh](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/FreedmanSackton_2024/ComparativeAugustus/slurm_scripts/RunCgpWithProtHintsDefModel.sh), the contents of which are as follows: 

```bash
#!/bin/sh
#SBATCH -p serial_requeue,shared
#SBATCH -n 1
#SBATCH --mem=8000
#SBATCH --time=08:00:00
#SBATCH --array=1-2123
#SBATCH -e logs/cgpprot_%A_%a.e
#SBATCH -o logs/cgpprot_%A_%a.o
#SBATCH -J cgp

augustus_species=$1
tree=$2
genomes_tbl=$3
sqldb=$4

AUGUSTUS_IMAGE="/n/singularity_images/informatics/augustus/augustus_3.4.0-afreedman-build.sif"
singularity exec --cleanenv ${AUGUSTUS_IMAGE} augustus --species=${augustus_species} --softmasking=1 --treefile=${tree} --alnfile=../maflinks/${SLURM_ARRAY_TASK_ID}.maf --dbaccess=${sqldb} --speciesfilenames=${genomes_tbl} --alternatives-from-evidence=0 --dbhints=1 --extrinsicCfgFile=extrinsic.M.RM.E.W.P.cfg --/CompPred/outdir=preds/pred${SLURM_ARRAY_TASK_ID} 
```

where *augustus_species* specifies the predefined species model (and associated HMM parameters) for running CGP, *tree* is a newick-formatted tree of the genome alignment, *genomes_tbl* is a tab-delimited table of species name and path to species genome fasta on each row, and *sqldb* is the sql database built following the Augustus developers guidelines, that includes the genomes, and their associated hints data. 


We then merged multi-species annotations generated for each MAF file, generating one *gff* file per species, using the Augustus *joingenes* program, following Augustus developer guidelines found [here](http://bioinf.uni-greifswald.de/augustus/binaries/tutorial-cgp/de_novo.html#merge).

## RNA-seq only
### Hint creation
We generated RNA-seq derived splice-site hints for Augustus using the following steps, which follow the recommendations found in [Hoff and Stanke, 2019](https://pubmed.ncbi.nlm.nih.gov/30466165/). 

First, we used *samtools* to merge sample-level bam files. 

Next, we use *samtools* to sort the merged bam file by read name using a SLURM script [namesortbam.sh]ttps://github.com/harvardinformatics/GenomeAnnotation/blob/master/FreedmanSackton_2024/ComparativeAugustus/slurm_scripts/namesortbam.sh), run simply as follows:

```bash
sbatch namesortbam.sh $mymergedbam
```

After name-sorting, we filtered the bam file with [filterBam](https://github.com/nextgenusfs/augustus/tree/master/auxprogs/filterBam), executed in a SLURM script[filterbam.sh](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/FreedmanSackton_2024/ComparativeAugustus/slurm_scripts/filterbam.sh), run as follows:

```bash
sbatch filterbam_FAS_informatics_version.sh $mymergeddbam
```

After filtering the bam file, we then generate "intron part" hints by running the Augustus tool bam2hints with [bam2hints](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/ComparativeAugustus/slurm_scripts/bam2hints.sh):
```bash
sbatch bam2hints $myfilteredbam
``` 

We then generate "exon part" hints. To do so, we first esort the filtered bam file back into coordinate order with [coordsortbam.sh](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/ComparativeAugustus/slurm_scripts/coordsortbam.sh):
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
### Running CGP
Similar to how we ran CGP with protein hints, we supply an RNA-seq tailored parameter file, and command line arguments pointing to sql database, genomes table, tree file, and an Augustus species. An example parameter file, that we used with our mammals data is [extrinsic-rnaseq_mammals.cfg](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/FreedmanSackton_2024/ComparativeAugustus/misc/extrinsic-rnaseq_mammals.cfg), and the CGP job is run with the SLURM script [RunCgpWithRNAseqHints.sh](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/FreedmanSackton_2024/ComparativeAugustus/slurm_scripts/RunCgpWithRNAseqHints.sh), after which *joingenes* is used to merge predictions.
