import sys

def ParseMrnaAttributes(attributes):
    attribute_list = attributes.split(';')
    attribute_dict = {}
    for attribute in attribute_list:
        key,value =  attribute.split('=')
        attribute_dict[key] = value
    return attribute_dict

gffin = open(sys.argv[1],'r')
genebed = open(sys.argv[2],'w')
fields = ['seqid', 'source', 'type',
          'start', 'end', 'score', 
          'strand', 'phase', 'attributes']

genelist = []
genes = dict()
for line in gffin:
    if line[0] != '#':
        linedict = dict(zip(fields,line.strip().split('\t')))
        if linedict['type'] == 'mRNA':
            attribute_dict = ParseMrnaAttributes(linedict['attributes'])
            if attribute_dict['geneID'] in genes:
                if genes[attribute_dict['geneID']]['start'] > int(linedict['start']):
                    genes[attribute_dict['geneID']]['start'] = int(linedict['start'])
                if genes[attribute_dict['geneID']]['end'] < int(linedict['end']):
                    genes[attribute_dict['geneID']]['end'] = int(linedict['end'])
            else:
                genes[attribute_dict['geneID']] = {}
                genes[attribute_dict['geneID']]['start'] = int(linedict['start'])
                genes[attribute_dict['geneID']]['end'] = int(linedict['end'])
                genes[attribute_dict['geneID']]['chrom'] = linedict['seqid']
                genelist.append(attribute_dict['geneID'])
for gene in genelist:
    genebed.write('%s\t%s\t%s\t%s\n' % (genes[gene]['chrom'],genes[gene]['start']-1,genes[gene]['end'],gene))

genebed.close()
