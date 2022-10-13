#!/usr/bin/env python3
from os.path import basename
import argparse
from Bio import SeqIO


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='split fasta files into mulitple files of max specified number of seqs')
    parser.add_argument('-f','--fasta-infile',dest='fastain',type=str,help='input fasta file')
    parser.add_argument('-maxn','--max-number-records',dest='maxn',type=int,help='max number of fasta records per split file')
    parser.add_argument('-filst','--subfile-list',dest='filelist',type=str,help='output file name for names of subfiles')
    opts = parser.parse_args()
    
    file_index = 1
    seqcount = 0
    fout = open('%s_%s' % (file_index,opts.fastain),'w')
    filelist = open('%s' % opts.filelist,'w')
    filelist.write('%s_%s\n' % (file_index,basename(opts.fastain)))

    for record in SeqIO.parse(opts.fastain,'fasta'):
        if seqcount <=opts.maxn-1:
            SeqIO.write(record,fout,'fasta')
            seqcount+=1
        else:
            file_index+=1
            fout.close()
            fout = open('%s_%s' % (file_index,opts.fastain),'w') 
            filelist.write('%s_%s\n' % (file_index,basename(opts.fastain)))
            SeqIO.write(record,fout,'fasta')
            seqcount=1 
    
    fout.close()
    filelist.close()
