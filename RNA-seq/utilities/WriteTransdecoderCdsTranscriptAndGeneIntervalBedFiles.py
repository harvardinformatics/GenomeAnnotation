import argparse
from collections import OrderedDict

fields = ["seqid", "source", "type", "start",
          "end", "score", "strand", "phase", "attributes"]

ts_dict = OrderedDict()
ts2gene = {}
gene_dict = OrderedDict()

def ParseTransdecoderAttributes(attributes):
    attribute_dict = {}
    attribute_list = attributes.split(';')
    for attribute in attribute_list:
        key,value = attribute.split('=')
        attribute_dict[key] =  value
    return attribute_dict

if __name__=="__main__": 
    parser = argparse.ArgumentParser(description="Generate CDS transcript and gene interval bed without UTRs")
    parser.add_argument('-tdecgff3','--transdecoder-annotation-gff3',dest='tdecgff3',type=str,help='transdecoder genome-coordinate  gff3')
    parser.add_argument('-o','--output-bed-prefix',dest='bedprefix',type=str,help='prefix for output bed files')
    opts = parser.parse_args()
    
    gffin = open(opts.tdecgff3,'r')
    for line in gffin:
        if line[0] != '#':
            line_dict = dict(zip(fields,line.strip().split('\t')))
            if line_dict['type'] == 'mRNA':
                attribute_dict = ParseTransdecoderAttributes(line_dict['attributes'])
                tsid = '.'.join(attribute_dict['ID'].split('.')[:-1])
                geneid = attribute_dict['Parent']
                ts2gene[tsid] = geneid
            elif line_dict['type'] == 'CDS':
                attribute_dict = ParseTransdecoderAttributes(line_dict['attributes'])
                tsid = '.'.join(attribute_dict['Parent'].split('.')[:-1])
                #try:
                geneid = ts2gene[tsid]
                #except:
                #    tsid = tsid.replace('gene','rna')
                #    geneid = ts2gene[tsid]

                # transcript level #
                if tsid not in ts_dict:
                    ts_dict[tsid] = {'strand': line_dict['strand'],'chr': line_dict['seqid'],'start': int(line_dict['start']), 'end': int(line_dict['end'])}
                else:
                    ts_dict[tsid]['start'] = min(int(line_dict['start']),ts_dict[tsid]['start'])
                    ts_dict[tsid]['end'] = max(int(line_dict['end']),ts_dict[tsid]['end'])
                
                # gene level #
                if geneid not in gene_dict:
                    gene_dict[geneid] = {'strand': line_dict['strand'],'chr': line_dict['seqid'],'start': int(line_dict['start']), 'end': int(line_dict['end'])} 
                else:
                    gene_dict[geneid]['start'] = min(int(line_dict['start']),gene_dict[geneid]['start'])
                    gene_dict[geneid]['end'] = max(int(line_dict['end']),gene_dict[geneid]['end']) 
    
    tsout = open('%s_transdecoder_CDS_transcript_interval.bed' % opts.bedprefix,'w')
    geneout = open('%s_transdecoder_CDS_gene_interval.bed' % opts.bedprefix,'w') 

    for transcript in ts_dict:
        tsout.write('%s\t%s\t%s\t%s\t.\t%s\n' % (ts_dict[transcript]['chr'],ts_dict[transcript]['start']-1,ts_dict[transcript]['end'],transcript,ts_dict[transcript]['strand']))
    for gene in gene_dict:
        geneout.write('%s\t%s\t%s\t%s\t.\t%s\n' % (gene_dict[gene]['chr'],gene_dict[gene]['start']-1,gene_dict[gene]['end'],gene,gene_dict[gene]['strand']))

    tsout.close()
    geneout.close()                         
