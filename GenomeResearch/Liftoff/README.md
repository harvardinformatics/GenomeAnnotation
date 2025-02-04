#Liftoff
[Liftoff](https://github.com/agshumate/Liftoff) transfers annotations from a high-quality reference annotation to a new genome, via internally computed whole-genome alignment. It performs such transfer on both coding and non-coding genome annotation features. Because we implemented Liftoff across varying degrees of evolutionary divergence, we also supplied additional parameters that are believed to improve performance. Specifically, we ran lifoff as follows:
```
liftoff -p $NUMBER_THREADS -polish -g $REFERENCE_GFF -o ${TARGET_GENOME}.gff3 -flank 0.2 -d 3 $TARGET_GENOME_FASTA $REFERENCE_GENOME_FASTA
```

where the instance of upper case strings preceeded with "$" indicate values for command line arguments to be supplied by the user. The `-polish` switch makes Liftoff attempt to correct disruptions of open reading frames (likely due to errors during the whole genome alignment step). When this switch is used, Liftoff generates both the raw, and polished predicted annotations, with the former being generated first. In a number of cases polishing fails, producing hard to diagnose error messages, although an "empty array" component to the exception makes us suspect that there may not be enough candidate polishings to be evaluated, i.e. polishing may not be necessary. In these cases, we simply use the raw annotation output. 
