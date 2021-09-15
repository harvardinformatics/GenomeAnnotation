rule stringtie:
    input:
        config["bamDir"] + "sorted_" + "{sample}" + "_" + config["alignment_tool"] + ".bam"
    output:
        config["assemblyDir"] + "{sample}" + "_stringtie_" + config["alignment_tool"] + ".gtf"
    conda:
        "../envs/stringtie.yml"
    shell:
        "stringtie {input} -p %s -o {output}"  % res_config['stringtie']['cpus']

rule merge:
    input:
        expand("{outdir}{sample}_stringtie_{aligner}.gtf", outdir=config["assemblyDir"],sample=SAMPLES,aligner=config["alignment_tool"])
    output:
        config["mergeDir"] + config["mergeLabel"] + "_stringtie-merge_" + config["alignment_tool"] + ".gtf"
    conda:
        "../envs/stringtie.yml"
    shell:
        "stringtie -p %s --merge gtflist.txt -o %s%s_stringtie-merge_%s.gtf" % (res_config['merge']['cpus'],config["mergeDir"],config["mergeLabel"],config["alignment_tool"])
