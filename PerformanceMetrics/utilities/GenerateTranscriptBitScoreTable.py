import argparse

fields = ['qseqid', 'sseqid', 'pident',
         'length', 'mismatch', 'gapopen',
         'qstart', 'qend', 'sstart', 'send',
         'evalue','bitscore']

if __name__=="__main__": 
    parser = argparse.ArgumentParser(description="remove UTR intervals from all features")
    parser.add_argument('-blastp','--blastp-outfmt6',dest='blastp',type=str,help='blastp results on unfiltered proteins')
    parser.add_argument('-aa','--annotation-protein-fasta',dest='prot',type=str,help='gffread translated protein fasta of annotation')
    parser.add_argument('-o','--bitscore-table-output',dest='output',type=str,help='name of output table to score bitscore info')
    opts = parser.parse_args()
    
    # load protein data #
    annot_aa = open(opts.prot,'r')
    protein_list = []
    for line in annot_aa:
        if line[0] == '>':
            protein_list.append(line[1:].strip().split()[0])
    
    # generate blastp results dictionary #
    hit_dict = {}
    blastin = open(opts.blastp,'r')
    for line in blastin:
        linedict = dict(zip(fields,line.strip().split('\t')))
        if linedict['qseqid'] not in hit_dict:
            hit_dict[linedict['qseqid']] = {'evalue': linedict['evalue'],'bitscore': linedict['bitscore']}

    # write output #
    fout = open(opts.output,'w')
    fout.write('tsid\teval\tbitscore\n')
    for tsid in protein_list:
        if tsid in hit_dict:           
            fout.write('%s\t%s\t%s\n' % (tsid,hit_dict[tsid]['evalue'],hit_dict[tsid]['bitscore']))
    fout.close()
    hit_fraction = len(hit_dict)/float(len(protein_list)) 
    summary = open('hitfraction_summary.txt','w')
    summary.write('summary for %s\n' % opts.prot)
    summary.write('fraction of proteins with blastp hits: %s\n' % hit_fraction)
    summary.close() 
