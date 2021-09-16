rule scallop:
    input:
        config["bamDir"] + "sorted_" + "{sample}" + "_" + config["alignment_tool"] + ".bam"
    output:
        config["assemblyDir"] + "{sample}" + "_scallop_" + config["alignment_tool"] + ".gtf"
    conda:
        "../envs/scallop.yml"
    shell:
        "scallop -i {input} -o {output}"  

rule taco:
    input:
        expand("{outdir}{sample}_scallop_{aligner}.gtf", outdir=config["assemblyDir"],sample=SAMPLES,aligner=config["alignment_tool"])
    output:
        config["mergeDir"] + "assembly.gtf"
    conda:
        "../envs/taco.yml"
    shell:
        "taco_run -p %s --gtf-expr-attr RPKM -o %s gtflist.txt" % (res_config["taco"]["cpus"],config["mergeDir"])
