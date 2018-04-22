import sys
import time
import logging
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from datetime import datetime

from solver_feasible import Solver
from eams import EAMS
import numpy as np


def calcElectricityBill(kWh):    
    logging.info("Note: this is for daily quota!! It's different from multiple days calculations!")
    if kWh > 300:
        extra = kWh - 300
        return (300 * 0.2541) + (extra * 0.3003)
    else:
        return kWh * 0.2541
    
def plot_stackbar(logfile, ylabel, xticklabel, data1, data2, data3):
    fig, ax = plt.subplots()    
    ind = np.arange(len(data1))    
    width = 0.4
    
    data = np.array([data1, data2, data3])
    bottom = np.vstack((np.zeros((data.shape[1],), dtype=data.dtype),
                        np.cumsum(data, axis=0)[:-1]))
    colors = ('r', 'g', 'b')
    labels = ('Fan', 'Cooling', 'Heating')
    for dat, col, lab, bot in zip(data, colors, labels, bottom):
        plt.bar(ind, dat, width, color=col, label=lab, bottom=bot)
    
    handles, labels = ax.get_legend_handles_labels()
    fontP = FontProperties()
    fontP.set_size('small')
    ax.legend(handles, labels, loc='best', prop=fontP)   
      
    ax.set_xticks(ind+width/2)  
    ax.set_xticklabels(xticklabel) 
    ax.set_ylabel(ylabel) 
    
    fig.autofmt_xdate()
    
    plt.savefig('Output\\'+ logfile +'.png')
#     plt.show()
    plt.close(fig)
    
def plot_tribar(logfile, ylabel, xticklabel, data1, data2, data3):
    fig, ax = plt.subplots()    
    ind = np.arange(len(data1))    
    width = 0.35       # the width of the bars
    
    rects1 = ax.bar(ind, data1, width, color='r', label='Fan')
    rects2 = ax.bar(ind+width, data2, width, color='g', label='Cooling')
    rects3 = ax.bar(ind+(2*width), data3, width, color='b', label='Heating')
    
    handles, labels = ax.get_legend_handles_labels()
    fontP = FontProperties()
    fontP.set_size('small')
    ax.legend(handles, labels, loc='best', prop=fontP)   
      
    ax.set_xticks(ind+width)  
    ax.set_xticklabels(xticklabel) 
    ax.set_ylabel(ylabel) 
    
    fig.autofmt_xdate()
    
    def autolabel(rects):
        # attach some text labels
        for rect in rects:
            height = rect.get_height()
            if height >= 1:
                ax.text(rect.get_x()+rect.get_width()/2., 1.01*height, '%d'%int(height),
                    ha='center', va='bottom', fontsize=10)
        
    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)
    plt.savefig('Output\\'+ logfile +'.png')
#     plt.show()
    plt.close(fig)
    
    
def plot_bar(logfile, ylabel, xticklabel, data):
    
    fig, ax = plt.subplots()    
    ind = np.arange(len(data))
    print ind
    width = 0.35       # the width of the bars
    
    rects1 = ax.bar(ind, data, width, color='b')
    ax.set_xticks(ind+width)  
    ax.set_xticklabels(xticklabel) 
    ax.set_ylabel(ylabel) 
    
    fig.autofmt_xdate()
    
    def autolabel(rects):
        # attach some text labels
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x()+rect.get_width()/2., 1.01*height, '%d'%int(height),
                    ha='center', va='bottom')
        
    autolabel(rects1)
    plt.savefig('Output\\'+ logfile +'.png')
#     plt.show()
    plt.close(fig)

def plot_graph(logfile):
    fstr = 'Output\\' + logfile      
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()
    
    lines = data.split('\n')    
    case = []
    total_power_kJs = []
    total_energy_kJ = []
    total_energy_kWh = []
    total_fan_energy_kWh = []
    total_cond_energy_kWh = []
    total_heat_energy_kWh = []
#     bill = []
    for i in xrange(len(lines)-1):        
        line = lines[i]
        parts = line.split()        
        case.append(parts[0])
        total_power_kJs.append(float(parts[1]))
        total_energy_kJ.append(float(parts[2]))
        total_energy_kWh.append(float(parts[3]))
        total_fan_energy_kWh.append(float(parts[4]))
        total_cond_energy_kWh.append(float(parts[5]))
        total_heat_energy_kWh.append(float(parts[6]))
#         bill.append(calcElectricityBill(float(parts[3])))
                  
#     print total_power_kJs
#     print total_energy_kJ
#     print total_energy_kWh
    
#     plot_bar(logfile+"_kW", "Power (kJ/s or kW)", case, total_power_kJs)    
#     plot_bar(logfile+"_kJ","Energy (kJ)", case, total_energy_kJ)
    plot_bar(logfile+"_kWh","Energy (kWh)", case, total_energy_kWh)
#     plot_tribar(logfile+"_kWh_dist_tri", "Energy (kWh)", case, total_fan_energy_kWh, total_cond_energy_kWh, total_heat_energy_kWh)
    plot_stackbar(logfile+"_kWh_dist_stacked", "Energy (kWh)", case, total_fan_energy_kWh, total_cond_energy_kWh, total_heat_energy_kWh)         
#     plot_bar(logfile+"_dollar","Dollar ($)", case, bill)
              

def plot_specific_room_graph(logfile):
    fstr = 'Output\\' + logfile      
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()
    
    lines = data.split('\n')    
    case = []
    total_power_kJs = []
    total_energy_kJ = []
    total_energy_kWh = []
    total_fan_energy_kWh = []
    total_cond_energy_kWh = []
    total_heat_energy_kWh = []
#     bill = []
    for i in xrange(0,len(lines)-1,10):        # this loop is diff from plot_graph
        line = lines[i]
        parts = line.split()        
        case.append(parts[0])
        total_power_kJs.append(float(parts[1]))
        total_energy_kJ.append(float(parts[2]))
        total_energy_kWh.append(float(parts[3]))
        total_fan_energy_kWh.append(float(parts[4]))
        total_cond_energy_kWh.append(float(parts[5]))
        total_heat_energy_kWh.append(float(parts[6]))
        
    print case
    plot_bar(logfile+"_kWh","Energy (kWh)", case, total_energy_kWh)
    plot_stackbar(logfile+"_kWh_dist_stacked", "Energy (kWh)", case, total_fan_energy_kWh, total_cond_energy_kWh, total_heat_energy_kWh)         
# 

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