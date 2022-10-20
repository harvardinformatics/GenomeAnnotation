rule minimap2_index:
    input:
        genome_fasta = config["genome"]
    output:
       minimizer_index = config["Minimap2IndexDir"] + config["speciesname"] + "_" + config["minimap2_index_datatype"] + ".mmi" 
    conda:
        "../envs/minimap2.yml"
    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config["minimap2_index"]["mem_mb"],
        time = res_config["minimap2_index"]["time"]
    params:
        indexdir = config["Minimap2IndexDir"],
        datatype_params =  datatypes["minimap2_datatype2params"][config["minimap2_index_datatype"]]
    shell:
        "minimap2 -d {output.minimizer_index} -x {params.datatype_params} {input.genome_fasta}"

rule minimap2_align:
    input:
        minimap2index = config["Minimap2IndexDir"] + config["speciesname"] + "_" + config["minimap2_index_datatype"] + ".mmi",
        longreads = config["longreadsDir"] + "{sample}" + config["longreads_file_extension"]
    output:
       config["minimap2_outdir"] + "{sample}" + "_" + config["minimap2_index_datatype"] + ".sam"
    conda:
        "../envs/minimap2.yml"
    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config["minimap2_align"]["mem_mb"],
        time =  res_config["minimap2_align"]
    params:
        datatype = config["minimap2_index_datatype"],
        datatype_params = datatypes["minimap2_datatype2params"][config["minimap2_index_datatype"]],
        outdir = config["minimap2_outdir"]
    shell:
        "minimap2 -ax {params.datatype_params} {input.minimap2index} {input.longreads} > {params.outdir}{wildcards.sample}_{params.datatype}_minimap2.sam"
    
rule minimap2_sort:
    input:
        config["minimap2_outdir"] + "{sample}" + config["minimap2_index_datatype"] + ".sam"
    output:
        config["minimap2SamsortOutdir"] + "sorted_" + "{sample}" + "_" + config["minimap2_index_datatype"] + ".bam"
    conda:
        "../envs/samtools.yml"
    threads:
        res_config['samsort']['threads']
    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config['samsort']['mem_mb'],
        time = res_config['samsort']['time']
    params:
        outdir = config["minimap2SamsortOutdir"]
    shell:
        "rm -f {params.outdir}tmp/{wildcards.sample}.aln.sorted*bam;"
        "samtools sort -@ {threads} -T {params.outdir}tmp/{wildcards.sample}.aln.sorted -O bam -o {output} {input}"  
