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
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config['hisat2_align']['mem_mb'],
        time = res_config['hisat2_align']['time']
    params:
        indexdir = config["Hisat2IndexDir"],
        indexprefix = config["Hisat2IndexPrefix"]
    script:
        "scripts/run_hisat2.py -p {threads} -i {params.indexdir}{params.indexprefix} -strand {params.strandedness} \
        -minintron {params.intronmin} -maxintron {params.intronmax} -1 {input.r1} -2 {input.r2}"  
            
rule samsort_hisat2:
    input:
        config["Hisat2Outdir"] + "{sample}" + "_hisat2.sam"
    output:
        config["Hisat2SamsortOutdir"] + "sorted_" + "{sample}" + "_hisat2.bam"
    conda:
        "../envs/samtools.yml"
    threads:
        res_config['samsort']['threads']
    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config['samsort']['mem_mb'],
        time = res_config['samsort']['time']
    params:
        outdir = config["Hisat2SamsortOutdir"]
    shell:
        "rm -f {params.outdir}tmp/{wildcards.sample}.aln.sorted*bam;"
        "samtools sort -@ {threads} -T {params.outdir}tmp/{wildcards.sample}.aln.sorted -O bam -o {output} {input}" 

