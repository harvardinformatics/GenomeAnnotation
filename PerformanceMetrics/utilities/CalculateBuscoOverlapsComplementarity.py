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

### Create RNAseq vs Protein recovery table ###
protein_vs_rna_table = open('%s_proteinonly_vs_rnaseq_buscorecovery.tsv' % sys.argv[1],'w')
protein_vs_rna_table.write('species\tgroup\tdatatype\tbusco_score\n')
#by_data_type = {'protein':set(), 'rnaseq': set(), 'toga': set()}

by_data_type = {'protein':set(), 'rnaseq-assembler': set(), 'rnaseq-abinit': set(), 'toga': set()}

for key in busco_dict:
    if key in [0,2]:
        by_data_type['protein'] = by_data_type['protein'].union(busco_dict[key])
    elif key in [1,3]:
        by_data_type['rnaseq-abinit'] = by_data_type['rnaseq-abinit'].union(busco_dict[key])
    elif key in [4,5,6,7]:
        by_data_type['rnaseq-assembler'] = by_data_type['rnaseq-assembler'].union(busco_dict[key])
    elif key == 8:
        by_data_type['toga'] = by_data_type['toga'].union(busco_dict[key])

for i in ['protein','rnaseq-abinit','rnaseq-assembler','toga']:
    protein_vs_rna_table.write('%s\t%s\t%s\t%s\n' % (sys.argv[1],sys.argv[2],i,len(by_data_type[i])/len(buscos_searched)))

protein_vs_rna_table.close()

## Generate Busco id by data type table ##
buscoid_by_type_table = open('%s_buscoid_by_type.tsv' % sys.argv[1],'w')
buscoid_by_type_table.write('buscoid\tprotein\trnaseq_abinit\t\trnaseq_assembler\ttoga\n')

print(len(buscos_searched))
for id in buscos_searched:
    present = {'protein' : 'missing', 'rnaseq-abinit' : 'missing' ,'rnaseq-assembler': 'missing', 'toga': 'missing'}
    if id in by_data_type['protein']:
        present['protein'] = 'present'
    if id in by_data_type['rnaseq-abinit']:
        present['rnaseq-abinit'] = 'present'
    if id in by_data_type['rnaseq-assembler']:
        present['rnaseq-assembler'] = 'present'    
    if id in by_data_type['toga']:
        present['toga'] = 'present'
    buscoid_by_type_table.write('%s\t%s\t%s\t%s\t%s\n' % (id,present['protein'],present['rnaseq-abinit'],present['rnaseq-assembler'],present['toga']))

buscoid_by_type_table.close()    

