import sys
togagff3 = open(sys.argv[1],'r')
fout = open('genelabelfix_%s' % sys.argv[1],'w')

ref_iso_2_gene = {}
refiso2genefile = open(sys.argv[2],'r')
for line in refiso2genefile:
    linelist = line.strip().split()
    print(linelist)
    
    ref_iso_2_gene[linelist[0]] = linelist[1]


for line in togagff3:
    if line[0] == '#':
        fout.write(line)
    else:
        linelist = line.strip().split('\t')
        if linelist[2] == 'mRNA':
            gene = ref_iso_2_gene['.'.join(linelist[8].split(';')[0].replace('ID=','').split('.')[0:2])]
            newline = '%sgeneID=%s\n' % (line.split('geneID=')[0],gene)
            fout.write(newline)
        else:
            fout.write(line)

fout.close() 
   
