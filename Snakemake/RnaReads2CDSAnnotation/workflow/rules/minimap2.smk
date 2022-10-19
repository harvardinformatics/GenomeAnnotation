rule minimap2_index:
    input:
        genome_fasta = config["genome"]
    output:
       minimizer_index = config["minimap2_index_dir"] + config["species"] + "_" + config["minimap2_index_datatype"] + ".mmi" 
    conda:
        "../envs/minimap2.yml"
    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config["minimap2_index"]["mem_mb"],
        time = res_config["minimap2_index"]["time"]
    params:
        indexdir = config["Minimap2IndexDir"],
        datatype_params =  config["minimap2_datatype_dict"][config["minimap2_index_datatype"]]
    shell:
        "minimap2 -d {output.minimizer_index} -x {params.datatype_params} {input.genome_fasta}"

rule minimap2_align:
    input:
        minimap2index = config["minimap2_index_dir"] + config["species"] + "_" + config["minimap2_index_datatype"] + ".mmi",
        longreads = expand({datadir}{sample}.{ext},datadir=config["longreadsDir"],ext=[".fa",".fq",".fastq"])
    output:
       config["minimap_outdir"] + "{sample}" + config["minimap2_index_datatype"] + ".sam"
    conda:
        "../envs/minimap2.yml"
    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config["minimap2_align"]["mem_mb"],
        time =  res_config["minimap2_align"]
    params:
        datatype = config["minimap2_index_datatype"]
        datatype_params = config["minimap2_datatype_dict"][config["minimap2_index_datatype"]],
        outdir = config["minimap_outdir"]
    shell:
        "minimap2 -ax {params.datatype_params} {input.minimapindex} {input.longreads} > {params.outdir}{wildcards.sample}_{params.datatype}_minimap2.sam"
     
