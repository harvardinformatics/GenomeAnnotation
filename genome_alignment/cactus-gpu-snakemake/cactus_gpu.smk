#############################################################################
# Pipeline for read mapping simulations with varying divergence
#############################################################################

import sys
import os
import re
import subprocess

sys.path.append(os.path.abspath(os.path.join(os.path.realpath(workflow.basedir), "lib/")))
import cactuslib
# Add the path to the helper functions library and import it

#############################################################################
# Example cmd for mouse genome

# Need to first run the cactus-preprocess script to generate commands and cactus config files:
# cactus-prepare genomes.txt --outDir turtle-output --outSeqFile turtle-output/turtles.txt --outHal turtle-output/turtles.hal --jobStore jobstore --gpu --defaultCores 32

# Run snakemake
# snakemake -p -s cactus_gpu.smk --configfile turtle-cfg.yaml --profile profiles/slurm_profile/ --dryrun

# To generate rulegraph image:
# snakemake -p -s cactus_gpu.smk --configfile turtle-cfg.yaml --profile profiles/slurm_profile/ --dryrun --rulegraph | dot -Tpng > dag-new.png

#############################################################################

# Cactus works via a post-order transversal of the input tree and runs several steps at each node of the tree.
# For tip nodes Cactus runs its preprocess command which masks the input fasta for each genome
#   1. Preprocess (mask)
#       Inputs: Original genome fasta
#       Output: Masked genome fasta with same basename as input fasta, but in the Cactus output directory
#
# For each internal node, cactus runs 3 commands:
#   2. Blast
#       Inputs: The fasta sequences of the descendant nodes. For a tip this is the one from step 1, for an internal node
#               this is the result of step 4
#       Output: A .cigar file
#
#   3. Align
#       Inputs: The .cigar file from the previous step and the fasta sequences of the descendant nodes. 
#               For a tip this is the one from step 1, for an internal node this is the result of step 4 
#       Output: A .hal file
#               
#   4. Convert (hal2fasta)
#       Inputs: The .hal file from the previous step
#       Output: A fasta file for the current node
#
#   5. Append (halAppendSubtree)
#       Inputs: All .hal files from each internal node in the tree
#       Outputs: The .hal file at the root of the tree (Anc00.hal) with all alignments appended to it

#############################################################################
# System setup

debug = False;

wd = config["working_dir"];
os.chdir(wd);
#print(os.getcwd());
# Switching to the working directory of the project so paths can be relative

TMPDIR = config["tmp_dir"];
# A directory with lots of space to use for temporary files generated by the cactus-align command

CACTUS_PATH = "singularity exec --nv --cleanenv " + config["cactus_path"];
CACTUS_PATH_TMP = "singularity exec --nv --cleanenv --bind " + TMPDIR + ":/tmp " + config["cactus_path"];
# The path to the cactus executable with and without a tmpdir binding
# Must be gpu enabled for now

#############################################################################
# Input files and output paths

INPUT_FILE = config["input_file"];
# The cactus input file used to generate the config file with cactus-prepare

OUTPUT_DIR = config["output_dir"];
# The output directory specified when cactus-prepare was run

CACTUS_FILE = os.path.join(OUTPUT_DIR, os.path.basename(INPUT_FILE));
CONFIG_FILE = os.path.join(OUTPUT_DIR, "config-prepared.xml");
# The config files genearated from cactus-prepare
# config: XML config file probably read by some of the sub-programs...
# output: lists the sequence files expected as output for all nodes in the tree

#job_path = os.path.join(OUTPUT_DIR, "jobstore");
# The temporary/job directory specified in cactus-prepare

# final_hal_file = "turtles.hal";
# The final hal file generated on the root node -- currently still encoded as Anc00.hal

#############################################################################
# Reading files

tips = {};
# The main dictionary hold information and file paths for tips in the tree:
# [output fasta file from mask step] : { 'input' : "original genome fasta file", 'name' : "genome name in tree", 'output' : "expected output from mask step (same as key)" }

first = True;
for line in open(INPUT_FILE):
    if first:
        #tree = line.strip();
        first = False;
        continue;
    # The first line contains the input tree... skip

    line = line.strip().split("\t");
    cur_base = os.path.basename(line[1]);
    tips[line[0]] = { 'input' : [line[1]], 'name' : line[0], 'output' : "NA" };
