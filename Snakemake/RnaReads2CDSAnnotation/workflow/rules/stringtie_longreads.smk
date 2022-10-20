rule stringtie_longreads:
    input:
        config["minimap2SamsortOutdir"] + "sorted_" + "{sample}" + "_" + config["minimap2_index_datatype"] + ".bam"
    output:
       config["StringtieLongReadsAssemblyDir"] + "{sample}" + "_" + config["minimap2_index_datatype"] + "_stringtie-minimap2.gtf"
    conda:
        "../envs/stringtie.yml"
    threads:
        threads = res_config["stringtie"]["threads"]
    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config["stringtie"]["mem_mb"],
        time =  res_config["stringtie"]["time"]
    params:
        datatype = config["minimap2_index_datatype"],
        outdir = config["minimap2_outdir"]
    shell:
        "stringtie {input} -p {threads} -L -o {output}"


rule stringtie_longreads_merge:
    input:
        expand("{outdir}{sample}_{datatype}_stringtie-minimap2.gtf",outdir=config["StringtieLongReadsAssemblyDir"],sample=SAMPLES,datatype=config["minimap2_index_datatype"])
    output:
        config["StringtieLongReadsMergeDir"] + config["speciesname"] + "_" + config["minimap2_index_datatype"] + "_stringtie-minimap2_merge.gtf"
    conda:
        "../envs/stringtie.yml"
    threads:
        res_config["stringtie_merge"]["threads"]
    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config["stringtie_merge"]["mem_mb"],
        time = res_config["stringtie_merge"]["time"]
    params:
        mergedir = config["StringtieLongReadsMergeDir"],
        species = config["speciesname"],
        datatype = config["minimap2_index_datatype"]
    shell:
        "rm -f stringtie-longreads_gtflist.txt \n"
        "for sample in {input}; do echo $sample >> stringtie-longreads_gtflist.txt;done \n"
        "stringtie -p {threads} --merge stringtie-longreads_gtflist.txt -o {params.mergedir}{params.species}_{datatype}_stringtie-minimap2_merge.gtf" 

