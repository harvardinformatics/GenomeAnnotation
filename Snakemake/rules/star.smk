rule star_1stpass:
    input:
        r1=config["fastqDir"] + "{sample}" + "_1_val_1.fq.gz",
        r2=config["fastqDir"] + "{sample}" + "_2_val_2.fq.gz"
    output:
        config["Star1stPassOutdir"] + "{sample}" + "_STAR1stpass.sam"
    conda:
        "../envs/star.yml"
    shell:
        "STAR --runThreadN %s --genomeDir %s --readFilesCommand zcat -outFileNamePrefix %s{wildcards.sample}_STAR1stpass --readFilesIn {input.r1} {input.r2}" % (res_config['star_1stpass']['cpus'],config["StarIndexDir"],config["Star1stPassOutdir"])

rule star_2ndpass:
    input:
        tables=glob("%s*tab" % config["Star1stPassOutdir"]),
        r1=config["fastqDir"] + "{sample}" + "_1_val_1.fq.gz",
        r2=config["fastqDir"] + "{sample}" + "_2_val_2.fq.gz"
    output:
        config["Star2ndPassOutdir"] + "{sample}" + "_STAR2ndpass.sam"
    conda:
        "../envs/star.yml"
    
    shell:
        "STAR --runThreadN %s --genomeDir %s --outSAMstrandField intronMotif --readFilesCommand zcat --sjdbFileChrStartEnd {input.tables} --outFileNamePrefix %s{wildcards.sample}_STAR2ndpass --readFilesIn {input.r1} {input.r2}" % (res_config['star_1stpass']['cpus'],config["StarIndexDir"],config["Star2ndPassOutdir"])


rule samsort:
    input:
        config["Star2ndPassOutdir"] + "{sample}" + "_STAR2ndpass.sam"
    output:
        config["samsortOutdir"] + "sorted_" + "{sample}" + "_STAR2ndpass.bam"
    conda:
        "../envs/samtools.yml"
    shell:
        "samtools sort -@ %s -T tmp/{wildcards.sample}.aln.sorted -O bam -o {output} {input}" % res_config['samsort']['cpus'] 
