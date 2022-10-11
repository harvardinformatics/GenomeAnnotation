localrules: GtfGenome2CdnaFasta,Gtf2Gff3

rule GtfGenome2CdnaFasta:
    input: 
        genome=config["genome"]
        gtf= config["StringtieHisat2MergeDir"] + config["speciesname"] + "_stringtie_merge.gtf"
    output:
       config["StringtieHisat2MergeDir"] + "CDSannotation/" + config["speciesname"] +"_stringtie_transcripts.fa"
    shell:
        "gtf_genome_to_cdna_fasta.pl {input.gtf} {input.genome} > {output}

rule Gtf2Gff3:
    input:
        config["StringtieHisat2MergeDir"] + config["speciesname"] + "_stringtie_merge.gtf"
    output:
        config["StringtieHisat2MergeDir"] + "CDSannotation/" + config["speciesname"] + "_stringtie_merge.gff3"
    shell:
        "gtf_to_alignment_gff3.pl {input} > {output}

rule transdecoder_longorfs:
    input:
        config["StringtieHisat2MergeDir"] + "CDSannotation/" + config["speciesname"] +"_stringtie_transcripts.fa"
    output:
        config["StringtieHisat2MergeDir"] + "CDSannotation/" + config["speciesname"] + "_stringtie_transcripts.fa.transdecoder_dir/longest_orfs.pep" 
    shell:
        "TransDecoder.LongOrfs -t {input}
