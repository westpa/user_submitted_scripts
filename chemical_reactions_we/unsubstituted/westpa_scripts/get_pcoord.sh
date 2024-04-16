#!/bin/bash
cd $WEST_BSTATE_DATA_REF || exit 1
echo $WEST_BSTATE_DATA_REF
paste pcoord.init pcoord2.init > $WEST_PCOORD_RETURN
