import sys
from collections import defaultdict
ts2gene = {}
gffin = open(sys.argv[1],'r')
for line in gffin:
    if line[0] != '#':
        linelist = line.strip().split('\t')
        if linelist[2] == 'mRNA':
            linelist[8] = linelist[8].replace('geneID=','').replace('ID=','').replace('gene_name=','')
            if len(linelist[8].split(';')) ==3:
                ts,gene,name=linelist[8].split(';')
            else:
                ts,gene,name=linelist[8].split(';')[:-1]
            ts2gene[ts] = gene
overlapdict = defaultdict(list)
fields = ['predchrom','predstart','predend','predstrand',
              'pred_attributes','refchrom','refstart','refend',
              'refstrand','ref_attributes']

overlaps = open(sys.argv[2],'r')
for line in overlaps:
    linedict = dict(zip(fields,line.strip().split('\t')))
    if linedict['predstrand']  == linedict['refstrand']:
        predgene = ts2gene[linedict['pred_attributes'].replace('Parent=','')]
        selfgene = ts2gene[linedict['ref_attributes'].replace('Parent=','')]
        if predgene!=selfgene:
            overlapdict[predgene].append(selfgene)

fout = open('ncbi_self_intergene_cds_overlaps.tsv','w')
fout.write('gene\toverlaps\tnum_overlaps\n')
for gene in overlapdict.keys():
    if len(set(overlapdict[gene])) > 0:
        genes = ';'.join(list(set(overlapdict[gene])))
        fout.write('%s\t%s\t%s\n' % (gene,genes,len(set(overlapdict[gene]))))
    else:
        fout.write('%s\tNone\t0\n' % gene)

fout.close()
