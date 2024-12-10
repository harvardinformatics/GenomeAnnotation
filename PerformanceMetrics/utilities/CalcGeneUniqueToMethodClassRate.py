
methods = ['braker','cgp','lift','maker','scal','stie']
def ClassifyMethodList(methods,methodlist):
    method_classes = set()
    if 'ncbi' in methodlist:
        ncbi = True
    else:
        ncbi = False

    for method in methods:
        method_present = [method in i for i in methodlist]
        if True in method_present:
            method_classes.add(method)
        if sum(method_present) >0:
            if len(method_present) == sum(method_present):
                unique = True
                return unique,ncbi,list(method_classes)
                break
            elif len(method_present) - sum(method_present) == 1 and 'ncbi' in methodlist:
                unique = True
                return unique,ncbi,list(method_classes)
                break
    if 'unique' not in locals():
        return False,ncbi,list(method_classes)

import sys
from numpy import corrcoef
from scipy.stats import pearsonr
from collections import defaultdict
mergebed = open(sys.argv[1],'r')
species =  sys.argv[2]
method_total = defaultdict(int)
method_intergenic = defaultdict(int)
method_unique = defaultdict(int)
for method in methods:
    method_total[method] = 0
    method_intergenic[method] =0
    method_unique[method] = 0


for line in mergebed:
    methodlist = line.strip().split()[3].split(',')
    unique,ncbi,method_classes = ClassifyMethodList(methods,methodlist)
    for methodclass in method_classes:
        method_total[methodclass]+=1
    
    if unique == True and ncbi == False:
        method_unique[method_classes[0]]+=1
        method_intergenic[method_classes[0]]+=1
    elif unique == True and ncbi ==True:
        method_unique[method_classes[0]]+=1
    elif unique == False and ncbi == False:
        for method in method_classes:
            method_intergenic[method]+=1


fout = open('{}_methodclass_unique_intergenic_rates.tsv'.format(sys.argv[1]),'w')
fout.write('species\tmethodclass\tclassunique\tclassintergenic\n')
x= []
y=[]
for methodclass in methods:
    x.append(method_unique[methodclass]/method_total[methodclass])
    y.append(method_intergenic[methodclass]/method_total[methodclass])
    fout.write('{}\t{}\t{}\t{}\n'.format(species,methodclass,method_unique[methodclass]/method_total[methodclass],method_intergenic[methodclass]/method_total[methodclass]))

fout.close()

print(corrcoef(x,y))
print(pearsonr(x,y))
