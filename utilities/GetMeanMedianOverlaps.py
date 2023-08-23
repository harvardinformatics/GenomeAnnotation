import sys
from numpy import mean,median
bedin = open(sys.argv[1],'r')
counts=[]
percentages = []
for line in bedin:
    if line[0] != "#":
        linelist = line.strip().split()
        counts.append(int(linelist[5]))
        percentages.append(float(linelist[6]))

fout = open('%s_overlaps.txt' % sys.argv[1],'w')
fout.write('mean count: %s\n'  % mean(counts))
fout.write('median count: %s\n'  % median(counts))
fout.write('mean percentage: %s\n'  % mean(percentages))
fout.write('median percentage: %s\n'  % median(percentages))


fout.close()
