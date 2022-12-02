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


def BuildPredictorTranscript2GeneDict(predictorgff3,method):
    ts2gene = {}
    fopen = open(predictorgff3,'r')
    for line in fopen:
        if line[0] != '#':
            linelist = line.strip().split('\t')
            if linelist[2] == 'mRNA':
                ts,gene = linelist[8].replace('geneID=','').replace('ID=','').replace('Parent=','').split(';')
                if method == 'stringtie':
                    ts = '.'.join(ts.split('.')[0:3])
                elif method == 'scallop':
                    ts = ts.split('.')[0]
                elif method == 'braker':
                    pass
                ts2gene[ts] = gene
    return ts2gene     

def ExtractPredictorGeneID(linedict,method,ts2gene):
    if method == 'stringtie':
        predgene = '.'.join(linedict['pred_attributes'].replace('ID=','').replace('Parent=','').split(';')[1].split('.')[0:2])
        predcds = '.'.join(linedict['pred_attributes'].replace('ID=','').replace('Parent=','').split(';')[0].split('.')[1:4])
    elif method == 'scallop':
        predcds = linedict['pred_attributes'].replace('ID=','').split(';')[0].split('.')[1]
        predgene = ts2gene[predcds]
    elif method == 'braker':
        predcds = linedict['pred_attributes'].replace('Parent=','')
        predgene = ts2gene[predcds]
    return predgene,predcds



if __name__=="__main__": 
    parser = argparse.ArgumentParser(description="Calculate frequency of putative CDS fusions by looking for one-to-many overlaps of predicted to reference CDS")
    parser.add_argument('-refgff3','--reference-annotation-gff3',dest='refgff3',type=str,help='reference gff3')
    parser.add_argument('-predgff3','--predictor-annotation-gff3',dest='predgff3',type=str,help='prediction method gff3')
    parser.add_argument('-overlaps','--overlap-bed-file',dest='overlapbed',type=str,help='output of intersectBed -loj -a prediction -b ncbi')
    parser.add_argument('-method','--gene-predction-method',dest='method',type=str,help='bioinformatics tool for predicting genes')
    parser.add_argument('-o','--overlap-summary-outfile',dest='summary',type=str,help='name of output overlap summary file')
    opts = parser.parse_args()


    predictor_ts2gene = BuildPredictorTranscript2GeneDict(opts.predgff3,opts.method)
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
    cds_overlapdict = defaultdict(list)

    fields = ['predchrom','predstart','predend','predstrand',
              'pred_attributes','refchrom','refstart','refend',
              'refstrand','ref_attributes']

    for line in intersectbed:
        linelist = line.strip().split('\t') 
        linedict = dict(zip(fields,linelist))
        predgene,predcds = ExtractPredictorGeneID(linedict,opts.method,predictor_ts2gene)
        if opts.method == 'scallop':
            predgene = predictor_ts2gene[predcds]    
        if linelist[-1] == '.':
            overlapdict[predgene].append('None')
            cds_overlapdict[predcds].append('None')

        elif linedict['predstrand'] == linedict['refstrand']:
            refgene = ref_mrna2gene[linelist[-1].replace('Parent=','')]
            overlapdict[predgene].append(refgene)
            cds_overlapdict[predcds].append(refgene)
  
        elif linedict['predstrand'] != linedict['refstrand']:
            refgene = ref_mrna2gene[linelist[-1].replace('Parent=','')]
            overlapdict[predgene].append('%s-oppstrand' % refgene)            
            cds_overlapdict[predcds].append('%s-oppstrand' % refgene)

    genestats = open('geneoverlapstats.txt','w')
    gene_overlap_count_list = []
    gene_opposite_strand_overlap_counter = 0
    fout = open(opts.summary,'w')
    fout.write('predgene\trefgenes\tnumfusions\n')
    for predgene in overlapdict:
        overlapset = set(overlapdict[predgene])
        if len(overlapset) == 1 and overlapset == set(['None']): 
            fout.write('%s\tNone\t0\n' % predgene)
            gene_overlap_count_list.append(0)
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
                gene_opposite_strand_overlap_counter+=1
                fout.write('%s\tOppositeStrand\t0\n' % predgene)   
            else:
                fout.write('%s\t%s\t%s\n' % (predgene,';'.join(list(overlapset)),len(overlapset)))
            gene_overlap_count_list.append(len(overlapset)) 
     
    numberfusions = len([i for i in gene_overlap_count_list if i >1])
    novelgenes = len([i for i in gene_overlap_count_list if i ==0])
    genestats.write('number of predicted genes: %s\n' % len(overlapdict.keys()))
    genestats.write('number of putative fusions: %s\n' % numberfusions)
    genestats.write('number novel predicted genes %s\n' % novelgenes)
    genestats.write('mean overlapping reference genes: %s\n' % mean(gene_overlap_count_list))
    genestats.write('median overlapping reference genes: %s\n' % median(gene_overlap_count_list))
    genestats.write('number opposite strand overlaps: %s\n' % gene_opposite_strand_overlap_counter) 
    genestats.close()
    fout.close()

    ### CDS level ###
    cdsstats = open('cdsoverlapstats.txt','w')
    cds_overlap_count_list = []
    cds_opposite_strand_overlap_counter = 0
    cdsfout = open('cds_%s' % opts.summary,'w')
    cdsfout.write('predcds\tpredgene\trefgenes\tnumfusions\n')
    for predcds in cds_overlapdict:
        predgene = predictor_ts2gene[predcds]
        overlapset = set(cds_overlapdict[predcds])
        if len(overlapset) == 1 and overlapset == set(['None']):
            cdsfout.write('%s\t%s\tNone\t0\n' % (predcds,predgene))
            cds_overlap_count_list.append(0)
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
                cds_opposite_strand_overlap_counter+=1
                cdsfout.write('%s\t%s\tOppositeStrand\t0\n' % (predcds,predgene))
            else:
                cdsfout.write('%s\t%s\t%s\t%s\n' % (predcds,predgene,';'.join(list(overlapset)),len(overlapset)))
            cds_overlap_count_list.append(len(overlapset))
    
    numberfusions = len([i for i in cds_overlap_count_list if i >1])
    novelcds = len([i for i in cds_overlap_count_list if i ==0])
    cdsstats.write('number of predicted cds: %s\n' % len(overlapdict.keys()))
    cdsstats.write('number of putative fusions: %s\n' % numberfusions)
    cdsstats.write('number novel predicted cds %s\n' % novelcds)
    cdsstats.write('mean overlapping reference genes: %s\n' % mean(cds_overlap_count_list))
    cdsstats.write('median overlapping reference genes: %s\n' % median(cds_overlap_count_list))
    cdsstats.write('number opposite strand overlaps: %s\n' % cds_opposite_strand_overlap_counter)
    cdsstats.close()
    cdsfout.close()
