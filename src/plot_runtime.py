import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np
  
   
def plot_runtime_graph(rfile):
    
    fstr = 'Output\\' + rfile      
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()
     
    runtime_s = []
    case = [] 
    lines = data.split('\n')
    for i in xrange(len(lines)-1):
        line = lines[i]
        parts = line.split()
        case.append(parts[0]) 
#         print float(parts[7])
        runtime_s.append(float(parts[7]))
             
    fig, ax = plt.subplots()    
    ind = np.arange(len(runtime_s))  
    width = 0.3       # the width of the bars

    ax.bar(ind, runtime_s, width, color='r')
    
#     handles, labels = ax.get_legend_handles_labels()
#     fontP = FontProperties()
#     fontP.set_size('small')
#     ax.legend(handles, labels, loc='upper right', prop=fontP)   
      
    ax.set_xticks(ind+width)  
    ax.set_xticklabels(case) 
    ax.set_ylabel("Runtime (s)") 
    ax.set_ylim([0,5500])
    
    fig.autofmt_xdate()
    
    plt.savefig('Output\\'+ rfile +'.png')
#     plt.show()
    plt.close(fig)
    print "Done!"
    
    
           
# plot_runtime_graph("eams_run_m10_f_stats.txt")
# plot_runtime_graph("eams_run_m10_ns_stats.txt")
# plot_runtime_graph("eams_run_m10_ws_stats.txt")
# plot_runtime_graph("eams_run_m20_f_stats.txt")
# plot_runtime_graph("eams_run_m20_ns_stats.txt")
# plot_runtime_graph("eams_run_m20_ws_stats.txt")
# plot_runtime_graph("eams_run_m50_f_stats.txt")
# plot_runtime_graph("eams_run_m50_ns_stats.txt")
plot_runtime_graph("eams_run_m50_ws_stats.txt")
  
  


    