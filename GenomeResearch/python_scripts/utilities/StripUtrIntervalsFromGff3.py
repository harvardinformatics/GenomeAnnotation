import argparse
from collections import defaultdict,OrderedDict
from subprocess import Popen,PIPE

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
    
def BuildTranscriptCDSIntervalDict(cdsbed):
    tscript_cds_intervals = {}
    fopen = open(cdsbed,'r')
    for line in fopen:
        seqid,start,end,strand,tsid=line.strip().split('\t')
        if ';' in tsid: # this deals with transdecoder and other tools where gff3 has a cds id and and parent in attributes
            tsid = tsid.split(';')[1]
            #if tsid[:5] =='gene-': # this deals with mtDNA genes for which the geneid is the same as ts id for CDS features
            #    tsid = tsid.replace('gene','rna')
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
    parser.add_argument('-liftoff','--liftoff-gff3',dest='liftoff',action='store_true',help='indicates sources is liftoff annotation')
    opts = parser.parse_args()

    if opts.liftoff == True:
        ts_types = ['mRNA']
    else:
        ts_types = ['mRNA','transcript']

    # generate cds.bed file #
    awk_cds_cmd = "awk '!/^#/' %s | awk -F\"\\t\" '$3==\"CDS\"{print $1\"\\t\"$4-1\"\\t\"$5\"\\t\"$7\"\\t\"$9}' | sed 's/Parent=//g' > cds_%s.bed" % (opts.gff3,opts.gff3)   
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
    cds_genes= {}
    tscript_ids = [] #new
    with open(opts.gff3,'r') as firstpass:
        for line in firstpass:
            if line[0] != '#':
                linedict = dict(zip(fields,line.strip().split('\t')))
                attribute_dict = ParseAttributes(linedict)
                if linedict['type'] in ts_types:
                    if 'geneID' in attribute_dict:
                        ts2gene[attribute_dict['ID']]  = attribute_dict['geneID']
                    elif 'Parent' in attribute_dict:
                        ts2gene[attribute_dict['ID']]  = attribute_dict['Parent']
                    
                elif linedict['type'] == 'CDS':
                    if attribute_dict['Parent'] not in cds_genes:
                        cds_genes[attribute_dict['Parent']] = {'start' : linedict['start'], 'end': linedict['end']}
    
    firstpass.close()

    for ts in ts2gene:
        gene = ts2gene[ts]
        if gene not in gene_interval_dict:
            if ts in tscript_intervals:
                gene_interval_dict[gene] = {'start': tscript_intervals[ts]['start'],'end': tscript_intervals[ts]['end']}
            else:
                pass
                #print("transcript {} does not appear to contain CDS features".format(ts))
        elif ts in tscript_intervals: # this conditional passes over cases where a ts is not in cds interval bed because it doesn't have a cds feature, i.e. liftoff
            gene_interval_dict[gene]['start'] = min(tscript_intervals[ts]['start'],gene_interval_dict[gene]['start'])
            gene_interval_dict[gene]['end'] = max(tscript_intervals[ts]['end'],gene_interval_dict[gene]['end'])
        else:
            pass
            #print("tscript {} does not appear to contain CDS features".format(ts))
            #if 'gene-ArthCp002' in gene_interval_dict:
            #   print('gene-ArthCp002 is in gene intervals')
    gene_interval_dict.update(cds_genes) # adds in genes that have CDS and gene but no tscript features

# 2nd pass #
    ts2exoncount = defaultdict(int)
    genes_2ndpass = set()
    fout = open('utr-stripped_%s' % opts.gff3,'w')
    with open(opts.gff3,'r') as secondpass:
        for line in secondpass:
            if line[0] == '#':
                fout.write(line)
            else:
                linedict = OrderedDict(zip(fields,line.strip().split('\t')))
                attribute_dict = ParseAttributes(linedict)
                if linedict['type'] == 'gene' and attribute_dict['ID'] in gene_interval_dict:
                    linedict['start'] = gene_interval_dict[attribute_dict['ID']]['start']
                    linedict['end'] = gene_interval_dict[attribute_dict['ID']]['end']
                    linelist = []
                    for key in linedict:
                        linelist.append(str(linedict[key]))
                    fout.write('%s\n' % ('\t'.join(linelist)))
                    genes_2ndpass.add(attribute_dict['ID'])
                elif linedict['type'] in ts_types and attribute_dict['ID'] in tscript_intervals: # makes sure only looking at things with CDS features
                    linedict['start'] = tscript_intervals[attribute_dict['ID']]['start']
                    linedict['end'] = tscript_intervals[attribute_dict['ID']]['end']
                    linelist = []
                    for key in linedict:
                        linelist.append(str(linedict[key]))
                    
                    ### setting of gene id ###
                    if 'geneID' in attribute_dict:
                        geneid = attribute_dict['geneID']
                        
                    else:
                        geneid = attribute_dict['Parent']
                    #########################

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
                    ts2exoncount[attribute_dict['Parent']]+=1
                    cds_linelist = []
                    exon_linelist = []

                    for key in linedict:
                        #if key =='attributes':
                        #    linedict[key] =  linedict[key].replace('Parent=gene','Parent=rna')
                        cds_linelist.append(str(linedict[key]))

                    linedict['type'] = 'exon'
                    
                    for key in linedict:
                        if key == 'attributes':
                            attribute_list = linedict['attributes'].split(';')
                            attribute_list[0] = 'ID=exon-{}-{}'.format(attribute_dict['Parent'].replace('rna-','').replace('gene-',''),ts2exoncount[attribute_dict['Parent']])
                            linedict['attributes'] = ';'.join(attribute_list)
                            
                        exon_linelist.append(str(linedict[key]))
                    fout.write('%s\n' % ('\t'.join(exon_linelist)))
                    fout.write('%s\n' % ('\t'.join(cds_linelist)))
                else:
                    pass
                    #print('WARNING: other line type: %s' % linedict['type'])
    fout.close()

    # third pass to remove duplicate gene entries seen for liftoff
    if opts.liftoff == True:
        genes = set()
        final_open = open('utr-stripped_%s' % opts.gff3,'r')
        final_out = open('rmdupgenes_utr-stripped_%s' % opts.gff3,'w')
        for line in final_open:
            if line[0] == '#':
                final_out.write(line)
            else:
                line_dict = dict(zip(fields,line.strip().split('\t')))
                #print(line_dict)
                if line_dict['type'] == 'gene':
                    gene = '{}_{}_{}_{}'.format(line_dict['attributes'].split(';')[0].replace('ID=',''),line_dict['seqid'],line_dict['start'],line_dict['end'])
                    if gene not in genes:
                        genes.add(gene)
                        final_out.write(line)
                else:
                    final_out.write(line)
        final_out.close()            
