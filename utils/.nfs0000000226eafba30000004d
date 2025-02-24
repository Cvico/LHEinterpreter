import ROOT
import gzip 
from utils.auxiliars import color_msg
import copy
import array

class LHEToRootConversor(object):
    def __init__(
            self, 
            lhefile, 
            dictEntries, 
            defaults
        ):
      
        """ Transform the output lhe file into a friend-tree like rootfile with the weights as entries
        lhefile     : input lhefile from the reweighting
        dictEntries : a dictionary with pretty labels for the different parameters (i.e. create branches with pretty parameter names instead of things like dim6 1).
        defaults : default values of the parameters (not read from the banner, technically can be random values as it will be overwritten)
        """
        # Load lhe file
        self.lhefile = lhefile
        self.inp     = gzip.open(self.lhefile,"rb")
        color_msg(
            "Loading whole LHE file, this might take a while...",
            color = "green",
            indentlevel = 0
        )
        
        
        self.thelines = self.inp.readlines()
        self.dictEntries = dictEntries
        self.defaults = defaults
        self.central = ""
        
        # Get weights definitions from the banner
        self.loadWeightDefs()
        self.nWeights = len(self.weightVars) 
        
        # Build output file
        self.outputRootFile = ROOT.TFile(
            self.lhefile.replace(".lhe.gz",".root"), 
            "RECREATE"
        )
        
        #self.sf = self.outputRootFile.mkdir("sf")
        self.outputTree = ROOT.TTree("Friends","LHEweight tree")
        self.initTree()

        # This is the insideloop function
        self.getEvents()
        self.sf.cd()
    
        # Write and close
        self.outputTree.Write()
        self.outputRootFile.Close()

    def getEvents(self):
        readEvent = False
        readWeight = False
        iev = 0
        events = -1
        iL = 0
        totL = len(self.thelines)
        for l in self.thelines:
            iL += 1
            if b"<event" in l: #Start reading event
                iev += 1
                #print("Processing event (total number estimated) ... %i/%i"%(iev, (totL)/(iL/iev) ))
                readEvent = True
                self.ret = copy.copy(self.branchPointers)
        
            if readEvent: # Check if we should start or stop reading weights and read if we should be doing it
                if b"<rwgt" in l: 
                    readWeight = True
                if readWeight:
                    if b"wgt id" in l:
                        idw = l.split(b">")[0].replace(b"<wgt id='",b"").replace(b"'",b"")
                        if int(idw.replace(b"rwgt_",b""))-1 >= 1000: 
                            continue
                        val = float(l.split(b">")[1].replace(b"</wgt",b"").replace(b" ",b""))
                        self.ret["LHERew_weights"][int(idw.replace(b"rwgt_",b""))-1] = val

                    if b"</rwgt>" in l: 
                        readWeight = False
                if b"</event>" in l:
                    # Normalize to SM value defined as all EFT parameters set to 0
                    toNorm = self.ret["LHERew_weights"][self.central]
                    for i in range(0, self.nWeights):
                        self.ret["LHERew_weights"][i] = self.ret["LHERew_weights"][i]/toNorm
                    readEvent = False
                    self.branchPointers = self.ret
                    self.outputTree.Fill()
     
    def initTree(self):
        # Open and initialize the whole output tree
        self.branchPointers = {}
        for k in self.dictEntries:
            self.branchPointers[k] = array.array('f',[1.]*self.nWeights)
            self.outputTree.Branch("LHERew_"+ self.dictEntries[k], self.branchPointers[k], "LHERew_%s[%i]/F"%(self.dictEntries[k],self.nWeights))
        self.branchPointers["LHERew_weights"] = array.array('f',[1.]*self.nWeights)
        self.outputTree.Branch("LHERew_weights", self.branchPointers["LHERew_weights"], "LHERew_weights[%i]/F"%self.nWeights)
        for i in range(1, self.nWeights):
            for k in self.branchPointers:
                if k=="LHERew_weights": continue
                self.branchPointers[k][i-1] = self.weightVars["rwgt_%i"%i][k]

    def loadWeightDefs(self):
        # Read weight definition from the banner to later save it
        color_msg(
            "Finding weights in banner....",
            color = "blue",
            indentlevel = 1
        )
        
        readingBlock  = False
        readingWeight = False
        self.weightVars = {}
        iL = 0
        
        for l in self.thelines:
            l = l.decode()
            
            # Identify weight group blocks
            if "weightgroup name='mg_reweighting'" in l:
                readingBlock = True
                
            
            if readingBlock:
                
                
                # Stop if the "/weightgroup" label is found
                if "/weightgroup" in l: readingBlock = False
                
                
                # Read if "<weight" label is found
                elif "<weight" in l: 
                    
                    weightinfo = l.split( ">" )[0]
                    weightname = weightinfo.replace("<weight id='","").replace("'","")
                    currentWeightName = weightname
                    
                    # Save the weight information in the weight dictionary
                    self.weightVars[currentWeightName] = copy.copy(self.defaults)
                    if "set param" in l.split(">")[1]:
                        w = l.split(">")[1].split("#")[0]
                        sett, param, mod, entry, value, dummy = w.split(" ")
                        self.weightVars[currentWeightName][mod + " " + entry] = float(value)
                
                # Read parameter if "set param" is found
                elif "set param" in l:
                    sett, param, mod, entry, value, dummy = l.split("#")[0].split(" ")
                    self.weightVars[currentWeightName][mod + " " + entry] = float(value)
                
                # Stop reading weight info if "/weight" label is found
                if "</weight>" in l:
                    readingWeight = False
                    print(currentWeightName, self.weightVars[currentWeightName])
                    if all([self.weightVars[currentWeightName][k] == 0 for k in self.weightVars[currentWeightName]]):
                        self.central = int(currentWeightName.replace("rwgt_",""))-1
                        print("Found all parameters at 0 (SM-like candidate) at weight %s"%currentWeightName)
