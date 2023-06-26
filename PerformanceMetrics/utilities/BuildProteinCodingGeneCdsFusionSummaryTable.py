import argparse
from collections import defaultdict

def ProcessGeneFusions(predicted_gene,fusion_dict):
   master_set = set()
   cds_to_refgenes = []
   fusion_array = []
   cdslist = list(fusion_dict[predicted_gene].keys())
   cdslist.remove('refgenes')
   for cds in cdslist:
       fusion_array.append(len(fusion_dict[predicted_gene][cds]['samestrand']))
       master_set = master_set.union(fusion_dict[predicted_gene][cds]['samestrand'])
       cds_to_refgenes.append(fusion_dict[predicted_gene][cds]['samestrand'])

   count_differences = []
   for entry in cds_to_refgenes:
       count_differences.append(len(master_set.difference(entry)))
       

   if len(master_set) != 0:
       if min(count_differences) > 0:
           multi_cds_fusion = True
       else:
           multi_cds_fusion = False
   else:
       multi_cds_fusion = False

   number_fusion_cds = sum(i > 1 for i in fusion_array) 
   if multi_cds_fusion == True and number_fusion_cds >0:
       mixed_fusion = True
   else:
       mixed_fusion =  False
   
   return {'mixed_fusion': mixed_fusion,'multi_cds_fusion': multi_cds_fusion,'number_cds_fusions' : number_fusion_cds}
       

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
            if linelist[2] in ['mRNA','transcript']:
                if method == 'maker':
                    ts,gene = linelist[8].replace('ID=','').replace('Parent=','').split(';')[0:2]
                    print(ts,gene)
                else:    
                    ts,gene = linelist[8].replace('geneID=','').replace('ID=','').replace('Parent=','').split(';')
                if method == 'stringtie':
                    ts = '.'.join(ts.split('.')[0:3])
                elif method == 'scallop':
                    ts = ts.split('.')[0]
                ts2gene[ts] = gene
    return ts2gene     

def ExtractPredictorGeneID(linedict,method,ts2gene):
    if method == 'stringtie':
        predgene = '.'.join(linedict['pred_attributes'].replace('ID=','').replace('Parent=','').split(';')[1].split('.')[0:2])
        predcds = '.'.join(linedict['pred_attributes'].replace('ID=','').replace('Parent=','').split(';')[0].split('.')[1:4])
    elif method == 'scallop':
        predcds = linedict['pred_attributes'].replace('ID=','').split(';')[0].split('.')[1]
        predgene = ts2gene[predcds]
    elif method in ['braker','maker','toga','TOGA','cgp','CGP']:
        predcds = linedict['pred_attributes'].replace('Parent=','')
        predgene = ts2gene[predcds]
    return predgene,predcds

def gene_nested_test(newgene,geneset):
    test = False
    for gene in geneset:
        if newgene in gene:
            test = True
    if test == True:
        return geneset
    else:
        removes = []
        for gene in geneset:
            if gene in newgene:
                removes.append(gene)
        for gene in removes:
            geneset.remove(gene)
        geneset.add(newgene)
        return geneset
    

        


