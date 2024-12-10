import sys
fields = ['seqid', 'source', 'type', 'start',
          'end', 'score', 'strand', 'phase', 'attributes']
def ParseAttributes(linedict):
    """
    parser for the attributes field (column 9)
    of a gff3 file
    """
    attribute_list = linedict['attributes'].split(';')
    attribute_dict = {}
    for attribute in attribute_list:
        key,value = attribute.split('=')
        attribute_dict[key] = value
    return attribute_dict


liftoff_in = open(sys.argv[1],'r')
liftoff_out = open('nosegments_{}'.format(sys.argv[1]),'w')
segment_genes = set()
for line in liftoff_in:
    if line[0] == '#':
        liftoff_out.write(line)
    else:
        linelist = line.strip().split('\t')
        linedict = dict(zip(fields,linelist))
        attribute_dict = ParseAttributes(linedict)

        if '_segment' in linedict['type']:
            segment_genes.add(linelist[8].split(';')[1].replace('Parent=',''))
        elif linelist[2] == 'gene':
            if 'segment' not in attribute_dict['gene_biotype']:     
                liftoff_out.write(line)
            else:
                segment_genes.add(attribute_dict['ID'])
        else:
            if attribute_dict['Parent'].replace('id','gene') not in segment_genes:
                liftoff_out.write(line)

liftoff_out.close()                
    
