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

