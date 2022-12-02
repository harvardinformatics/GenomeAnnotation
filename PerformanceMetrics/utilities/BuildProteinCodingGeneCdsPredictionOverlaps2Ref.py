import argparse
from collections import defaultdict
from numpy import mean,median

def CreateGffAttributeDict(linelist):
    attribute_list = linelist[8].split(';')
    attribute_dict = {}
    for keyvalpair in attribute_list:
        key,value =  keyvalpair.split('=')
        attribute_dict[key] = value
    return attribute_dict

def ExtractPredictorGeneID(linedict,method):
    if method == 'stringtie':
        predgene = '.'.join(linedict['pred_attributes'].replace('ID=','').replace('Parent=','').split(';')[1].split('.')[0:2])
    elif method == 'scallop':
        predgene = linedict['pred_attributes'].split(';')[1].replace('Parent=','').split('.')[0]
    return predgene



if __name__=="__main__": 
    parser = argparse.ArgumentParser(description="Calculate frequency of putative CDS fusions by looking for one-to-many overlaps of predicted to reference CDS")
    parser.add_argument('-refgff3','--reference-annotation-gff3',dest='refgff3',type=str,help='reference gff3')
    parser.add_argument('-overlaps','--overlap-bed-file',dest='overlapbed',type=str,help='output of intersectBed -loj -a prediction -b ncbi')
    parser.add_argument('-method','--gene-predction-method',dest='method',type=str,help='bioinformatics tool for predicting genes')
    parser.add_argument('-o','--overlap-summary-outfile',dest='summary',type=str,help='name of output overlap summary file')
    opts = parser.parse_args()



    refannot = open(opts.refgff3,'r')
    ref_mrna2gene = {}
    for line in refannot:
        if line[0]!= '#':
            linelist = line.strip().split('\t')
            if linelist[2] =='mRNA':
                attribute_dict = CreateGffAttributeDict(linelist)
                ref_mrna2gene[attribute_dict['ID']] = attribute_dict['geneID']

    intersectbed = open(opts.overlapbed,'r')
    overlapdict = defaultdict(list)
    fields = ['refchrom','refstart','refend','refstrand',
              'ref_attributes','predchrom','predstart','predend',
              'predstrand','pred_attributes']

    for line in intersectbed:
        linelist = line.strip().split('\t') 
        linedict = dict(zip(fields,linelist))
        refgene = ref_mrna2gene[linelist[4].replace('Parent=','')]
        
        if linelist[-1] == '.':
            overlapdict[refgene].append('None')
        elif linedict['predstrand'] == linedict['refstrand']:
            predgene = ExtractPredictorGeneID(linedict,opts.method)
            overlapdict[refgene].append('%s' % predgene)  
        elif linedict['predstrand'] != linedict['refstrand']:
            predgene = ExtractPredictorGeneID(linedict,opts.method)
            overlapdict[refgene].append('%s-oppstrand' % predgene) 
           
    stats = open('overlapp2refstats.txt','w')
    overlap_count_list = []
    opposite_strand_overlap_counter = 0
    fout = open(opts.summary,'w')
    fout.write('refgene\tpredgenes\tnumoverlaps\n')
    for refgene in overlapdict:
        overlapset = set(overlapdict[refgene])
        if len(overlapset) == 1 and overlapset == set(['None']): 
            fout.write('%s\tNone\t0\n' % refgene)
            overlap_count_list.append(0)
        else:
            if 'None' in overlapset:
                overlapset.remove('None')
            
            opposite_strands = 0
            overlaplist = list(overlapset)
            for gene in overlaplist:
                if 'oppstrand' in gene:
                    overlaplist.remove(gene)
                    opposite_strands+=1
            overlapset = set(overlaplist)
            if opposite_strands > 0 and len(overlapset) == 0:
                opposite_strand_overlap_counter+=1
                fout.write('%s\tOppositeStrand\t0\n' % refgene)   
            else:
                fout.write('%s\t%s\t%s\n' % (refgene,';'.join(list(overlapset)),len(overlapset)))
            overlap_count_list.append(len(overlapset))
 
    print('length overlap count list; %s' %len(overlap_count_list))
    numbermultipred2ref = len([i for i in overlap_count_list if i >1])
    numberone2one = len([i for i in overlap_count_list if i ==1])
    numberNoOverlaps = len([i for i in overlap_count_list if i ==0])

    stats.write('number of reference genes: %s\n' % len(overlap_count_list))
    stats.write('number of ref genes with one pred overlap: %s\n' % numberone2one)
    stats.write('number of ref genes with multiple pred overlaps: %s\n' % numbermultipred2ref)
    stats.write('number of ref genes missing in pred annotation: %s\n' % numberNoOverlaps)
    stats.write('mean overlapping predicted genes: %s\n' % mean(overlap_count_list))
    stats.write('median overlapping predicted genes: %s\n' % median(overlap_count_list))
    stats.write('number opposite strand overlaps: %s\n' % opposite_strand_overlap_counter) 
    stats.close()
    fout.close()