## Read the genome names and original genome fasta file paths from the same cactus input file used with cactus-prepare

if debug:
    for g in tips:
        print(g, tips[g]);
    print("===================================================================================");


####################

internals = {};
# The main dictionary hold information and file paths for internal nodes in the tree:
# [node name] : { 'name' : "node name in tree", 'blast-inputs' : [the expected inputs for the blast step], 'align-inputs' : [the expected inputs for the align step],
#                   'hal-inputs' : [the expected inputs for the hal2fasta step], 'blast-output' : "the .cigar file output from the blast step",
#                   'align-output' : "the .hal file output from the align step", 'hal-output' : "the fasta file output from the hal2fasta step" }

first = True;
for line in open(CACTUS_FILE):
    if first:
        anc_tree = line.strip();
        first = False;
        continue;
    # The first line contains the tree with internal nodes labeled... save this for later

    line = line.strip().split("\t");
    name = line[0];
    cur_base = os.path.basename(line[1]);

    if name in tips:
        tips[name]['output'] = cur_base;
    else:
        internals[name] = {  'name' : name, 
                                'input-seqs' : "NA", 
                                'hal-file' : cur_base.replace(".fa", ".hal"), 
                                'cigar-file' : cur_base.replace(".fa", ".cigar"), 
                                'seq-file' : cur_base };
## Read the internal node labels and output file paths from the file generated by cactus-prepare

####################

tinfo, anc_tree, root = cactuslib.treeParse(anc_tree);
internal_nodes = [ n for n in tinfo if tinfo[n][2] != 'tip' ];
root_name = tinfo[root][3];
## Parse the tree with the internal node labels

####################

for node in internal_nodes:
    name = tinfo[node][3];
    # The cactus node label

    internals[name]['round'] = cactuslib.maxDistToTip(node, tinfo);
## One loop through the tree to get the round each node is in based on its maximum
## distance to a tip

####################

for node in internal_nodes:
    name = tinfo[node][3];
    # Get the name of the current node

    expected_seq_inputs = [];
    # We will construct a list of all sequences required as input for this node -- all those
    # from nodes in the previous round

    if internals[name]['round'] == 0:
    # If the node is in round 0, both of its descendants are tip nodes and the inputs are those
    # from the mask rule for those sequences

        cur_desc = cactuslib.getDesc(node, tinfo);
        # Get descendant nodes for the current node

        for desc in cur_desc:
            #expected_seq_inputs.append([ desc_key for desc_key in tips if tips[desc_key]['name'] == desc ][0]);
            expected_seq_inputs.append(tips[desc]['output']);
        # Get the output of the mask rule for both descendants as the inputs for this node

    else:
    # If the node is not in round 0, we need to gather all output sequences from the previous round
    # as input to this node

        for node_check in internal_nodes:
            name_check = tinfo[node_check][3];
            if internals[name]['round']-1 != internals[name_check]['round']:
                continue;
            expected_seq_inputs.append(internals[name_check]['seq-file']);
        # Go through the internal nodes again and skip any that aren't in the previous round

    internals[name]['input-seqs'] = expected_seq_inputs;
     # Add the expected input seqs to the main internals dict for this node       
## Another loop through the tree to get the input sequences for each node

if debug:
    for g in tips:
        print(g, tips[g]);
    print("===================================================================================");

    for g in internals:
        print(g, internals[g]);
    print("===================================================================================");
    for name in tips:
        print(name, tips[name]['output']);
    sys.exit("debug ok");
## Some output for debugging

#############################################################################
# Final rule - rule that depends on final expected output file and initiates all
# the other rules

localrules: all

rule all:
    input:
        expand(os.path.join(OUTPUT_DIR, "{final_tip}"), final_tip=[tips[name]['output'] for name in tips]),
        # The masked input files from rule mask

        expand(os.path.join(OUTPUT_DIR, "{internal_node}.fa"), internal_node=[node for node in internals]),
        # The final FASTA sequences from each internal node after rules blast and align

        os.path.join(OUTPUT_DIR, "hal-append-subtree.log")
        # The log file from the append rule (halAppendSubtree)
## Rule all specifies the final output files expected

# #############################################################################
# # Pipeline rules

