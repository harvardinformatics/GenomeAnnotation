import sys
gfcomp_tfrag_table = open(sys.argv[1])
total_tfrags = 0
from collections import defaultdict

summary_dict = {'match' : 0,'c' : 0,'k' : 0,'m' : 0,
               'n': 0, 'j':0 ,'e': 0,'o': 0, 'y': 0,
               'u' : 0 ,'i': 0, 'xs': 0 ,'p': 0,
               'other' : 0}

gfcomp_tfrag_table.readline()
for line in gfcomp_tfrag_table:
    linelist = line.strip().split("\t")
    if linelist[2] == '=':
        summary_dict['match']+=1
    elif linelist[2] == 'c':
        summary_dict['c'] +=1
    elif linelist[2] == 'k':
        summary_dict['k'] +=1
    elif linelist[2] =='m':
        summary_dict['m'] +=1
    elif linelist[2] == 'n':
        summary_dict['n'] +=1
    elif linelist[2] =='j':
        summary_dict['j'] +=1
    elif linelist[2] =='e':
        summary_dict['e'] +=1
    elif linelist[2] =='o':
        summary_dict['o'] +=1
    elif linelist[2] == 'i':
        summary_dict['i']+=1
    elif linelist[2] == 'u':
        summary_dict['u'] +=1
    elif linelist[2] in ['x','s']:
        summary_dict['xs']+=1
    elif linelist[2] == 'p':
        summary_dict['p']+=1
    elif linelist[2] == 'y':
        summary_dict['y']+=1
    else:
        summary_dict['other']+=1
        print(linelist)
print(summary_dict)
for code in ['match','c','k','xs','m', 'n', 'j', 'e', 'o','i','u','p','y','other']:
#for code in ['p', 'y','other']:  #['match','c','k','xs','m', 'n', 'j', 'e', 'o','i','u','p','other']:
    print('%s\t%s\n' % (code,summary_dict[code]))

