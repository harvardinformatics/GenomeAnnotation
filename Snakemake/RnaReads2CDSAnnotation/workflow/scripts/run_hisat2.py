import argparse
from subprocess import Popen,PIPE


if __name__=="__main__": 
    parser = argparse.ArgumentParser(description='wrapper for running hisat2 within snakemake pipeline')
    parser.add_argument('-i','--hisat2-index',dest='hisatindex',type=str,help='location of hisat2 index')
    parser.add_argument('-strand','--rnastrandedness',dest='libstrand',type=str,default='NA',help='strandedness flag for hisat2')
    parser.add_argument('-minintron','--minimum-intron-length',dest='minintron',type=int,help='minimum intron length')
    parser.add_argument('-maxintron','--maximum-intron-length',dest='maxintron',type=int,help='maximum intron length')
    parser.add_argument('-1','--R1',dest='r1',type=str,help='R1 of PE library')
    parser.add_argument('-2','--R2',dest='r2',type=str,help='R2 of PE library')
    parser.add_argument('-p','--threads',dest='p',type=int,help='number of threads')
    parser.add_argument('-o','--outputsam',dest='sam',type=str,help='name of output sam alignment file')
    opts = parser.parse_args()

    if opts.libstrand == 'NA':
        hisat_cmd ='hisat2 -p %s -x %s -q --phred33 --dta --min-intronlen %s --max-intronlen %s -1 %s -2 %s -S %s'   % (opts.p,opts.hisatindex,opts.minintron,opts.maxintron,opts.r1,opts.r2,opts.sam)
    else:
        hisat_cmd ='hisat2 -p %s -x %s --rna-strandedness %s -q --phred33 --dta --min-intronlen %s --max-intronlen %s -1 %s -2 %s -S %s'   % (opts.p,opts.hisatindex,opts.libstrand,opts.minintron,opts.maxintron,opts.r1,opts.r2,opts.sam)

    print('hisat2 cmd is: %s' %  hisat_cmd)
    hisat_runner = Popen(hisat_cmd, shell=True, stdout=PIPE, stderr=PIPE)
    hisat_out, hisat_err = hisat_runner.communicate()
