rule star_1stpass:
    input:
        r1=config["fastqDir"] + "{sample}" + "_1_val_1.fq.gz",
        r2=config["fastqDir"] + "{sample}" + "_2_val_2.fq.gz"
    output:
        config["Star1stPassOutdir"] + "{sample}" + "_STAR1stpassAligned.out.sam"
    conda:
        "../envs/star.yml"
    threads:
        res_config['star_1stpass']['threads']
    resources:
        mem_mb = res_config['star_1stpass']['mem_mb'],
        time = res_config['star_1stpass']['time']
    shell:
        "STAR --runThreadN {threads} --genomeDir %s --outFileNamePrefix %s{wildcards.sample}_STAR1stpass --outTmpDir {wildcards.sample}_1stpassSTARtmp --readFilesIn <(gunzip -c {input.r1}) <(gunzip -c {input.r2})" % (config["StarIndexDir"],config["Star1stPassOutdir"])

rule star_2ndpass:
    input:
        expand("{outdir}{sample}_STAR1stpassAligned.out.sam",outdir=config["Star1stPassOutdir"],sample=SAMPLES),
        r1=config["fastqDir"] + "{sample}" + "_1_val_1.fq.gz",
        r2=config["fastqDir"] + "{sample}" + "_2_val_2.fq.gz"
    output:
        config["Star2ndPassOutdir"] + "{sample}" + "_STAR2ndpassAligned.out.sam"
    conda:
        "../envs/star.yml"
    threads:
        res_config['star_2ndpass']['threads']
    resources:
        mem_mb = res_config['star_2ndpass']['mem_mb'],
        time = res_config['star_2ndpass']['time']
    
    shell: 
        "STAR --runThreadN {threads} --genomeDir %s --outSAMstrandField intronMotif --outTmpDir {wildcards.sample}_2ndpassSTARtmp --sjdbFileChrStartEnd {TABLES} --outFileNamePrefix %s{wildcards.sample}_STAR2ndpass --readFilesIn <(gunzip -c {input.r1}) <(gunzip -c {input.r2})" % (config["StarIndexDir"],config["Star2ndPassOutdir"])


rule samsort:
    input:
        config["Star2ndPassOutdir"] + "{sample}" + "_STAR2ndpassAligned.out.sam"
    output:
        config["StarSamsortOutdir"] + "sorted_" + "{sample}" + "_STAR2ndpass.bam"
    conda:
        "../envs/samtools.yml"
    threads:
        res_config['samsort']['threads']
    resources:
        mem_mb = res_config['samsort']['mem_mb'],
        time = res_config['samsort']['time']
    shell:
        "samtools sort -@ {threads} -T tmp/{wildcards.sample}.aln.sorted -O bam -o {output} {input}"  
