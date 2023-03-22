from Bio import SeqIO
import sys
import numpy

input=open(sys.argv[1],'r')
output = open('%s_byprotein.stats' % sys.argv[1].replace('.pep','').replace('.fasta','').replace('.faa',''),'w')
lengths=[]
internal_stop_counter = 0
completes = 0
total = 0
output.write('SeqId\tSeqLength\tStartCodon\tStopCodon\tComplete\tNumInternalStops\n')

for record in SeqIO.parse(input,'fasta'):
    bp=len(record.seq)
    total+=1
    numstops = max(record.seq[:-1].count('.'),record.seq[:-1].count('*'))
    lengths.append(bp)
    if numstops > 0 :
        internal_stop_counter+=1
        #print(record.id)
    if record.seq[0] == 'M':
        startcodon = 'Y'
    else:
        startcodon='N'
    if record.seq[-1] in ['.','*','X']:
        stopcodon = 'Y'
    else:
        stopcodon = 'N'
    if startcodon == 'Y' and stopcodon == 'Y':
        complete = 'Y'
    else:
        complete = 'N'
    
    if complete == 'Y':
        completes+=1 
    output.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (record.id,bp,startcodon,stopcodon,complete,numstops))
output.close()

summary = open('%s_protein.globalstats' % sys.argv[1].replace('.pep','').replace('.fasta','').replace('.faa',''),'w')
summary.write('NumProteins\tNumComplete\tFracComplete\tFracInternalStops\tMedianLength\tMeanLength\n')
summary.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (total,completes,completes/float(total),internal_stop_counter/float(total),numpy.median(lengths),numpy.mean(lengths))) 
summary.close()
