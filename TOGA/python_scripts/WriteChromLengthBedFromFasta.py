import sys
from Bio import SeqIO
source_species=sys.argv[1]
chrombed = open('%s_chromlengths.bed' % source_species,'w')

for record in SeqIO.parse(sys.argv[2], "fasta"):
    chrombed.write('%s\t0\t%s\n' % (record.id,len(record.seq)))

chrombed.close()
