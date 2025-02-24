#!/bin/bash

step=$1

if [[ $step == 1 ]]; then
    echo "Running step $step"
    
    # Hardcode the file 
    file="/lustrefs/hdd_pool_dir/nanoAODv12/16dec2023_noSkimWZ/WZsignalSamples_Run3Summer22/WZto3LNu-1Jets-4FS_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/Run3Summer22NanoAODv12/250208_115544/0000/GEN-Run3Summer22NanoAODv12-00519_28.root"

    python3 createLHEFormatFromROOTFile.py $file output -1 
fi
