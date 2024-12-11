import argparse

fields='qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qlen slen'.split()

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='calculate fraction of reference proteins covered by at least one predicted protein')
    parser.add_argument('-blast','--blast-table',dest='blast',type=str,help='blast output table')
    parser.add_argument('-refn','--number-reference-proteins',dest='refprotn',type=int,help='number of reference proteins')
    parser.add_argument('-cov','--ref-cov-threshold',dest='coverage',type=float,help='fractional coverage threshold')
    opts = parser.parse_args()

    refprotset=set()
    fopen = open(opts.blast,'r')
    for line in fopen:
        linedict = dict(zip(fields,line.strip().split('\t')))
        coverage = int(linedict['length'])/int(linedict['qlen'])
        if float(linedict['evalue']) <= 10**-5 and coverage >opts.coverage:
            refprotset.add(linedict['qseqid'])

    frac_covered = len(refprotset)/int(opts.refprotn)
    fout = open('refprotein_proportioncovered_cov_{}covthresh.txt'.format(opts.coverage),'w')
    fout.write('proportion ref proteins with coverage:{}\n'.format(str(frac_covered)))
    print(frac_covered)

    fout.close()


   


   
