import sys
cdsisoforms = open(sys.argv[1],'r') # tab-sep table, col1 = gene, col2=isoform id
cdsisoforms.readline()
isolist = []
for line in cdsisoforms:
    isolist.append(line.strip().split()[1])
entrycount = 0
bedin = open(sys.argv[2],'r')
bedout= open('CDS_%s' % sys.argv[2],'w')
for line in bedin:
    entrycount+=1
    if entrycount%10000 == 0:
        print('processing transcript %s\n' % entrycount)
    linelist = line.strip().split('\t')
    if linelist[3] in isolist:
        bedout.write(line)


bedout.close()
