from Bio import SeqIO
import sys

fields = ['qseqid', 'sseqid', 'pident', 'length',
          'mismatch', 'gapopen', 'qstart', 'qend',
          'sstart', 'send', 'evalue', 'bitscore']

def buildProteinLengthDict(fastahandle):
    len_dict = {}
    for record in SeqIO.parse(fastahandle,'fasta'):
        len_dict[record.id] = len(record.seq)
    return len_dict

refproteins = open(sys.argv[1],'r')
predproteins = open(sys.argv[2],'r')

ref_dict = buildProteinLengthDict(refproteins)
pred_dict = buildProteinLengthDict(predproteins)

blastin = open(sys.argv[3],'r')
method = sys.argv[4]

blastout = open("withseqlengths_%s" % sys.argv[3],'w')
blastout.write('%s\tquery_length\tref_target_length\tmethod\n' % '\t'.join(fields))
queries = []
for line in blastin:
    linedict = dict(zip(fields,line.strip().split('\t')))
    if linedict['qseqid'] not in queries:
        blastout.write('%s\t%s\t%s\t%s\n' % (line.strip(),pred_dict[linedict['qseqid']],ref_dict[linedict['sseqid']],method))
        queries.append(linedict['qseqid'])
blastout.close()
