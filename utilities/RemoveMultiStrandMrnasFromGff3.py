import sys
gffin = open(sys.argv[1],'r')
gffout = open('nomultistrand_%s' % sys.argv[1],'w')

multis = open(sys.argv[2],'r')
multistrand_list = []
for line in multis:
    multistrand_list.append(line.strip())

for line in gffin:
    if line[0] == '#':
        gffout.write(line)
    else:
        fail=0
        for multi in multistrand_list:
            if '%s;' % multi in line:
                fail+=1
                break
        if fail == 0:
            gffout.write(line)

gffout.close()
                
        
        
