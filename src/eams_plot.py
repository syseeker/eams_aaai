
import logging
from string import split
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from matplotlib.font_manager import FontProperties
from matplotlib.dates import WEEKLY, DAILY, HOURLY, MINUTELY, rrulewrapper, RRuleLocator

class GraphPlot:
    def __init__(self):
        pass
    
    def _getPlotRule(self, ptype):         
        if ptype == 0:
            return MINUTELY
        if ptype == 1:
            return HOURLY
        if ptype == 2:
            return DAILY
        if ptype == 3:
            return WEEKLY
        else:
            logging.error("Unknown Plot Type. Set to default DAILY")
            return DAILY
    
    def plotTemperature(self, cfg_idx, pinterval, pstep, rname, rcfg, mcfg, oatdat, pcfg, 
                        Tinit, Toccmin, Toccmax, aSA, TSAoccmin, TSAoccmax,
                        zt, oat, tsa, ra):

        t = zt.get('Time')
        ZT = zt.get('Celcius')
        OT = oat.values()
        TSA = tsa.get('Celcius')
       
#         years    = mdates.YearLocator()   # every year
#         months   = mdates.MonthLocator()  # every month
#         days    = mdates.DayLocator()     # every day
#         hours = mdates.HourLocator()      # every hour      
#         minutes = mdates.MinuteLocator()  # every minute  
#         yearsFmt = mdates.DateFormatter('%Y')
#         hoursFmt = mdates.DateFormatter('%H')
        ymdhFmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
        
        fig = plt.figure()   
        rafig = fig.add_subplot(211)
        ztfig = fig.add_subplot(212)
        
        rafig.set_title('Room Name: [' + rname + ']\nRoomConfig: ' + rcfg + " \nMeetingsConfig: " + mcfg + " \nOutdoorTemp: " + oatdat + "\nConfig: " + pcfg, fontsize=12)
        rafig.plot(t, ra)        
        rafig.set_ylabel("Meeting #",fontsize=12)
        rafig.set_yticks((min(ra), max(ra), 1))
        
        ztfig.set_title('Initial Temp: [' + str(Tinit) + 'C]\nZone Temp Bound: [' + str(Toccmin) + 'C $\leq$ T $\leq$ ' + str(Toccmax) +'C]\nMass Air Flow: [' + str(aSA) + ' kg/s]\nSupply Air Temperature Bound: [' + str(TSAoccmin) + 'C $\leq$ T $\leq$ ' + str(TSAoccmax) + 'C]', fontsize=12)
        ztfig.plot(t, ZT, 'b-', label='Zone Temperature')    
        ztfig.plot(t, OT, 'r-', label='Outdoor Temperature')
        ztfig.plot(t, TSA, 'g-', label='Supply Air Temperature')
        handles, labels = ztfig.get_legend_handles_labels()
        fontP = FontProperties()
        fontP.set_size('small')
        ztfig.legend(handles, labels, loc='best', prop=fontP)        
        ztfig.set_xlabel("Scheduling Period",fontsize=12)
        ztfig.set_ylabel("Celcius",fontsize=12)
        # format the ticks
#         rule = rrulewrapper(DAILY, interval=1)
#         rule = rrulewrapper(HOURLY, interval=30)
#         rule = rrulewrapper(MINUTELY, interval=30)
#         rule_1 = rrulewrapper(HOURLY, interval=30)
        rule_1 = rrulewrapper(self._getPlotRule((int)(pinterval)), interval=(int)(pstep)) 
#         rule_2 = rrulewrapper(DAILY, interval=1)     
        loc_1 = RRuleLocator(rule_1)
#         loc_2 = RRuleLocator(rule_2)
        ztfig.xaxis.set_major_locator(loc_1)
        ztfig.xaxis.set_major_formatter(ymdhFmt)
