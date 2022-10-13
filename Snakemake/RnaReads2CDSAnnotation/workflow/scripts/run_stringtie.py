#!/usr/bin/env python3

import argparse
from subprocess import Popen,PIPE


if __name__=="__main__": 
    parser = argparse.ArgumentParser(description='wrapper for running hisat2 within snakemake pipeline')
    parser.add_argument('-i','--input-bam',dest='bamin',type=str,help='sorted bam alignment input file')
    parser.add_argument('-strand','--rnastrandedness',dest='libstrand',type=str,default='NA',help='strandedness flag for stringtie')
    parser.add_argument('-p','--threads',dest='p',type=int,help='number of threads')
    parser.add_argument('-gtf','--output-gtf',dest='gtf',type=str,help='name of output sam alignment file')
    opts = parser.parse_args()

    strand_dict = {'RF' ; '--rf','FR': '--fr','NA': ''}
    if opts.libstrand == 'NA':
        stringtie_cmd = 'stringtie %s -p %s -o %s' % (opts.bamin,opts.p,opts.gtf)
    elif opts.libstrand in ['RF','FR']:
        stringtie_cmd = 'stringtie %s %s -p %s -o %s' % (opts.bamin,strand_dict[opts.libstrand],opts.p,opts.gtf)

    print('stringtie cmd is: %s' %  stringtie_cmd) 
    
    stringtie_runner = Popen(stringtie_cmd, shell=True, stdout=PIPE, stderr=PIPE)
    stringtie_out, stringtie_err = stringtie_runner.communicate()
