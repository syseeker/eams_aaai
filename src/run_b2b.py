import sys
import time
import logging
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from datetime import datetime

# from solver_b2b import Solver
from solver_b2b_v2 import Solver
from eams import EAMS
import numpy as np

def run_it(cfg_data, cfg_idx):
    cfg = cfg_data.split('\n')
    runCount = int(cfg[0])
    
    for i in range(1, runCount+1):        
        if not cfg[i]:
            sys.exit("Invalid run... No config file exists.")
            
        print "\n\nRunning " + cfg[i] + "..."        
        eams.readProblemInstance(cfg[i])
         
        caseid = cfg[i].replace('/','_').replace('.','_')
        solver = Solver(eams, caseid)        
        solver.solve()
        solver.logSchedulingResults()   
            
        mname = cfg[i].replace('/',' ').replace('.',' ').split() 
        solver.createFixedMeetingSchedule(mname[1])     
            
if __name__ == '__main__':    
    eams = EAMS() 
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        run_config_file = open(file_location, 'r')
        cfg_data = ''.join(run_config_file.readlines())
        run_config_file.close()        
        
        cfg_idx = file_location.replace('\\',' ').replace('.',' ').split() # exclude folder and .cfg  
        run_it(cfg_data, cfg_idx[1])        

    else:
        print 'This test requires an input file.  Please select one from the data directory. (i.e. python run.py ./Input/eams.cfg)'