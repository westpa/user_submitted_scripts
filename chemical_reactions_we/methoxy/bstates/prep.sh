#!/bin/bash

#a=1
#for i in {100000..1000000..100000}; do
#  mkdir ${a}
#  mv gen_bstates_2.rst_${i} ${a}/bstate.rst
#  a=$((a+1))
#done
#a=11
#for i in {100000..1000000..100000}; do
#  mkdir ${a}
#  mv gen_bstates_3.rst_${i} ${a}/bstate.rst
#  a=$((a+1))
#done
#a=21
#for i in {100000..1000000..100000}; do
#  mkdir ${a}
#  mv gen_bstates_4.rst_${i} ${a}/bstate.rst
#  a=$((a+1))
#done
#a=31
#for i in {100000..1000000..100000}; do
#  mkdir ${a}
#  mv gen_bstates_5.rst_${i} ${a}/bstate.rst
#  a=$((a+1))
#done
#a=41
#for i in {100000..1000000..100000}; do
#  mkdir ${a}
#  mv gen_bstates_6.rst_${i} ${a}/bstate.rst
#  a=$((a+1))
#done
for i in {1..50}; do
  cd ${i}
  cpptraj -i ../cpptraj.in
  cpptraj -i ../cpptraj2.in
#  cpptraj -i ../cpptraj3.in
  cd ../
done
for i in {1..50}; do
  cd ${i}
  cat pcoord_raw.init | tail -n +2 | awk {'print $4'} > pcoord.init
#  cat pcoord2_raw.init | tail -n +2 | awk {'print $2'} > pcoord2.init
  cat pcoord2_raw.init | tail -n +2 | awk {'print $4'} > pcoord2.init
#  cat pcoord3_raw.init | tail -n +2 | awk {'print $7'} > pcoord4.init
#  cat pcoord3_raw.init | tail -n +2 | awk {'print $10'} > pcoord5.init
#  cat pcoord3_raw.init | tail -n +2 | awk {'print $13'} > pcoord6.init
#  cat pcoord3_raw.init | tail -n +2 | awk {'print $16'} > pcoord7.init
#  cat pcoord3_raw.init | tail -n +2 | awk {'print $19'} > pcoord8.init
#  cat pcoord3_raw.init | tail -n +2 | awk {'print $22'} > pcoord9.init
#  cat pcoord3_raw.init | tail -n +2 | awk {'print $25'} > pcoord10.init
#  cat pcoord3_raw.init | tail -n +2 | awk {'print $28'} > pcoord11.init
  rm pcoord_raw.init
  rm pcoord2_raw.init
  #rm pcoord3_raw.init
  cd ../
done
