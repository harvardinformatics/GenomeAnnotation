localrules: GtfGenome2CdnaFasta,Gtf2Gff3,LongOrfsSplit

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

rule TransdecoderLongOrfs:
    input:
        config["StringtieHisat2MergeDir"] + "CDSannotation/" + config["speciesname"] +"_stringtie_transcripts.fa"
    output:
        config["StringtieHisat2MergeDir"] + "CDSannotation/" + config["speciesname"] + "_stringtie_transcripts.fa.transdecoder_dir/longest_orfs.pep" 
    shell:
        "TransDecoder.LongOrfs -t {input}

rule LongOrfsSplit:
    input:
        config["StringtieHisat2MergeDir"] + "CDSannotation/" + config["speciesname"] + "_stringtie_transcripts.fa.transdecoder_dir/longest_orfs.pep"
    output:
        config["StringtieHisat2MergeDir"] + "CDSannotation/blastp/orf_splitfile_list.txt"
    script:
        "FastaSplitter.py -f {input} -maxn 1000 -counter {output}

rule LongorfsBlastp:
    input:
        config["StringtieHisat2MergeDir"] + "CDSannotation/blastp/longest_orfs_" + {subfile} + ".fasta"
    output:
        config["StringtieHisat2MergeDir"] + "CDSannotation/blastp/longest_orfs_" + {subfile} + ".blastp.outfmt6.tsv"
    shell:
        blastp -max_target_seqs 5 -num_threads 8 -evalue 1e-4 -query {input} -outfmt 6 -db config["BlastpDb"] > {output} 