rule mask:
    input:
        lambda wildcards: [ tips[name]['input'] for name in tips if tips[name]['output'] == wildcards.final_tip ][0]
    output:
        os.path.join(OUTPUT_DIR, "{final_tip}")
    params:
        path = CACTUS_PATH,
        input_file = INPUT_FILE,
        config_file = os.path.join(OUTPUT_DIR, CONFIG_FILE),
        cactus_file = os.path.join(OUTPUT_DIR, CACTUS_FILE),
        genome_name = lambda wildcards: [ name for name in tips if tips[name]['output'] == wildcards.final_tip ][0],#  tips[wildcards.final_tip]['name'],
        #job_dir = lambda wildcards: os.path.join(TMPDIR, tips[wildcards.final_tip]['name'] + "-mask")
        job_dir = lambda wildcards: os.path.join(TMPDIR, [ name for name in tips if tips[name]['output'] == wildcards.final_tip ][0] + "-mask")
    resources:
        partition = "gpu",
        gpu = 2,
        cpus = 64,
        mem = "100g",
        time = "1:00:00"
    run:
        if os.path.isdir(params.job_dir):
            shell("{params.path} cactus-preprocess {params.job_dir} {params.input_file} {params.cactus_file} --inputNames {params.genome_name} --realTimeLogging --logInfo --retryCount 0 --configFile {params.config_file} --maxCores {resources.cpus} --gpu --restart")
        else:
            shell("{params.path} cactus-preprocess {params.job_dir} {params.input_file} {params.cactus_file} --inputNames {params.genome_name} --realTimeLogging --logInfo --retryCount 0 --configFile {params.config_file} --maxCores {resources.cpus} --gpu")
        # When not requesting all CPU on a node: toil.batchSystems.abstractBatchSystem.InsufficientSystemResources: The job LastzRepeatMaskJob is requesting 64.0 cores, more than the maximum of 32 cores that SingleMachineBatchSystem was configured with, or enforced by --maxCores.Scale is set to 1.0.
## This rule runs cactus-preprocess for every genome (tip in the tree), which does some masking
## Runtimes for turtles range from 8 to 15 minutes with the above resoureces

####################

rule blast:
    input:
        lambda wildcards: [ os.path.join(OUTPUT_DIR, input_file) for input_file in internals[wildcards.internal_node]['input-seqs'] ]
    output:
        os.path.join(OUTPUT_DIR, "{internal_node}.cigar")
    params:
        path = CACTUS_PATH_TMP,
        config_file = os.path.join(OUTPUT_DIR, CONFIG_FILE),
        cactus_file = os.path.join(OUTPUT_DIR, CACTUS_FILE),
        node = lambda wildcards: wildcards.internal_node,
        #job_dir = lambda wildcards: os.path.join(TMPDIR, wildcards.internal_node + "-blast")
        job_dir = lambda wildcards: os.path.join("/tmp", wildcards.internal_node + "-blast")
    resources:
        partition = "gpu",
        gpu = 4,
        cpus = 64,
        mem = "400g",
        time = "24:00:00"
    run:
        if os.path.isdir(params.job_dir):
            shell("{params.path} cactus-blast {params.job_dir} {params.cactus_file} {output} --root {params.node} --realTimeLogging --logInfo --retryCount 0 --configFile {params.config_file} --maxCores {resources.cpus} --gpu --restart")
        else:
            shell("{params.path} cactus-blast {params.job_dir} {params.cactus_file} {output} --root {params.node} --realTimeLogging --logInfo --retryCount 0 --configFile {params.config_file} --maxCores {resources.cpus} --gpu")
## This rule runs cactus-blast for every internal node
## Runtimes for turtles range from 1 to 10 hours with the above resources

####################

