import argparse
from collections import defaultdict

def ParseGtf(gtffile,gtf_gene_dict):
    fopen = open(gtffile,'r')
    fields =  ['seqname', 'source', 'type', 'start',
              'end','score','strand','frame', 'attribute']
    gtf_dict = {}
    for line in fopen:
        if line[0] != '#':
            line = line.replace('; ',';')
            line_dict =  dict(zip(fields,line.strip()[:-1].split('\t')))
            attribute_dict = {}
            
            for entry in line_dict['attribute'].replace('"','').split(';'):
                key,value = entry.split()
                attribute_dict[key] = value
            
            if line_dict['type'] == 'transcript':
                if attribute_dict['gene_id'] in gtf_gene_dict:
                    gtf_gene_dict[attribute_dict['gene_id']]['start'] = min(int(line_dict['start']),gtf_gene_dict[attribute_dict['gene_id']]['start'])
                    gtf_gene_dict[attribute_dict['gene_id']]['end'] = max(int(line_dict['end']),gtf_gene_dict[attribute_dict['gene_id']]['end'])
                
                else:
                  
                    gtf_gene_dict[attribute_dict['gene_id']] = {'start':'','end':'','strand':'','seqname': line_dict['seqname'],'source': line_dict['source']}
                    gtf_gene_dict[attribute_dict['gene_id']]['start'] = int(line_dict['start'])
                    gtf_gene_dict[attribute_dict['gene_id']]['end'] = int(line_dict['end']) 
                    gtf_gene_dict[attribute_dict['gene_id']]['strand'] = line_dict['strand']
                    gtf_dict[attribute_dict['gene_id']] = defaultdict(list)
                
                gtf_dict[attribute_dict['gene_id']][attribute_dict['transcript_id']].append(line) 
            
            elif line_dict['type'] == 'exon':
                gtf_dict[attribute_dict['gene_id']][attribute_dict['transcript_id']].append(line)
        
            else:
                raise ValueError('gtf feature type invalid')
    
    return gtf_dict
             
def ParseTransdecoderGff3(gff3file):
    fields =  ['seqid', 'source', 'type', 'start',
              'end','score','strand','phase', 'attributes']
    ts_to_gene_dict = {}
    gff3_dict = {}
    gffopen = open(gff3file)
    for line in gffopen:
        if line[0] != '#' and 'ID' in line:
            line_dict =  dict(zip(fields,line.strip().split('\t')))
            attribute_dict = {}
            attribute_keys = []
            for entry in line_dict['attributes'].split(';'):
                key,value = entry.split('=')
                attribute_dict[key] = value
                attribute_keys.append(key)
            
            newlinelist = []
            for field in fields[:-1]:
                newlinelist.append(line_dict[field])
          
            if 'Name' in attribute_dict:
               del attribute_dict['Name']
               attribute_keys.remove('Name')   
            if line_dict['type'] == 'gene':
                new_attributes = []
                for key in attribute_keys:
                    new_attributes.append('%s=%s' % (key,attribute_dict[key]))
                    newlinelist.append(';'.join(new_attributes))
                gff3_dict[attribute_dict['ID']] = {'strand': line_dict['strand'],'geneid': attribute_dict['ID'],'geneline': '%s\n' % '\t'.join(newlinelist),'transcripts' : {}}
        
            elif line_dict['type'] == 'mRNA':
                attribute_dict['ID'] = attribute_dict['ID'].split('.p')[0]
                ts_to_gene_dict[attribute_dict['ID']] = attribute_dict['Parent']
                
                new_attributes = []
                for key in attribute_keys:
                    new_attributes.append('%s=%s' % (key,attribute_dict[key]))
                newlinelist.append(';'.join(new_attributes))
                gff3_dict[attribute_dict['Parent']]['transcripts'][attribute_dict['ID']] = []
                gff3_dict[attribute_dict['Parent']]['transcripts'][attribute_dict['ID']].append('%s\n' % '\t'.join(newlinelist))

            elif line_dict['type'] in ['CDS','exon','five_prime_UTR','three_prime_utr']: 
                attribute_dict['Parent'] = attribute_dict['Parent'].split('.p')[0]
                
                new_attributes = []
                for key in attribute_keys:
                    new_attributes.append('%s=%s' % (key,attribute_dict[key]))
                newlinelist.append(';'.join(new_attributes))
                tsid =  attribute_dict['ID'].replace('cds.','').split('.p')[0]
                gff3_dict[ts_to_gene_dict[attribute_dict['Parent']]]['transcripts'][tsid].append('%s\n' %  '\t'.join(newlinelist))

    return gff3_dict

