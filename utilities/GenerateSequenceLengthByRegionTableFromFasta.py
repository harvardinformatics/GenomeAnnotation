from Bio import SeqIO
import numpy
import argparse
from numpy import median

if __name__=="__main__": 
    parser = argparse.ArgumentParser(description='args for computing stats from assembly fiile')
    parser.add_argument('-f','--fastain',dest='frecords',type=str,help='input transcriptome fasta file')
    parser.add_argument('-o','--out-prefix',dest='outprefix',type=str,help='name of output table')
    parser.add_argument('-intergenic','--intergenic-ids-file',dest='intergenic',type=str,help='putative FP intergenic ids')
    opts = parser.parse_args()

    intergenic_ids = set()
    
    intergenic_lengths = []
    genic_lengths = []

    interopen = open(opts.intergenic,'r')
    for line in interopen:
        intergenic_ids.add(line.strip())

    fout = open('%s_lengthtable.tsv' % (opts.outprefix),'w')
    fout.write('seqid\tlength\tregionclass\n')
    for record in SeqIO.parse(opts.frecords,'fasta'):
        if '.'.join(record.id.split('.')[:-1]) in intergenic_ids or record.id in intergenic_ids:
            fout.write('%s\t%s\tintergenic\n' % (record.id, len(record.seq)))
            intergenic_lengths.append(len(record.seq))
        
        else:
            fout.write('%s\t%s\tgenic\n' % (record.id, len(record.seq)))
            genic_lengths.append(len(record.seq))

    stats = open('%s_byregionsummaries.tsv' % opts.outprefix,'w')
    stats.write('median genic: %s\n' % median(genic_lengths))
    stats.write('median intergenic: %s\n' % median(intergenic_lengths))
    stats.close()  
          


fout.close()
    
 


