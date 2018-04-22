import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np
  
def plot_fourbar(logfile, ylabel, lrlc, lrhc, hrlc, hrhc, brbc):
  
    fig, ax = plt.subplots()    
    ind = np.arange(len(lrlc))
    width = 0.15       # the width of the bars
    
    xlabel=['No Meeting', '0900-1000', '1000-1100', '1100-1200', '1200-1300', '1300-1400', '1400-1500', '1500-1600', '1600-1700', '0900-1700']
#     ax.bar(ind, hrhc, width, color='#ededed', label='R1') 
#     ax.bar(ind+width, hrlc, width, color='#666666', label='R2', hatch="/")
#     ax.bar(ind+(2*width), lrhc, width, color='#d6d6d6', label='R3', hatch=".")
#     ax.bar(ind+(3*width), lrlc, width, color='#adadad', label='R4', hatch="\\")

#     ax.bar(ind, hrhc, width, color='#ededed', label='HRHC') 
#     ax.bar(ind+width, hrlc, width, color='#666666', label='HRLC', hatch="/")
#     ax.bar(ind+(2*width), lrhc, width, color='#d6d6d6', label='LRHC', hatch=".")
#     ax.bar(ind+(3*width), lrlc, width, color='#adadad', label='LRLC', hatch="\\")
    
    ax.bar(ind, hrhc, width, color='#ededed', label='HRHC') 
    ax.bar(ind+width, hrlc, width, color='#666666', label='HRLC', hatch="/")
    ax.bar(ind+(2*width), brbc, width, color='#adadad', label='MRMC', hatch="x")
    ax.bar(ind+(3*width), lrhc, width, color='#d6d6d6', label='LRHC', hatch=".")
    ax.bar(ind+(4*width), lrlc, width, color='#adadad', label='LRLC', hatch="\\")
    
    
#     ax.plot([1, 3.8], [220, 220], 'r-', lw=2)
#     ax.annotate('Prefer LR Room', xy=(1, 230),  xycoords='data')
#     
#     ax.plot([4, 5.8], [280, 280], 'r-', lw=2)
#     ax.annotate('Prefer LC Room', xy=(4, 290),  xycoords='data')
#     
#     ax.plot([6, 8.8], [380, 380], 'r-', lw=2)
#     ax.annotate('Prefer HR Room', xy=(6, 390),  xycoords='data')
#     
#     ax.plot([9, 9.8], [555, 555], 'r-', lw=2)
#     ax.annotate('Prefer HC Room', xy=(7.8, 565),  xycoords='data')
        
    handles, labels = ax.get_legend_handles_labels()
    fontP = FontProperties()
    fontP.set_size('large')
    ax.legend(handles, labels, loc='best', prop=fontP)   
      
    ax.set_xticks(ind+width)  
    ax.set_xticklabels(xlabel) 
    ax.set_ylabel(ylabel) 
    ax.set_xlabel('Scheduling Periods') 
    
    fig.autofmt_xdate()
    

#     plt.show()
    plt.savefig('Output\\'+ logfile +'.png', dpi=400)
    plt.close(fig)
    
def getIndex(fstr):    
    parts = fstr.split()
    s = parts[0].split('/')
    return s[1].split('.')[0]

def parseData(cfg_data):    
    lines = cfg_data.split('\n')
    for i in xrange(0,10):    
        line = lines[i]
        parts = line.split()
        lrlc.append(float(parts[3]))
    print "lrlc:", lrlc
        
    for i in xrange(10,20):    
        line = lines[i]
        parts = line.split()
        lrhc.append(float(parts[3]))
    print "lrhc:", lrhc
        
    for i in xrange(20,30):    
        line = lines[i]
        parts = line.split()
        hrlc.append(float(parts[3]))
    print "hrlc:", hrlc
        
    for i in xrange(30,40):    
        line = lines[i]
        parts = line.split()
        hrhc.append(float(parts[3]))
    print "hrhc:", hrhc
    
    for i in xrange(40,50):    
        line = lines[i]
        parts = line.split()
        brbc.append(float(parts[3]))
    print "brbc:", brbc
        


# run_config_file = open("Output/ecom1.txt", 'r')
# run_config_file = open("Output/winter.txt", 'r')
run_config_file = open("Output/eams_run_best.txt", 'r')
# run_config_file = open("Output/LRHC_4r_each.txt", 'r')

cfg_data = ''.join(run_config_file.readlines())
run_config_file.close()        

lrlc = []
lrhc = []
hrlc = []
hrhc = []
brbc = []
parseData(cfg_data)
plot_fourbar("mip_room_energy", "Energy (kWh)", lrlc, lrhc, hrlc, hrhc, brbc)
# plot_fourbar("e_bestroom", "Energy (kWh)", lrlc, lrhc, hrlc, hrhc, brbc)
# plot_fourbar("e_LRHC_4R", "Energy (kWh)", lrlc, lrhc, hrlc, hrhc)
    