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
