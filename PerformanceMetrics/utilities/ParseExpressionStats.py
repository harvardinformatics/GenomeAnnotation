import sys
from glob import glob
from numpy import median
prefix = sys.argv[1]

gene_tables = glob("*genes.results")
gene_low_fractions = []

tscript_tables = glob("*isoforms.results")
tscript_low_fractions = []

for table in gene_tables:
    feature_count = 0
    low_tpm_count = 0
    data = open(table,'r')
    header=data.readline().strip().split('\t')
    for line in data:
        data_dict = dict(zip(header,line.strip().split('\t')))
        feature_count +=1
        if float(data_dict['TPM']) < 1:
            low_tpm_count+=1
    gene_low_fractions.append(low_tpm_count/float(feature_count))

for table in tscript_tables:
    feature_count = 0
    low_tpm_count = 0
    data = open(table,'r')
    header=data.readline().strip().split('\t')
    for line in data:
        data_dict = dict(zip(header,line.strip().split('\t')))
        feature_count +=1
        if float(data_dict['TPM']) < 1:
            low_tpm_count+=1
    tscript_low_fractions.append(low_tpm_count/float(feature_count))

fout = open('MedianLowTPMFrac_%s.txt' % prefix,'w')
fout.write('gene:\t%s\ntscript:\t%s\n' % (median(gene_low_fractions),median(tscript_low_fractions)))
fout.close()
    
