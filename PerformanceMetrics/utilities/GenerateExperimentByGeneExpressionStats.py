import sys
from glob import glob
from numpy import median
from collections import defaultdict
import argparse

prefix = sys.argv[1]
gff = open(sys.argv[2],'r')
gff_exon_dict = defaultdict(int)
for line in gff:
    if line[0] != "#":
        linelist = line.strip().split('\t')
        if linelist[2] == 'CDS':
            tsid = linelist[-1].split(';')[0].replace('cds.','').replace('"','')
            if '=' in tsid:
                tsid = tsid.split('=')[1]
            else:
                tsid = tsid.replace('transcript_id ','')
            gff_exon_dict[tsid]+=1


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



genes_out = open('%s_TPMstats_by_gene.tsv' % prefix,'w')
genes_out.write('gene_id\tmedianTPM\tmaxTPM\tfracTPMlessThan1\n')
for gene in gene_tpm_dict:
    genes_out.write('%s\t%s\t%s\t%s\n' % (gene,median(gene_tpm_dict[gene]),max(gene_tpm_dict[gene]),sum(i < 1 for i in gene_tpm_dict[gene])/float(len(gene_tpm_dict[gene]))))
genes_out.close()

tscripts_out = open('%s_TPMstats_by_isoform.tsv' % prefix,'w')
tscripts_out.write('tscript_id\tnumber_exons\tmedianTPM\tmaxTPM\tfractTPMlessThan1\n')
for tscript in ts_tpm_dict:
    tscripts_out.write('%s\t%s\t%s\t%s\t%s\n' % (tscript,gff_exon_dict[tscript],median(ts_tpm_dict[tscript]),max(ts_tpm_dict[tscript]),sum(i < 2 for i in ts_tpm_dict[tscript])/float(len(ts_tpm_dict[tscript]))))
tscripts_out.close()
