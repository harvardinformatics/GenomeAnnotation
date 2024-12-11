import sys
liftoff_open = open(sys.argv[1],'r')
cdsgff_out = open('pcoding_{}'.format(sys.argv[1]),'w')
genes_keep = set()
mrnas_keep = set()
for line in liftoff_open:
    if line[0] == '#':
        cdsgff_out.write(line)
    else:
        linelist = line.strip().split('\t')
        if linelist[2] == "gene" and "protein_coding" in linelist[8]:
            genes_keep.add(linelist[8].split(';')[0].replace('ID=',''))
            cdsgff_out.write(line)
        elif linelist[2] == 'mRNA':
            mrnas_keep.add(linelist[8].split(';')[0].replace('ID=',''))
            cdsgff_out.write(line)
        elif linelist[2] == 'exon':
            parent = linelist[8].split(';')[1].replace('Parent=','')
            if parent in mrnas_keep:
                cdsgff_out.write(line)
        elif linelist[2] == 'CDS':
            cdsgff_out.write(line)

cdsgff_out.close()            
