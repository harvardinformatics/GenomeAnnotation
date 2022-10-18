rule minimap2_index:
    input:
        genome_fasta = config['genome']
    output:
       minimizer_index = config['species'] + "_" + res_config['minimap2_index_datatype'] + '.mmi' 
    conda:
        "../envs/minimap2.yml"
    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config['minimap2_index']['mem_mb']
        time = res_config['minimap2_index']['time']
    params:
        indexdir = config["Minimap2IndexDir"]
        datatype_params =  config['minimap2_datatype_dict'][config['minimap2_index_datatype']
    shell:
        "minimap2 -d {output.minimizer_index} -x {params.datatype_params} {input.genome_fasta} 
