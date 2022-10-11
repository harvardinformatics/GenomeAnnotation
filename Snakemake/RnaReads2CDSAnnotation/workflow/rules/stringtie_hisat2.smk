rule stringtie_hisat2:
    input:
        config["Hisat2SamsortOutdir"] + "sorted_" + "{sample}" + "_hisat2.bam"
    output:
        config["StringtieHisat2AssemblyDir"] + "{sample}" + "_stringtie-hisat2.gtf"
    conda:
        "../envs/stringtie.yml"
    threads:
        res_config['stringtie']['threads']

    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config['stringtie']['mem_mb'],
        time = res_config['stringtie']['time'] 
    run:
        if {params.strandedness} == "NA":
            shell("stringtie {input} -p {threads} -o {output}")
        elif {params.strandedness} == "FR":
            shell("stringtie {input} --fr -p {threads} -o {output}")
        elif {params.strandedness} == "RF":
            shell("stringtie {input} --fr -p {threads} -o {output}")
        else:
            raise ValueError('strandedness value not in allowable values ["FR","RF","NA"]')  


rule stringtie_hisat2_merge:
    input:
        expand("{outdir}{sample}_stringtie-hisat2.gtf",outdir=config["StringtieHisat2AssemblyDir"],sample=SAMPLES)
    output:
        config["StringtieHisat2MergeDir"] + config["speciesname"] + "_stringtie-hisat2_merge.gtf"
    conda:
        "../envs/stringtie.yml"
    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config['stringtie_merge']['mem_mb'],
        time = res_config['stringtie_merge']['time']
    params:
        mergedir = config["StringtieHisat2MergeDir"],
        species = config["speciesname"]
    shell:
        "rm -f stringtie-hisat2_gtflist.txt \n"
        "for sample in {input}; do echo $sample >> stringtie-hisat2_gtflist.txt;done \n"
        "stringtie -p {threads} --merge stringtie-hisat2_gtflist.txt -o {params.mergedir}{params.species}_stringtie-hisat2_merge.gtf"

