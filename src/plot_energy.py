import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np
  
def plot_case_stackbar(logfile, ylabel, xticklabel, input1, input2, input3, input4):
    
    fig = plt.figure()   
    efig = fig.add_subplot(111)
        
    ind = np.arange(len(input1))    
    width = 0.4
    
    data = np.array([input1, input2, input3, input4]) 
    bottom = np.vstack((np.zeros((data.shape[1],), dtype=data.dtype), np.cumsum(data, axis=0)[:-1]))
    
    colors = ('r', 'g', 'b', 'c')
#     labels = ('LRLC', 'LRHC', 'HRLC', 'HRHC')
    labels = ('R1', 'R2', 'R3', 'R4')
    for dat, col, lab, bot in zip(data, colors, labels, bottom):
        plt.bar(ind, dat, width, color=col, label=lab, bottom=bot)
     
    handles, labels = efig.get_legend_handles_labels()
    fontP = FontProperties()
    fontP.set_size('small')
    efig.legend(handles, labels, loc='best', prop=fontP)   
       
    efig.set_xticks(ind+width/2)  
    efig.set_xticklabels(xticklabel) 
    efig.set_ylabel(ylabel) 
    efig.set_ylim([0,1800])
#     efig.set_ylim([0,550])
    efig.grid(True)
     
    fig.autofmt_xdate()
     
    plt.savefig('Output\\'+ logfile +'.png')
#     plt.show()
    plt.close(fig)
    print "Done!"

    
def plot_case_energy_graph(logfile):
    
    num_room = 4   
    fstr = 'Output\\' + logfile      
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()
    
    lines = data.split('\n')    
    case = []    
    total_energy_kWh_r1 = []
    total_energy_kWh_r2 = []
    total_energy_kWh_r3 = []
    total_energy_kWh_r4 = []
    test = []
      
    for i in xrange(len(lines)-1):
        line = lines[i]
        parts = line.split()
        
        j = i % num_room           
        if j==0:
            case.append(parts[0]) 
            total_energy_kWh_r1.append(float(parts[3]))
            test.append(float(parts[3]))
        elif j==1:
            total_energy_kWh_r2.append(float(parts[3]))
        elif j==2:
            total_energy_kWh_r3.append(float(parts[3]))
        elif j==3:
            total_energy_kWh_r4.append(float(parts[3]))

    plot_case_stackbar(logfile+"_kWh_case_energy", "Energy (kWh)", case, 
                       total_energy_kWh_r1,
                       total_energy_kWh_r2,
                       total_energy_kWh_r3,
                       total_energy_kWh_r4) 
    
           
    
# plot_case_energy_graph("eams_run_m10_f.txt")     
# plot_case_energy_graph("eams_run_m10_ns.txt")     
# plot_case_energy_graph("eams_run_m10_ws.txt")
# plot_case_energy_graph("eams_run_m20_f.txt")     
# plot_case_energy_graph("eams_run_m20_ns.txt")     
# plot_case_energy_graph("eams_run_m20_ws.txt")
# plot_case_energy_graph("eams_run_m50_f.txt")     
# plot_case_energy_graph("eams_run_m50_ns.txt")     
# plot_case_energy_graph("eams_run_m50_ws.txt")

# plot_case_energy_graph("eams_run_m10_f_ns")
# plot_case_energy_graph("eams_run_m20_f_ns")
# plot_case_energy_graph("eams_run_m50_f_ns")


# plot_case_energy_graph("eams_run_m50_f_b2b_ws_hrhc")
# plot_case_energy_graph("eams_run_m20_f_b2b_ws_hrhc")
# plot_case_energy_graph("eams_run_m10_f_b2b_ws_hrhc")
# plot_case_energy_graph("eams_run_m50_f_b2b_ws_lrlc")
# plot_case_energy_graph("eams_run_m20_f_b2b_ws_lrlc")
# plot_case_energy_graph("eams_run_m10_f_b2b_ws_lrlc")


# plot_case_energy_graph("eams_run_m10_f_ns")
# plot_case_energy_graph("eams_run_m10_f")
# plot_case_energy_graph("eams_run_m10_f_b2b_ns")
# plot_case_energy_graph("eams_run_m10_f_b2b_ws")
# plot_case_energy_graph("eams_run_m10_ns")
# plot_case_energy_graph("eams_run_m10_ws")

# plot_case_energy_graph("eams_run_m20_f_ns")
# plot_case_energy_graph("eams_run_m20_f")
# plot_case_energy_graph("eams_run_m20_f_b2b_ns")
# plot_case_energy_graph("eams_run_m20_f_b2b_ws")
# plot_case_energy_graph("eams_run_m20_ns.txt")
# plot_case_energy_graph("eams_run_m20_ws.txt")

# plot_case_energy_graph("eams_run_m50_f_ns")
# plot_case_energy_graph("eams_run_m50_f")
# plot_case_energy_graph("eams_run_m50_f_b2b_ns")
# plot_case_energy_graph("eams_run_m50_f_b2b_ws")
# plot_case_energy_graph("eams_run_m50_ns.txt")
# plot_case_energy_graph("eams_run_m50_ws.txt")

# plot_case_energy_graph("eams_run_m50_ws_90minsTL")
# plot_case_energy_graph("eams_run_m50_ns_90minsTL")

# plot_case_energy_graph("eams_run_m50_ws_120minsTL")
# plot_case_energy_graph("eams_run_m50_ns_120minsTL")

    