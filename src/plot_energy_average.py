import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np
  
   
def plot_average_energy_graph(fnslog, fwslog, fb2bnslog, fb2bwslog, nslog, wslog, figfile):
    
    total_energy_kWh_fns = 0
    total_energy_kWh_fws = 0
    total_energy_kWh_fb2bns = 0
    total_energy_kWh_fb2bws = 0    
    total_energy_kWh_ns = 0
    total_energy_kWh_ws = 0
       
    # Fixed with No Standby Schedule
    fstr = 'Output\\' + fnslog + '.txt'     
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()
     
    lines = data.split('\n')
    for i in xrange(len(lines)-1):
        line = lines[i]
        parts = line.split()
        total_energy_kWh_fns += float(parts[3])
    avg_fns = total_energy_kWh_fns/(len(lines)-1)
         
    # Fixed with Standby Schedule
    fstr = 'Output\\' + fwslog  + '.txt'     
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()
     
    lines = data.split('\n')
    for i in xrange(len(lines)-1):
        line = lines[i]
        parts = line.split()
        total_energy_kWh_fws += float(parts[3])
    avg_fws = total_energy_kWh_fws/(len(lines)-1)
        
    # Fixed with Back-to-back, No Standby Schedule
    fstr = 'Output\\' + fb2bnslog   + '.txt'    
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()
     
    lines = data.split('\n')
    for i in xrange(len(lines)-1):
        line = lines[i]
        parts = line.split()
        total_energy_kWh_fb2bns += float(parts[3])
    avg_fb2bns = total_energy_kWh_fb2bns/(len(lines)-1)
        
    # Fixed with Back-to-back, with Standby Schedule
    fstr = 'Output\\' + fb2bwslog    + '.txt'   
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()
     
    lines = data.split('\n')
    for i in xrange(len(lines)-1):
        line = lines[i]
        parts = line.split()
        total_energy_kWh_fb2bws += float(parts[3])
    avg_fb2bws = total_energy_kWh_fb2bws/(len(lines)-1)        
         
    # No Standby Schedule
    fstr = 'Output\\' + nslog    + '.txt'   
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()
     
    lines = data.split('\n')
    for i in xrange(len(lines)-1):
        line = lines[i]
        parts = line.split()
        total_energy_kWh_ns += float(parts[3])
    avg_ns = total_energy_kWh_ns/(len(lines)-1) 
        
         
    # With Standby Schedule
    fstr = 'Output\\' + wslog     + '.txt'  
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()
     
    lines = data.split('\n')
    for i in xrange(len(lines)-1):
        line = lines[i]
        parts = line.split()
        total_energy_kWh_ws += float(parts[3])
    avg_ws = total_energy_kWh_ws/(len(lines)-1)    
         
    
    perc_f_ns = (avg_fns-avg_ws)/avg_ws*100
    perc_f_ws = (avg_fws-avg_ws)/avg_ws*100
    perc_fb2bns_ws = (avg_fb2bns-avg_ws)/avg_ws*100
    perc_fb2bws_ws = (avg_fb2bws-avg_ws)/avg_ws*100
    perc_ns_ws = (avg_ns-avg_ws)/avg_ws*100
    
    print len(lines)-1
    print total_energy_kWh_fns
    print total_energy_kWh_fws
    print total_energy_kWh_fb2bns
    print total_energy_kWh_fb2bws
    print total_energy_kWh_ns    
    print total_energy_kWh_ws
    
    print " "
    print avg_fns
    print avg_fws
    print avg_fb2bns
    print avg_fb2bws
    print avg_ns
    print avg_ws
    
    print " "
    print perc_f_ns
    print perc_f_ws
    print perc_fb2bns_ws
    print perc_fb2bws_ws
    print perc_ns_ws
    #         
    fig, ax = plt.subplots()    
    ind = np.arange(1)  
    width = 0.4       # the width of the bars
    space = 0.1
    
    # AAAI presentation
#     rects1 = ax.bar(ind, avg_fns, width, color='#666666', label='Arbitrary')  
#     rects3 = ax.bar(ind+width+space, avg_fb2bns, width, color='#a3a3a3', label='Heuristic')
#     rects6 = ax.bar(ind+(2*width)+(2*space), avg_ws, width, color='#ffffff', label='Optimal') 
    
#     print ind
    rects1 = ax.bar(ind, avg_fns, width, color='#666666', label='AN')                             # Fixed Schedule with No Standby
    rects2 = ax.bar(ind+width+space, avg_fws, width, color='#858585', label='AS')                             # Fixed Schedule with Standby
    rects3 = ax.bar(ind+(2*width)+(2*space), avg_fb2bns, width, color='#a3a3a3', label='HN')            # Fixed Back-to-Back Schedule without Standby
    rects4 = ax.bar(ind+(3*width)+(3*space), avg_fb2bws, width, color='#c2c2c2', label='HS')    # Fixed Back-to-Back Schedule with Standby
    rects5 = ax.bar(ind+(4*width)+(4*space), avg_ns, width, color='#e0e0e0', label='ON')        # Optimal Schedule without Standby
    rects6 = ax.bar(ind+(5*width)+(5*space), avg_ws, width, color='#ffffff', label='OS')        # Optimal Schedule with Standby

    handles, labels = ax.get_legend_handles_labels()
    fontP = FontProperties()
    fontP.set_size('large')
    ax.legend(handles, labels, loc='upper right', prop=fontP)   
    
      
