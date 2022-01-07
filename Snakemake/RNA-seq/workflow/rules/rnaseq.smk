###########
#  HISAT2 #
###########

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
    shell:
        "hisat2 -p {threads} -x {params.indexdir}{params.indexprefix} -q --phred33 --dta --min-intronlen 20 --max-intronlen 500000 -1 {input.r1} -2 {input.r2} -S {output}"

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

#########
#  STAR #
#########

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
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config['star_1stpass']['mem_mb'],
        time = res_config['star_1stpass']['time']
    params:
        outdir = config["Star1stPassOutdir"],
        indexdir = config["StarIndexDir"]
    shell:
        "rm -rf {params.outdir}{wildcards.sample}_1stpassSTARtmp;"
        "STAR --runThreadN {threads} --genomeDir {params.indexdir} " 
         "--outFileNamePrefix {params.outdir}{wildcards.sample}_STAR1stpass " 
         "--outTmpDir {params.outdir}{wildcards.sample}_1stpassSTARtmp "
         "--readFilesIn <(gunzip -c {input.r1}) <(gunzip -c {input.r2})"



def CreateStarSpliceTableList(outdir,SAMPLES=SAMPLES):
    tablelist = expand("{outdir}{sample}_STAR1stpassSJ.out.tab", outdir=config["Star1stPassOutdir"],sample=SAMPLES)
    tablestring = ' '.join(tablelist)
    return tablestring

rule star_2ndpass:
    input:
        tables = CreateStarSpliceTableList(config["Star1stPassOutdir"]),
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
    shell:
        "rm -rf {params.outdir}{wildcards.sample}_2ndpassSTARtmp;"
        "STAR --runThreadN {threads} "
        "--genomeDir {params.indexdir} --outSAMstrandField intronMotif "
        "--outTmpDir {params.outdir}{wildcards.sample}_2ndpassSTARtmp --sjdbFileChrStartEnd {input.tables} "
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

############
# STRINGTIE #
############

# HISAT2 #
rule stringtie_hisat2:
    input:
        config["Hisat2SamsortOutdir"] + "sorted_" + "{sample}" + "_hisat2.bam"
    output:
        config["StringtieHisat2AssemblyDir"] + "{sample}" + "_stringtie-hisat2.gtf"
    conda:
        "../envs/stringtie.yml"
    threads:
        res_config['stringtie']['threads']

    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config['stringtie']['mem_mb'],
        time = res_config['stringtie']['time'] 
    shell:
        "stringtie {input} -p {threads} -o {output}"  


rule stringtie_hisat2_merge:
    input:
        expand("{outdir}{sample}_stringtie-hisat2.gtf",outdir=config["StringtieHisat2AssemblyDir"],sample=SAMPLES)
    output:
        config["StringtieHisat2MergeDir"] + config["speciesname"] + "_stringtie-hisat2_merge.gtf"
    conda:
        "../envs/stringtie.yml"
    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config['stringtie_merge']['mem_mb'],
        time = res_config['stringtie_merge']['time']
    params:
        mergedir = config["StringtieHisat2MergeDir"],
        species = config["speciesname"]
    shell:
        "rm -f stringtie-hisat2_gtflist.txt \n"
        "for sample in {input}; do echo $sample >> stringtie-hisat2_gtflist.txt;done \n"
        "stringtie -p {threads} --merge stringtie-hisat2_gtflist.txt -o {params.mergedir}{params.species}_stringtie-hisat2_merge.gtf"

# STAR #
rule stringtie_star:
    input:
        config["StarSamsortOutdir"] + "sorted_" + "{sample}" + "_STAR2ndpass.bam"
    output:
        config["StringtieStarAssemblyDir"] + "{sample}" + "_stringtie-star.gtf"
    conda:
        "../envs/stringtie.yml"
    threads:
        res_config['stringtie']['threads']

    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config['stringtie']['mem_mb'],
        time = res_config['stringtie']['time']
    shell:
        "stringtie {input} -p {threads} -o {output}"

rule stringtie_star_merge:
    input:
        expand("{outdir}{sample}_stringtie-star.gtf",outdir=config["StringtieStarAssemblyDir"],sample=SAMPLES)
    output:
        config["StringtieStarMergeDir"] + config["speciesname"] + "_stringtie-star_merge.gtf"
    conda:
        "../envs/stringtie.yml"
    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config['stringtie_merge']['mem_mb'],
        time = res_config['stringtie_merge']['time']
    params:
        mergedir = config["StringtieStarMergeDir"],
        species = config["speciesname"]
    shell:
        "rm -f stringtie-star_gtflist.txt \n"
        "for sample in {input}; do echo $sample >> stringtie-star_gtflist.txt;done \n"
        "stringtie -p {threads} --merge stringtie-star_gtflist.txt -o {params.mergedir}{params.species}_stringtie-star_merge.gtf"

###########
# SCALLOP #
###########

# HISAT2 #
rule scallop_hisat2:
    input:
        config["Hisat2SamsortOutdir"] + "sorted_" + "{sample}" + "_hisat2.bam"
    output:
        config["ScallopHisat2AssemblyDir"] + "{sample}" + "_scallop-hisat2.gtf"
    conda:
        "../envs/scallop.yml"
    threads:
        res_config['scallop']['threads']
    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config['scallop']['mem_mb'],
        time = res_config['scallop']['time'] 
    shell:
        "scallop -i {input} -o {output}"  

rule taco_hisat2:
    input:
        expand("{outdir}{sample}_scallop-hisat2.gtf", outdir=config["ScallopHisat2AssemblyDir"],sample=SAMPLES)
    output:
        touch("mytask.taco.hisat2.done")
    conda:
        "../envs/taco.yml"
    threads:
        res_config['taco']['threads']
    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config['taco']['mem_mb'],
        time = res_config['taco']['time']
    params:
        tacodir = config["TacoHisat2Dir"] 
    shell:
        "rm -f scallop.gtflist.hisat2.txt \n"
        "for sample in {input}; do echo $sample >> scallop.gtflist.hisat2.txt;done \n"
        "taco_run -p {threads} --gtf-expr-attr RPKM -o {params.tacodir} scallop.gtflist.hisat2.txt"

rule scallop_star:
    input:
        config["StarSamsortOutdir"] + "sorted_" + "{sample}" + "_STAR2ndpass.bam"
    output:
        config["ScallopStarAssemblyDir"] + "{sample}" + "_scallop-star.gtf"
    conda:
        "../envs/scallop.yml"
    threads:
        res_config['scallop']['threads']
    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config['scallop']['mem_mb'],
        time = res_config['scallop']['time']
    shell:
        "scallop -i {input} -o {output}"

rule taco_star:
    input:
        expand("{outdir}{sample}_scallop-star.gtf", outdir=config["ScallopStarAssemblyDir"],sample=SAMPLES)
    output:
        touch("mytask.taco.star.done")
    conda:
        "../envs/taco.yml"
    threads:
        res_config['taco']['threads']
    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config['taco']['mem_mb'],
        time = res_config['taco']['time']
    params:
        tacodir = config["TacoStarDir"]
    shell:
        "rm -f scallop.gtflist.star.txt \n"
        "for sample in {input}; do echo $sample >> scallop.gtflist.star.txt;done \n"
        "taco_run -p {threads} --gtf-expr-attr RPKM -o {params.tacodir} scallop.gtflist.star.txt"
