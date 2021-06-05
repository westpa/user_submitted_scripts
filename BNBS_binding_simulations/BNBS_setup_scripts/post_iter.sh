#!/bin/bash

cd $WEST_SIM_ROOT || exit 1

if [[ $((WEST_CURRENT_ITER % 10)) -eq 0 ]];then
# Keep seg_logs from exploding
IT=$(printf "%06d" $WEST_CURRENT_ITER)
SEG_LOG_TAR=seg_logs_$(printf "%06d" $WEST_CURRENT_ITER).tar
time tar -c -f $SEG_LOG_TAR seg_logs/*.log && rm -f seg_logs/*.log
if [ -e $SEG_LOG_TAR ] ; then 
    time xz -9v $SEG_LOG_TAR
    time tar -r -f seg_logs_all.tar $SEG_LOG_TAR.xz && rm $SEG_LOG_TAR.xz
fi
else

if [[ ! -e seg_logs ]];then
  mkdir seg_logs
fi

cd seg_logs
rm ${IT}-*log

fi

# save .gro, .trr, and .edr files from each segment
#if [[ $WEST_CURRENT_ITER -gt 2 ]] ; then
    #del_iter=$[ $WEST_CURRENT_ITER - 2]
    #del_iter_dir=traj_segs/$(printf "%06d" $del_iter)
    #pushd $del_iter_dir &> /dev/null || exit 1
        #for seg_id in *; do
            #pushd $seg_id &> /dev/null || exit 1 
                ## protect files to save
		#if [ -e seg.trr ]; then
                #for ext in edr.xz gro trr ; do
                    #mv seg.$ext .seg.$ext
                #done
                ## delete everything else (dotfiles ignored in glob)
                #rm *
                ## deprotect files to save
                #for ext in edr.xz gro trr ; do
                    #mv .seg.$ext seg.$ext
                #done                
		#fi
            #popd &> /dev/null
        #done
    #popd &> /dev/null
    #time tar -c $del_iter_dir > $del_iter_dir.tar && rm -Rf $del_iter_dir
#fi
