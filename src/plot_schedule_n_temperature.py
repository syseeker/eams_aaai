from datetime import datetime
import numpy as np
import collections
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties
from matplotlib.dates import WEEKLY, DAILY, HOURLY, MINUTELY, rrulewrapper, RRuleLocator

def _getPlotRule(ptype):         
        if ptype == 0:
            return MINUTELY
        if ptype == 1:
            return HOURLY
        if ptype == 2:
            return DAILY
        if ptype == 3:
            return WEEKLY
        else:
            print "Unknown Plot Type. Set to default DAILY"
            return DAILY
        
        
def plot_airflow_roomsche_twingraph(logfile, hvac_sche, t, pinterval, pstep, room_asa):
    
    fig = plt.figure()   
    rsfig = fig.add_subplot(111)
    tfig = rsfig.twinx()
        
    ind = t # np.arange(len(room_sche[0]))    
    width = 0.02
#     num_room = len(room_sche)
    colors = ('r', 'g', 'b', 'y')
    t_labels = ('R1', 'R2', 'R3', 'R4')
    labels = ('R1', 'R2', 'R3', 'R4')
#     t_labels = ('LRLC', 'LRHC', 'HRLC', 'HRHC')
#     labels = ('LRLC', 'LRHC', 'HRLC', 'HRHC')
    
    inputd = []
    for i in xrange(len(hvac_sche)):        
        inputd.append(hvac_sche[i])        
    data = np.array(inputd)     
    bottom = np.vstack((np.zeros((data.shape[1],), dtype=data.dtype),
                        np.cumsum(data, axis=0)[:-1]))
    
    for dat, col, lab, bot in zip(data, colors, labels, bottom):
        plt.bar(ind, dat, width, color=col, label=lab, bottom=bot)
    
    for i in xrange(len(room_asa)):   
        tfig.plot(ind, room_asa[i], colors[i], label=t_labels[i])
    tfig.grid(True)
    tfig.set_ylabel("Air Flow Rate (kg/s)")
     
    rsfig.axes.set_yticks([])
    rsfig.set_xlabel("Scheduling Periods")
    rsfig.set_ylabel("HVAC Activation")
    
    handles, labels = tfig.get_legend_handles_labels()
    fontP = FontProperties()
    fontP.set_size('small')
    rsfig.legend(handles, labels, loc='best', prop=fontP)
           
    ymdhFmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
    rule_1 = rrulewrapper(_getPlotRule((int)(pinterval)), interval=(int)(pstep)) 
    loc_1 = RRuleLocator(rule_1)
    rsfig.xaxis.set_major_locator(loc_1)    
    rsfig.xaxis.set_major_formatter(ymdhFmt)
    datemin = datetime(min(t).year, min(t).month, min(t).day, min(t).hour, min(t).minute) 
    datemax = datetime(max(t).year, max(t).month, max(t).day, max(t).hour, max(t).minute)
    rsfig.set_xlim(datemin, datemax)  
     
    fig.autofmt_xdate()
     
    plt.savefig('Output\\'+ logfile +'_hvac_asa.png')
#     plt.show()
    plt.close(fig)
    print "Done!"
    
def plot_temperature_roomsche_twingraph(logfile, room_sche, t, pinterval, pstep, oat, room_zt, room_tsa):
    
    fig = plt.figure()   
#     tfig = fig.add_subplot(111)
#     rsfig = tfig.twinx()    
    rsfig = fig.add_subplot(111)
    tfig = rsfig.twinx()
        
    ind = t # np.arange(len(room_sche[0]))    
    width = 0.02
#     num_room = len(room_sche)
    colors = ('r', 'g', 'b', 'y')
    t_labels = ('R1', 'R2', 'R3', 'R4')
    labels = ('R1', 'R2', 'R3', 'R4')
#     t_labels = ('LRLC', 'LRHC', 'HRLC', 'HRHC')
#     labels = ('LRLC', 'LRHC', 'HRLC', 'HRHC')

    inputd = []
    for i in xrange(len(room_sche)):        
        inputd.append(room_sche[i])        
    data = np.array(inputd)     
    bottom = np.vstack((np.zeros((data.shape[1],), dtype=data.dtype),
                        np.cumsum(data, axis=0)[:-1]))
    
    for dat, col, lab, bot in zip(data, colors, labels, bottom):
        plt.bar(ind, dat, width, color=col, label=lab, bottom=bot)
    
    tfig.plot(ind, oat, 'k', label='Outdoor')
    for i in xrange(len(room_zt)):   
        tfig.plot(ind, room_zt[i], colors[i], label=t_labels[i])        
    tfig.plot(ind, [21]*len(ind), 'k--', label='Comfort Bounds')
    tfig.plot(ind, [23]*len(ind), 'k--')
    tfig.grid(True)
    tfig.set_ylabel("Temperature (Celcius)")
     
    rsfig.axes.set_yticks([])
    rsfig.set_xlabel("Scheduling Periods")
    rsfig.set_ylabel("# of Meetings")
    
    handles, labels = tfig.get_legend_handles_labels()
    fontP = FontProperties()
    fontP.set_size('small')
    rsfig.legend(handles, labels, ncol=2, loc='best', prop=fontP)
           
    ymdhFmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
    rule_1 = rrulewrapper(_getPlotRule((int)(pinterval)), interval=(int)(pstep)) 
    loc_1 = RRuleLocator(rule_1)
    rsfig.xaxis.set_major_locator(loc_1)    
    rsfig.xaxis.set_major_formatter(ymdhFmt)
    datemin = datetime(min(t).year, min(t).month, min(t).day, min(t).hour, min(t).minute) 
    datemax = datetime(max(t).year, max(t).month, max(t).day, max(t).hour, max(t).minute)
    rsfig.set_xlim(datemin, datemax)  
     
    fig.autofmt_xdate()
     
    plt.savefig('Output\\'+ logfile +'_temperature_ralloc.png')
