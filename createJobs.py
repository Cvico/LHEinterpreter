import os
import sys
import gzip
import argparse
from utils.auxiliars import color_msg

def add_parsing_options():
    """ This is a custom parser that allows for passing options to the code """
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseInputLHEDir', dest = "baseInputLHEDir", default = None, help = "Directory with the output from createLHEFormatFromROOTFile.py")
    parser.add_argument('--baseGridpack', dest = "baseGridpack", default = None, help = "Path to the tar.gz file wiht the gridpack. ")
    parser.add_argument('--templateRun', dest = "templateRun", default = "banner.lhe.gz",  help = "An lhe.gz file containing only the banner and general settings.")
    parser.add_argument('--baseOutputLHEDir', dest = "baseOutputLHEDir", default = "jobs",  help = "Output where to store each job")
    return parser.parse_args()


if __name__ == "__main__":
    
    opts = add_parsing_options()
    baseInputLHEDir = opts.baseInputLHEDir  # lhe events as obtained from createLHEFormatFromROOTFile.py
    baseGridpack    = opts.baseGridpack     # tar.gz file with the gridpack
    templateRun     = opts.templateRun      # a .lhe file containing only the banner and general run settings and handle where events should be
    baseOutputLHEDir = opts.baseOutputLHEDir # output directory

    newOnly = True

    # Read empty lhe file
    inBase = gzip.open( templateRun, "r" )
    baseHeader = inBase.read()
    inBase.close()
    
    
    iJob = 0
    maindir = os.path.dirname(os.path.realpath(__file__))
    
    # Get a list of LHE files
    lhefiles = [ _file for _file in os.listdir( baseInputLHEDir ) if ".lhe" in _file ]
    # Loop over the chunks to process
    for ifile, _file in enumerate(lhefiles):
        
        color_msg( f"Creating job for file {_file}", color = "green", indentlevel = 0)
        
        short = _file.replace( ".lhe", "" )
        
        # Create a temporary directory
        eventsDir = baseOutputLHEDir + f"/unrwgt_events/"
        
        if not os.path.exists( eventsDir ):
            os.system(f"mkdir -p {eventsDir} ")
        
        tmpdir = f"{baseOutputLHEDir}/tmp"
        if not os.path.exists( tmpdir ):
            os.system(f"mkdir -p {tmpdir} ")
        
        
        # Copy the events form the previous step in the unwgt_events folder
        inEvFile = open(baseInputLHEDir + "/" + _file, "rb")
        inEvents = inEvFile.read()
        
        inEvents_withBanner_name =  f"{eventsDir}/events.chunk{ifile}.lhe.gz"
        inEvents_withBanner = gzip.open( inEvents_withBanner_name , "wb") 
        header = baseHeader.replace(b"[[[ PLACE YOUR EVENTS HERE ]]]", inEvents)
        inEvents_withBanner.write(header)
        inEvents_withBanner.close()
        inEvFile.close()
        
        # Now create the job executable
        jobTemplate = open( f"{maindir}/jobTemplate.sh", "rb" )
        jobInText = jobTemplate.read()
        jobTemplate.close()
        newjob = open( f"{tmpdir}/job.sh", "wb")
        
        jobtext = jobInText.replace(b"[REPODIR]", maindir.encode())
        jobtext = jobtext.replace(b"[GRIDPACK]", f"{maindir}/{baseGridpack}".encode())
        jobtext = jobtext.replace(b"[INEVENTS]", f"{maindir}/{eventsDir}".encode())        
        jobtext = jobtext.replace(b"[OUTDIR]", f"{maindir}/{baseOutputLHEDir}".encode() )
        
        newjob.write( jobtext )
        newjob.close()
        iJob +=1
