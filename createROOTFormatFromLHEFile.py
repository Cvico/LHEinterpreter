import os
from utils.root_converter import LHEToRootConversor
from utils.auxiliars import color_msg
import argparse

def add_parsing_options():
    """ This is a custom parser that allows for passing options to the code """
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputFolder', dest = "inputFolder", default = None, help = "Folder with outputs from reweighting step")
    return parser.parse_args()

if __name__ == "__main__":  
    for df in os.listdir("output"):
        color_msg(
            f"Processing file {df}...", 
            color = "green",
            indentlevel = 0 
        )
        
        outname = df.replace(".lhe.gz",".root")
        if "root" in df: 
            continue
        
        if os.path.isfile( f"output/{outname}" ): 
            os.system( f"rm output/{outname}" )
        
        LHEToRootConversor(
            lhefile = f"output/{df}", 
            dictEntries = {
                "dim6 1" : "cwww",
                "dim6 2" : "cw",
                "dim6 3" : "cb", 
                "dim6 4" : "cPwww",
                "dim6 5" : "cPw", 
                "dim6 6" : "cPhid",
                "dim6 7" : "cPhiW",
                "dim6 8" : "cPhib"
            }, 
            defaults = {
                "dim6 1":3,
                "dim6 2":4,
                "dim6 3":150, 
                "dim6 4":100,
                "dim6 5":100, 
                "dim6 6":100,
                "dim6 7":100,
                "dim6 8":100
            }
        )
