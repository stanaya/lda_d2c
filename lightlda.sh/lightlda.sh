#!/bin/sh
#
#    lightlda.sh
#    wrapper script to execute LightLDA in an ordinary fashion.
#    $Id: lightlda.sh,v 1.10 2018/10/23 02:57:28 daichi Exp $
#

usage () {
    echo 'lightlda.sh: wrapper to execute LightLDA in a standard way.'
    echo 'usage: lightlda.sh K iters train model [alpha] [beta]'
    echo '$Id: lightlda.sh,v 1.10 2018/10/23 02:57:28 daichi Exp $'
    exit 0
}

root=$HOME/lightlda
mhsteps=2

#
# script body
#
if [ $# -lt 4 ]; then
    usage
fi

topics=$1
iters=$2
train=/tmp/train.$$
model=$4
base=`basename $3`
alpha=${5:-0.1}
beta=${6:-0.01}

trap 'rm -f $train; exit 1' 2 3 9 15

# create directory
if [ ! -d $model ]; then
    mkdir -p $model
fi
if [ ! -d $model/data ]; then
    mkdir -p $model/data
fi

echo "alpha = $alpha beta = $beta topics = $topics iters = $iters" \
| tee $model/param

# prepare data
echo "preparing data at $model .."
cat -n $3 > $train
cd $model
python $root/example/get_meta.py $train $base.tf
$root/bin/dump_binary $train $base.tf data 0
mv $base.tf data/

# inspect statistics
docs=`wc -l $train | awk '{print 100*(1+int($1/100))}'`
echo "docs  = $docs"
vocab=`wc -l data/$base.tf | awk '{print 100*(1+int($1/100))}'`
echo "vocab = $vocab"
size=`python -c 'import os;print os.path.getsize("data/block.0")' | \
awk '{print 1+int($0/1000000)}'`
echo "size  = $size"

# remove intermediate
rm -f /tmp/train.$$

# execute
echo "executing LightLDA .."
$root/bin/lightlda \
-num_vocabs $vocab -num_topics $topics -num_iterations $iters \
-alpha $alpha -beta $beta -mh_steps $mhsteps \
-num_local_workers 1 -num_blocks 1 -max_num_document $docs \
-input_dir data -data_capacity $size

# finalize
rm -r data

# store
echo "converting to standard parameters.."
python ../lightlda2model.py .
cd ..
echo "finished."
