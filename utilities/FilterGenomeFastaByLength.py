from Bio import SeqIO
import numpy
import argparse

if __name__=="__main__": 
    parser = argparse.ArgumentParser(description='args for computing stats from assembly fiile')
    parser.add_argument('-f','--fastain',dest='frecords',type=str,help='input transcriptome fasta file')
    parser.add_argument('-minlen','--min_sequence_length',dest='minlen',type=int,help='minimum sequence length')
    opts = parser.parse_args()

    fout = open('minlength_%s_%s' % (opts.minlen,opts.frecords),'w')
    for record in SeqIO.parse(opts.frecords,'fasta'):
        if len(record.seq) >= opts.minlen:
            SeqIO.write(record,fout,'fasta')

fout.close()
    
 


