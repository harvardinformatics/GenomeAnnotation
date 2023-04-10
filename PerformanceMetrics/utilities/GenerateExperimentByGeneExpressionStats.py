import sys
from glob import glob
from numpy import median
from collections import defaultdict

prefix = sys.argv[1]

gene_tables = glob("*genes.results")

tscript_tables = glob("*isoforms.results")

gene_tpm_dict = defaultdict(list)
ts_tpm_dict = defaultdict(list)


for table in gene_tables:
    data = open(table,'r')
    header=data.readline().strip().split('\t')
    for line in data:
        data_dict = dict(zip(header,line.strip().split('\t')))
        gene_tpm_dict[data_dict['gene_id']].append(float(data_dict['TPM']))
    
for table in tscript_tables:
    data = open(table,'r')
    header=data.readline().strip().split('\t')
    for line in data:
        data_dict = dict(zip(header,line.strip().split('\t')))
        ts_tpm_dict[data_dict['transcript_id']].append(float(data_dict['TPM']))



genes_out = open('%s_medianTPMbygene.tsv' % prefix,'w')
genes_out.write('gene_id\t%smedianTPM\n')
for gene in gene_tpm_dict:
    genes_out.write('%s\t%s\n' % (gene,median(gene_tpm_dict[gene])))
genes_out.close()

tscripts_out = open('%s_medianTPMbyisoform.tsv' % prefix,'w')
tscripts_out.write('tscript_id\tmedianTPM\n')
for tscript in ts_tpm_dict:
    tscripts_out.write('%s\t%s\n' % (tscript,median(ts_tpm_dict[tscript])))
tscripts_out.close()
