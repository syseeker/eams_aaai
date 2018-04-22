import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np
  
   
def plot_average_energy_graph(canslog, conslog, cowslog, fnslog, fwslog, fb2bnslog, fb2bwslog, nslog, wslog, figfile):
    
    total_energy_kWh_cans = 0
    total_energy_kWh_cons = 0
    total_energy_kWh_cows = 0    
    total_energy_kWh_fns = 0
    total_energy_kWh_fws = 0
    total_energy_kWh_fb2bns = 0
    total_energy_kWh_fb2bws = 0    
    total_energy_kWh_ns = 0
    total_energy_kWh_ws = 0
       
    # Conventional arbitrary with No Standby Schedule
    fstr = 'Output\\' + canslog      
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()
     
    lines = data.split('\n')
    for i in xrange(len(lines)-1):
        line = lines[i]
        parts = line.split()
        total_energy_kWh_cans += float(parts[3])
    avg_cans = total_energy_kWh_cans/(len(lines)-1)
    
    # Conventional optimal with No Standby Schedule
    fstr = 'Output\\' + conslog      
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()
     
    lines = data.split('\n')
    for i in xrange(len(lines)-1):
        line = lines[i]
        parts = line.split()
        total_energy_kWh_cons += float(parts[3])
    avg_cons = total_energy_kWh_cons/(len(lines)-1)
    
    # Conventional optimal then  Standby Schedule
    fstr = 'Output\\' + cowslog      
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()
     
    lines = data.split('\n')
    for i in xrange(len(lines)-1):
        line = lines[i]
        parts = line.split()
        total_energy_kWh_cows += float(parts[3])
    avg_cows = total_energy_kWh_cows/(len(lines)-1)
    
    # Fixed with No Standby Schedule
    fstr = 'Output\\' + fnslog      
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
    fstr = 'Output\\' + fwslog      
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
    fstr = 'Output\\' + fb2bnslog      
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
    fstr = 'Output\\' + fb2bwslog      
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
    fstr = 'Output\\' + nslog      
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
    fstr = 'Output\\' + wslog      
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()
     
    lines = data.split('\n')
    for i in xrange(len(lines)-1):
        line = lines[i]
        parts = line.split()
        total_energy_kWh_ws += float(parts[3])
    avg_ws = total_energy_kWh_ws/(len(lines)-1)    
         
    # baseline is ws
    perc_cans_ws = (avg_cans-avg_ws)/avg_ws*100
    perc_cons_ws = (avg_cons-avg_ws)/avg_ws*100
    perc_cows_ws = (avg_cows-avg_ws)/avg_ws*100
    perc_f_ns = (avg_fns-avg_ws)/avg_ws*100
    perc_f_ws = (avg_fws-avg_ws)/avg_ws*100
    perc_fb2bns_ws = (avg_fb2bns-avg_ws)/avg_ws*100
    perc_fb2bws_ws = (avg_fb2bws-avg_ws)/avg_ws*100
    perc_ns_ws = (avg_ns-avg_ws)/avg_ws*100
    
    # baseline is cans, ignore variable naming    
#     perc_cons_ws = (avg_cons-avg_cans)/avg_cans*100
#     perc_cows_ws = (avg_cows-avg_cans)/avg_cans*100
#     perc_f_ns = (avg_fns-avg_cans)/avg_cans*100
#     perc_f_ws = (avg_fws-avg_cans)/avg_cans*100
#     perc_fb2bns_ws = (avg_fb2bns-avg_cans)/avg_cans*100
#     perc_fb2bws_ws = (avg_fb2bws-avg_cans)/avg_cans*100
#     perc_ns_ws = (avg_ns-avg_cans)/avg_cans*100
#     perc_cans_ws = (avg_ws-avg_cans)/avg_cans*100
    
    print len(lines)-1
    print total_energy_kWh_cans
    print total_energy_kWh_cons
    print total_energy_kWh_cows
    print total_energy_kWh_fns
    print total_energy_kWh_fws
    print total_energy_kWh_fb2bns
    print total_energy_kWh_fb2bws
    print total_energy_kWh_ns    
    print total_energy_kWh_ws
    
    print " "
    print avg_cans
    print avg_cons
    print avg_cows
    print avg_fns
    print avg_fws
    print avg_fb2bns
    print avg_fb2bws
    print avg_ns
    print avg_ws
    
    print " "
    print perc_cans_ws
    print perc_cons_ws
    print perc_cows_ws
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
    
