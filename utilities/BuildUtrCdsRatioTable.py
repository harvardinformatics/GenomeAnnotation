import sys
from numpy import median

cds_lengths = open(sys.argv[1],'r')
cds_fields = cds_lengths.readline().strip().split('\t')
cds_dict = {}
for line in cds_lengths:
    line_dict =  dict(zip(cds_fields,line.strip().split('\t')))
    cds_dict[line_dict['seqid']] = int(line_dict['length'])

utr_lengths = open(sys.argv[2],'r')
utr_fields = utr_lengths.readline().strip().split('\t')
utr_dict = {}
for line in utr_lengths:
    line_dict =  dict(zip(utr_fields,line.strip().split('\t')))
    utr_dict[line_dict['tsid']] = int(line_dict['total_utr_length'])

utr2cds_ratios = []

fout = open(sys.argv[3],'w')
fout.write('tsid\tcds_length\tutr_length\tutr2cds\n')
for tsid in cds_dict:
    if tsid in utr_dict:
        fout.write('%s\t%s\t%s\t%s\n' % (tsid,cds_dict[tsid],utr_dict[tsid],utr_dict[tsid]/cds_dict[tsid]))
        utr2cds_ratios.append(utr_dict[tsid]/cds_dict[tsid])
    else:
        fout.write('%s\t%s\t0\t0\n' % (tsid,cds_dict[tsid]))

fout.close()
print(median(utr2cds_ratios))
