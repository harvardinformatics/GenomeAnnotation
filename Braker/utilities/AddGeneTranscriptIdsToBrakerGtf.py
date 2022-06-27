import sys
from collections import defaultdict
exon_tracker = defaultdict(int)
cds_tracker = defaultdict(int)
intron_tracker=defaultdict(int)

def CreateId(linelist,exon_tracker,cds_tracker,intron_tracker):
    if linelist[2] == 'gene':
        newid = 'gene_id "%s"' % linelist[8]
    elif linelist[2] == 'transcript':
       newid = 'gene_id "%s"; transcript_id "%s"' % (linelist[8].split('.')[0],linelist[8])
    else:
        col8list = linelist[8].replace('"','').split(';')[:-1]
        datadict = {}
        for field in col8list:
            key,value = field.split()
            datadict[key] = value        
        if linelist[2] == 'stop_codon':
            newid = 'ID "%s-stop"' % datadict['transcript_id']
        elif linelist[2] == 'start_codon':
            newid = 'ID "%s-start"' % datadict['transcript_id'] 
        elif linelist[2] == 'exon':
            exon_tracker[datadict['transcript_id']]+=1
            newid = 'ID "%s-exon%s"' % (datadict['transcript_id'],exon_tracker[datadict['transcript_id']])
        elif linelist[2] == 'CDS':
            cds_tracker[datadict['transcript_id']]+=1           
            newid = 'ID "%s-cds%s"' % (datadict['transcript_id'],cds_tracker[datadict['transcript_id']])
        elif linelist[2] == 'intron':
            intron_tracker[datadict['transcript_id']]+=1 
            newid = 'ID "%s-intron%s"' % (datadict['transcript_id'],intron_tracker[datadict['transcript_id']])
        else:
            raise ValueError("Unknown data type")
    return newid       


gtfin = open(sys.argv[1],'r')
gtfout = open('IdsAdded_%s' % sys.argv[1],'w')
for line in gtfin:
    if line[0] == '#':
        gtfout.write(line)
    else:
        linelist = line.strip().split('\t')
        newid = CreateId(linelist,exon_tracker,cds_tracker,intron_tracker)
        newline = '%s\t%s; %s\n' % ('\t'.join(linelist[:8]),newid,linelist[8])
        gtfout.write(newline)


gtfout.close() 
