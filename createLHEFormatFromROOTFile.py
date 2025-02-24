import ROOT
import sys
import argparse

from utils.lhe_converter import LHEPrinter

def add_parsing_options():
    """ This is a custom parser that allows for passing options to the code """
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', dest = "infile", default = None, help = "File to be postmortem-reweighted")
    parser.add_argument('--outfolder', dest = "outfolder", default = "lhe_output", help = "Path where to store the LHE format.")
    parser.add_argument('--nchunks', dest = "nchunks", default = 1, type = int, help = "Number of chunks in which events are splitted.")
    parser.add_argument('--maxEvents', dest = "maxEvents", default = -1, type = int, help = "Maximum number of events to process.")
    return parser.parse_args()

if __name__ == "__main__":
  opts = add_parsing_options()
  
  infile = opts.infile
  outfolder = opts.outfolder
  nchunks = opts.nchunks
  maxEvents = opts.maxEvents
  
  printer = LHEPrinter(
    theFile = infile,
    theTree = "Events",
    outfolder = outfolder,
    undoDecays = [ -24, 24, 23 ],
    nchunks = nchunks, 
    maxEvents = maxEvents,
    prDict = { str(i) : i for i in range(1000) }
  ) #PRDict by default set to not change anything as it is rare to use it 
  
  # Call the main loop
  printer.insideLoop()
