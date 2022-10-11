rule star_1stpass:
    input:
        r1=config["fastqDir"] + "{sample}" + "_1_val_1.fq.gz",
        r2=config["fastqDir"] + "{sample}" + "_2_val_2.fq.gz"
    output:
        config["Star1stPassOutdir"] + "{sample}" + "_STAR1stpassSJ.out.tab"
    conda:
        "../envs/star.yml"
    threads:
        res_config['star_1stpass']['threads']
    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config['star_1stpass']['mem_mb'],
        time = res_config['star_1stpass']['time']
    params:
        outdir = config["Star1stPassOutdir"],
        indexdir = config["StarIndexDir"]
    shell:
        "rm -rf {params.outdir}{wildcards.sample}_1stpassSTARtmp;"
        "STAR --runThreadN {threads} --genomeDir {params.indexdir} --sjdbOverhang {params.overhang} " 
         "--outFileNamePrefix {params.outdir}{wildcards.sample}_STAR1stpass " 
         "--outTmpDir {params.outdir}{wildcards.sample}_1stpassSTARtmp "
         "--readFilesIn <(gunzip -c {input.r1}) <(gunzip -c {input.r2})"

rule star_2ndpass:
    input:
        tablelist = expand("{outdir}{sample}_STAR1stpassSJ.out.tab", outdir=config["Star1stPassOutdir"],sample=SAMPLES),
        r1=config["fastqDir"] + "{sample}" + "_1_val_1.fq.gz",
        r2=config["fastqDir"] + "{sample}" + "_2_val_2.fq.gz"
    output:
        config["Star2ndPassOutdir"] + "{sample}" + "_STAR2ndpassAligned.out.sam"
    conda:
        "../envs/star.yml"
    threads:
        res_config['star_2ndpass']['threads']
    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config['star_2ndpass']['mem_mb'],
        time = res_config['star_2ndpass']['time']
    params:
        outdir = config["Star2ndPassOutdir"],
        indexdir = config["StarIndexDir"],
        tablestring = ' '.join(expand("{outdir}{sample}_STAR1stpassSJ.out.tab", outdir=config["Star1stPassOutdir"],sample=SAMPLES))
    shell:
        "rm -rf {params.outdir}{wildcards.sample}_2ndpassSTARtmp;"
        "STAR --runThreadN {threads} "
        "--genomeDir {params.indexdir} --outSAMstrandField intronMotif "
        "--outTmpDir {params.outdir}{wildcards.sample}_2ndpassSTARtmp "
        " --sjdbOverhang {params.overhang} --sjdbFileChrStartEnd {params.tablestring} "
        "--outFileNamePrefix {params.outdir}{wildcards.sample}_STAR2ndpass "
        "--readFilesIn <(gunzip -c {input.r1}) <(gunzip -c {input.r2})" 
     
rule samsort_star:
    input:
        config["Star2ndPassOutdir"] + "{sample}" + "_STAR2ndpassAligned.out.sam"
    output:
        config["StarSamsortOutdir"] + "sorted_" + "{sample}" + "_STAR2ndpass.bam"
    conda:
        "../envs/samtools.yml"
    threads:
        res_config['samsort']['threads']
    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config['samsort']['mem_mb'],
        time = res_config['samsort']['time']
    params:
        outdir = config["StarSamsortOutdir"]
    shell:
        "rm -f {params.outdir}tmp/{wildcards.sample}.aln.sorted*bam;"
        "samtools sort -@ {threads} -T {params.outdir}tmp/{wildcards.sample}.aln.sorted -O bam -o {output} {input}" 
