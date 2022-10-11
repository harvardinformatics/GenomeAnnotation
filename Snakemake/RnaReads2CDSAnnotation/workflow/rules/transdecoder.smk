localrules: GtfGenome2CdnaFasta,Gtf2Gff3

rule GtfGenome2CdnaFasta:
    input: 
        genome=config["genome"]
        gtf={params.mergedir}{params.species}_stringtie_merge.gtf
    output:
       {params.mergedir}transdecoder/{params.species}_stringtie_transcripts.fa
    shell:
        "gtf_genome_to_cdna_fasta.pl {input.gtf} {input.genome} > {output}

rule Gtf2Gff3:
    input:
        {params.mergedir}{params.species}_stringtie_merge.gtf
    output:
        {params.mergedir}{params.species}_stringtie_merge.gff3
    shell:
        "gtf_to_alignment_gff3.pl {input} > {output}     
