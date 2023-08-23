from Bio import SeqIO
from numpy import median
import argparse

if __name__=="__main__": 
    parser = argparse.ArgumentParser(description='args for computing stats from assembly fiile')
    parser.add_argument('-f','--fastain',dest='frecords',type=str,help='input transcriptome fasta file')
    parser.add_argument('-colname','--output-column-name',dest='colname',type=str,help='column name for written table')
    opts = parser.parse_args()

    lengths=[]
    fout = open('%s_seqlengths.tsv' % (opts.frecords),'w')
    fout.write('seqid\tlength\tmethod\n')
    for record in SeqIO.parse(opts.frecords,'fasta'):
        fout.write('%s\t%s\t%s\n' % (record.id,len(record.seq),opts.colname))
        lengths.append(len(record.seq))
    print('median: %s\n' % median(lengths))
    print('max: %s\n' % max(lengths))
    print('min: %s\n' % min(lengths))
fout.close()
    
 


