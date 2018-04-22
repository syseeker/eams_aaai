import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np
  
   
def plot_optimality_graph(rfile):
    
    fstr = 'Output\\' + rfile      
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()
     
    color_arr = []
    optimality = []
    case = [] 
    lines = data.split('\n')
    for i in xrange(len(lines)-1):
        line = lines[i]
        parts = line.split()
        case.append(parts[0])
        
        if parts[1] == "TIME_LIMIT":
            color_arr.append('r')
        else:
            color_arr.append('b')            
        optimality.append(float(parts[12]))
             
    fig, ax = plt.subplots()    
    ind = np.arange(len(optimality))  
    width = 0.3       # the width of the bars
        
    ax.bar(ind, optimality, width, color=color_arr)
    
#     handles, labels = ax.get_legend_handles_labels()
#     fontP = FontProperties()
#     fontP.set_size('small')
#     ax.legend(handles, labels, loc='upper right', prop=fontP)   
      
    ax.set_xticks(ind+width)  
    ax.set_xticklabels(case) 
    plt.setp(ax.get_xticklabels(), rotation='vertical', fontsize=8)
    ax.set_ylabel("Optimality Gap") 
    ax.set_ylim([0,80])
    
    fig.autofmt_xdate()
    
    plt.savefig('Output\\'+ rfile +'_opgap.png')
#     plt.show()
    plt.close(fig)
    print "Done!"
    
    
           
# plot_optimality_graph("eams_run_m10_ws_stats")
# plot_optimality_graph("eams_run_m10_ns_stats")
# plot_optimality_graph("eams_run_m10_f_b2b_ws_stats")
# plot_optimality_graph("eams_run_m10_f_b2b_ns_stats")
# plot_optimality_graph("eams_run_m10_f_ns_stats")
# plot_optimality_graph("eams_run_m10_f_stats")
# 
# plot_optimality_graph("eams_run_m20_ws_stats")
# plot_optimality_graph("eams_run_m20_ns_stats.txt")
# plot_optimality_graph("eams_run_m20_f_b2b_ws_stats")
# plot_optimality_graph("eams_run_m20_f_b2b_ns_stats")
# plot_optimality_graph("eams_run_m20_f_ns_stats")
# plot_optimality_graph("eams_run_m20_f_stats")
# 
# plot_optimality_graph("eams_run_m50_ws_stats.txt")
# plot_optimality_graph("eams_run_m50_ns_stats.txt")
# plot_optimality_graph("eams_run_m50_f_b2b_ws_stats")
# plot_optimality_graph("eams_run_m50_f_b2b_ns_stats")
# plot_optimality_graph("eams_run_m50_f_ns_stats")
# plot_optimality_graph("eams_run_m50_f_stats")
  
  
# plot_optimality_graph("eams_run_m50_ns_90minsTL_stats")
# plot_optimality_graph("eams_run_m50_ws_90minsTL_stats")
  
  
# plot_optimality_graph("eams_run_m50_ns_120minsTL_stats")
plot_optimality_graph("eams_run_m50_ws_120minsTL_stats")

    