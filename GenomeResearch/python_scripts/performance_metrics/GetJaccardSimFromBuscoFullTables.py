from sklearn import metrics
import numpy as np
import sys
from collections import defaultdict
from glob import glob
files=glob('*buscos.tsv')
species = sys.argv[1] 
factor_dict = {'braker-protein':1,'braker-rnaseq':2,'cgp-denovo':3,'cgp-protein':4,'cgp-rnaseq':5,'scallop-hisat':6,'scallop-star':7,'stringtie-hisat':8,'stringtie-star':9}   
def parse_busco_full_table(file):
    fopen = open(file,'r')
    buscos_dict = defaultdict(int) 
    for line in fopen:
        if line[0] !="#":
            linelist = line.strip().split('\t')
            if linelist[1] =="Missing":
                buscos_dict[linelist[0]] = 0
            else:
                buscos_dict[linelist[0]] = 1
    return buscos_dict

fout = open('buscos_%s_jaccardindex.tsv' % species,'w')
fout.write('method1\tmethod2\tjaccard_index\tx\ty\n')
method_pairs = []
for i in range(len(files)):
    for j in range(len(files)):
        method_set =  set([files[i],files[j]])
        #print(files[i],files[j],method_set)
        file1suffix = files[i].replace('_buscos.tsv','').replace('%s_' % species,'').replace('_','-')
        file2suffix = files[j].replace('_buscos.tsv','').replace('%s_' % species,'').replace('_','-')
        if method_set not in method_pairs:
            method_pairs.append(method_set)
            if files[i] != files[j] :
                buscos1 = parse_busco_full_table(files[i])
                buscos2 = parse_busco_full_table(files[i-j])
                buscos = set(buscos1.keys()).union(set(buscos2.keys()))
                buscos1_binary = []
                buscos2_binary = []
                for busco in buscos:
                    buscos1_binary.append(buscos1[busco])
                    buscos2_binary.append(buscos2[busco])

                buscos1_binary = np.array(buscos1_binary)
                buscos2_binary = np.array(buscos2_binary)
                fout.write('%s\t%s\t%s\t%s\t%s\n' % (file1suffix,file2suffix,metrics.jaccard_score(buscos1_binary,buscos2_binary),factor_dict[file1suffix],factor_dict[file2suffix]))
            elif files[i] == files[j]:
                fout.write('%s\t%s\tNA\t%s\t%s\n' % (file1suffix,file2suffix,factor_dict[file1suffix],factor_dict[file2suffix]))


fout.close()