#     plt.show()
    plt.close(fig)
    print "Done!"
        
def plotScheduleNTemp(fs, ft, start, end, pinterval, pstep):
            
    # Read schedule data
    if fs:
        fsstr = 'Output\\' + fs
        sche_data_file = open(fsstr, 'r')
        sche_data = ''.join(sche_data_file.readlines())
        sche_data_file.close()
        
    # Read temperature data
    if ft:
        ftstr = 'Output\\' + ft
        temperature_data_file = open(ftstr, 'r')
        temperature_data = ''.join(temperature_data_file.readlines())
        temperature_data_file.close()
    
    # Get timeslot information        
    if sche_data:
        sche_lines = sche_data.split('\n')
        slot_parts = sche_lines[0].split(",")
#         num_room = sche_lines[1] 
               
    if temperature_data:
        temperature_lines = temperature_data.split('\n')   
#         slot_parts = temperature_lines[0].split(",")
        oat_parts = temperature_lines[1].split(",")
    
    t = []    
    for i in xrange(len(slot_parts)):
        t.append(datetime.strptime(slot_parts[i], "%Y-%m-%d %H:%M:%S"))
        
    oat = []
    for i in xrange(len(oat_parts)):
        oat.append(float(oat_parts[i]))
        
    sidx = -1
    eidx = -1
    s = datetime.strptime(start, "%Y-%m-%d %H:%M")
    e = datetime.strptime(end, "%Y-%m-%d %H:%M")    
    for ridx, x in enumerate(t):
        if x == s:
            sidx = ridx
        if x == e:
            eidx = ridx
             
    if sidx == -1 or eidx == -1:
        print "Error, start and end out of range!"
        
#     print sidx, " ", eidx
           
    room_vz = []
    room_vw = []    
    for i in xrange(2, len(sche_lines)-1, 2):
        
        #Options: select either one
#         tmp_vz = [int(x) for x in sche_lines[i].split(",")]
        tmp_vz = [int(x)*3 for x in sche_lines[i].split(",")]
        room_vz.append(tmp_vz[sidx:eidx])
        
        #Options: select either one
#         tmp_vw = [int(x) for x in sche_lines[i+1].split(",")]  
        
        #TODO:  BP! Uncomment this for "with standby mode", and comment this for "no standby mode"      
        tmp_vw = [float(x)/10 for x in sche_lines[i+1].split(",")]
        room_vw.append(tmp_vw[sidx:eidx])
         
        
        
    room_zt = []
    room_tsa = []
    room_asa = []
    for i in xrange(3, len(temperature_lines)-1, 3):        
        tmp_zt = [float(x) for x in temperature_lines[i].split(",")]
        tmp_tsa = [float(x) for x in temperature_lines[i+1].split(",")]
        tmp_asa = [float(x) for x in temperature_lines[i+2].split(",")]         
        room_zt.append(tmp_zt[sidx:eidx])
        room_tsa.append(tmp_tsa[sidx:eidx])  
        room_asa.append(tmp_asa[sidx:eidx])
        
    plot_temperature_roomsche_twingraph(fs, room_vz, t[sidx:eidx], pinterval, pstep, oat[sidx:eidx], room_zt, room_tsa)
     #TODO:  BP! Uncomment this for "with standby mode", and comment this for "no standby mode"  
    plot_airflow_roomsche_twingraph(fs, room_vw, t[sidx:eidx], pinterval, pstep, room_asa)
                
    
# plotScheduleNTemp("eams_meeting_test_schedules", "eams_meeting_test_temperatures", "2013-01-07 00:00", "2013-01-12 00:30", 1, 8)
# plotScheduleNTemp("eams_meeting_m20_07_716000_0_ws_schedules", "eams_meeting_m20_07_716000_0_ws_temperatures", "2013-01-07 08:00", "2013-01-09 00:30", 1, 8)

# plotScheduleNTemp("eams_LRHC_WN_mwd_w_schedules", "eams_LRHC_WN_mwd_w_temperatures", "2013-06-26 18:00", "2013-06-28 00:30", 1, 1)


