import sys
from numpy import mean,median
bedin = open(sys.argv[1],'r')
lengths=[]
for line in bedin:
    linelist = line.strip().split()
    lengths.append(int(linelist[2])-int(linelist[1]))

fout = open('%s_lengthreport.txt' % sys.argv[1],'w')
fout.write('mean length: %s\n'  % mean(lengths))
fout.write('median length: %s\n'  % median(lengths))
fout.close()
