rule stringtie_star:
    input:
        config["StarSamsortOutdir"] + "sorted_" + "{sample}" + "_STAR2ndpass.bam"
    output:
        config["StringtieStarAssemblyDir"] + "{sample}" + "_stringtie-star.gtf"
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

rule stringtie_star_merge:
    input:
        expand("{outdir}{sample}_stringtie-star.gtf",outdir=config["StringtieStarAssemblyDir"],sample=SAMPLES)
    output:
        config["StringtieStarMergeDir"] + config["speciesname"] + "_stringtie-star_merge.gtf"
    conda:
        "../envs/stringtie.yml"
    resources:
        mem_mb = lambda wildcards, attempt: attempt * 1.5 * res_config['stringtie_merge']['mem_mb'],
        time = res_config['stringtie_merge']['time']
    params:
        mergedir = config["StringtieStarMergeDir"],
        species = config["speciesname"]
    shell:
        "rm -f stringtie-star_gtflist.txt \n"
        "for sample in {input}; do echo $sample >> stringtie-star_gtflist.txt;done \n"
        "stringtie -p {threads} --merge stringtie-star_gtflist.txt -o {params.mergedir}{params.species}_stringtie-star_merge.gtf"