rule align:
    input:
        cigar_file = os.path.join(OUTPUT_DIR, "{internal_node}.cigar"),
        #seq_files = lambda wildcards: [ os.path.join(OUTPUT_DIR, input_file) for input_file in internals[wildcards.internal_node]['desc-seqs'] ]
    output:
        os.path.join(OUTPUT_DIR, "{internal_node}.hal")
    params:
        path = CACTUS_PATH_TMP,
        config_file = os.path.join(OUTPUT_DIR, CONFIG_FILE),
        cactus_file = os.path.join(OUTPUT_DIR, CACTUS_FILE),
        node = lambda wildcards: wildcards.internal_node,
        #job_dir = lambda wildcards: os.path.join(TMPDIR, wildcards.internal_node + "-align"),
        job_dir = lambda wildcards: os.path.join("/tmp", wildcards.internal_node + "-align"),
        work_dir = TMPDIR
    resources:
        partition = "bigmem",
        cpus = 64,
        mem = "450g",
        time = "24:00:00"
    run:
        if os.path.isdir(params.job_dir):
            shell("{params.path} cactus-align {params.job_dir} {params.cactus_file} {input.cigar_file} {output} --root {params.node} --realTimeLogging --logInfo --retryCount 0 --configFile {params.config_file} --workDir {params.work_dir} --maxCores {resources.cpus} --defaultDisk 450G --restart")
        else:
            shell("{params.path} cactus-align {params.job_dir} {params.cactus_file} {input.cigar_file} {output} --root {params.node} --realTimeLogging --logInfo --retryCount 0 --configFile {params.config_file} --workDir {params.work_dir} --maxCores {resources.cpus} --defaultDisk 450G ")
## This rule runs cactus-align for every internal node
## Runtimes for turtles range from 4 to 16 hours with the above resources

####################

rule convert:
    input:
        os.path.join(OUTPUT_DIR, "{internal_node}.hal")
        #lambda wildcards: [ os.path.join(output_dir, input_file) for input_file in internals[wildcards.internal_node]['hal-inputs'] ][0]
    output:
        os.path.join(OUTPUT_DIR, "{internal_node}.fa")
    params:
        path = CACTUS_PATH,
        node = lambda wildcards: wildcards.internal_node,
    resources:
        partition = "shared",
        cpus = 8,
        mem = "12g",
        time = "1:00:00"
    shell:
        """
        {params.path} hal2fasta {input} {params.node} --hdf5InMemory > {output}
        """
## This rule runs hal2fasta to convert .hal files for each internal node to .fasta files
## Runtime for turtles is only about 30 seconds per node

####################

rule append:
    input:
        expand(os.path.join(OUTPUT_DIR, "{internal_node}.fa"), internal_node=internals)
    output:
        touch(os.path.join(OUTPUT_DIR, "hal-append-subtree.log"))
    resources:
        partition = "shared",
        cpus = 8,
        mem = "100g",
        time = "12:00:00"
    run:
        with open(os.path.join(OUTPUT_DIR, "hal-append-subtree.log"), "w") as appendfile:
            for node in internals:
                appendfile.write(node + "\n");
                if node == root_name:
                    appendfile.write("Node is root node. Nothing to be done.");
                    appendfile.write("----------" + "\n\n");
                    appendfile.flush();
                    continue;
                # If the node is the root we don't want to append since that is the hal file we
                # are appending to

                cmd = ["singularity", "exec", "--nv", "--cleanenv", "--bind " + TMPDIR + ":/tmp", config["cactus_path"], "halAppendSubtree", os.path.join(OUTPUT_DIR, root_name + ".hal"), os.path.join(OUTPUT_DIR, node + ".hal"), node, node, "--merge", "--hdf5InMemory"];
                appendfile.write("RUNNING COMMAND:\n");
                appendfile.write(" ".join(cmd) + "\n");
                appendfile.flush();
                # Generate the command for the current node

                result = subprocess.run(cmd, capture_output=True, text=True);
                # Rune the command for the current node and capture the output

                appendfile.write("COMMAND STDOUT:\n")
                appendfile.write(result.stdout + "\n");
                appendfile.write("COMMAND STDERR:\n")
                appendfile.write(result.stderr + "\n");
                appendfile.write("\nDONE!\n");
                appendfile.write("----------" + "\n\n");
                appendfile.flush();
                # Print the output of the command to the log file
                # TODO: Maybe check for errors in stderr and exit with non-zero if found? Not sure if that would work...
        ## End node loop
    ## This rule runs halAppendSubtree on every internal node in the tree to combine alignments into a single file.
    ## Because this command writes to the same file for every node, jobs must be run serially, so this command
    ## is run in a run block with pyhton's subprocess.run() function.
    ## Output is captured in the 'hal-append-subtree.log'

#############################################################################