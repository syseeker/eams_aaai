import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np
  
   
def plot_average_energy_graph(fconv, fnslog, fwslog, fb2bnslog, fb2bwslog, nslog, wslog, figfile):
    
    total_energy_kWh_conv = 0
    total_energy_kWh_fns = 0
    total_energy_kWh_fws = 0
    total_energy_kWh_fb2bns = 0
    total_energy_kWh_fb2bws = 0    
    total_energy_kWh_ns = 0
    total_energy_kWh_ws = 0
    
    # Conventional HVAC - On in all four rooms 9-5 for 5 days
    fstr = 'Output\\' + fconv      
    data_file = open(fstr, 'r')
    data = ''.join(data_file.readlines())
    data_file.close()
     
    lines = data.split('\n')
    for i in xrange(len(lines)-1):
        line = lines[i]
        parts = line.split()
        total_energy_kWh_conv += float(parts[3])
    avg_conv = total_energy_kWh_conv/(len(lines)-1)
       
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
         
#     perc_f_ns = (avg_conv-avg_fns)/avg_conv*100
#     perc_f_ws = (avg_conv-avg_fws)/avg_conv*100
#     perc_fb2bns = (avg_conv-avg_fb2bns)/avg_conv*100
#     perc_fb2bws = (avg_conv-avg_fb2bws)/avg_conv*100
#     perc_ns = (avg_conv-avg_ns)/avg_conv*100
#     perc_ws = (avg_conv-avg_ws)/avg_conv*100
    
    perc_f_ns = (avg_fns)/avg_conv*100
    perc_f_ws = (avg_fws)/avg_conv*100
    perc_fb2bns = (avg_fb2bns)/avg_conv*100
    perc_fb2bws = (avg_fb2bws)/avg_conv*100
    perc_ns = (avg_ns)/avg_conv*100
    perc_ws = (avg_ws)/avg_conv*100
    
#     print len(lines)-1
    print total_energy_kWh_conv
    print total_energy_kWh_fns
    print total_energy_kWh_fws
    print total_energy_kWh_fb2bns
    print total_energy_kWh_fb2bws
    print total_energy_kWh_ns    
    print total_energy_kWh_ws
    
    print " "
    print avg_conv
    print avg_fns
    print avg_fws
    print avg_fb2bns
    print avg_fb2bws
    print avg_ns
    print avg_ws
    
    print " "
    print perc_f_ns
    print perc_f_ws
    print perc_fb2bns
    print perc_fb2bws
    print perc_ns
    print perc_ws
    
    #         
    fig, ax = plt.subplots()    
    ind = np.arange(1)  
    width = 0.4       # the width of the bars
    space = 0.1
    
#     colors = ['#73da4a', '#1a95d0', '#eba2ea', '#858585', '#c6dd5a', '#e1b76b', '#e5887d', '#e88fb6', '#eba2ea', '#d1b5ef', '#c8cbf2','#B8B8B8', '#8A8A8A']
    #     colors = ['#a50026', '#d73027', '#f46d43', '#fdae61', '#fee090', '#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695']
    colors = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c', '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a']

#  PhD Seminar
    rects6 = ax.bar(ind, avg_ws, width, color=colors[0], label='Optimal, With Standby Mode (OS)')        # Optimal Schedule with Standby
    rects5 = ax.bar(ind+(0.9*width)+(0.9*space), avg_ns, width, color=colors[1], label='Optimal, No Standby Mode (ON)')        # Optimal Schedule without Standby
    rects4 = ax.bar(ind+(2*width)+(2*space), avg_fb2bws, width, color=colors[2], label='Heuristic, With Standby Mode (HS)')    # Fixed Back-to-Back Schedule with Standby
    rects3 = ax.bar(ind+(2.9*width)+(2.9*space), avg_fb2bns, width, color=colors[3], label='Heuristic, No Standby Mode (HN)')            # Fixed Back-to-Back Schedule without Standby    
    rects2 = ax.bar(ind+(4*width)+(4*space), avg_fws, width, color=colors[4], label='Arbitrary, With Standby Mode (AS)')                             # Fixed Schedule with Standby
    rects1 = ax.bar(ind+(4.9*width)+(4.9*space), avg_fns, width, color=colors[5], label='Arbitrary, No Standby Mode (AN)')                             # Fixed Schedule with No Standby
    rects7 = ax.bar(ind+(6*width)+(6*space), avg_conv, width, color=colors[6], label='Current Practice (CO)')    # Conventional

    
    # Sylvie presentation - with conv
#     rects6 = ax.bar(ind, avg_ws, width, color=colors[0], label='Our Approach')
#     rects3 = ax.bar(ind+width+space, avg_fb2bns, width, color=colors[1], label='State of the Art')
#     rects1 = ax.bar(ind+(2*width)+(2*space), avg_fns, width, color=colors[2], label='Pure HVAC Control')   
#     rects7 = ax.bar(ind+(3*width)+(3*space), avg_conv, width, color=colors[3], label='Current Practice')
    
