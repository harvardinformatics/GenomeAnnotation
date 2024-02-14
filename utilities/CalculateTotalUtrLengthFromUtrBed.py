import sys
from collections import defaultdict
from numpy import median

ts_list = []
tscript_fasta = open(sys.argv[1],'r')
for line in tscript_fasta:
    if line[0] == '>':
        ts_list.append(line.strip().split()[0].replace('>',''))


utr_bed_open = open(sys.argv[2],'r')

utr_length_dict = defaultdict(int)
for interval in utr_bed_open:
    chrom,start,end,tsid = interval.strip().split('\t')
    utr_length_dict[tsid] += int(end)-int(start)

fout = open('%s_utrlengths.tsv' % sys.argv[1],'w')
fout.write('tsid\ttotal_utr_length\n')
utr_lengths = []
for tsid in ts_list:
    if tsid in utr_length_dict: 
        fout.write('%s\t%s\n' % (tsid,utr_length_dict[tsid]))
        utr_lengths.append(utr_length_dict[tsid])
else:
        fout.write('%s\t0\n' % tsid)
        utr_lengths.append(0)
fout.close()

utr_median = open('%s_utrmedian_length.txt' % sys.argv[1],'w')
utr_median.write('%s\n' % median(utr_lengths))
utr_median.close()
