import argparse
from collections import defaultdict

def LoadTransdecoderQuerySet(tdecgff):
    fopen = open(tdecgff,'r')
    mrnalist = []
    for line in fopen:
        linelist = line.strip().split('\t')
        if linelist !=[''] and linelist[2] == 'mRNA':
            mrnalist.append(linelist[8].split(';')[0].split('.p')[0].replace('ID=',','))
    return mrnalist
   
def LoadBuscos(buscofile):
    fopen = open(buscofile,'r')
    busco_dict = defaultdict(list)
    for line in fopen:
        if line[0] != "#":
            linelist = line.strip().split('\t')
            if linelist[1] != 'Missing':
                busco_dict[linelist[0]].append(linelist[2].split(':')[0].split('.p')[0])
            else:
                busco_dict[linelist[0]].append('Missing')
    return busco_dict

 

if __name__=="__main__": 
    parser = argparse.ArgumentParser(description="assess whether BUSCO loss caused by failure of TransDecoder to carry over BUSCO containing transcripts")
    parser.add_argument('-tdecgff3','--transdecoder-genome-gff3',dest='tdecgff3',type=str,help='transdecoder genome gff3 file')
    parser.add_argument('-raw-buscos','--raw-full-busco-table',dest='rawbuscos',type=str,help='transcriptome assembly full busco table')
    parser.add_argument('-tdec-buscos','--transdecoder-busco-table',dest='tdecbuscos',type=str,help='post-transdecoder full busco table')
    opts = parser.parse_args()

    tdec_mrna_ids = LoadTransdecoderQuerySet(opts.tdecgff3)
    raw_buscos = LoadBuscos(opts.rawbuscos)
    tdec_buscos = LoadBuscos(opts.tdecbuscos)
  
    fout = open('%s_MissingBuscoDetail.tsv' % opts.tdecgff3.replace('.gff3',''),'w')
    notinraw = open('%s_HitsInTdecNotRawSummary.tsv' % opts.tdecgff3.replace('.gff3',''),'w')
    notinraw.write('Busco\tRawFNmRNAs\n')
    fout.write('Busco\tRawNumMatches\tTdecNumMatches\tRawQueriesInTdec\n')
    for busco in raw_buscos:
        # both missing #
        if raw_buscos[busco] == ['Missing'] and tdec_buscos[busco] == ['Missing']:
            fout.write('%s\t0\t0\tNA\n' % busco)
        
        # present in raw, missing in tdec #
        if 'Missing' not in raw_buscos[busco] and tdec_buscos[busco] == ['Missing']:
            counter = 0
            for mrna in raw_buscos[busco]:
                if mrna in tdec_buscos[busco]:
                    counter+=1
            fout.write('%s\t%s\t0\t%s\n' % (busco,len(raw_buscos[busco]),counter))

        # present in tdec not in raw #
        elif 'Missing' not in tdec_buscos[busco] and raw_buscos[busco] == ['Missing']:
           fout.write('%s\t0\t%s\tNA\n' % (busco,len(tdec_buscos[busco])))
           notinraw.write('%s\t%s\n' % (busco,';'.join(tdec_buscos[busco]))) 


    fout.close()
    notinraw.close()
 
