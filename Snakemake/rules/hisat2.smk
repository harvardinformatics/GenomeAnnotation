rule hisat2_align:
    input:
        hisat2index=glob("%s*.ht2" % config["Hisat2IndexDir"]),
        r1=config["fastqDir"] + "{sample}" + "_1_val_1.fq.gz",
        r2=config["fastqDir"] + "{sample}" + "_2_val_2.fq.gz"
    output:
        config["Hisat2Outdir"] + "{sample}" + "_hisat2.sam"
    conda:
        "../envs/hisat2.yml"
    threads:
        res_config['hisat2_align']['threads']
    resources:
        mem_mb = res_config['hisat2_align']['mem_mb'],
        time = res_config['hisat2_align']['time']
    shell:
        "hisat2 -p {threads} -x %s%s -q --phred33 --dta --min-intronlen 20 --max-intronlen 500000 -1 {input.r1} -2 {input.r2} -S {output}" % (config["Hisat2IndexDir"],config["Hisat2IndexPrefix"])

rule samsort:
    input:
        config["Hisat2Outdir"] + "{sample}" + "_hisat2.sam"
    output:
        config["Hisat2SamsortOutdir"] + "sorted_" + "{sample}" + "_hisat2.bam"
    conda:
        "../envs/samtools.yml"
    threads:
        res_config['samsort']['threads']
    resources:
        mem_mb = res_config['samsort']['mem_mb'],
        time = res_config['samsort']['time']
    shell:
        "samtools sort -@ {threads} -T tmp/{wildcards.sample}.aln.sorted -O bam -o {output} {input}"  
