import ROOT 

def color_msg(msg, color = "none", indentlevel=0):
    """ Prints a message with ANSI coding so it can be printout with colors """
    codes = {
        "none" : "0m",
        "green" : "1;32m",
        "red" : "1;31m",
        "blue" : "1;34m",
        "yellow" : "1;33m"
    }

    if indentlevel == 0: indentSymbol=">> "
    if indentlevel == 1: indentSymbol="+ "
    if indentlevel >= 2: indentSymbol="* "

    indent = indentlevel*" " + indentSymbol
    print("\033[%s%s%s \033[0m"%(codes[color], indent, msg))
    return

class HEPPart(object):
  def __init__(self,event, idx):
    """
    Miniclass to organize the description of a particle in the LHE event
    event : whole event information (usually a entry in the input TTree)
    idx : the index of the particle inside the LHE file
    """
    
    self.attrs = [
        "pt", "eta", "phi", "mass",
        "lifetime",
        "pdgId", "status", "spin",
        "color1", "color2",
        "mother1", "mother2",
        "incomingpz"
    ]
    
    for att in self.attrs :
      setattr(self, att, getattr( event, f"LHEPart_{att}")[idx] )
    
    self.setP4()
    
  def setP4(self):
    self.p4 = ROOT.TLorentzVector()
    if self.status != -1:
      self.p4.SetPtEtaPhiM(self.pt, self.eta, self.phi, self.mass)
    else:
      self.p4.SetPxPyPzE(0.,0.,self.incomingpz, abs(self.incomingpz))
 
  def printPart(self):
    pdg = self.pdgId
    status = self.status
    mother1 = self.mother1
    mother2 = self.mother2
    color1 = self.color1
    color2 = self.color2
    px = self.p4.Px()
    py = self.p4.Py()
    pz = self.p4.Pz()
    energy = self.p4.E()
    mass = self.mass
    time = self.lifetime
    spin = self.spin
    
    lhe_event = f"       {pdg:d} {status:d}    {mother1:d}    {mother2:d}  {color1:d}  {color2:d} {px:e} {py:e} {pz:e} {energy:e} {mass:e} {time:e} {spin:e}\n"
    return lhe_event