#     rects6 = ax.bar(ind, avg_ws, width, color='#ffffff', label='OS')        # Optimal Schedule with Standby
#     rects5 = ax.bar(ind+width+space, avg_ns, width, color='#e0e0e0', label='ON')        # Optimal Schedule without Standby
#     rects4 = ax.bar(ind+(2*width)+(2*space), avg_fb2bws, width, color='#c2c2c2', label='HS')    # Fixed Back-to-Back Schedule with Standby
#     rects3 = ax.bar(ind+(3*width)+(3*space), avg_fb2bns, width, color='#a3a3a3', label='HN')            # Fixed Back-to-Back Schedule without Standby    
#     rects2 = ax.bar(ind+(4*width)+(4*space), avg_fws, width, color='#858585', label='AS')                             # Fixed Schedule with Standby
#     rects1 = ax.bar(ind+(5*width)+(5*space), avg_fns, width, color='#666666', label='AN')                             # Fixed Schedule with No Standby
#     rects7 = ax.bar(ind+(6*width)+(6*space), avg_conv, width, color='#ffffff', label='CN')    # Conventional
       
    
    # AAAI presentation
#     rects1 = ax.bar(ind, avg_fns, width, color='#666666', label='Arbitrary')  
#     rects3 = ax.bar(ind+width+space, avg_fb2bns, width, color='#a3a3a3', label='Heuristic')
#     rects6 = ax.bar(ind+(2*width)+(2*space), avg_ws, width, color='#ffffff', label='Optimal') 
    
#     print ind
#     rects1 = ax.bar(ind, avg_fns, width, color='#666666', label='AN')                             # Fixed Schedule with No Standby
#     rects2 = ax.bar(ind+width+space, avg_fws, width, color='#858585', label='AS')                             # Fixed Schedule with Standby
#     rects3 = ax.bar(ind+(2*width)+(2*space), avg_fb2bns, width, color='#a3a3a3', label='HN')            # Fixed Back-to-Back Schedule without Standby
#     rects4 = ax.bar(ind+(3*width)+(3*space), avg_fb2bws, width, color='#c2c2c2', label='HS')    # Fixed Back-to-Back Schedule with Standby
#     rects5 = ax.bar(ind+(4*width)+(4*space), avg_ns, width, color='#e0e0e0', label='ON')        # Optimal Schedule without Standby
#     rects6 = ax.bar(ind+(5*width)+(5*space), avg_ws, width, color='#ffffff', label='OS')        # Optimal Schedule with Standby

    handles, labels = ax.get_legend_handles_labels()
    fontP = FontProperties()
    fontP.set_size('large')
    ax.legend(handles, labels, loc='upper left', prop=fontP)   
    
      
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
            ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., '%.1f%%'%(perc_fb2bns),
                    ha='center', va='bottom', weight='semibold', fontsize=12)
        elif index == 3:
            ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., '%.1f%%'%(perc_fb2bws),
                    ha='center', va='bottom', weight='semibold', fontsize=12)
        elif index == 4:
            ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., '%.1f%%'%(perc_ns),
                    ha='center', va='bottom', weight='semibold', fontsize=12)
        elif index == 5:
            ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., '%.1f%%'%(perc_ws),
                    ha='center', va='bottom', weight='semibold', fontsize=12)
#             ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., 'Baseline',
#                     ha='center', va='bottom', weight='semibold', fontsize=12)            
        elif index == 6:
            ax.text(rect.get_x()+rect.get_width()/2., rect.get_y()+rect.get_height()/2., 'Baseline',
                    ha='center', va='bottom', weight='semibold', fontsize=12)
                    
    autolabel(rects1,0)
    autolabel(rects2,1)
    autolabel(rects3,2)
    autolabel(rects4,3)
    autolabel(rects5,4)
    autolabel(rects6,5)
    autolabel(rects7,6)
    
    plt.tight_layout()
    
    plt.savefig('Output\\phdseminar_'+ figfile +'.png', dpi=400)
#     plt.savefig('Output\\new_'+ figfile +'.png', dpi=400)
# #     plt.show()
    plt.close(fig)
    
#     Image.open('Output\\'+ figfile +'.png').convert('L').save('Output\\'+ figfile +'_grey.png')
        
    print "Done!"
    
    


plot_average_energy_graph("eams_run_conventional1", "eams_run_f_ns.txt", "eams_run_f.txt","eams_run_f_b2b_ns.txt", "eams_run_f_b2b_ws.txt", "eams_run_ns.txt","eams_run_ws.txt", "avg_energy_kwh_all")
