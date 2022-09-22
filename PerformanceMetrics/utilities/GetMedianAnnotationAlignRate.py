import sys
from glob import glob
from numpy import median
prefix = sys.argv[1]

logs = glob("*log")
rates = []
for log in logs:
    logopen = open(log,'r')
    logread = logopen.readlines()
    for line in logread:
        if 'overall' in line:
            rate = float(line.split()[0].replace('%',''))  
            rates.append(rate)
fout = open('median_align_rate_%s.txt' % prefix, 'w')
fout.write('median annotation align rate: %s\n' % median(rates))
fout.close()