#     print ind
    rects1 = ax.bar(ind, avg_cans, width, color='#1D1D1D', label='CAN')                          # Conventional arbitrary with No Standby Schedule
    rects2 = ax.bar(ind+width+space, avg_cons, width, color='#313131', label='CON')                          # Conventional optimal with No Standby Schedule
    rects3 = ax.bar(ind+(2*width)+(2*space), avg_cows, width, color='#484848', label='COS')                          # Conventional optimal then with Standby Schedule
    rects4 = ax.bar(ind+(3*width)+(3*space), avg_fns, width, color='#616161', label='AN')                             # Fixed Schedule with No Standby
    rects5 = ax.bar(ind+(4*width)+(4*space), avg_fws, width, color='#7B7B7B', label='AS')                             # Fixed Schedule with Standby
    rects6 = ax.bar(ind+(5*width)+(5*space), avg_fb2bns, width, color='#959595', label='HN')            # Fixed Back-to-Back Schedule without Standby
    rects7 = ax.bar(ind+(6*width)+(6*space), avg_fb2bws, width, color='#AFAFAF', label='HS')    # Fixed Back-to-Back Schedule with Standby
    rects8 = ax.bar(ind+(7*width)+(7*space), avg_ns, width, color='#CACACA', label='ON')        # Optimal Schedule without Standby
    rects9 = ax.bar(ind+(8*width)+(8*space), avg_ws, width, color='#E5E5E5', label='OS')        # Optimal Schedule with Standby

    handles, labels = ax.get_legend_handles_labels()
    fontP = FontProperties()
    fontP.set_size(12)
    ax.legend(handles, labels, loc='upper right', prop=fontP)   
    
      
#     ax.set_xticks(ind+width)  
#     ax.set_xticklabels() 
    ax.axes.get_xaxis().set_visible(False)
    ax.set_ylabel("Average Energy Consumption (kWh)") 
    ax.set_ylim([0,650])
    
    
    def autolabel(rects, index):
        for rect in rects:            
            height = rect.get_height()
            if height >= 1:
                ax.text(rect.get_x()+rect.get_width()/2., 1.01*height, '%d'%(int(height)),
                    ha='center', va='bottom', fontsize=10)
                
        if index == 0:
#             ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., 'Baseline',
#                     ha='center', va='bottom', weight='semibold', fontsize=10, color='white')
            ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., '%.1f%%'%(perc_cans_ws),
                    ha='center', va='bottom', weight='semibold', fontsize=10, color='white')        
        elif index == 1:
            ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., '%.1f%%'%(perc_cons_ws),
                    ha='center', va='bottom', weight='semibold', fontsize=10, color='white')
        elif index == 2:
            ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., '%.1f%%'%(perc_cows_ws),
                    ha='center', va='bottom', weight='semibold', fontsize=10, color='white')
        elif index == 3:
            ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., '%.1f%%'%(perc_f_ns),
                    ha='center', va='bottom', weight='semibold', fontsize=10)        
        elif index == 4:
            ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., '%.1f%%'%(perc_f_ws),
                    ha='center', va='bottom', weight='semibold', fontsize=10)
        elif index == 5:
            ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., '%.1f%%'%(perc_fb2bns_ws),
                    ha='center', va='bottom', weight='semibold', fontsize=10)
        elif index == 6:
            ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., '%.1f%%'%(perc_fb2bws_ws),
                    ha='center', va='bottom', weight='semibold', fontsize=10)
        elif index == 7:
            ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., '%.1f%%'%(perc_ns_ws),
                    ha='center', va='bottom', weight='semibold', fontsize=10)
        elif index == 8:
#             ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., '%.1f%%'%(perc_cans_ws),
#                     ha='center', va='bottom', weight='semibold', fontsize=10)
            ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., 'Baseline',
                    ha='center', va='bottom', weight='semibold', fontsize=10)
                    
    autolabel(rects1,0)
    autolabel(rects2,1)
    autolabel(rects3,2)
    autolabel(rects4,3)
    autolabel(rects5,4)
    autolabel(rects6,5)
    autolabel(rects7,6)
    autolabel(rects8,7)
    autolabel(rects9,8)
    
#     plt.savefig('Output\\'+ figfile +'.png', dpi=400)
    plt.show()
#     plt.close(fig)
    
        
    print "Done!"
    
    


plot_average_energy_graph("eams_run_ns_conv_arb.txt", "eams_run_ns_conv_opt.txt", "eams_run_ns_conv_opt_then_standby.txt", "eams_run_f_ns.txt", "eams_run_f.txt","eams_run_f_b2b_ns.txt", "eams_run_f_b2b_ws.txt", "eams_run_ns.txt","eams_run_ws.txt", "avg_energy_kwh_all_ws_baseline")