if __name__=="__main__": 
    parser = argparse.ArgumentParser(description="Calculate frequency of putative CDS fusions by looking for one-to-many overlaps of predicted to reference CDS")
    parser.add_argument('-refgff3','--reference-annotation-gff3',dest='refgff3',type=str,help='reference gff3')
    parser.add_argument('-predgff3','--predictor-annotation-gff3',dest='predgff3',type=str,help='prediction method gff3')
    parser.add_argument('-overlaps','--overlap-bed-file',dest='overlapbed',type=str,help='output of intersectBed -loj -a prediction -b ncbi')
    parser.add_argument('-method','--gene-predction-method',dest='method',type=str,help='bioinformatics tool for predicting genes')
    parser.add_argument('-o','--overlap-summary-outfile',dest='summary',type=str,help='name of output overlap summary file')
    parser.add_argument('-filter-nested','--filter-nested-fusion-genes',dest='filter',action='store_true',help='switch to filter ref genes nested in annotated fusions')
    opts = parser.parse_args()

    ### build annotation method mRNA-to-gene mappings dictionary ###
    predictor_ts2gene = BuildPredictorTranscript2GeneDict(opts.predgff3,opts.method)
    
    ###############################################################

    ### build reference annotation mRNA-to-gene mappings dictionary ###
    refannot = open(opts.refgff3,'r')
    ref_mrna2gene = {}
    for line in refannot:
        if line[0]!= '#':
            linelist = line.strip().split('\t')
            if linelist[2] =='mRNA':
                attribute_dict = CreateGffAttributeDict(linelist)
                ref_mrna2gene[attribute_dict['ID']] = attribute_dict['geneID']
    ###################################################################
    
    ### load left join intersectBed table for ref CDS exons joined ###
    ### to annotation method CDS intervals ###
     
    intersectbed = open(opts.overlapbed,'r')
   
    ### create dictionaries to store overlap ids ###
    #overlapdict = defaultdict(list) # gene-level
    #cds_overlapdict = defaultdict(list) # cds transcsript level
   
    fields = ['predchrom','predstart','predend','predstrand',
              'pred_attributes','refchrom','refstart','refend',
              'refstrand','ref_attributes']

    ###

    fusion_dict = {}

    for line in intersectbed:
        linelist = line.strip().split('\t') 
        linedict = dict(zip(fields,linelist))
        predgene,predcds = ExtractPredictorGeneID(linedict,opts.method,predictor_ts2gene)
        # build gene/cds dict structures #
        if predgene not in fusion_dict:
            fusion_dict[predgene] = {} 
            fusion_dict[predgene][predcds] = {'samestrand' : set(), 'oppstrand' : set()}
            fusion_dict[predgene]['refgenes'] = set()
        elif predgene in fusion_dict and predcds not in fusion_dict[predgene]:
            fusion_dict[predgene][predcds] = {'samestrand' : set(), 'oppstrand' : set()}
        
        #################################
        
        ## parse bed overlap data ##
        # no overlap #
        if linelist[-1] == '.': 
            pass
        
        # same strand #
        elif linedict['predstrand'] == linedict['refstrand']:
            refgene = ref_mrna2gene[linelist[-1].replace('Parent=','')]
            if opts.filter == False:
                fusion_dict[predgene][predcds]['samestrand'].add(refgene)
                fusion_dict[predgene]['refgenes'].add(refgene)
            else:
                fusion_dict[predgene][predcds]['samestrand'] = gene_nested_test(refgene,fusion_dict[predgene][predcds]['samestrand'])
                fusion_dict[predgene]['refgenes'] = gene_nested_test(refgene,fusion_dict[predgene]['refgenes'])


        # opposite strand
        elif linedict['predstrand'] != linedict['refstrand']:
            refgene = ref_mrna2gene[linelist[-1].replace('Parent=','')]
            if opts.filter == False:
                fusion_dict[predgene][predcds]['oppstrand'].add(refgene)
            else:
                fusion_dict[predgene][predcds]['oppstrand'] = gene_nested_test(refgene,fusion_dict[predgene][predcds]['oppstrand'])

    fout = open('%s_fusionsummary.tsv' % opts.summary,'w')
    fout.write('PredictedGeneId\tcds_fusions\tmulti_cds_fusion\tmulti_mixed_fusion\trefgenes\n')
    
    genecounter=0
    #gene_list = list(fusion_dict.keys())
    #gene_list.sort()
    for gene in fusion_dict:
        genecounter+=1
        if genecounter%100 == 0:
            print('processing gene %s' % genecounter)
        genestats = ProcessGeneFusions(gene,fusion_dict)
        if len(list(fusion_dict[gene]['refgenes'])) > 0:
            fout.write('%s\t%s\t%s\t%s\t%s\n' % (gene,genestats['number_cds_fusions'],
        str(genestats['multi_cds_fusion']),str(genestats['mixed_fusion']),';'.join(list(fusion_dict[gene]['refgenes']))))
        else:
            fout.write('%s\t%s\t%s\t%s\tNone\n' % (gene,genestats['number_cds_fusions'],
            str(genestats['multi_cds_fusion']),str(genestats['mixed_fusion'])))
    fout.close()
