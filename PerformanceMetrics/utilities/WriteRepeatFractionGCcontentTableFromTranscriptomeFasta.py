import sys
from Bio import SeqIO,SeqUtils
from numpy import mean,median

tsfasta = open(sys.argv[1],'r')
output = open('%s_repeatfractions_gc.tsv' % sys.argv[1],'w')
output.write('transcriptID\tsoftmaskprop\thardmaskprop\ttotalrepprop\tGCcontent\n')

sm_fracs = []
hm_fracs = []
total_fracs = []
for record in SeqIO.parse(tsfasta,'fasta'):
    transcript_length=len(record.seq)
    gc = SeqUtils.GC(record.seq)
    softmask_base_count = 0
    hardmask_base_count = 0
    for base in record.seq:
        if base == 'N' :
            hardmask_base_count+=1
        elif base.islower() == True and base != 'n':
            softmask_base_count+=1

    softmaskprop = softmask_base_count/float(transcript_length)
    hardmaskprop = hardmask_base_count/float(transcript_length)
    totalmaskprop = (softmask_base_count+hardmask_base_count)/float(transcript_length)    
    
    sm_fracs.append(softmaskprop)
    hm_fracs.append(hardmaskprop)
    total_fracs.append(totalmaskprop)    

    output.write('%s\t%s\t%s\t%s\t%s\n' % (record.id,softmaskprop,hardmaskprop,totalmaskprop,gc))

output.close()
stats = open('%s.repeatstats' % sys.argv[1],'w')
stats.write('mean softmask fraction: %s\n' % mean(sm_fracs))
stats.write('median softmask fraction: %s\n' % median(sm_fracs))

stats.write('mean hardmask fraction: %s\n' % mean(hm_fracs))
stats.write('median hardmask fraction: %s\n' % median(hm_fracs))

stats.write('mean soft+hard masked fraction: %s\n' % mean(total_fracs))
stats.write('median soft+hard masked fraction: %s\n' % median(total_fracs))
stats.write('max soft+hard mask fraction: %s\n' % max(total_fracs))

stats.write('mean gc content: %s\n' % mean(gc))
stats.write('median gc content: %s\n' % median(gc))
stats.close()


