#!/usr/bin/env python3

import argparse
from Bio import SeqIO


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='split fasta files into mulitple files of max specified number of seqs')
    parser.add_argument('-f','--fasta-infile',dest='fastain',type=str,help='input fasta file')
    parser.add_argument('-maxn','--max-number-records',dest='maxn',type=int,help='max number of fasta records per split file')
    parser.add_argument('-counter','--number-subfiles-out',dest='numfiles',type=int,help='output file name for count of subfiles')
    opts = parser.parse_args()
    
    file_index = 1
    seqcount = 0
    fout = open('%s_%s' % (file_index,opts.fastain),'w')
    
    for record in SeqIO.parse(opts.fastain,'fasta'):
        if seqcount <=opts.maxn-1:
            SeqIO.write(record,fout,'fasta')
            seqcount+=1
        else:
            file_index+=1
            fout.close()
            fout = open('%s_%s' % (file_index,opts.fastain),'w') 
            SeqIO.write(record,fout,'fasta')
            seqcount=1 
    fout.close()

    counterout = open('%s' % opts.numfiles,'w')
    counterout.write('%s\n' % file_index)
    counterout.close()
