#!/bin/bash
repodir=[REPODIR]
outdir=[OUTDIR]
inevents=[INEVENTS]
gridpack=[GRIDPACK]

# Move to the output directory

cd $outdir/tmp

# Run one event manually to generate the code
tar -xvf $gridpack
bash runcmsgrid.sh 1 123456 1

export PYTHONPATH=${outdir}/process/rwgt:$PYTHONPATH

# Prepare reweighting
cd process/

# Now launch a reweighting for each input event
iev=0
for event_file in $( ls $inevents/* ); do
    cp -r Events/cmsgrid Events/cmsgrid_${iev}/

    cp ${event_file} Events/cmsgrid_${iev}/events.lhe.gz
    iev=$(( $iev + 1 ))
    
    # Launch reweight
    echo "0" | ./bin/aMCatNLO reweight cmsgrid_${iev} 

    # Collect output
    cp Events/cmsgrid_${iev}/events.lhe.gz $outdir/rwgt_events.chunk${iev}.lhe.gz
done

# Cleanup
cd $outdir
rm -rf tmp
