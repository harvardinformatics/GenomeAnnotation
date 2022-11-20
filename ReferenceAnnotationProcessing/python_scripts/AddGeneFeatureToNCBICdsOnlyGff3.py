import sys


def CreateGffAttributeDict(linelist):
    attribute_list = linelist[8].split(';')
    attribute_dict = {}
    for keyvalpair in attribute_list:
        key,value =  keyvalpair.split('=')
        attribute_dict[key] = value
    return attribute_dict


fullreffgff3 = open(sys.argv[1], 'r') # /n/holylfs05/LABS/informatics/Lab/genome_annotation_project/dipterans/genomes/dmel/GCF_000001215.4_Release_6_plus_ISO1_MT_genomic.gff

genedict = {}
seen_genes = []

for line in fullreffgff3:
    if line[0] != '#':
        linelist = line.strip().split('\t')
        if linelist[2] == 'gene':
            attribute_dict = CreateGffAttributeDict(linelist)                
            genedict[attribute_dict['ID']] = line

cdsgff = open(sys.argv[2],'r')
gffout = open('wgenefeatures_%s' % sys.argv[2],'w')
for line in cdsgff:
    if line[0] == '#':
        gffout.write(line)
    elif line[0] != '#':
        linelist = line.strip().split('\t')
        if linelist[2] == 'mRNA':
            attribute_dict = CreateGffAttributeDict(linelist)
            if attribute_dict['geneID'] in seen_genes:
                pass
            elif attribute_dict['geneID'] in genedict:
                gffout.write('%s' % genedict[attribute_dict['geneID']])
                genedict.pop(attribute_dict['geneID'])
                seen_genes.append(attribute_dict['geneID'])
                new_mrnaline = line.replace('geneID','Parent')
                gffout.write(new_mrnaline)
            else:
               raise ValueError('gene id missing from genedict')
        else:
            gffout.write(line)    