#         ztfig.xaxis.set_minor_locator(loc_2)        
        datemin = datetime(min(t).year, min(t).month, min(t).day, min(t).hour, min(t).minute) 
        datemax = datetime(max(t).year, max(t).month, max(t).day, max(t).hour, max(t).minute)
        ztfig.set_xlim(datemin, datemax)        
        # format the coords message box
        def temperature(x): return '$%1.2f'%x
        ztfig.format_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M')
        ztfig.format_ydata = temperature
        ztfig.grid(True)
        
        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()
        plt.tight_layout()
        
        plt.savefig('Output\\'+ str(cfg_idx) + '_' + datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f') +'.png')        
#         plt.show()  
        plt.close(fig)
        
    def plotTemperatureNEnergy(self, cfg_idx, pinterval, pstep, rname, rcfg, mcfg, oatdat, pcfg, 
                        Tinit, Toccmin, ToccminRange, Toccmax, ToccRange, aSAmin, aSAmax, TSAoccmin, TSAoccmax,
                        zt, oat, ra, tsa, 
                        efan, econd, eheat, 
                        pfan, pcond, pheat, 
                        efankWh, econdkWh, eheatkWh,
                        ptotal, etotal):                                   
        
        t = zt.get('Time')
        ZT = zt.get('Celcius')
        OT = oat.values()
        TSA = tsa.get('Celcius')
        op_fan = efan.get('kWh')
        op_cond = econd.get('kWh') 
        op_heat = eheat.get('kWh')
        
        ymdhFmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
        
        fig = plt.figure()   
#         rafig = fig.add_subplot(311)
        ztfig = fig.add_subplot(211)
        efig = fig.add_subplot(212)
        
#         rafig.set_title('Room Name: [' + rname + ']\nRoomConfig: ' + rcfg + " \nMeetingsConfig: " + mcfg + " \nOutdoorTemp: " + oatdat + "\nConfig: " + pcfg, fontsize=12)
#         rafig.plot(t, ra)        
#         rafig.set_ylabel("Meeting #",fontsize=12)
#         rafig.set_yticks((min(ra), max(ra), 1))
                
        ztfig.set_title('Room Name: [' + rname + ']\nRoomConfig: ' + rcfg + " \nMeetingsConfig: " + 
                        mcfg + " \nOutdoorTemp: " + oatdat + "\nInitial Temp: [" + str(Tinit) + 'C]\n Occ Zone Temp Bound: [' +
                        str(Toccmin+ToccminRange) + 'C $\leq$ T $\leq$ ' + str(Toccmax-ToccRange) + ']\n UnOcc Zone Temp Bound: [' +
                        str(Toccmin) + 'C $\leq$ T $\leq$ ' + str(Toccmax) +
                        'C]\nSupply Air Temperature Bound: [' + str(TSAoccmin) + 'C $\leq$ T $\leq$ ' + str(TSAoccmax) + 'C]', fontsize=12)
        ztfig.plot(t, ZT, 'b-', label='Zone Temperature')    
        ztfig.plot(t, OT, 'r-', label='Outdoor Temperature')
        ztfig.plot(t, TSA, 'g-', label='Supply Air Temperature')
        ztfig_handles, ztfig_labels = ztfig.get_legend_handles_labels()
#         ztfig.legend(ztfig_handles, ztfig_labels, loc='best', prop=ztfig_fontP)        
        ztfig.set_xlabel("Scheduling Period",fontsize=12)
        ztfig.set_ylabel("Celcius",fontsize=12)
        
        ztfig_fontP = FontProperties()
        ztfig_fontP.set_size('small')
#         ztfig.legend(ztfig_handles, ztfig_labels, loc='best', prop=ztfig_fontP)        
        # Shink current axis's height by 10% on the bottom
        box = ztfig.get_position()
        ztfig.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
        # Put a legend below current axis
        ztfig.legend(loc='upper center', bbox_to_anchor=(0.5, -0.001), fancybox=True, shadow=True, ncol=5, prop=ztfig_fontP)
        
        ztfig_rule_1 = rrulewrapper(self._getPlotRule((int)(pinterval)), interval=(int)(pstep)) 
        ztfig_loc_1 = RRuleLocator(ztfig_rule_1)
        ztfig.xaxis.set_major_locator(ztfig_loc_1)
        ztfig.xaxis.set_major_formatter(ymdhFmt)
        ztfig_datemin = datetime(min(t).year, min(t).month, min(t).day, min(t).hour, min(t).minute) 
        ztfig_datemax = datetime(max(t).year, max(t).month, max(t).day, max(t).hour, max(t).minute)
        ztfig.set_xlim(ztfig_datemin, ztfig_datemax)        

        efig.set_title("\nTotal Fan Power: " + str(round(pfan,2)) + " kW, Fan Energy: " + str(round(efankWh,2)) + " kWh" +
                        "\nTotal Cooling Power:" + str(round(pcond,2)) + " kW, Cooling Energy: " + str(round(econdkWh,2)) + " kWh" +
                        "\nTotal Heating Power:" + str(round(pheat,2)) + " kW, Heating Energy: " + str(round(eheatkWh,2)) + " kWh" + 
                        "\nTotal Power Consumption:" + str(round(ptotal,2)) + " kW, Total Energy:" + str(round(etotal,2)) + " kWh", fontsize=12)        
        efig.plot(t, op_fan, '-', label='Fan')    
        efig.plot(t, op_cond, '-*', label='Cooling')
        efig.plot(t, op_heat, '-+', label='Heating')
        efig_handles, efig_labels = efig.get_legend_handles_labels()
        efig_fontP = FontProperties()
        efig_fontP.set_size('small')
        efig.legend(efig_handles, efig_labels, loc='best', prop=efig_fontP)        
        efig.set_xlabel("Scheduling Period",fontsize=12)
        efig.set_ylabel("Energy Consumption (kWh)",fontsize=12)        
        efig_rule_1 = rrulewrapper(self._getPlotRule((int)(pinterval)), interval=(int)(pstep)) 
        efig_loc_1 = RRuleLocator(efig_rule_1)
        efig.xaxis.set_major_locator(efig_loc_1)
        efig.xaxis.set_major_formatter(ymdhFmt)
        efig_datemin = datetime(min(t).year, min(t).month, min(t).day, min(t).hour, min(t).minute) 
        efig_datemax = datetime(max(t).year, max(t).month, max(t).day, max(t).hour, max(t).minute)
        efig.set_xlim(efig_datemin, efig_datemax)   
        
        fig.autofmt_xdate()
        plt.tight_layout()
        
        plt.savefig('Output\\'+ str(cfg_idx) + '_TemperatureEnergy_' + rname + "_"  + datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f') +'.png')        
#         plt.show()   
        plt.close(fig)
        
    def plotTemperatureNAirMass(self, cfg_idx, pinterval, pstep, rname, cfg, rcfg, mcfg, oatdat, pcfg, 
                        Tinit, Toccmin, ToccminRange, Toccmax, ToccRange, aSAmin, aSAmax, TSAoccmin, TSAoccmax,
                        zt, oat, ra, tsa, asa):
        
        
        t = zt.get('Time')
        ZT = zt.get('Celcius')
        OT = oat.values()
        TSA = tsa.get('Celcius')
        ASA = asa.get('Kg/s')
        ASA_UB = list()
        ASA_UB[0:len(t)] = [aSAmax]*(len(t))
                
        maxZT = float(max(ZT))
        maxOT = float(max(OT))
        maxTSA = float(max(TSA))
        maxT = max([maxZT, maxOT, maxTSA])
        ymdhFmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
        
        fig = plt.figure()   
        ztfig = fig.add_subplot(211)
        afig = fig.add_subplot(212)
                        
        ztfig.set_title('Room Name: [' + rname + ']\nProbConfig:' + cfg + '\nRoomConfig: ' + rcfg + " \nMeetingsConfig: " + 
                        mcfg + " \nOutdoorTemp: " + oatdat + 
                        "\n\nInitial Temp: [" + str(Tinit) + 'C]\n Occ Zone Temp Bound: [' +
                        str(Toccmin+ToccminRange) 
                        + 'C $\leq$ T $\leq$ ' 
                        + str(Toccmax-ToccRange) 
                        + ']\n UnOcc Zone Temp Bound: [' 
                        + str(Toccmin) + 'C $\leq$ T $\leq$ ' 
                        + str(Toccmax) +'C]\nSupply Air Temperature Bound: [' 
                        + str(TSAoccmin) + 'C $\leq$ T $\leq$ ' 
                        + str(TSAoccmax) + 'C]', fontsize=12)
        ztfig.plot(t, ZT, 'b-', label='Zone Temperature')    
        ztfig.plot(t, OT, 'r-', label='Outdoor Temperature')
        ztfig.plot(t, TSA, 'g-', label='Supply Air Temperature')
        ztfig_handles, ztfig_labels = ztfig.get_legend_handles_labels()
        ztfig.set_xlabel("Scheduling Period",fontsize=12)
        ztfig.set_ylabel("Celcius",fontsize=12)
        ztfig.set_ylim(ymax=maxT+5)
        
        ztfig_fontP = FontProperties()
        ztfig_fontP.set_size('small')
#         ztfig.legend(ztfig_handles, ztfig_labels, loc='best', prop=ztfig_fontP)        
        # Shink current axis's height by 10% on the bottom
        box = ztfig.get_position()
        ztfig.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
        # Put a legend below current axis
        ztfig.legend(loc='upper center', bbox_to_anchor=(0.5, -0.001), fancybox=True, shadow=True, ncol=5, prop=ztfig_fontP)
        
        ztfig_rule_1 = rrulewrapper(self._getPlotRule((int)(pinterval)), interval=(int)(pstep)) 
        ztfig_loc_1 = RRuleLocator(ztfig_rule_1)
        ztfig.xaxis.set_major_locator(ztfig_loc_1)
        ztfig.xaxis.set_major_formatter(ymdhFmt)
        ztfig_datemin = datetime(min(t).year, min(t).month, min(t).day, min(t).hour, min(t).minute) 
        ztfig_datemax = datetime(max(t).year, max(t).month, max(t).day, max(t).hour, max(t).minute)
        ztfig.set_xlim(ztfig_datemin, ztfig_datemax)        
                
#         afig.plot(t, aSAmin, 'r-', label='Lower Bound')    
        afig.plot(t, ASA, '-*', label='Air Mass Flow Rate')
#         afig.plot(t, ASA_UB, 'g-', label='Upper Bound')
        afig_handles, afig_labels = afig.get_legend_handles_labels()
        afig_fontP = FontProperties()
        afig_fontP.set_size('small')
        afig.legend(afig_handles, afig_labels, loc='best', prop=afig_fontP)        
        afig.set_xlabel("Scheduling Period",fontsize=12)
        afig.set_ylabel("Air Mass Flow Rate (kg/s)",fontsize=12)        
        afig_rule_1 = rrulewrapper(self._getPlotRule((int)(pinterval)), interval=(int)(pstep)) 
        afig_loc_1 = RRuleLocator(afig_rule_1)
        afig.xaxis.set_major_locator(afig_loc_1)
        afig.xaxis.set_major_formatter(ymdhFmt)
        afig_datemin = datetime(min(t).year, min(t).month, min(t).day, min(t).hour, min(t).minute) 
        afig_datemax = datetime(max(t).year, max(t).month, max(t).day, max(t).hour, max(t).minute)
        afig.set_xlim(afig_datemin, afig_datemax)   
        
        fig.autofmt_xdate()
        plt.tight_layout()
        
        plt.savefig('Output\\'+ str(cfg_idx) + '_TemperatureAirMass_' + rname + "_" + datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f') +'.png')        
#         plt.show()      
        plt.close(fig)
        
        
        
    def plotTemperatureNAirMassZoom(self, cfg_idx, rname, pinterval, pstep, zt, oat, tsa, asa, start, end):
        
        t = zt.get('Time')
        ZT = zt.get('Celcius')
        OT = oat.values()
        TSA = tsa.get('Celcius')
        ASA = asa.get('Kg/s')
        s = datetime.strptime(start, "%Y-%m-%d %H:%M")
        e = datetime.strptime(end, "%Y-%m-%d %H:%M")
        
        sidx = 0
        eidx = 0
        for ridx, x in enumerate(t):
            if x == s:
                sidx = ridx
            if x == e:
                eidx = ridx
    
        zoomt = []
        zoomc = []
        zoomoat = []
        zoomtsa = []
        zoomasa = []
        for i in range(sidx, eidx+1):
            zoomt.append(t[i])
            zoomc.append(ZT[i])
            zoomoat.append(OT[i])
            zoomtsa.append(TSA[i])
            zoomasa.append(ASA[i])
                    
                
        maxZT = float(max(ZT))
        maxOT = float(max(OT))
        maxTSA = float(max(TSA))
        maxT = max([maxZT, maxOT, maxTSA])

        ymdhFmt = mdates.DateFormatter('%H:%M')
#         ymdhFmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
        
        fig = plt.figure()   
        ztfig = fig.add_subplot(211)
        afig = fig.add_subplot(212)
        
        ztfig.plot(zoomt, zoomc, 'k-', label='Zone Temperature')    
        ztfig.plot(zoomt, zoomoat, 'r--', label='Outdoor Temperature')
        ztfig.plot(zoomt, zoomtsa, 'b-+', label='Supply Air Temperature')
        
        ztfig.set_xlabel("Scheduling Period",fontsize=12)
        ztfig.set_ylabel("Celcius",fontsize=12)
        ztfig.set_ylim(ymax=maxT+5)
        
        ztfig_fontP = FontProperties()
        ztfig_fontP.set_size('small')
        box = ztfig.get_position()
        ztfig.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])        
        ztfig.legend(loc='upper center', bbox_to_anchor=(0.5, -0.001), fancybox=True, shadow=True, ncol=5, prop=ztfig_fontP)
        
        ztfig_rule_1 = rrulewrapper(self._getPlotRule((int)(pinterval)), interval=(int)(pstep)) 
        ztfig_loc_1 = RRuleLocator(ztfig_rule_1)
        ztfig.xaxis.set_major_locator(ztfig_loc_1)
        ztfig.xaxis.set_major_formatter(ymdhFmt)
        ztfig_datemin = datetime(min(zoomt).year, min(zoomt).month, min(zoomt).day, min(zoomt).hour, min(zoomt).minute) 
        ztfig_datemax = datetime(max(zoomt).year, max(zoomt).month, max(zoomt).day, max(zoomt).hour, max(zoomt).minute)        
        ztfig.set_xlim(ztfig_datemin, ztfig_datemax)     
        ztfig.grid(True)   
                
        afig.plot(zoomt, zoomasa, '-x', label='Air Mass Flow Rate')
        afig_handles, afig_labels = afig.get_legend_handles_labels()
        afig_fontP = FontProperties()
        afig_fontP.set_size('small')
        afig.legend(afig_handles, afig_labels, loc='best', prop=afig_fontP)        
        afig.set_xlabel("Scheduling Period",fontsize=12)
        afig.set_ylabel("Air Mass Flow Rate (kg/s)",fontsize=12)        
        afig_rule_1 = rrulewrapper(self._getPlotRule((int)(pinterval)), interval=(int)(pstep)) 
        afig_loc_1 = RRuleLocator(afig_rule_1)
        afig.xaxis.set_major_locator(afig_loc_1)
        afig.xaxis.set_major_formatter(ymdhFmt)
        afig_datemin = datetime(min(zoomt).year, min(zoomt).month, min(zoomt).day, min(zoomt).hour, min(zoomt).minute) 
        afig_datemax = datetime(max(zoomt).year, max(zoomt).month, max(zoomt).day, max(zoomt).hour, max(zoomt).minute)        
        afig.set_xlim(afig_datemin, afig_datemax)   
        afig.grid(True)
        
        fig.autofmt_xdate()
        plt.tight_layout()
        
        plt.savefig('Output\\'+ str(cfg_idx) + '_TemperatureAirMass_' + rname + "_" + datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f') +'.png')        
#         plt.show()      
        plt.close(fig)
        
    def plotEnergyConsumption(self, cfg_idx, pinterval, pstep, rname, rcfg, mcfg, oatdat, efan, econd, eheat,
                              pfan, pcond, pheat, 
                              efankWh, econdkWh, eheatkWh,
                              efankJ, econdkJ, eheatkJ,
                              ptotal, etotalkWh, etotalkJ):

        t = efan.get('Time')
        fan_kW = efan.get('kW')
        cond_kW = econd.get('kW') 
        heat_kW = eheat.get('kW')
        fan_kWh = efan.get('kWh')
        cond_kWh = econd.get('kWh') 
        heat_kWh = eheat.get('kWh')
        fan_kJ = efan.get('kJ')
        cond_kJ = econd.get('kJ') 
        heat_kJ = eheat.get('kJ') 

        ymdhFmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
        fontP = FontProperties()
        fontP.set_size('small')
        rule_1 = rrulewrapper(self._getPlotRule((int)(pinterval)), interval=(int)(pstep)) 
        loc_1 = RRuleLocator(rule_1)
        datemin = datetime(min(t).year, min(t).month, min(t).day, min(t).hour, min(t).minute) 
        datemax = datetime(max(t).year, max(t).month, max(t).day, max(t).hour, max(t).minute)
        
        fig = plt.figure()   
        e_fig_kJs = fig.add_subplot(211)
#         e_fig_kWh = fig.add_subplot(212)
        e_fig_kJ = fig.add_subplot(212)
        
        e_fig_kJs.set_title('Room Name: [' + rname + ']\nRoomConfig: ' + rcfg + " \nMeetingsConfig: " + 
                        mcfg + " \nOutdoorTemp: " + oatdat + 
                        "\nTotal Fan Power: " + str(round(pfan,2)) + " kW" +
                        "\nTotal Cooling Power:" + str(round(pcond,2)) + " kW" +
                        "\nTotal Heating Power:" + str(round(pheat,2)) + " kW" +
                        "\nTotal:" + str(round(ptotal,2)) + " kW" , fontsize=12)        
        e_fig_kJs.plot(t, fan_kW, '-', label='Fan')    
        e_fig_kJs.plot(t, cond_kW, '-*', label='Cooling')
        e_fig_kJs.plot(t, heat_kW, '-+', label='Heating')
        handles, labels = e_fig_kJs.get_legend_handles_labels()
        e_fig_kJs.legend(handles, labels, loc='best', prop=fontP)        
        e_fig_kJs.set_xlabel("Scheduling Period",fontsize=12)
        e_fig_kJs.set_ylabel("Power Consumption (kW)",fontsize=12)
        e_fig_kJs.xaxis.set_major_locator(loc_1)
        e_fig_kJs.xaxis.set_major_formatter(ymdhFmt)        
        e_fig_kJs.set_xlim(datemin, datemax)
        e_fig_kJs.format_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M')        
        e_fig_kJs.grid(True)
        
        
#         e_fig_kWh.set_title("Total Fan Energy: " + str(round(efankWh,2)) + " kWh" +
#                         "\nTotal Cooling Energy:" + str(round(econdkWh,2)) + " kWh" +
#                         "\nTotal Heating Energy:" + str(round(eheatkWh,2)) + " kWh" +
#                         "\nTotal:" + str(round(etotalkWh,2)) + " kWh" , fontsize=12)        
#         e_fig_kWh.plot(t, fan_kWh, '-', label='Fan')    
#         e_fig_kWh.plot(t, cond_kWh, '-*', label='Cooling')
#         e_fig_kWh.plot(t, heat_kWh, '-+', label='Heating')
#         handles, labels = e_fig_kWh.get_legend_handles_labels()
#         e_fig_kWh.legend(handles, labels, loc='best', prop=fontP)        
#         e_fig_kWh.set_xlabel("Scheduling Period",fontsize=12)
#         e_fig_kWh.set_ylabel("Energy Consumption (kWh)",fontsize=12)
#         e_fig_kWh.xaxis.set_major_locator(loc_1)
#         e_fig_kWh.xaxis.set_major_formatter(ymdhFmt)        
#         e_fig_kWh.set_xlim(datemin, datemax)
#         e_fig_kWh.format_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M')        
#         e_fig_kWh.grid(True)
        
        
        e_fig_kJ.set_title("Total Fan Energy: " + str(round(efankJ,2)) + " kJ" +
                        "\nTotal Cooling Energy:" + str(round(econdkJ,2)) + " kJ" +
                        "\nTotal Heating Energy:" + str(round(eheatkJ,2)) + " kJ" +
                        "\nTotal:" + str(round(etotalkJ,2)) + " kJ" , fontsize=12)
        e_fig_kJ.plot(t, fan_kJ, '-', label='Fan')    
        e_fig_kJ.plot(t, cond_kJ, '-*', label='Cooling')
        e_fig_kJ.plot(t, heat_kJ, '-+', label='Heating')
        handles, labels = e_fig_kJ.get_legend_handles_labels()
        e_fig_kJ.legend(handles, labels, loc='best', prop=fontP)        
        e_fig_kJ.set_xlabel("Scheduling Period",fontsize=12)
        e_fig_kJ.set_ylabel("Energy Consumption (kJ)",fontsize=12)
        e_fig_kJ.xaxis.set_major_locator(loc_1)
        e_fig_kJ.xaxis.set_major_formatter(ymdhFmt)        
        e_fig_kJ.set_xlim(datemin, datemax)
        e_fig_kJ.format_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M')        
        e_fig_kJ.grid(True)
        
        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()
        plt.tight_layout()
        
        plt.savefig('Output\\'+ str(cfg_idx) + '_Energy_' + rname + "_" + datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f') +'.png')        
#         plt.show()
        plt.close(fig)
    
    def plotTemperatureZoom(self, cfg_idx, pinterval, pstep, rname, rcfg, mcfg, start, end, zt):
        t = zt.get('Time')
        c = zt.get('Celcius')
        s = datetime.strptime(start, "%Y-%m-%d %H:%M")
        e = datetime.strptime(end, "%Y-%m-%d %H:%M")
        sidx = 0
        eidx = 0
        for ridx, x in enumerate(t):
            if x == s:
                sidx = ridx
#                 logging.debug("start: %d, celcius: %f" %(ridx, c[ridx]))
            if x == e:
                eidx = ridx
#                 logging.debug("end: %d, celcius: %f" %(ridx, c[ridx]))
    
        zoomt = []
        zoomc = []
        for i in range(sidx, eidx+1):
            zoomt.append(t[i])
#             zoomc.append(round(c[i],1))
            zoomc.append(c[i])
            
#             zoomc.append(c[i])
             
# method A:
#             strC = split(str(c[i]), ".")
#             strC = strC[0] + "." + strC[1][:3]    
#             zoomc.append(strC)
            
#         logging.debug(zoomt)
#         logging.debug(zoomc)
        
        ymdhFmt = mdates.DateFormatter('%H:%M')
#         ymdhFmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
         
        fig = plt.figure()
        ztfig = fig.add_subplot(111) 
        ztfig.set_title('Room Name: [' + rname + ']\nRoomConfig: ' + rcfg + " \nMeetingsConfig: " + mcfg, fontsize=12)
        #----------------------------
        # Plot Pattern #1 - no label
#         ztfig.plot(zoomt, zoomc, 'b-', label='Zone Temperature')
# #         ztfig.set_ylim(21, 29)      # NOTE: just for overall room temperature analysis
        #----------------------------
        # Plot Pattern #2 - label data at every point        
        ztfig.plot(zoomt, zoomc, 'bx-', label='Zone Temperature')
#         print zoomc
        
        k = 0
        for i,j in zip(zoomt,zoomc):
            val = "{0:.1f}".format(zoomc[k])
            ztfig.annotate(str(val),xy=(i,j), xytext=(0,-10), textcoords='offset points')
            k = k+1
        #----------------------------
        handles, labels = ztfig.get_legend_handles_labels()
        fontP = FontProperties()
        fontP.set_size('small')
        ztfig.legend(handles, labels, loc='best', prop=fontP)        
        ztfig.set_xlabel("Scheduling Period",fontsize=12)
        ztfig.set_ylabel("Celcius",fontsize=12)
        # format the ticks
#         rule = rrulewrapper(DAILY, interval=1)
#         rule = rrulewrapper(HOURLY, interval=30)
        rule_1 = rrulewrapper(self._getPlotRule((int)(pinterval)), interval=(int)(pstep)) 
        loc_1 = RRuleLocator(rule_1)
        ztfig.xaxis.set_major_locator(loc_1)
        ztfig.xaxis.set_major_formatter(ymdhFmt)
        datemin = datetime(min(zoomt).year, min(zoomt).month, min(zoomt).day, min(zoomt).hour, min(zoomt).minute) 
        datemax = datetime(max(zoomt).year, max(zoomt).month, max(zoomt).day, max(zoomt).hour, max(zoomt).minute)
        ztfig.set_xlim(datemin, datemax)
#         ztfig.set_ylim(18, 25)
#         ztfig.set_ylim(19, 29)
        ztfig.grid(True)
         
        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()
#         plt.tight_layout()
         
        plt.savefig('Output\\'+ str(cfg_idx) + '_ZoomTemp_' + rname + "_" + datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f') +'.png')        
#         plt.show()      
        plt.close(fig)
        
        
    def plotOutdoor(self, pinterval, pstep, oatdat, pcfg,
                    Tinit, Toccmin, ToccminRange, Toccmax, ToccRange, xtime, oat):
        
        t = xtime
        OT = oat.values()
        min_occ1 = [21] * len(t)
        max_occ1 = [23] * len(t)
        min_occ2 = [22] * len(t)
        max_occ2 = [24] * len(t)
        
        ymdhFmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
        
        fig = plt.figure()
        ztfig = fig.add_subplot(111)         
#         ztfig.set_title(" \nOutdoorTemp: " + oatdat + "\nInitial Temp: [" + str(Tinit) + 'C]\n Occ Zone Temp Bound: [' +
#                         str(Toccmin+ToccminRange) + 'C $\leq$ T $\leq$ ' + str(Toccmax-ToccRange) + ']\n UnOcc Zone Temp Bound: [' +
#                         str(Toccmin) + 'C $\leq$ T $\leq$ ' + str(Toccmax) +
#                         'C]', fontsize=12)
            
        ztfig.plot(xtime, OT, 'r-', label='Outdoor Temperature')
        ztfig.plot(xtime, min_occ1, 'g-', label='Min Occupied Zone Temperature 21C')        
        ztfig.plot(xtime, max_occ1, 'b-', label='Max Occupied Zone Temperature 23C')
        ztfig.plot(xtime, min_occ2, 'g--', label='Min Occupied Zone Temperature 22C')        
        ztfig.plot(xtime, max_occ2, 'b--', label='Max Occupied Zone Temperature 24')
        ztfig.set_xlabel("Scheduling Period",fontsize=12)
        ztfig.set_ylabel("Celcius",fontsize=12)
        
        handles, labels = ztfig.get_legend_handles_labels()
        fontP = FontProperties()
        fontP.set_size('small')
        ztfig.legend(handles, labels, loc='best', prop=fontP)  
        
        ztfig_rule_1 = rrulewrapper(self._getPlotRule((int)(pinterval)), interval=(int)(pstep)) 
        ztfig_loc_1 = RRuleLocator(ztfig_rule_1)
        ztfig.xaxis.set_major_locator(ztfig_loc_1)
        ztfig.xaxis.set_major_formatter(ymdhFmt)
        ztfig_datemin = datetime(min(t).year, min(t).month, min(t).day, min(t).hour, min(t).minute) 
        ztfig_datemax = datetime(max(t).year, max(t).month, max(t).day, max(t).hour, max(t).minute)
        ztfig.set_xlim(ztfig_datemin, ztfig_datemax)        
        
        fig.autofmt_xdate()
        plt.tight_layout()
        
        plt.savefig('Output\\OutdoorTemperature_' + datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f') +'.png')        
#         plt.show()   
        plt.close(fig)
        
        