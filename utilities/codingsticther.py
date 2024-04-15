def codingsticher(inputgff, fasta, outfile):
    """
    # Author: Gaurav Sablok
    # Universitat Potsdam
    # Date: 2024-4-15
    a coding regions stichter for the genome annotations and can 
    annotated and extract all the coding regions present by the alignment
    of the protein to the genome regions. It writes a fasta and if you want
    then you can invoke this a part of the tokenziers but dont forget to add the 
    padding. such as 
    import keras 
    import sklearn 
    ** add padding for the sequence labelling. 
    """
    readfile = [i for i in open(inputgff, "r").readlines() if "#" not in i]
    with open(inputgff + ".coding.gff", "w") as writegff:
        writegff.write("col0 \t col1 \t col2 \t col3 \t col4 \t col5 \t col6 \t col7 \t col8 \t col9\n")
        for line in readfile:
            writegff.write(line)
        writegff.close()
    iterator = [i.strip().split() for i in open(inputgff + ".coding.gff").readlines() if i.strip().split()[2] == "CDS"]
    iteratorids = list(set([i[0] for i in iterator]))
    iteratorgetter = []
    for i in range(len(iterator)):
        for j in range(len(iteratorids)):
            if iteratorids[j] == str(iterator[i][0]):
                iteratorgetter.append([iterator[i][0],iterator[i][2],iterator[i][3], iterator[i][4]])
    read_transcripts = [i.strip() for i in open(fasta, "r").readlines()]
    fasta_transcript_dict = {}
    for i in read_transcripts:
        if i.startswith(">"):
            path = i.strip()
            if i not in fasta_transcript_dict:
                fasta_transcript_dict[i] = ""
                continue
        fasta_transcript_dict[path] += i.strip()
    fasta_sequences = list(fasta_transcript_dict.values())
    fasta_names = [i.replace(">", "") for i in list(fasta_transcript_dict.keys())]
    extractcoding = []
    for i in range(len(iteratorgetter)):
        for j in range(len(fasta_names)):
            for k in range(len(fasta_sequences)):
                if iteratorgetter[i][0] == fasta_names[j]:
                    extractcoding.append([iteratorgetter[i][0], fasta_sequences[k][int(iteratorgetter[i][2]):int(iteratorgetter[i][3])]])
    with open(outfile, "w") as fastawrite:
        for i in range(len(extractcoding)):
            fastawrite.write(f">{extractcoding[i][0]}\n{extractcoding[i][1]}\n")
        fastawrite.close()
