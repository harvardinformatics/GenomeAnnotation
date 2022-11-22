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
    fields = ['predchrom','predstart','predend','predstrand',
              'pred_attributes','refchrom','refstart','refend',
              'refstrand','ref_attributes']

    for line in intersectbed:
        linelist = line.strip().split('\t') 
        linedict = dict(zip(fields,linelist))
        predgene = ExtractPredictorGeneID(linedict,opts.method)
        
        if linelist[-1] == '.':
            overlapdict[predgene].append('None')
        else:
            if linedict['predstrand'] == linedict['refstrand']:
                refgene = ref_mrna2gene[linelist[-1].replace('Parent=','')]
                overlapdict[predgene].append(refgene)
    
    stats = open('overlapstats.txt','w')
    overlap_count_list = []
    fout = open(opts.summary,'w')
    fout.write('predgene\trefgenes\tnumfusions\n')
    for predgene in overlapdict:
        overlapset = set(overlapdict[predgene])
        if len(overlapset) == 1 and overlapset == set(['None']): 
            fout.write('%s\tNone\t0\n' % predgene)
            overlap_count_list.append(0)
        else:
            if 'None' in overlapset:
                overlapset.remove('None')
            overlap_count_list.append(len(overlapset))    
            fout.write('%s\t%s\t%s\n' % (predgene,';'.join(list(overlapset)),len(overlapset)))
    
    numberfusions = len([i for i in overlap_count_list if i >1])

    stats.write('number of predicted genes: %s\n' % len(overlap_count_list))
    stats.write('number of putative fusions: %s\n' % numberfusions)
    stats.write('mean overlapping reference genes: %s\n' % mean(overlap_count_list))
    stats.write('median overlapping reference genes: %s\n' % median(overlap_count_list))
    
    stats.close()
    fout.close()
