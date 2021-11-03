rule star_1stpass:
    input:
        r1=config["fastqDir"] + "{sample}" + "_1_val_1.fq.gz",
        r2=config["fastqDir"] + "{sample}" + "_2_val_2.fq.gz"
    output:
        config["Star1stPassOutdir"] + "{sample}" + "_STAR1stpass.sam"
    conda:
        "../envs/star.yml"
    shell:
        "STAR --runThreadN %s --genomeDir %s --outFileNamePrefix %s{wildcards.sample}_STAR1stpass --outTmpDir {wildcards.sample}_1stpassSTARtmp --readFilesIn <(gunzip -c {input.r1}) <(gunzip -c {input.r2})" % (res_config['star_1stpass']['cpus'],config["StarIndexDir"],config["Star1stPassOutdir"])

rule star_2ndpass:
    input:
        expand("{outdir}{sample}_STAR1stpass.sam",outdir=config["Star1stPassOutdir"],sample=SAMPLES),
        r1=config["fastqDir"] + "{sample}" + "_1_val_1.fq.gz",
        r2=config["fastqDir"] + "{sample}" + "_2_val_2.fq.gz"
    output:
        config["Star2ndPassOutdir"] + "{sample}" + "_STAR2ndpass.sam"
    conda:
        "../envs/star.yml"
    
    shell: 
        "STAR --runThreadN %s --genomeDir %s --outSAMstrandField intronMotif --outTmpDir {wildcards.sample}_2ndpassSTARtmp --sjdbFileChrStartEnd {TABLES} --outFileNamePrefix %s{wildcards.sample}_STAR2ndpass --readFilesIn <(gunzip -c {input.r1}) <(gunzip -c {input.r2})" % (res_config['star_1stpass']['cpus'],config["StarIndexDir"],config["Star2ndPassOutdir"])


rule samsort:
    input:
        config["Star2ndPassOutdir"] + "{sample}" + "_STAR2ndpass.sam"
    output:
        config["samsortOutdir"] + "sorted_" + "{sample}" + "_STAR2ndpass.bam"
    conda:
        "../envs/samtools.yml"
    shell:
        "samtools sort -@ %s -T tmp/{wildcards.sample}.aln.sorted -O bam -o {output} {input}" % res_config['samsort']['cpus'] 
