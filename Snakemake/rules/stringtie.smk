rule stringtie:
    input:
        config["StringtieBamDir"] + "sorted_" + "{sample}" + "_" + config["StringtieAlignmentTool"] + ".bam"
    output:
        config["StringtieAssemblyDir"] + "{sample}" + "_stringtie_" + config["StringtieAlignmentTool"] + ".gtf"
    conda:
        "../envs/stringtie.yml"
    threads:
        res_config['stringtie']['threads']

    resources:
        mem_mb = res_config['stringtie']['mem_mb'],
        time = res_config['stringtie']['time'] 
    shell:
        "stringtie {input} -p {threads} -o {output}"  

rule stringtie_merge:
    input:
        expand("{outdir}{sample}_stringtie_{aligner}.gtf", outdir=config["StringtieAssemblyDir"],sample=SAMPLES,aligner=config["StringtieAlignmentTool"])
    output:
        config["StringtieMergeDir"] + config["StringtieMergeLabel"] + "_stringtie-merge_" + config["StringtieAlignmentTool"] + ".gtf"
    conda:
        "../envs/stringtie.yml"
    shell:
        "stringtie -p {threads} --merge gtflist.txt -o %s%s_stringtie-merge_%s.gtf" % (config["StringtieMergeDir"],config["StringtieMergeLabel"],config["StringtieAlignmentTool"])