def ConvertGtfLinetoGff3(line):
    linelist = line.strip()[:-1].split('\t')
    fields =  ['seqname', 'source', 'type', 'start',
              'end','score','strand','frame', 'attribute']
    line_dict = dict(zip(fields,linelist))
    if line_dict['type'] == 'transcript':
        line_dict['type'] = 'mRNA'
    attribute_dict = {}
    for entry in line_dict['attribute'].replace('"','').split(';'):
        key,value = entry.split()
        attribute_dict[key] = value
    newlist = []
    for field in fields[:-1]:
        newlist.append(line_dict[field])
    
    if line_dict['type'] == 'mRNA':
        if 'ref_gene_id' in line:
            newline = '%s\tID=%s;Parent=%s;RefGeneId=%s\n' % ('\t'.join(newlist),attribute_dict['transcript_id'],attribute_dict['gene_id'],attribute_dict['ref_gene_id'])
        else:
            newline = '%s\tID=%s;Parent=%s\n' % ('\t'.join(newlist),attribute_dict['transcript_id'],attribute_dict['gene_id'])
    elif line_dict['type'] == 'exon':
        newline = '%s\tID=%s.exon%s;Parent=%s\n' % ('\t'.join(newlist),attribute_dict['transcript_id'],attribute_dict['exon_number'],attribute_dict['transcript_id'])         
    return newline




if __name__=="__main__": 
    parser = argparse.ArgumentParser(description='merge transdecoder CDS predictions into original rna-seq assembly')
    parser.add_argument('-tdecgff','--transdecoder-gff3',dest='tdecgff',help='transdecoder CDS integrated rna-seq transcript assembly (from scallop or stringtie)')
    parser.add_argument('-gtf','--assembly-gtf',dest='gtf',type=str,help='rna-seq transcript assembly gtf, from scallop or stringtie')
    parser.add_argument('-gff3out','--merged-gff3',dest='merged',type=str,help='ncRNAs integrated into transdecoder gff3 output')
    opts = parser.parse_args()   
    
    # set up gtf gene dict to update outer coordinates
    gtf_gene_dict = {}
    assembly_gtf_dict = ParseGtf(opts.gtf,gtf_gene_dict)    
    tdec_dict = ParseTransdecoderGff3(opts.tdecgff)
    
    ncrna = open('MissingOrNoncodingGeneIds.txt','w') 
    gff3out = open('%s' % opts.merged,'w')
    for gene in assembly_gtf_dict:
        if gene not in tdec_dict:
            ncrna.write('%s\n' % gene)
            geneline = '%s\t%s\tgene\t%s\t%s\t.\t%s\t.\tID=%s\n' % (gtf_gene_dict[gene]['seqname'],gtf_gene_dict[gene]['source'],gtf_gene_dict[gene]['start'],gtf_gene_dict[gene]['end'],gtf_gene_dict[gene]['strand'],gene)
            gff3out.write(geneline)
            for transcript in assembly_gtf_dict[gene]:
                for line in assembly_gtf_dict[gene][transcript]:
                    newline = ConvertGtfLinetoGff3(line)
                    gff3out.write(newline)
 
       # next write from tdec gff3 dict
        else:
            gff3out.write(tdec_dict[gene]['geneline'])
            gtf_tscript_list =  assembly_gtf_dict[gene].keys()
            for tscript in gtf_tscript_list:
                if tscript not in tdec_dict[gene]['transcripts']:
                    for line in assembly_gtf_dict[gene][tscript]:
                        newline = ConvertGtfLinetoGff3(line)
                        gff3out.write(newline)
                else:
                    gff3out.write(''.join(tdec_dict[gene]['transcripts'][tscript]))

ncrna.close()
gff3out.close()         
