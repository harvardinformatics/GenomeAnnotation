## RNA-seq data set selection
For each species within each taxonomic group we investigated, when selecting SRA RNA-seq accessions, to the extent possible we employed the following criteria:
* Retain 15-20 Biosamples per species
* Select 1 experiment consisting of one Run per Biosample
* Use paired-end sequencing only
    * Minimum read length of 100bp
* Use data from HiSeq and later Illumina instruments, i.e. no Genome Analyzer data
* For metazoans, we preferentially selected brain or head samples if available
* Avoid experimental treatment such as knockdowns
* Select runs with a release date of 2011 or later

For species for which there are not enough Runs to reach the 15-20 Biosample goal, we relax the above criteria, including:
* Require a minimum read length of 50 instead of 100bp
    * This includes cases where there are >20 Biosamples on SRA, but they are dominated by only a few tissues, i.e. we relax the assumption to increase transcriptome representation
* Accept Runs with pre-2011 release dates

During the testing phase of this project, we evaluated useability of annotation tools with heliconine genomes and samples prior to establishing these criteria, such that we included a smalla number of GAII-derived samples, and we included more samples per species than noted above; in all cases we included less than 30 Biosamples per species.
  
## RNA-seq QC, pre-processing, and alignment
### QC and pre-processing
Prior to aligning RNA-seq paired-end reads to their respective genomes, we first do a quick quality check on libraries with [fastqc](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/), v. 0.11.8. We then strip residual adapter sequences from reads with [Trim Galore!](https://www.bioinformatics.babraham.ac.uk/projects/trim_galore/) v. 0.6.4, which is used to wrap [cutadapt](https://cutadapt.readthedocs.io/en/stable/) v. 2.10. A second run of fastqc is then peroformed to confirm success in removing residual adapter sequences. A generic example of our Trim Galore! command line is as follows:

```bash
trim_galore --path_to_cutadapt /FULL/PATH/TO/cutadapt --paired --retain_unpaired --phred33 --output_dir $(pwd)/trimmed_reads --length 35 -q 0 --stringency 5 -e 0.1 SRAId_R1.fastq SraId_R2.fastq
```
We do not trim on a base quality threshold (*-q 0*), and require a minimum read length of 35 bases. Trimmed reads < 35bp are discarded leading to unpaired "orphan" reads. While in our command line we keep unpaired reads, we do not use these reads subsequently for downstream analysis. The *stringency* and *-e* arguments influence the stringency of criteria for matching to hypothetical adapter sequences; see the *Trim Galore!* or *cutadapt* documentation for more details.

### Short read alignment
We align the adapter-trimmed RNA-seq reads to their respective reference genomes with two different aligners: [HISAT2](https://daehwankimlab.github.io/hisat2/) v. 2.2.1 and [STAR](https://github.com/alexdobin/STAR) v. 2.7.5c. 

#### HISAT2

We first build a HISAT2 index:

```bash
hisat2-build -p 6 /PATH/TO/GENOME/genome.fasta IndexBaseName
```
where IndexBaseName is simply the name you assign as the prefix for the various index files, and -p indicates the number of threads.

Then, run HISAT2:

```bash
hisat2 -p 12 -x /PATH/TO/HISAT2/INDEX/IndexBaseName -q --phred33 --min-intronlen 20 --max-intronlen 500000 -1 SRAId_adaptertrimmed_R1.fq SRAId_adaptertrimmed_R2.fq -S SRAId_hisat2.sam
```

The intron length arguments reflect defaults.

#### STAR

We run STAR in two-pass mode in a manner that leverages evidence for splice sites across all samples for a dataset (in our case, *heliconine* species) when performing alignment for individual samples.

We first build a STAR index:

```bash
STAR --runMode genomeGenerate --genomeSAindexNbases 13 --genomeDir $(pwd) --genomeFastaFiles /PATH/TO/GENOME/genome.fasta --runThreadN 12
```

The --genomeSAindexNbases argument is necessary for smaller genomes, otherwise the *genomeGenerate* tools will raise an exception.

Next, we perform 1st pass mapping:

```bash
STAR --runThreadN 8 --genomeDir /STAR/INDEX/DIRECTORY --outFileNamePrefix SRAId_STAR1stpass --readFilesIn SRAId_adaptertrimmed_R1.fq SRAId_adaptertrimmed_R2.fq
```

Finally, we perform 2nd-pass mapping, using the splice tables obtained for all samples in an experiment (i.e. species) to increase sensitivity with respect to possible splice sites. To do this, we make a director entitled *1stpass*,and move all the outputs from 1st pass alignment into that directory. We then feed a space-separated list of those tables to STAR:

```bash
tables=$(ls 1stpass/*tab)
STAR --runThreadN 8 --genomeDir /STAR/INDEX/DIRECTORY --sjdbFileChrStartEnd $tables --outFileNamePrefix SRAId_STAR2ndpass  --readFilesIn SRAId_adaptertrimmed_R1.fq SRAId_adaptertrimmed_R2.fq
```
