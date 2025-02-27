import ROOT
import sys, os
from utils.auxiliars import HEPPart, color_msg

class LHEPrinter(object):
    def __init__(self, 
        theFile, 
        theTree, 
        outfolder, 
        undoDecays=[ ], 
        nchunks = -1, 
        maxEvents = -1,
        prDict={ }
    ):
        """
        theFile : path to input root file with the custom nano format
        theTree : number of ttree inside the file, usually "Events"
        outputLHE: number of output .lhe file
        undoDecays: pdgId of particles whose decays we want to undo (i.e. W that are decayed with madspin, as the reweighting is called before madspin)
        chunkers: process by chunks in case we want to later multithread the jobs
        prDict  : a dictionary indicating possible mismatchings between the ProcessID in the new gridpack and the old (matching the numbers at generate p p > blah blah @0 in the run card)
        """

        # Save attributes
        self.fil  = ROOT.TFile( theFile,"open" )
        self.tree = self.fil.Get(theTree)
        filename = theFile.split("/")[-1].replace(".root", "")
        
        self.create_folder( outfolder )
        self.outputLHE = f"{outfolder}/{filename}"
        self.undoDecays = undoDecays
        self.nchunks = nchunks
        self.maxEvents = maxEvents
        self.prDict = prDict    

        # Declare headers for the LHE output
        self.baseheader =  "<event nplo=\" {nplo} \" npnlo=\" {npnlo} \">\n"
        self.baseline1 = " {nparts}      {prid} {weight} {scale} {aqed} {aqcd}\n"
        self.baseender = "<rwgt>\n</rwgt>\n</event>\n"

    def create_folder( self, name ):
        """ Create the output folder """
        if not os.path.exists( name ):
            os.system( f"mkdir -p {name}" )
        

    def insideLoop(self):
        """ Main loop """
        totalEvents = self.tree.GetEntries()

        if totalEvents < self.maxEvents:
            color_msg( 
                f"Input number of events is: {self.maxEvents}," + \
                "which is lower than the total number of events " + \
                f"in the file: {totalEvents}. Code will run over " + \
                f"{totalEvents} events.",
                color = "green",
                indentlevel = 0
            )    
            self.maxEvents = totalEvents
        
        if self.maxEvents == -1:
            self.maxEvents = totalEvents
            
            
        self.nevents_per_chunk = self.maxEvents // self.nchunks
        
        overhead = self.maxEvents - self.nevents_per_chunk * self.nchunks

        color_msg( 
            f"Will run over {self.maxEvents}. There is an overhead of {overhead} events" + \
            " that will be stored in a separate file.",
            color = "green",
            indentlevel = 0
        )
        
        
        ichunk = 0
        iev_chunk = 0
        
        self.output = open(
            self.outputLHE + f".chunk{ichunk}.lhe",
            "w"
        )
        
        for iev, ev in enumerate( self.tree ):
            
            if iev > self.maxEvents - 1: break
            
            if iev_chunk > self.nevents_per_chunk - 1:
                ichunk += 1
                iev_chunk = 0
                
                self.output = open(
                    self.outputLHE + f".chunk{ichunk}.lhe",
                    "w"
                )
                 
            color_msg( 
                f"...Event {iev+1}/{self.maxEvents} (chunk {ichunk + 1})",
                color = "blue",
                indentlevel = 1
            )
            
            # Process the event
            self.process(ev)
            iev_chunk += 1


    def process(self, ev):
        """ Process the event information and get the LHE info """    
        # First produce the global line that looks like <event nplo=" -1 " npnlo=" 1 ">
        self.output.write(
            self.baseheader.format(
                nplo = ord( str(ev.LHE_NpLO) ) if ord(str(ev.LHE_NpLO)) != 255 else -1, 
                npnlo = ord(str(ev.LHE_NpNLO)) if ord(str(ev.LHE_NpNLO)) != 255 else -1
            )
        )

        # Then we need to treat the whole thing to undo the madspin decays, update statuses and rewrite particle order
        lhepart = []
        deletedIndexes = []

        for i in range( getattr(ev, "nLHEPart") ):
            testPart = HEPPart(ev, i)
            print( i, testPart.mother1, testPart.mother2 ) 
            testPart.mother1 = testPart.mother1 - sum([1*(testPart.mother1 > d) for d in deletedIndexes])
            testPart.mother2 = testPart.mother2 - sum([1*(testPart.mother2 > d) for d in deletedIndexes])
            if testPart.mother1 != 0:
                if abs( lhepart[ testPart.mother1-1 ].pdgId ) in self.undoDecays: #If it is from something that decays after weighting just skip it
                    deletedIndexes.append(i)
                    continue
            if abs( testPart.pdgId ) in self.undoDecays: # If it is something that decays after weighting, change status
                testPart.status = 1 
            
            lhepart.append( testPart )

        # Now we can compute properly the number of particles at LHE
        self.output.write(
            self.baseline1.format( 
                nparts = len(lhepart), 
                prid = self.prDict[ str(ord(str(ev.LHE_ProcessID))) ], 
                weight = ev.LHEWeight_originalXWGTUP, 
                scale = ev.LHE_Scale,
                aqed = ev.LHE_AlphaQED,
                aqcd = ev.LHE_AlphaS
            )
        )
        
        # And save each particle information
        for part in lhepart:
            self.output.write( part.printPart() )   
        
        self.output.write( self.baseender )
