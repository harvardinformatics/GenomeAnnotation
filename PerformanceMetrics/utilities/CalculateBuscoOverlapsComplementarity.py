#!/usr/bin/env python3 
from glob import glob
import sys
species = sys.argv[1]

def BuildBuscoSet(busco_file):
    fopen = open(busco_file,'r')
    busco_set = set()
    for line in fopen:
        if line[0] != "#":
            linelist = line.strip().split('\t')
            if linelist[1] != 'Missing':
                busco_set.add(linelist[0])
    return busco_set


file_dict = {0 : glob("*braker*protein*tsv"), 1 : glob("*braker*rnaseq*tsv"), 2 : glob("*cgp*protein*tsv"), 
             3 : glob("*cgp*rnaseq*tsv"), 4 : glob("*scallop*hisat*tsv"), 5 : glob("*scallop*star*tsv"), 
             6 : glob("*stringtie*hisat*tsv"), 7: glob("*stringtie*star*tsv"), 8 : glob("*toga*tsv")}


label_dict = {0 : 'braker-protein', 1 : 'braker-rnaseq', 2 : 'cgp-protein', 
              3 : 'cgp-rnaseq', 4 : 'scallop-hisat', 5 : 'scallop-star',
              6 : 'stringtie-hisat', 7 : 'stringtie-star', 8 : 'toga'}


print(file_dict)

### build list of all searched BUSCOS ###
buscos_searched = set()
busco_open = open(file_dict[1][0],'r')
for line in busco_open:
    if line[0] != '#':
        linelist = line.strip().split('\t')
        buscos_searched.add(linelist[0])
#########################################


### Built dict of recovered BUSCO sets per method ###
busco_dict = {}
for key in file_dict:
    busco_dict[key] = BuildBuscoSet(file_dict[key][0])
#####################################################

### Create cumulative recovery table ###
all_recovered = set()

cumulative_out = open('%s_cumulative_busco_recovery.tsv' % sys.argv[1],'w')
cumulative_out.write('method\tfrac_buscos_recovered\n')
for key in busco_dict:
    all_recovered = all_recovered.union(busco_dict[key])
    cumulative_out.write('%s\t%s\n' % (key,len(all_recovered)/len(buscos_searched)))
cumulative_out.close()
#######################################

### Create Recovery-by-method-pair table ###

by_method_pair = open('%s_busco_recovery_by_method_pair.tsv' % sys.argv[1],'w')
by_method_pair.write('species\tmethod1\tmethod2\tbusco_score\n')
for i in range(9):
    for j in range(9):
        if j>=i:
            joint_recovery = len(busco_dict[i].union(busco_dict[j]))/len(buscos_searched)
            by_method_pair.write('%s\t%s\t%s\t%s\n' % (sys.argv[1],label_dict[i],label_dict[j],joint_recovery))

by_method_pair.close()