#     ax.set_xticks(ind+width)  
#     ax.set_xticklabels() 
    ax.axes.get_xaxis().set_visible(False)
    ax.set_ylabel("Average Energy Consumption (kWh)") 
#     ax.set_ylim([0,250])
#     ax.set_ylim([0,500])
    
    
    def autolabel(rects, index):
        for rect in rects:            
            height = rect.get_height()
            if height >= 1:
                ax.text(rect.get_x()+rect.get_width()/2., 1.01*height, '%d'%(int(height)),
                    ha='center', va='bottom', fontsize=10)
                
        if index == 0:
            ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., '%.1f%%'%(perc_f_ns),
                    ha='center', va='bottom', weight='semibold', fontsize=12)
        elif index == 1:
            ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., '%.1f%%'%(perc_f_ws),
                    ha='center', va='bottom', weight='semibold', fontsize=12)
        elif index == 2:
            ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., '%.1f%%'%(perc_fb2bns_ws),
                    ha='center', va='bottom', weight='semibold', fontsize=12)
        elif index == 3:
            ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., '%.1f%%'%(perc_fb2bws_ws),
                    ha='center', va='bottom', weight='semibold', fontsize=12)
        elif index == 4:
            ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., '%.1f%%'%(perc_ns_ws),
                    ha='center', va='bottom', weight='semibold', fontsize=12)
        elif index == 5:
            ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., 'Baseline',
                    ha='center', va='bottom', weight='semibold', fontsize=12)
                    
    autolabel(rects1,0)
    autolabel(rects2,1)
    autolabel(rects3,2)
    autolabel(rects4,3)
    autolabel(rects5,4)
    autolabel(rects6,5)
    
#     plt.savefig('Output\\aaai_'+ figfile +'.png', dpi=400)
    plt.show()
#     plt.close(fig)
    
#     Image.open('Output\\'+ figfile +'.png').convert('L').save('Output\\'+ figfile +'_grey.png')
        
    print "Done!"
    
    


plot_average_energy_graph("eams_run_f_ns", "eams_run_f","eams_run_f_b2b_ns", "eams_run_f_b2b_ws", "eams_run_ns","eams_run_ws", "avg_energy_kwh_all")
# plot_average_energy_graph("eams_run_m10_f_ns", "eams_run_m10_f","eams_run_m10_f_b2b_ns", "eams_run_m10_f_b2b_ws", "eams_run_m10_ns","eams_run_m10_ws", "eams_run_m10")
# plot_average_energy_graph("eams_run_m20_f_ns", "eams_run_m20_f","eams_run_m20_f_b2b_ns", "eams_run_m20_f_b2b_ws", "eams_run_m20_ns","eams_run_m20_ws", "eams_run_m20")
# plot_average_energy_graph("eams_run_m50_f_ns", "eams_run_m50_f","eams_run_m50_f_b2b_ns", "eams_run_m50_f_b2b_ws", "eams_run_m50_ns","eams_run_m50_ws", "eams_run_m50")

# plot_average_energy_graph("eams_run_f_ns.txt", "eams_run_f.txt","eams_run_f_b2b_ns_linobj.txt", "eams_run_f_b2b_ws_linobj.txt", "eams_run_ns.txt","eams_run_ws.txt", "avg_energy_kwh_all_f_b2b_linobj")
# plot_average_energy_graph("eams_run_m10_f_ns", "eams_run_m10_f","eams_run_m10_f_b2b_ns_linobj", "eams_run_m10_f_b2b_ws_linobj", "eams_run_m10_ns","eams_run_m10_ws", "eams_run_m10_f_b2b_linobj")
# plot_average_energy_graph("eams_run_m20_f_ns", "eams_run_m20_f","eams_run_m20_f_b2b_ns_linobj", "eams_run_m20_f_b2b_ws_linobj", "eams_run_m20_ns.txt","eams_run_m20_ws.txt", "eams_run_m20_f_b2b_linobj")
# plot_average_energy_graph("eams_run_m50_f_ns", "eams_run_m50_f","eams_run_m50_f_b2b_ns_linobj", "eams_run_m50_f_b2b_ws_linobj", "eams_run_m50_ns.txt","eams_run_m50_ws.txt", "eams_run_m50_f_b2b_linobj")
 
# plot_average_energy_graph("eams_run_m50_f_ns", "eams_run_m50_f","eams_run_m50_f_b2b_ns", "eams_run_m50_f_b2b_ws", "eams_run_m50_ns_90minsTL","eams_run_m50_ws_90minsTL", "eams_run_m50_HNHSquadObj_ONOS90minsTL")
# plot_average_energy_graph("eams_run_m50_f_ns", "eams_run_m50_f","eams_run_m50_f_b2b_ns_linobj", "eams_run_m50_f_b2b_ws_linobj", "eams_run_m50_ns_90minsTL","eams_run_m50_ws_90minsTL", "eams_run_m50_HNHSlinearObj_ONOS90minsTL")
# plot_average_energy_graph("eams_run_m50_f_ns", "eams_run_m50_f","eams_run_m50_f_b2b_ns", "eams_run_m50_f_b2b_ws", "eams_run_m50_ns_120minsTL","eams_run_m50_ws_120minsTL", "eams_run_m50_HNHSquadObj_ONOS120minsTL")
