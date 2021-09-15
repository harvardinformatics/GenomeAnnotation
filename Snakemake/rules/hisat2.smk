rule hisat2_align:
    input:
        hisat2index=glob("%s*.ht2" % config["hisat2IndexDir"]),
        r1=config["fastqDir"] + "{sample}" + "_1_val_1.fq.gz",
        r2=config["fastqDir"] + "{sample}" + "_2_val_2.fq.gz"
    output:
        config["hisat2Outdir"] + "{sample}" + "_hisat2.sam"
    conda:
        "../envs/hisat2.yml"
    shell:
        "hisat2 -p %s -x %s%s -q --phred33 --dta --min-intronlen 20 --max-intronlen 500000 -1 {input.r1} -2 {input.r2} -S {output}" % (res_config['hisat2_align']['cpus'],config["hisat2IndexDir"],config["hisat_index_prefix"])

rule samsort:
    input:
        config["hisat2Outdir"] + "{sample}" + "_hisat2.sam"
    output:
        config["samsortOutdir"] + "sorted_" + "{sample}" + "_hisat2.bam"
    conda:
        "../envs/samtools.yml"
    shell:
        "samtools sort -@ %s -T tmp/{wildcards.sample}.aln.sorted -O bam -o {output} {input}" % res_config['samsort']['cpus']  
