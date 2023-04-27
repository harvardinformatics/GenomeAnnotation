import argparse
from collections import defaultdict,OrderedDict
from subprocess import Popen,PIPE

fields = ['seqid', 'source', 'type', 'start',
          'end', 'score', 'strand', 'phase', 'attributes']


def ParseAttributes(linedict):
    attribute_list = linedict['attributes'].split(';')
    attribute_dict = {}
    for attribute in attribute_list:
        key,value = attribute.split('=')
        attribute_dict[key] = value
    return attribute_dict
"""
def BuildGeneIntervalDict(gene_interval_dict,mrna_linedict,mrna_attribute_dict):
    if 'geneID' in mrna_attribute_dict:
        geneid = mrna_attribute_dict['geneID']
    elif 'Parent' in mrna_attribute_dict:
        geneid = mrna_attribute_dict['Parent']
    else:
        raise ValueError("gene id key not in attribute_dict")
    
    start = int(mrna_linedict['start'])
    end = int(mrna_linedict['end'])
    if geneid in gene_interval_dict:
        gene_interval_dict[geneid]['start'] = min(gene_interval_dict[geneid]['start'],start)
        gene_interval_dict[geneid]['end'] = max(gene_interval_dict[geneid]['end'],end) 
    else:
        gene_interval_dict[geneid] = {'start': start, 'end': end}
    
    return gene_interval_dict   
"""


def BuildTranscriptCDSIntervalDict(cdsbed):
    tscript_cds_intervals = {}
    fopen = open(cdsbed,'r')
    for line in fopen:
        seqid,start,end,strand,tsid=line.strip().split('\t')
        if ';' in tsid: # this deals with transdecoder and other tools where gff3 has a cds id and and parent in attributes
            tsid = tsid.split(';')[1]
        if tsid in tscript_cds_intervals:
            tscript_cds_intervals[tsid]['start'] = min(tscript_cds_intervals[tsid]['start'],int(start)+1)
            tscript_cds_intervals[tsid]['end'] = max(tscript_cds_intervals[tsid]['end'],int(end))
        else:
            tscript_cds_intervals[tsid] = {}
            tscript_cds_intervals[tsid]['start'] = int(start)+1
            tscript_cds_intervals[tsid]['end'] = int(end)       
    
    return tscript_cds_intervals
        
    


if __name__=="__main__": 
    parser = argparse.ArgumentParser(description="remove UTR intervals from all features")
    parser.add_argument('-gff3','--gff3-file',dest='gff3',type=str,help='gff3 file')
    opts = parser.parse_args()

    # generate cds.bed file #
    awk_cds_cmd = "grep -v \"#\" %s | awk -F\"\\t\" '$3==\"CDS\"{print $1\"\\t\"$4-1\"\\t\"$5\"\\t\"$7\"\\t\"$9}' | sed 's/Parent=//g' > cds_%s.bed" % (opts.gff3,opts.gff3)   
    print(awk_cds_cmd)
    cds_bed_create = Popen(awk_cds_cmd,shell=True,stderr=PIPE,stdout=PIPE)
    cds_out,cds_err = cds_bed_create.communicate()
    if cds_bed_create.returncode == 0:
        pass
    else:
        raise Exception(cds_err)
    

    # build transcript utr-stripped interval bed #
    tscript_intervals = BuildTranscriptCDSIntervalDict("cds_%s.bed" % opts.gff3)
    #print(tscript_intervals)
    
    gene_interval_dict = {}
    ts2gene = {}  
    with open(opts.gff3,'r') as firstpass:
        for line in firstpass:
            if line[0] != '#':
                linedict = dict(zip(fields,line.strip().split('\t')))
                if linedict['type'] in ['mRNA','transcript']:
                    attribute_dict = ParseAttributes(linedict)
                    #gene_interval_dict = BuildGeneIntervalDict(gene_interval_dict,linedict,attribute_dict)
                    if 'geneID' in attribute_dict:
                        ts2gene[attribute_dict['ID']]  = attribute_dict['geneID']
                    elif 'Parent' in attribute_dict:
                        ts2gene[attribute_dict['ID']]  = attribute_dict['Parent']
    firstpass.close()

    for ts in ts2gene:
        gene = ts2gene[ts]
        if gene not in gene_interval_dict:
            gene_interval_dict[gene] = {'start': tscript_intervals[ts]['start'],'end': tscript_intervals[ts]['end']}
        else:
            gene_interval_dict[gene]['start'] = min(tscript_intervals[ts]['start'],gene_interval_dict[gene]['start'])
            gene_interval_dict[gene]['end'] = max(tscript_intervals[ts]['end'],gene_interval_dict[gene]['end'])    

# 2nd pass #
    genes_2ndpass = set()
    fout = open('utr-stripped_%s' % opts.gff3,'w')
    with open(opts.gff3,'r') as secondpass:
        for line in secondpass:
            if line[0] == '#':
                fout.write(line)
            else:
                linedict = OrderedDict(zip(fields,line.strip().split('\t')))
                attribute_dict = ParseAttributes(linedict)
                if linedict['type'] == 'gene':
                    linedict['start'] = gene_interval_dict[attribute_dict['ID']]['start']
                    linedict['end'] = gene_interval_dict[attribute_dict['ID']]['end']
                    linelist = []
                    for key in linedict:
                        linelist.append(str(linedict[key]))
                    fout.write('%s\n' % ('\t'.join(linelist)))
                    genes_2ndpass.add(attribute_dict['ID'])
                elif linedict['type'] in ['mRNA','transcript']:
                    linedict['start'] = tscript_intervals[attribute_dict['ID']]['start']
                    linedict['end'] = tscript_intervals[attribute_dict['ID']]['end']
                    linelist = []
                    for key in linedict:
                        linelist.append(str(linedict[key]))
                    #fout.write('%s\n' % ('\t'.join(linelist)))
                    if 'geneID' in attribute_dict:
                        geneid = attribute_dict['geneID']
                        
                    else:
                        geneid = attribute_dict['Parent']
                    if geneid not in genes_2ndpass:
                        genedict = linedict.copy()
                        genedict['type'] = 'gene'
                        genedict['start'] =  gene_interval_dict[geneid]['start']
                        genedict['end'] =  gene_interval_dict[geneid]['end']
                        genedict['attributes'] = 'ID=%s' % geneid
                        gene_linelist = []
                        for key in genedict:
                            gene_linelist.append(str(genedict[key]))
                        fout.write('%s\n' % ('\t'.join(gene_linelist)))
                        genes_2ndpass.add(geneid)
                    fout.write('%s\n' % ('\t'.join(linelist).replace('geneID=','Parent=')))
                elif linedict['type'] == 'exon':
                    pass
                elif linedict['type'] == 'CDS':
                    cds_linelist = []
                    exon_linelist = []
                    for key in linedict:
                        cds_linelist.append(str(linedict[key]))
                    linedict['type'] = 'exon'
                    for key in linedict:
                        exon_linelist.append(str(linedict[key]))
                    fout.write('%s\n' % ('\t'.join(exon_linelist)))
                    fout.write('%s\n' % ('\t'.join(cds_linelist)))
                else:
                    pass
                    #print('WARNING: other line type: %s' % linedict['type'])
    fout.close()    