# plotScheduleNTemp("eams_meeting_m50_07_944000_7_m_ns_f_b2b_schedules", "eams_meeting_m50_07_944000_7_m_ns_f_b2b_temperatures", "2013-01-10 00:00", "2013-01-11 00:00", 2, 1)
# plotScheduleNTemp("eams_meeting_m20_07_886000_7_ns_f_b2b_schedules", "eams_meeting_m20_07_886000_7_ns_f_b2b_temperatures", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)
# plotScheduleNTemp("eams_meeting_m20_07_716000_0_ns_f_b2b_schedules", "eams_meeting_m20_07_716000_0_ns_f_b2b_temperatures", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)
# plotScheduleNTemp("eams_meeting_m20_07_838000_5_ns_f_b2b_schedules", "eams_meeting_m20_07_838000_5_ns_f_b2b_temperatures", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)
# plotScheduleNTemp("eams_meeting_m10_04_694000_4_ns_f_b2b_schedules", "eams_meeting_m10_04_694000_4_ns_f_b2b_temperatures", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)
# plotScheduleNTemp("eams_meeting_m10_04_905000_9_ns_f_b2b_schedules", "eams_meeting_m10_04_905000_9_ns_f_b2b_temperatures", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)
# plotScheduleNTemp("eams_meeting_m10_04_186000_4_ns_f_b2b_schedules", "eams_meeting_m10_04_186000_4_ns_f_b2b_temperatures", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)

# plotScheduleNTemp("eams_LRHC_WN_m7_w_schedules", "eams_LRHC_WN_m7_w_temperatures", "2013-06-26 00:00", "2013-06-28 00:00", 1, 2)
# plotScheduleNTemp("eams_LRHC_WN_m2_w_schedules", "eams_LRHC_WN_m2_w_temperatures", "2013-06-26 00:00", "2013-06-28 00:00", 1, 2)

# plotScheduleNTemp("eams_meeting_m50_07_944000_7_m_ws_f_b2b_schedules", "eams_meeting_m50_07_944000_7_m_ws_f_b2b_temperatures", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)
# plotScheduleNTemp("eams_meeting_m20_07_707000_0_ws_f_b2b_schedules", "eams_meeting_m20_07_707000_0_ws_f_b2b_temperatures", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)

# plotScheduleNTemp("eams_meeting_m10_04_186000_4_ws_schedules", "eams_meeting_m10_04_186000_4_ws_temperatures", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)
# plotScheduleNTemp("eams_meeting_m10_04_694000_4_ws_schedules", "eams_meeting_m10_04_694000_4_ws_temperatures", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)

# plotScheduleNTemp("eams_meeting_m50_07_944000_1_m_ws_f_b2b_schedules", "eams_meeting_m50_07_944000_1_m_ws_f_b2b_temperatures", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)
# plotScheduleNTemp("eams_meeting_m50_07_807000_3_m_ws_f_b2b_schedules", "eams_meeting_m50_07_807000_3_m_ws_f_b2b_temperatures", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)

# plotScheduleNTemp("eams_LRHC_WN_m1_5d_schedules", "eams_LRHC_WN_m1_5d_temperatures", "2013-01-06 00:00", "2013-01-11 00:00", 2, 1)

# plotScheduleNTemp("eams_meeting_m10_04_227000_2_ws_f_b2b_schedules", "eams_meeting_m10_04_227000_2_ws_f_b2b_temperatures", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)
# plotScheduleNTemp("eams_meeting_m10_04_227000_2_ws_f_b2b_schedules_qobj", "eams_meeting_m10_04_227000_2_ws_f_b2b_temperatures_qobj", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)

# plotScheduleNTemp("eams_meeting_m50_07_738000_0_ws_f_b2b_schedules", "eams_meeting_m50_07_738000_0_ws_f_b2b_temperatures", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)
# plotScheduleNTemp("eams_meeting_m50_07_738000_0_ws_f_b2b_schedules_qobj", "eams_meeting_m50_07_738000_0_ws_f_b2b_temperatures_qobj", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)


# plotScheduleNTemp("eams_meeting_m50_07_944000_7_m_ws_schedules", "eams_meeting_m50_07_944000_7_m_ws_temperatures", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)
# plotScheduleNTemp("eams_meeting_m50_07_944000_7_m_ns_schedules", "eams_meeting_m50_07_944000_7_m_ns_temperatures", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)


# plotScheduleNTemp("eams_meeting_m50_07_807000_3_ws_schedules", "eams_meeting_m50_07_807000_3_ws_temperatures", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)
# plotScheduleNTemp("eams_meeting_m50_07_807000_3_ns_schedules", "eams_meeting_m50_07_807000_3_ns_temperatures", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)
# 
# plotScheduleNTemp("eams_meeting_m50_07_738000_5_ws_schedules", "eams_meeting_m50_07_738000_5_ws_temperatures", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)
# plotScheduleNTemp("eams_meeting_m50_07_738000_5_ns_schedules", "eams_meeting_m50_07_738000_5_ns_temperatures", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)

# plotScheduleNTemp("eams_meeting_m10_04_227000_2_ns_schedules", "eams_meeting_m10_04_227000_2_ns_temperatures", "2013-01-07 00:00", "2013-01-12 00:00", 2, 1)

