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
We followed recommendations by the AUGUSTUS developers (see link above) whereby we split the alignment into chunks and converting it to maf ... leading to a number of smaller, more tractable MAF files, such that their boundaries did not intersect known gene coordinates for the reference species. Following this procedure, for ease of iterating over individual MAFs, we create a directory for symlinks to the MAF files, changing the link names such that they have integers in those names that range from 1 to the total number of MAFs. We then modified [extrinsic.M.RM.E.W.P.cfg](https://github.com/harvardinformatics/GenomeAnnotation-ComparativeAugustus/blob/main/configuration_files/extrinsic.M.RM.E.W.P.cfg), the configuration file recommended by the AUGUSTUS developers for analysis with protein-derived hints. Specifically, we edited the entires in the GROUP block to reflect the names of your species as they are represented in the whole-genome alignment. We ran CGP with protein evidence using an singularity container, that we execute via a slurm script [RunCgpWithProtHintsDefModel.sh](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/FreedmanSackton_2024/ComparativeAugustus/slurm_scripts/RunCgpWithProtHintsDefModel.sh), the contents of which are as follows: 

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
