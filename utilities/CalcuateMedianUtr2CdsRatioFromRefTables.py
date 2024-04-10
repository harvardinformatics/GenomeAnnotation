from numpy import median
import sys
# seqid length method #
exons  = open(sys.argv[1],'r')
fields=exons.readline().strip().split()
exons_dict = {}
for line in exons:
    line_dict = dict(zip(fields,line.strip().split('\t')))
    exons_dict[line_dict['seqid']] = int(line_dict['length'])

cds = open(sys.argv[2],'r')
cds.readline()
cds_dict = {}
for line in cds:
    line_dict = dict(zip(fields,line.strip().split('\t')))
    cds_dict[line_dict['seqid']] = int(line_dict['length'])

utr_lengths = []
utr2cdsratios = []

fout = open(sys.argv[3],'w')
fout.write('seqid\tcds_length\tutr_length\tutr2cdsratio\n')
for tsid in cds_dict:
    utr_length = exons_dict[tsid] - cds_dict[tsid]
    utr_lengths.append(utr_length)
    fout.write('%s\t%s\t%s\t%s\n' % (tsid,cds_dict[tsid],utr_length,utr_length/cds_dict[tsid]))
    utr2cdsratios.append(utr_length/cds_dict[tsid])

print(median(utr_lengths))
print(median(utr2cdsratios))




