# Scallop
[Scallop](https://github.com/Kingsford-Group/scallop), like StringTie, assembles transcripts directly from RNA-seq spliced alignments to a genome. It's approach is slightly different in that it uses a phase-preserving graph decomposition algorithm that putatively preserves long-range phase information in a splice graph such that it should, in theory, be better able to distinguish alternative splice variants than other approaches. Reported performance metrics in [Shao and Kingsford, 2017, **Nature Biotechnology**](https://www.nature.com/articles/nbt.4020) indicate it outperforms StringTie, a more commonly used method. Like StringTie, Scallop assembles a set of transcripts for an individual sample. Unlike StringTie however, it has no built-in function for merging sample-level assemblies. Following the practice of scallop developers, we use [TACO](https://tacorna.github.io/) to merge individual scallop assemblies.

Similar to how we implement StringTie, we first built a Scallop conda enviornment:
```bash
module load python
conda create -n scallop -c bioconda scallop
```
One then launches scallop with [scallop.sh](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/Scallop/slurm_scripts/scallop.sh)
```bash
sbatch scallop.sh $sorted.bam
```
where $sorted.bam is the spliced alignment to the genome of the RNA-seq reads. It is worth noting that, unlike StringTie, Scallop is single-threaded. While it is relatively fast, one may need to increase the time limit specified in the slurm script if the bam file originates from a deeply sequenced RNA-seq library.

Once individual Scallop assemblies have been generated, one merges them with taco using [taco.sh](https://github.com/harvardinformatics/GenomeAnnotation/blob/master/Scallop/slurm_scripts/taco.sh)
```bash
sbatch taco.sh $my_outputfile_prefix
```
where $my_outputfile_prefix is the name you specify for the analysis. TACO takes as its final argument a text file listing, one per line, the gtf files from the sample-level assemblies. The script we provide automatically generates this file, under the assumption that all the gtfs are in the directory from which you launched the script. If the gtfs are distributed in separate directories, remove the line in the script creating the text file and manually create your own with full paths to the sample gtf files. TACO will produce a directory named $my_outfile_prefix, within which the merged annotation is named *assembly.gtf*. 
