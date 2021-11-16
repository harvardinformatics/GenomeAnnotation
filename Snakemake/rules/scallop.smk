rule scallop:
    input:
        config["Hisat2SamsortOutdir"] + "sorted_" + "{sample}" + "_" + config["ScallopAlignmentTool"] + ".bam"
    output:
        config["ScallopAssemblyDir"] + "{sample}" + "_scallop_" + config["ScallopAlignmentTool"] + ".gtf"
    conda:
        "../envs/scallop.yml"
    threads:
        res_config['scallop']['threads']
    resources:
        mem_mb = res_config['scallop']['mem_mb'],
        time = res_config['scallop']['time'] 
    shell:
        "scallop -i {input} -o {output}"  

rule taco:
    input:
        expand("{outdir}{sample}_scallop_{aligner}.gtf", outdir=config["ScallopAssemblyDir"],sample=SAMPLES,aligner=config["ScallopAlignmentTool"])
    output:
        directory(config["TacoDir"]) + "assembly.gtf"
    conda:
        "../envs/taco.yml"
    threads:
        res_config['taco']['threads']
    resources:
        mem_mb = res_config['taco']['mem_mb'],
        time = res_config['taco']['time'] 
    shell:
        "taco_run -p {threads} --gtf-expr-attr RPKM -o %s gtflist.txt" % directory(config["TacoDir"])
