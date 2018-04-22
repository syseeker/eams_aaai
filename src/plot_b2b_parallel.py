import sys
import time
import logging
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from datetime import datetime
import numpy as np
  
def plot_tribar(logfile, ylabel, d1label, data1, d2label, data2, d3label, data3):
  
    fig, ax = plt.subplots()    
    ind = np.arange(len(data1))    
    width = 0.3       # the width of the bars
    
    rects1 = ax.bar(ind, data1, width, color='r', label='Parallel', hatch="/")
    rects2 = ax.bar(ind+width, data2, width, color='g', label='Back-to-Back in R1', hatch=".")
    rects3 = ax.bar(ind+(2*width), data3, width, color='b', label='Back-to-Back in R2', hatch="\\")
        
    handles, labels = ax.get_legend_handles_labels()
    fontP = FontProperties()
    fontP.set_size('small')
    ax.legend(handles, labels, loc='lower right', prop=fontP)   
      
    ax.set_xticks(ind+width)  
    
    # overwrite d1label    
#     print d1label
    d1label = ['NE & E', 'NE & N', 'E & C', 'E & SE', 'SE & S', 'S & SW', 'S & C', 'C & W', 'C & N', 'N & NW', 'NW & W', 'W & SW']
    ax.set_xticklabels(d1label) 
    ax.set_ylabel(ylabel) 
    ax.set_ylim(0,200)
    
    fig.autofmt_xdate()
    
#     def autolabel(rects):
#         for rect in rects:            
#             height = rect.get_height()
#             if height >= 1:
#                 ax.text(rect.get_x()+rect.get_width()/2., 1.01*height, '%d'%(int(height)),
#                     ha='center', va='bottom', fontsize=10)
#                     
#     autolabel(rects1)
#     autolabel(rects2)
#     autolabel(rects3)
    plt.savefig('Output\\'+ logfile +'.png')
#     plt.show()
    plt.close(fig)
    
def getIndex(fstr):    
    parts = fstr.split()
    s = parts[0].split('/')
    return s[1].split('.')[0]

def parseData(cfg_data):    
    lines = cfg_data.split('\n')
    for i in xrange(len(lines)):    
        line = lines[i]
        parts = line.split()
        
        idx = getIndex(parts[0])
        data = parts[3]
            
        if i%6 == 0 or i%6 == 1:
            if i%6 == 0:
                tmp = float(data)
            else:
                p_label.append(idx)
                p.append((tmp+float(data))/2)
        elif i%6 == 2 or i%6 == 3:        
            if i%6 == 2:
                tmp = float(data)
            else:            
                b2b_r1_label.append(idx)
                b2b_r1.append((tmp+float(data))/2)
        elif i%6 == 4 or i%6 == 5:        
            if i%6 == 4:
                tmp = float(data)
            else:            
                b2b_r2_label.append(idx)
                b2b_r2.append((tmp+float(data))/2)          
    # print len(p)
    # print p
    # print len(p_label)
    # 
    # print len(b2b_r1)
    # print b2b_r1
    # print len(b2b_r1_label)
    # 
    # print len(b2b_r2)
    # print b2b_r2
    # print len(b2b_r2_label)

# Step:  run either 1/3    
run_config_file = open("Output/compareB2BvsP_0900.txt", 'r')
# run_config_file = open("Output/compareB2BvsP_1200.txt", 'r')
# run_config_file = open("Output/compareB2BvsP_1500.txt", 'r')

cfg_data = ''.join(run_config_file.readlines())
run_config_file.close()        

p = []
b2b_r1 = []
b2b_r2 = []
p_label = []
b2b_r1_label = []
b2b_r2_label = []
parseData(cfg_data)

# Step:  run either 1/3
plot_tribar("p_vs_b2b_0900", "Average Energy Consumption (kWh)", p_label, p, b2b_r1_label, b2b_r1, b2b_r2_label, b2b_r2)
# plot_tribar("p_vs_b2b_1200", "Energy (kWh)", p_label, p, b2b_r1_label, b2b_r1, b2b_r2_label, b2b_r2)
# plot_tribar("p_vs_b2b_1500", "Average Energy Consumption (kWh)", p_label, p, b2b_r1_label, b2b_r1, b2b_r2_label, b2b_r2)
    