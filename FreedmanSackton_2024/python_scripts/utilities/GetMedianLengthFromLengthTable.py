import sys
from numpy import median
fopen=open(sys.argv[1],'r')
fopen.readline()
lengths=[]
for line in fopen:
    linelist=line.strip().split()
    lengths.append(int(linelist[1]))

fout = open('CDSoverall_lengthmedian.txt','w')
fout.write('%s\n' % median(lengths))
