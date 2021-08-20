#!/bin/sh
#SBATCH -p holy-info,shared
#SBATCH -n 1
#SBATCH --mem=12000
#SBATCH --time=48:00:00
#SBATCH -e wig2hints_%A.e
#SBATCH -o wig2hints_%A.o
#SBATCH -J wig2hints

#set -o errexit -o nounset -o xtrace
inwig=$1
echo "inwig is $inwig"

wigprefix=`echo $inwig |sed 's/.wig//g'`
echo "wigprefix is $wigprefix"

AUGUSTUS_IMAGE="/n/singularity_images/informatics/augustus/augustus_3.4.0-afreedman-build.sif"
singularity exec --cleanenv ${AUGUSTUS_IMAGE} wig2hints.pl --width=10 --margin=10 --minthresh=2 --minscore=4 --src=W --type=ep --radius=4.5 < $inwig > ${wigprefix}.hints.ep.gff

#singularity exec --cleanenv ${AUGUSTUS_IMAGE} cat $inwig | /root/augustus/scripts/wig2hints.pl --width=10 --margin=10 --minthresh=2 --minscore=4 --src=W --type=ep --radius=4.5 > ${wigprefix}.hints.ep.gff 

