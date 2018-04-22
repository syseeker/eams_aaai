import logging
from datetime import datetime
from time import time

from eams import EAMS
from eams_plot import GraphPlot
from gurobipy import *
import numpy as np

KJ_TO_KWh = 0.000277777778
N_OUTDOOR = 1000
N_NOT_EXIST = -1

       
class Solver:
    def __init__(self, EAMS, cfg_idx):
        self.model = Model('EAMS')
        self.EAMS = EAMS
        self.CFG_IDX = cfg_idx
                
        self.NUM_SLOT = len(self.EAMS.TS)-1
        self.NUM_MEETING = len(self.EAMS.ML)
        self.NUM_MEETING_TYPE = len(self.EAMS.MTYPE)
        self.NUM_ROOM = len(self.EAMS.RL)
        logging.debug("******************* #k = %d #m = %d #r = %d" %(self.NUM_SLOT, self.NUM_MEETING, self.NUM_ROOM))
        
        self._init_ScheduleVar()
        self._init_HVACVar()
        
        self.solveTime = 0
        self.EPSILON = 1.0e-06
        self.STATUS = ['', 'LOADED', 'OPTIMAL', 'INFEASIBLE', 'INF_OR_UNBD', 'UNBOUNDED', 'CUTOFF', 'ITERATION_LIMIT', 'NODE_LIMIT', 'TIME_LIMIT', 'SOLUTION_LIMIT', 'INTERRUPTED', 'NUMERIC', 'SUBOPTIMAL']
    
    def solve(self):
        start = time()
        self._initializeModel()
        self._createScheduleModel()
        self.model.optimize()
        self.logSchedulingResults()
        
        self._getBDV_x_MLK_setToOne()
        self._createScheduleCstr()        
        self._createHVACModel()
        self._createModelObjective()   
        self.model.update()        
        self.model.write('Output\EAMS_' + str(self.CFG_IDX) + '_' + datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f') +'.lp')
        
        self.model.optimize()
        self.solveTime = time() - start
        
    def _createScheduleCstr(self):
        for i in xrange(len(self.milp_alloc)):
            [fm,fl,fk] = self.milp_alloc[i]
            [m,l,k] = self.BDV_x_MLK_Dict.get(tuple([fm, fl, fk]))
#             print fm, " ", fl, " ", fk, " = ", m, " ", l, " ", k
            self.BDV_x_MLK[m][l][k].setAttr("LB", 1.0)
            self.model.update()
        
    def _getBDV_x_MLK_setToOne(self):
        logging.info("------------------- _getBDV_x_MLK_setToOne  Identify x=1")
        self.milp_alloc = []
        for m in xrange(self.NUM_MEETING_TYPE):
            for l in xrange(len(self.BDV_x_MLK[m])):
                for k in xrange(len(self.BDV_x_MLK[m][l])):
                    val = self.BDV_x_MLK[m][l][k].x                    
                    if val > self.EPSILON:
                        [fm,fl,fk] = self._getBDV_x_MLK([m,l,k]) 
                        self.milp_alloc.append([fm,fl,fk])
        logging.info("[fm, fl, fk]: %s" %(self.milp_alloc))
        
    def presolve(self):
        self._createModel()        
        mp = self.model.presolve()
        mp.write('Output\EAMS_' + str(self.CFG_IDX) + '_' + datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f') +'presolved.lp')
                        
    def _initializeModel(self):
        self.model.setParam(GRB.param.OutputFlag, 1)
        self.model.setParam(GRB.Param.Threads, 1)
        self.model.setParam(GRB.Param.FeasibilityTol, 1e-9)        
        self.model.setParam(GRB.Param.IntFeasTol, 1e-9)          
        self.model.setParam(GRB.Param.OptimalityTol, 1e-9)
        
#         Cope with out-of-memory error.
#         When the amount of memory used to store nodes (measured in GBytes) exceeds the specified parameter value, 
#         nodes are written to disk.  NodefileDir parameter can be used to choose a different location.
#         self.model.setParam(GRB.Param.NodefileStart, 1)

#         The MIP solver can change parameter settings in the middle of the search in order to adopt a strategy 
#             that gives up on moving the best bound and instead devotes all of its effort towards finding better 
#             feasible solutions. 
#            
#            This parameter allows you to specify the node count at which the MIP solver switches
#             to a solution improvement strategy. For example, setting this parameter to 10 will cause the MIP solver
#             to switch strategies once the node count is larger than 10.
#         self.model.setParam(GRB.Param.ImproveStartNodes, 10.0)

#            This parameter allows you to specify an optimality gap at which the MIP solver switches 
#            to a solution improvement strategy. For example, setting this parameter to 0.1 will cause the MIP solver 
#            to switch strategies once the relative optimality gap is smaller than 0.1.
#         self.model.setParam(GRB.Param.ImproveStartGap, 0.1)
        
#        self.model.setParam(GRB.param.Presolve,2)   
        
        self.model.setParam(GRB.Param.TimeLimit, 60*60) # 60s x  N minutes
#         self.model.setParam(GRB.Param.TuneTimeLimit, 180)  # 18000

#         The MIP solver will terminate (with an optimal result) when the relative gap between the lower 
#             and upper objective bound is less than MIPGap times the upper bound. Default value:    1e-4
#         self.model.setParam(GRB.Param.MIPGap, 0.015)
        
#         If you are more interested in finding feasible solutions quickly, you can select MIPFocus=1. 
#         If you believe the solver is having no trouble finding good quality solutions, and wish to focus more attention on proving optimality, select MIPFocus=2. 
#         If the best objective bound is moving very slowly (or not at all), you may want to try MIPFocus=3 to focus on the bound.
#         self.model.setParam(GRB.Param.MIPFocus, 3)

#         Indicates that you aren't interested in solutions whose objective values are worse than the specified value. 
#         If the objective value for the optimal solution is better than the specified cutoff, 
#             the solver will return the optimal solution. Otherwise, it will terminate with a CUTOFF status
#         self.model.setParam(GRB.Param.Cutoff, double value)

        
    def _createModel(self):
        logging.info("===============================================================")
        logging.info("Gurobi - Create model ")
        logging.info("===============================================================")  
        self._initializeModel()
        
        self._createScheduleModel()
        self._createHVACModel()
        
        self._createModelObjective()        
        
        self.model.update()
        self.model.write('Output\EAMS_' + str(self.CFG_IDX) + '_' + datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f') +'.lp')      
        
    def _init_ScheduleVar(self):                
        self.BDV_x_MLK = []                           # Binary Decision variable: The "Starting" slot of a meeting in Meeting x Location x Time
        self.BDV_w_LK = []                             # Binary Decision variable: represent if HVAC is activated from standby mode at location l at time k
        self.BAV_z_LK = []                            # Binary Auxiliary variable: represent if location l is occupied at time k (do not care which meeting)        
        self.DAV_Attendee_LK = []                   # Discrete Auxiliary variable: Number of attendee at room l at time k
        
        self.BDV_x_MLK_Dict = {}                       # d[(m,l,k)] = offset of (m,l,k) in BDV_x_MLK. Record index of meeting x location x time periods
        self.BDV_w_LK_Dict = {}                       # d[(l,k)] = offset of (l,k) in BDV_w_LK. Record index of location x time periods
                        
        self.CSTR_Schedule_Once_M = []              # Constraint: Every meeting must be scheduled to 1 room exactly at its starting time k
        self.CSTR_UniqueLocation = []               # Constraint: No overlapped meeting should occupy the same room
        self.CSTR_LocationTimeOccupied=[]           # Constraint:     set BAV_z_LK to 1 if at least 1 meeting is held at location l at time k
        self.CSTR_TotalAllocatedSlot=[]             # Force BAV_z_LK to 0 if no meeting is allocated.
        self.CSTR_NumAttendee = []                  # Constraint: Number of attendee at room l at time k
        self.CSTR_AttendeeConflict = []             # Constraint: Meeting which has similar attendee should not be allocated at the same timeslot
                
    def _init_HVACVar(self):
        self.CDV_T_SA_LK = []                       # Continuous Decision variable: Supply air temperature
        self.CDV_A_SA_LK = []                       # Continuous Decision variable: air mass flow rate                
        self.CAV_T_LK = []                          # Continuous Auxiliary variable: Room/Zone temperature        
        self.CAV_A_SA_Room_L = []                   # Continuous Auxiliary variable: Minimum air mass flow rate per location
        self.CAV_A_SA_MaxPeople_L = []              # Continuous Auxiliary variable: Minimum air mass flow rate per occupant required
        self.CAV_A_SA_T_z_LK = []                   # Continuous Auxiliary variable:  aT(SA,z)
        self.CAV_A_SA_T_z_y1_LK = []                # Continuous Auxiliary variable: on/off constraint for A_SA_T_z 1
        self.CAV_A_SA_T_z_y2_LK = []                # Continuous Auxiliary variable: on/off constraint for A_SA_T_z 2
        self.CAV_A_SA_T_z_y3_LK = []                # Continuous Auxiliary variable: on/off constraint for A_SA_T_z 3
        self.CAV_A_SA_T_z_y4_LK = []                # Continuous Auxiliary variable: on/off constraint for A_SA_T_z 4
        self.CAV_A_SA_T_SA_LK = []                  # Continuous Auxiliary variable:  aT(SA,SA)        
        self.CAV_E_FAN_LK = []                      # Auxiliary variable: Energy consumption of fan operation
        self.CAV_E_CONDITIONING_LK = []             # Auxiliary variable: Energy consumption of conditioning operation
        self.CAV_E_HEATING_LK = []                  # Auxiliary variable: Energy consumption of heating operation        
        self.CAV_T_z1_l_LK = []                        # Continuous Auxiliary variable: wall temperature from zone zl to zone l                    
        self.CAV_T_z2_l_LK = []                        # Continuous Auxiliary variable: wall temperature from zone z2 to zone l
        self.CAV_T_z3_l_LK = []                        # Continuous Auxiliary variable: wall temperature from zone z3 to zone l
        self.CAV_T_z4_l_LK = []                        # Continuous Auxiliary variable: wall temperature from zone z4 to zone l
        self.CAV_T_l_z1_LK = []                        # Continuous Auxiliary variable: wall temperature from zone l to zone z1
        self.CAV_T_l_z2_LK = []                        # Continuous Auxiliary variable: wall temperature from zone l to zone z2
        self.CAV_T_l_z3_LK = []                        # Continuous Auxiliary variable: wall temperature from zone l to zone z3
        self.CAV_T_l_z4_LK = []                        # Continuous Auxiliary variable: wall temperature from zone l to zone z4
        self.CAV_T_l_f_LK  = []                        # Continuous Auxiliary variable: wall temperature from zone l to zone f
        self.CAV_T_l_c_LK  = []                        # Continuous Auxiliary variable: wall temperature from zone l to zone c   
        self.A_SA_LB = []
        
        self.CSTR_T_SA_LK = []                      # Constraint:     T_CA*BAV_L <= T_SA <= T_SA_HIGH
        self.CSTR_T_LK_lb = []                      # Constraint: lower bound of room temperature
        self.CSTR_T_LK_ub = []                      # Constraint: upper bound of room temperature
        self.CSTR_T_LK = []                         # Constraint: Equation of room/zone temperature
        self.CSTR_T_z1_l_LK = []                    # Constraint: Equation of wall temperature from z1 to l
        self.CSTR_T_z2_l_LK = []                    # Constraint: Equation of wall temperature from z2 to l
        self.CSTR_T_z3_l_LK = []                    # Constraint: Equation of wall temperature from z3 to l
        self.CSTR_T_z4_l_LK = []                    # Constraint: Equation of wall temperature from z4 to l
        self.CSTR_T_l_z1_LK = []                    # Constraint: Equation of wall temperature from l to z1  
        self.CSTR_T_l_z2_LK = []                    # Constraint: Equation of wall temperature from l to z2
        self.CSTR_T_l_z3_LK = []                    # Constraint: Equation of wall temperature from l to z3
        self.CSTR_T_l_z4_LK = []                    # Constraint: Equation of wall temperature from l to z4
        self.CSTR_T_l_f_LK = []                     # Constraint: Equation of wall temperature from l to f
        self.CSTR_T_l_c_LK = []                     # Constraint: Equation of wall temperature from l to c

        self.CSTR_A_SA_LB_LK = []                   # Constraint: lower bound of air mass flow rate
        self.CSTR_A_SA_UB_LK = []                   # Constraint: upper bound of air mass flow rate
        self.CSTR_T_SA_LB_LK = []                   # Constraint: lower bound of T_SA
        self.CSTR_T_SA_UB_LK = []                   # Constraint: upper bound of T_SA

        self.CSTR_A_SA_T_z_1_LK = []                # Constraint: MacCormick relaxation for A_SA x T
        self.CSTR_A_SA_T_z_2_LK = []                # Constraint: MacCormick relaxation for A_SA x T
        self.CSTR_A_SA_T_z_3_LK = []                # Constraint: MacCormick relaxation for A_SA x T
        self.CSTR_A_SA_T_z_4_LK = []                # Constraint: MacCormick relaxation for A_SA x T
        self.CSTR_y1_LB_LK = []                      # Constraint: On/off constraint LB of ASA x T 1 
        self.CSTR_y1_UB_LK = []                      # Constraint: On/off constraint UB of ASA x T 1
        self.CSTR_y2_LB_LK = []                      # Constraint: On/off constraint LB of ASA x T 2
        self.CSTR_y2_UB_LK = []                      # Constraint: On/off constraint UB of ASA x T 2
        self.CSTR_y3_LB_LK = []                      # Constraint: On/off constraint LB of ASA x T 3
        self.CSTR_y3_UB_LK = []                      # Constraint: On/off constraint UB of ASA x T 3
        self.CSTR_y4_LB_LK = []                      # Constraint: On/off constraint LB of ASA x T 4
        self.CSTR_y4_UB_LK = []                      # Constraint: On/off constraint UB of ASA x T 4
        
        self.CSTR_A_SA_T_SA_1_LK = []                 # Constraint: MacCormick relaxation for A_SA x T_SA
        self.CSTR_A_SA_T_SA_2_LK = []                 # Constraint: MacCormick relaxation for A_SA x T_SA
        self.CSTR_A_SA_T_SA_3_LK = []                 # Constraint: MacCormick relaxation for A_SA x T_SA
        self.CSTR_A_SA_T_SA_4_LK = []                 # Constraint: MacCormick relaxation for A_SA x T_SA
        
        self.CSTR_E_FAN_LK = []                     # Constraint: Equation of energy consumption of fan operation
        self.CSTR_E_CONDITIONING_LK = []            # Constraint: Equation of energy consumption of air-conditioning operation
        self.CSTR_E_HEATING_LK = []                 # Constraint: Equation of energy consumption of heating operation
                
    def _createScheduleModel(self):
        
#         self._createBDV_x_MLK()
        self._createBDV_x_MLK_MT()
        self._createBAV_z_LK()
        self._createDAV_Attendee_LK()  
        
        #Option 1: Meeting Type
        self._createCSTR_Schedule_Once_MT()
        self._createCSTR_LocationTimeOccupied_MT()
        self._createCSTR_NumAttendee_MT()
        self._createCSTR_AttendeeConflict_MT()
        
        #Option 2: Meeting
#         self._createCSTR_Schedule_Once()
# #         self._createCSTR_UniqueLocation()
#         self._createCSTR_LocationTimeOccupied()
# #         self._createCSTR_TotalAllocatedSlot()        
#         self._createCSTR_NumAttendee()
#         self._createCSTR_AttendeeConflict()
        
        
    def _createHVACModel(self):
        self._createCDV_SupplyAirTemperature()
        self._createCDV_AirMassFlowRate()
        self._createCAV_RoomTemperature()
        self._createCAV_T_z1_l()
        self._createCAV_T_z2_l()  
        self._createCAV_T_z3_l()  
        self._createCAV_T_z4_l()  
        self._createCAV_T_l_z1()          
        self._createCAV_T_l_z2()
        self._createCAV_T_l_z3()
        self._createCAV_T_l_z4()
        self._createCAV_T_l_f()
        self._createCAV_T_l_c()
        self._createCAV_A_SA_T_z_LK()
        self._createCAV_A_SA_T_SA_LK()    
        
        self._createCSTR_RoomTemperature_LB()
        self._createCSTR_RoomTemperature_UB()
        self._createCSTR_RoomTemperature()
        self._createCSTR_T_z1_l()
        self._createCSTR_T_z2_l()  
        self._createCSTR_T_z3_l()  
        self._createCSTR_T_z4_l()  
        self._createCSTR_T_l_z1()          
        self._createCSTR_T_l_z2()
        self._createCSTR_T_l_z3()
        self._createCSTR_T_l_z4()
        self._createCSTR_T_l_f()
        self._createCSTR_T_l_c()
                
        if self.EAMS.STANDBY_MODE == '0':
            # HVAC mode - options - enable either 1 set
            # option 1: no standby mode. HVAC is OFF after standard working hours
            logging.info("HVAC running on non-standby mode... HVAC is off at night.")
            self._createHVAC_CSTR_noStandbyMode()
        else:
            # option 2: has standby mode. HVAC will be automatically turned on/off after standard working hours.
            logging.info("HVAC running on standby mode... HVAC can be turned on at night.")
            self._createHVAC_CSTR_hasStandbyMode()                
                                
                
    def _createHVAC_CSTR_noStandbyMode(self):
        self._createCSTR_SupplyAirTemperature_LB_noStandbyMode()        
        self._createCSTR_SupplyAirFlowRate_LB_noStandbyMode()  
        self._createHVAC_CSTR_A_SA_T_SA_noStandbyMode()
        self._createHVAC_CSTR_A_SA_T_z_with_LooseBoundedT_noStandbyMode()
        
    def _createHVAC_CSTR_hasStandbyMode(self):
        self._createBDV_w_LK()
        self._createCSTR_SupplyAirTemperature_LB_hasStandbyMode()
        self._createCSTR_SupplyAirTemperature_UB_hasStandbyMode()
        self._createCSTR_SupplyAirFlowRate_LB_hasStandbyMode()
        self._createCSTR_SupplyAirFlowRate_UB_hasStandbyMode()   
        self._createHVAC_CSTR_A_SA_T_SA_hasStandbyMode()
        self._createHVAC_CSTR_A_SA_T_z_with_LooseBoundedT_hasStandbyMode()        
                            
    def _getA_SA_LB(self, l, k):        
        if self.EAMS.SH[k] == 1:
            [width, length, height] = self.EAMS.getRoomThermalConfig(l, "Dim")
            A_SA_LB = self.EAMS.ALPHA_IAQ_FACTOR_OF_SAFETY*(
                                                    (self.EAMS.MASS_AIR_FLOW_OUTSIDE_AIR_PER_METER_SQUARE * width * length * height) /
                                                    (1-self.EAMS.MASS_AIR_FLOW_RETURN_AIR_RATIO))
        else:
            A_SA_LB = self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MIN
        
        return float(A_SA_LB)
    
    def _get_T_SA_LB(self, l, k):
        if self.EAMS.SH[k] == 1:
            return float(self.EAMS.TEMPERATURE_CONDITIONED_AIR)
        else:
            return float(self.EAMS.INITIAL_TEMPERATURE_SUPPLY_AIR_UNOCC)
        
    def _createHVAC_CSTR_A_SA_T_SA_hasStandbyMode(self):
        self._createCSTR_A_SA_T_SA_1_LK_hasStandbyMode()
        self._createCSTR_A_SA_T_SA_2_LK_hasStandbyMode()
        self._createCSTR_A_SA_T_SA_3_LK_hasStandbyMode()
        self._createCSTR_A_SA_T_SA_4_LK_hasStandbyMode()
        
    def _createHVAC_CSTR_A_SA_T_z_with_LooseBoundedT_hasStandbyMode(self):
        self._createCSTR_A_SA_T_z_1_LK_looseboundedT_hasStandbyMode()
        self._createCSTR_A_SA_T_z_2_LK_looseboundedT_hasStandbyMode()
        self._createCSTR_A_SA_T_z_3_LK_looseboundedT_hasStandbyMode()
        self._createCSTR_A_SA_T_z_4_LK_looseboundedT_hasStandbyMode()
            
#---------------------                
    def _createHVAC_CSTR_A_SA_T_SA_noStandbyMode(self):
        self._createCSTR_A_SA_T_SA_1_LK_noStandbyMode()
        self._createCSTR_A_SA_T_SA_2_LK_noStandbyMode()
        self._createCSTR_A_SA_T_SA_3_LK_noStandbyMode()
        self._createCSTR_A_SA_T_SA_4_LK_noStandbyMode()
        
    def _createHVAC_CSTR_A_SA_T_z_with_LooseBoundedT_noStandbyMode(self):
        self._createCSTR_A_SA_T_z_1_LK_looseboundedT_noStandbyMode()
        self._createCSTR_A_SA_T_z_2_LK_looseboundedT_noStandbyMode()
        self._createCSTR_A_SA_T_z_3_LK_looseboundedT_noStandbyMode()
        self._createCSTR_A_SA_T_z_4_LK_looseboundedT_noStandbyMode()
        
    def _createModelObjective(self):
        self._createCAV_EnergyConsumption_Fan()
        self._createCAV_EnergyConsumption_Conditioning()
        self._createCAV_EnergyConsumption_Heating()
        
        self._createCSTR_EnergyConsumption_Fan()
        self._createCSTR_EnergyConsumption_Conditioning()
        self._createCSTR_EnergyConsumption_Heating()
        
        self._createObjective()   
        
   
    #===========================================================================
    # Decision Variables
    #===========================================================================   
    def _createBDV_x_MLK_MT(self):
        """For each meeting type x feasible location x feasible time, create a decision variable  (M x L_m x K_m)"""
        
        for m in xrange(self.NUM_MEETING_TYPE):
            # Get feasible start time from any one meeting in MLS
            mid = self.EAMS.MTYPE[m].MLS[0]
                
            self.BDV_x_MLK.append([])
            ml = 0
            for l in xrange(self.NUM_ROOM):
                if l in self.EAMS.MR[m]:    # TODO: assume all meetings of the same type can access the same room. Re-group required if not!
                    self.BDV_x_MLK[m].append([])  
                    mk = 0                                      
                    for k in xrange(self.NUM_SLOT):                        
                        if self.EAMS.isInTimeWindows(mid,k) > 0:
                            logging.debug("M_L_K_%d_%d_%d = in array offset(%d, %d, %d)" %(m,l,k, m, ml, mk))
                            
                            name = ['BDV_x_MLK', str(m), str(l), str(k)]                            
                            name = '_'.join(name)         
                            self.BDV_x_MLK[m][ml].append(self.model.addVar(vtype=GRB.BINARY, name=name))
                            self.BDV_x_MLK_Dict[tuple([m,l,k])] = [m,ml,mk]
                            mk = mk+1
                    ml = ml+1
                
        self.model.update()                           
        logging.debug("BDV_x_MLK:\n %s" %self.BDV_x_MLK)
        logging.debug("BDV_x_MLK_Dict:\n %s" %self.BDV_x_MLK_Dict) 
     
    def _createBDV_x_MLK(self):
        """For each meeting x feasible location x feasible time, create a decision variable  (M x L_m x K_m)"""
        
        for m in xrange(self.NUM_MEETING):    
            self.BDV_x_MLK.append([])
            ml = 0
            for l in xrange(self.NUM_ROOM):
                if l in self.EAMS.MR[m]:
                    self.BDV_x_MLK[m].append([])  
                    mk = 0                                      
                    for k in xrange(self.NUM_SLOT):                        
                        if self.EAMS.isInTimeWindows(m,k) > 0:
                            logging.debug("M_L_K_%d_%d_%d = in array offset(%d, %d, %d)" %(m,l,k, m, ml, mk))
                            
                            name = ['BDV_x_MLK', str(m), str(l), str(k)]                            
                            name = '_'.join(name)         
                            self.BDV_x_MLK[m][ml].append(self.model.addVar(vtype=GRB.BINARY, name=name))
                            self.BDV_x_MLK_Dict[tuple([m,l,k])] = [m,ml,mk]
                            mk = mk+1
                    ml = ml+1
                
        self.model.update()                           
        logging.debug("BDV_x_MLK:\n %s" %self.BDV_x_MLK)
        logging.debug("BDV_x_MLK_Dict:\n %s" %self.BDV_x_MLK_Dict) 
        
#         for m in xrange(self.NUM_MEETING):    
#             ml = 0
#             for l in xrange(self.NUM_ROOM):
#                 if l in self.EAMS.MR[m]:
#                     mk = 0                                      
#                     for k in xrange(self.NUM_SLOT):                        
#                         if self.EAMS.isInTimeWindows(m,k) > 0:
#                             self.BDV_x_MLK[m][ml][mk].setAttr(GRB.attr.BranchPriority, 2)
#                             mk = mk+1
#                     ml = ml+1
                                
    def _createBDV_w_LK(self):
        """For each time k, where k falls on non-standard working hour, create a decision variable  (L x K)"""
        
        for l in xrange(self.NUM_ROOM):
            self.BDV_w_LK.append([])
            mk = 0
            for k in xrange(self.NUM_SLOT):
                if self.EAMS.SH[k] == 0:
                    name = ['BDV_w_LK', str(l), str(k)]
                    name = '_'.join(name)         
                    self.BDV_w_LK[l].append(self.model.addVar(vtype=GRB.BINARY, name=name))
                    self.BDV_w_LK_Dict[tuple([l,k])] = [l,mk]
                    mk = mk+1
             
        self.model.update()
        logging.debug("BDV_w_LK:\n %s" %self.BDV_w_LK)
        logging.debug("BDV_w_LK_Dict:\n %s" %self.BDV_w_LK_Dict)

#         for l in xrange(self.NUM_ROOM):
#             mk = 0
#             for k in xrange(self.NUM_SLOT):
#                 if self.EAMS.SH[k] == 0:
#                     self.BDV_w_LK[l][mk].setAttr(GRB.attr.BranchPriority, 2)
#                     mk = mk+1
                     
    def _createCDV_SupplyAirTemperature(self):
        """For each location at each timestep, create a decision variable of TSA, i.e. TSA(k,l)"""
        
        T_SA_UB = self.EAMS.TEMPERATURE_SUPPLY_AIR_HIGH
        for l in xrange(self.NUM_ROOM):
            self.CDV_T_SA_LK.append([])
            for k in xrange(self.NUM_SLOT):                
                name = ['CDV_T_SA_LK', str(l), str(k)]
                name = '_'.join(name)                
                
                self.CDV_T_SA_LK[l].append(self.model.addVar(lb=0, ub=T_SA_UB, vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CDV_T_SA_LK:\n %s" %self.CDV_T_SA_LK)
        
    
    def _createCDV_AirMassFlowRate(self):
        """For each location at each timestep, create a decision variable of aSA, i.e. aSA(k,l)"""
        
        A_SA_UB = self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MAX
        for l in xrange(self.NUM_ROOM):
            self.CDV_A_SA_LK.append([])
            for k in xrange(self.NUM_SLOT):                
                name = ['CDV_A_SA_LK', str(l), str(k)]
                name = '_'.join(name)                
                
                self.CDV_A_SA_LK[l].append(self.model.addVar(lb=0, ub=A_SA_UB, vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CDV_A_SA_LK:\n %s" %self.CDV_A_SA_LK)
        

        
    #===========================================================================
    # Objective
    #===========================================================================
    def _createObjective(self):
        """Create an energy consumption minimization objective """
        
        self.model.modelSense = GRB.MINIMIZE
        objective = 0
        for l in xrange(self.NUM_ROOM):
            for k in xrange(self.NUM_SLOT):
                objective += self.CAV_E_FAN_LK[l][k] + self.CAV_E_CONDITIONING_LK[l][k] + self.CAV_E_HEATING_LK[l][k]
    
        self.model.setObjective(objective)
        
    #===========================================================================
    # Auxiliary Variables
    #===========================================================================
    
    #===========================================================================
    # Auxiliary Variables: Room Alloc
    #===========================================================================   
    def _createBAV_z_LK(self):
        """For each location at timeslot k, create an auxiliary variable"""
        
        for l in xrange(self.NUM_ROOM):
            self.BAV_z_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['BAV_z_LK', str(l), str(k)]
                name = '_'.join(name)         
#                self.BAV_z_LK[l].append(self.model.addVar(vtype=GRB.BINARY, name=name))
                self.BAV_z_LK[l].append(self.model.addVar(lb=0, ub=1, vtype=GRB.CONTINUOUS, name=name))
             
        self.model.update()
        logging.debug("BAV_z_LK:\n %s" %self.BAV_z_LK)
         
    def _createDAV_Attendee_LK(self):
        """For each location at each timestamp, create an auxiliary variable representing number of attendee"""
         
        for l in xrange(self.NUM_ROOM):
            self.DAV_Attendee_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['DAV_Attendee_LK', str(l), str(k)]
                name = '_'.join(name)         
#                self.DAV_Attendee_LK[l].append(self.model.addVar(lb=0, vtype=GRB.INTEGER, name=name))
                self.DAV_Attendee_LK[l].append(self.model.addVar(lb=0, vtype=GRB.CONTINUOUS, name=name))                 
        self.model.update()
        logging.debug("DAV_Attendee_LK:\n %s" %self.DAV_Attendee_LK)
        
    #===========================================================================
    # Auxiliary Variables: HVAC
    #===========================================================================
    def _createCAV_RoomTemperature(self):
        """For each location at each timestep, create an auxiliary variable of room temperature T(k, l)"""
        for l in xrange(self.NUM_ROOM):
            self.CAV_T_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['CAV_T_LK', str(l), str(k)]
                name = '_'.join(name)         
                
                self.CAV_T_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_T_LK:\n %s" %self.CAV_T_LK)
        
    def _createCAV_T_z1_l(self):
        for l in xrange(self.NUM_ROOM):
            self.CAV_T_z1_l_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['CAV_T_z1_l_LK', str(l), str(k)]                
                name = '_'.join(name)         
                
                self.CAV_T_z1_l_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_T_z1_l_LK:\n %s" %self.CAV_T_z1_l_LK)
        
    def _createCAV_T_z2_l(self):
        for l in xrange(self.NUM_ROOM):
            self.CAV_T_z2_l_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['CAV_T_z2_l_LK', str(l), str(k)]
                name = '_'.join(name)         
                
                self.CAV_T_z2_l_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_T_z2_l_LK:\n %s" %self.CAV_T_z2_l_LK)
        
    def _createCAV_T_z3_l(self):
        for l in xrange(self.NUM_ROOM):
            self.CAV_T_z3_l_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['CAV_T_z3_l_LK', str(l), str(k)]
                name = '_'.join(name)         
                
                self.CAV_T_z3_l_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_T_z3_l_LK:\n %s" %self.CAV_T_z3_l_LK)
        
    def _createCAV_T_z4_l(self):
        for l in xrange(self.NUM_ROOM):
            self.CAV_T_z4_l_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['CAV_T_z4_l_LK', str(l), str(k)]
                name = '_'.join(name)         
                
                self.CAV_T_z4_l_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_T_z4_l_LK:\n %s" %self.CAV_T_z4_l_LK)
        
    def _createCAV_T_l_z1(self):
        for l in xrange(self.NUM_ROOM):
            self.CAV_T_l_z1_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['CAV_T_l_z1_LK', str(l), str(k)]                
                name = '_'.join(name)         
                
                self.CAV_T_l_z1_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_T_l_z1_LK:\n %s" %self.CAV_T_l_z1_LK)
        
    def _createCAV_T_l_z2(self):
        for l in xrange(self.NUM_ROOM):
            self.CAV_T_l_z2_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['CAV_T_l_z2_LK', str(l), str(k)]
                name = '_'.join(name)         
                
                self.CAV_T_l_z2_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_T_l_z2_LK:\n %s" %self.CAV_T_l_z2_LK)
        
    def _createCAV_T_l_z3(self):
        for l in xrange(self.NUM_ROOM):
            self.CAV_T_l_z3_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['CAV_T_l_z3_LK', str(l), str(k)]
                name = '_'.join(name)         
                
                self.CAV_T_l_z3_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_T_l_z3_LK:\n %s" %self.CAV_T_l_z3_LK)
        
    def _createCAV_T_l_z4(self):
        for l in xrange(self.NUM_ROOM):
            self.CAV_T_l_z4_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['CAV_T_l_z4_LK', str(l), str(k)]
                name = '_'.join(name)         
                
                self.CAV_T_l_z4_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_T_l_z4_LK:\n %s" %self.CAV_T_l_z4_LK)
        
    def _createCAV_T_l_f(self):
        for l in xrange(self.NUM_ROOM):
            self.CAV_T_l_f_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['CAV_T_l_f_LK', str(l), str(k)]
                name = '_'.join(name)         
                
                self.CAV_T_l_f_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_T_l_f_LK:\n %s" %self.CAV_T_l_f_LK)
        
    def _createCAV_T_l_c(self):
        for l in xrange(self.NUM_ROOM):
            self.CAV_T_l_c_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['CAV_T_l_c_LK', str(l), str(k)]
                name = '_'.join(name)         
                
                self.CAV_T_l_c_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_T_l_c_LK:\n %s" %self.CAV_T_l_c_LK)
        
    def _createCAV_A_SA_T_z_LK(self):
        """For each location at each timestep, create an auxiliary variable of aT(SA, z)"""
        for l in xrange(self.NUM_ROOM):
            self.CAV_A_SA_T_z_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['CAV_A_SA_T_z_LK', str(l), str(k)]
                name = '_'.join(name)         
                
                self.CAV_A_SA_T_z_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_A_SA_T_z_LK:\n %s" %self.CAV_A_SA_T_z_LK)
        
    def _createCAV_A_SA_T_SA_LK(self):
        """For each location at each timestep, create an auxiliary variable of aT(SA, SA)"""
        for l in xrange(self.NUM_ROOM):
            self.CAV_A_SA_T_SA_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['CAV_A_SA_T_SA_LK', str(l), str(k)]
                name = '_'.join(name)         
                
                self.CAV_A_SA_T_SA_LK[l].append(self.model.addVar(vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_A_SA_T_SA_LK:\n %s" %self.CAV_A_SA_T_SA_LK)
    
    #===========================================================================
    # Auxiliary Variables: Energy Consumption
    #===========================================================================
    def _createCAV_EnergyConsumption_Fan(self):
        """For each location at each timestep, create an auxiliary variable of e_fan(k, l)"""
        
        for l in xrange(self.NUM_ROOM):
            self.CAV_E_FAN_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['CAV_E_FAN_LK', str(l), str(k)]
                name = '_'.join(name)         
                self.CAV_E_FAN_LK[l].append(self.model.addVar(lb=0, vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_E_FAN_LK:\n %s" %self.CAV_E_FAN_LK)
        
    def _createCAV_EnergyConsumption_Conditioning(self):
        """For each location at each timestep, create an auxiliary variable of e_conditioning(k, l)"""
        
        for l in xrange(self.NUM_ROOM):
            self.CAV_E_CONDITIONING_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['CAV_E_CONDITIONING_LK', str(l), str(k)]
                name = '_'.join(name)         
                self.CAV_E_CONDITIONING_LK[l].append(self.model.addVar(lb=0, vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_E_CONDITIONING_LK:\n %s" %self.CAV_E_CONDITIONING_LK)
    
    def _createCAV_EnergyConsumption_Heating(self):
        """For each location at each timestep, create an auxiliary variable of e_heating(k, l)"""
        
        for l in xrange(self.NUM_ROOM):
            self.CAV_E_HEATING_LK.append([])
            for k in xrange(self.NUM_SLOT):
                name = ['CAV_E_HEATING_LK', str(l), str(k)]
                name = '_'.join(name)         
                self.CAV_E_HEATING_LK[l].append(self.model.addVar(lb=0, vtype=GRB.CONTINUOUS, name=name))
                
        self.model.update()
        logging.debug("CAV_E_HEATING_LK:\n %s" %self.CAV_E_HEATING_LK)
        
    #===========================================================================
    # Constraints
    #===========================================================================   
    
    #===========================================================================
    # Constraints: Room Alloc Based on Meeting Type
    #===========================================================================  
    def _createCSTR_Schedule_Once_MT(self):
        """Every meeting type must be scheduled to start at one feasible location exactly once within their respective time window."""
        
        for m in xrange(self.NUM_MEETING_TYPE):   
            num_meeting = len(self.EAMS.MTYPE[m].MLS) 
            self.CSTR_Schedule_Once_M.append([])                
            lcstr = 0
            for l in xrange(len(self.BDV_x_MLK[m])):                                    
                for k in xrange(len(self.BDV_x_MLK[m][l])):
                    lcstr += self.BDV_x_MLK[m][l][k] 
            
            name = ['CSTR_Schedule_Once_M', str(m)]
            name = '_'.join(name)
            self.CSTR_Schedule_Once_M[m].append(self.model.addConstr(lcstr == num_meeting, name))
                 
        self.model.update()
        logging.debug("CSTR_Schedule_Once_M:\n %s" %self.CSTR_Schedule_Once_M)  
        
    def _createCSTR_LocationTimeOccupied_MT(self):
        """Set BAV_z_LK=1 at all time periods k if meeting type m is allocated in room L"""
        
        for k in xrange(self.NUM_SLOT):             
            lcstr = []
            for l in xrange(self.NUM_ROOM):
                lcstr.append([])
                lcstr[l] = 0
                                     
            for m in xrange(self.NUM_MEETING_TYPE):
                # Get feasible start time from any one meeting in MLS
                mid = self.EAMS.MTYPE[m].MLS[0]
                   
                k_m = []
                k_m = self.EAMS.getFeasibleStartTime(mid, k)
                if k_m:
                    logging.debug("Meeting Type %d starts at %s still on-going at time period %d" %(m, k_m, k))                        
                    for l in xrange(self.NUM_ROOM):
                        if l in self.EAMS.MR[mid]:  #TODO: currently assume all meetings of the same type can use the same room! Need to re-group if not (_populateMeetingClique) !
                            for i in xrange(len(k_m)):
                                mlk = self.BDV_x_MLK_Dict.get(tuple([m, l, k_m[i]]))
#                                 logging.debug("MLK_%s" %mlk)                            
                                lcstr[l] += self.BDV_x_MLK[mlk[0]][mlk[1]][mlk[2]]
                            
            self.CSTR_LocationTimeOccupied.append([])
            for l in xrange(self.NUM_ROOM):  
                if lcstr[l]:
                    rcstr = self.BAV_z_LK[l][k]
#                     logging.debug("k:%d, l:%d, lcstr=%s" %(k,l,lcstr[l]))              
                    name = ['CSTR_LocationTimeOccupied_KL', str(k), str(l)]
                    name = '_'.join(name)
                    self.CSTR_LocationTimeOccupied[k].append(self.model.addConstr(lcstr[l] <= rcstr, name))
                    
        self.model.update()
        logging.debug("CSTR_LocationTimeOccupied:\n %s" %self.CSTR_LocationTimeOccupied)
           
    def _createCSTR_NumAttendee_MT(self):
        """For each meeting type, represent number of attendee as a unique constraint. Note: Number of attendee is grouped by 5, 15, 30 people."""
        
        for k in xrange(self.NUM_SLOT):             
            lcstr = []
            for l in xrange(self.NUM_ROOM):
                lcstr.append([])
                lcstr[l] = 0
                                     
            for m in xrange(self.NUM_MEETING_TYPE):   
                # Get feasible start time from any one meeting in MLS
                mid = self.EAMS.MTYPE[m].MLS[0]
                     
                k_m = []
                k_m = self.EAMS.getFeasibleStartTime(mid, k)
                if k_m:
#                     logging.debug("Meeting %d starts at %s still on-going at time period %d" %(m, k_m, k))                        
                    for l in xrange(self.NUM_ROOM):
                        if l in self.EAMS.MR[m]:    #TODO: currently assume all meetings of the same type can use the same room! Need to re-group if not (_populateMeetingClique) !
                            for i in xrange(len(k_m)):
                                mlk = self.BDV_x_MLK_Dict.get(tuple([m, l, k_m[i]]))
#                                 logging.debug("MLK_%s" %mlk)                            
                                lcstr[l] += len(self.EAMS.ML[m].Attendees)*self.BDV_x_MLK[mlk[0]][mlk[1]][mlk[2]]
                            
            self.CSTR_NumAttendee.append([])
            for l in xrange(self.NUM_ROOM):
                rcstr = self.DAV_Attendee_LK[l][k]
#                     logging.debug("k:%d, l:%d, lcstr=%s" %(k,l,lcstr[l]))              
                name = ['CSTR_NumAttendee_LK', str(l), str(k)]
                name = '_'.join(name)  
                if lcstr[l]:
                    self.CSTR_NumAttendee[k].append(self.model.addConstr(lcstr[l] == rcstr, name))
                else:
                    self.CSTR_NumAttendee[k].append(self.model.addConstr(0 == rcstr, name))
                    
        self.model.update()
        logging.debug("CSTR_NumAttendee:\n %s" %self.CSTR_NumAttendee)
        
    def _createCSTR_AttendeeConflict_MT(self):
        """Meetings Types which have the same attendee(s) should not be allocated into the same time period"""
        
        # CMT has duplicate MT set for different attendee, create a unique list.  
        #  {'1068': [1, 2], '6153': [0, 1, 2], '2425': [0, 1], '895': [0, 1]}
        #  -->  [1,2], [0,1,2], [0,1]   
        uniq_mtls = []
        mtls = self.EAMS.CMT.values() 
        for s in xrange(len(mtls)):
            if mtls[s] not in uniq_mtls:
                uniq_mtls.append(mtls[s]) 
        logging.debug("************************************** uniq_mtls:%s" %uniq_mtls)
                
        for k in xrange(self.NUM_SLOT):
            self.CSTR_AttendeeConflict.append([])
            for s in xrange(len(uniq_mtls)):      #TODO: this loop can be improved!      
                mts = uniq_mtls[s]
#                 logging.debug("Conflict Meeting Types:%s" %mts)
                om = []
                for mt in xrange(len(mts)):
                    mtid = mts[mt]                    
                    m = self.EAMS.MTYPE[mtid].MLS[0]
                    if self.EAMS.isInTimeWindows(m,k) > 0:   
                        logging.debug("++ k: %d" %k)    
                        logging.debug("----%s" %self.EAMS.getFeasibleStartTime(m, k))
                        om.append([mtid, self.EAMS.getFeasibleStartTime(m, k)])
                
                if len(om)>1: # has conflict
                        logging.debug("om: %s" %om)
                        lcstr = 0
                        for j in xrange(len(om)):    
                            logging.debug("om[%d]: %s" %(j,om[j]))    
                            logging.debug("om[%d][0]: %s" %(j, om[j][0]))
                            mk = om[j][1]
                            for p in xrange(len(mk)):
                                logging.debug("om[%d][1] [%d]: %s" %(j, p, mk[p]))      
                                         
                                for l in xrange(self.NUM_ROOM):
                                    mlk = self.BDV_x_MLK_Dict.get(tuple([om[j][0], l, mk[p]]))    
                                    logging.debug("MLK_%s" %mlk)
                                    if mlk:
                                        lcstr += self.BDV_x_MLK[mlk[0]][mlk[1]][mlk[2]]
                        logging.debug(lcstr)
                        name = ['CSTR_AttendeeConflict_K_CM', str(k), str(m)]
                        name = '_'.join(name)
                        self.CSTR_AttendeeConflict[k].append(self.model.addConstr(lcstr <= 1, name))
                    
        self.model.update()
        logging.debug("CSTR_AttendeeConflict:\n %s" %self.CSTR_AttendeeConflict)
        
        
            
    #===========================================================================
    # Constraints: Room Alloc
    #===========================================================================  
    def _createCSTR_Schedule_Once(self):
        """Every meeting must be scheduled to start at one feasible location exactly once within their respective time window."""
        
        for m in xrange(self.NUM_MEETING):    
            self.CSTR_Schedule_Once_M.append([])                
            lcstr = 0
            for l in xrange(len(self.BDV_x_MLK[m])):                                    
                for k in xrange(len(self.BDV_x_MLK[m][l])):
                    lcstr += self.BDV_x_MLK[m][l][k] 
            
            name = ['CSTR_Schedule_Once_M', str(m)]
            name = '_'.join(name)
            self.CSTR_Schedule_Once_M[m].append(self.model.addConstr(lcstr == 1, name))
                 
        self.model.update()
        logging.debug("CSTR_Schedule_Once_M:\n %s" %self.CSTR_Schedule_Once_M)   
        
#     def _createCSTR_UniqueLocation(self):    
#         """No more than one meeting in the same location at the same time."""
#             
#         for k in xrange(self.NUM_SLOT):  # TODO: improve this to working hour only. (and make sure all meeting start and finish within working hour)            
#             lcstr = []
#             for l in xrange(self.NUM_ROOM):
#                 lcstr.append([])
#                 lcstr[l] = 0
#                                      
#             for m in xrange(self.NUM_MEETING):  
#                 if self.EAMS.isInTimeWindows(m,k) > 0:                   
#                     k_m = []
#                     k_m = self.EAMS.getFeasibleStartTime(m, k)
#                     if k_m:
#     #                     logging.debug("Meeting %d starts at %s still on-going at time period %d" %(m, k_m, k))                        
#                         for l in xrange(self.NUM_ROOM):
#                             if l in self.EAMS.MR[m]:
#                                 for i in xrange(len(k_m)):
#                                     mlk = self.BDV_x_MLK_Dict.get(tuple([m, l, k_m[i]]))
#     #                                 logging.debug("MLK_%s" %mlk)                            
#                                     lcstr[l] += self.BDV_x_MLK[mlk[0]][mlk[1]][mlk[2]]
#                             
#             self.CSTR_UniqueLocation.append([])
#             for l in xrange(self.NUM_ROOM):  
#                 if lcstr[l]:
#                     logging.debug("k:%d, l:%d, lcstr=%s" %(k,l,lcstr[l]))              
#                     name = ['CSTR_UniqueLocation_KL', str(k), str(l)]
#                     name = '_'.join(name)
#                     self.CSTR_UniqueLocation[k].append(self.model.addConstr(lcstr[l] <= 1, name))
#                     
#         self.model.update()
#         logging.debug("CSTR_UniqueLocation:\n %s" %self.CSTR_UniqueLocation)
                    
    
    def _createCSTR_LocationTimeOccupied(self):
        """Set BAV_z_LK=1 at all time periods k if meeting m is allocated in room L"""
        
        for k in xrange(self.NUM_SLOT):  # TODO: improve this to working hour only. (and make sure all meeting start and finish within working hour)            
            lcstr = []
            for l in xrange(self.NUM_ROOM):
                lcstr.append([])
                lcstr[l] = 0
                                     
            for m in xrange(self.NUM_MEETING):   
                k_m = []
                k_m = self.EAMS.getFeasibleStartTime(m, k)
                if k_m:
#                     logging.debug("Meeting %d starts at %s still on-going at time period %d" %(m, k_m, k))                        
                    for l in xrange(self.NUM_ROOM):
                        if l in self.EAMS.MR[m]:
                            for i in xrange(len(k_m)):
                                mlk = self.BDV_x_MLK_Dict.get(tuple([m, l, k_m[i]]))
#                                 logging.debug("MLK_%s" %mlk)                            
                                lcstr[l] += self.BDV_x_MLK[mlk[0]][mlk[1]][mlk[2]]
                            
            self.CSTR_LocationTimeOccupied.append([])
            for l in xrange(self.NUM_ROOM):  
                if lcstr[l]:
                    rcstr = self.BAV_z_LK[l][k]
#                     logging.debug("k:%d, l:%d, lcstr=%s" %(k,l,lcstr[l]))              
                    name = ['CSTR_LocationTimeOccupied_KL', str(k), str(l)]
                    name = '_'.join(name)
                    self.CSTR_LocationTimeOccupied[k].append(self.model.addConstr(lcstr[l] <= rcstr, name))
                    
        self.model.update()
        logging.debug("CSTR_LocationTimeOccupied:\n %s" %self.CSTR_LocationTimeOccupied)
        
#     def _createCSTR_TotalAllocatedSlot(self):
#         """Force BAV_z_LK=0 at all time k if no meeting is allocated in room L at time period k"""
#         for k in xrange(self.NUM_SLOT):  # TODO: improve this to working hour only. (and make sure all meeting start and finish within working hour)            
#             lcstr = []
#             for l in xrange(self.NUM_ROOM):
#                 lcstr.append([])
#                 lcstr[l] = 0
#                                      
#             for m in xrange(self.NUM_MEETING):   
#                 k_m = []
#                 k_m = self.EAMS.getFeasibleStartTime(m, k)
#                 if k_m:
# #                     logging.debug("Meeting %d starts at %s still on-going at time period %d" %(m, k_m, k))                        
#                     for l in xrange(self.NUM_ROOM):
#                         if l in self.EAMS.MR[m]:
#                             for i in xrange(len(k_m)):
#                                 mlk = self.BDV_x_MLK_Dict.get(tuple([m, l, k_m[i]]))
# #                                 logging.debug("MLK_%s" %mlk)                            
#                                 lcstr[l] += self.BDV_x_MLK[mlk[0]][mlk[1]][mlk[2]]
#                             
#             self.CSTR_TotalAllocatedSlot.append([])
#             for l in xrange(self.NUM_ROOM):  
#                 if lcstr[l]:
#                     rcstr = self.BAV_z_LK[l][k]
# #                     logging.debug("k:%d, l:%d, lcstr=%s" %(k,l,lcstr[l]))              
#                     name = ['CSTR_TotalAllocatedSlot_KL', str(k), str(l)]
#                     name = '_'.join(name)
#                     self.CSTR_TotalAllocatedSlot[k].append(self.model.addConstr(lcstr[l] >= rcstr, name))
#                     
#         self.model.update()
#         logging.debug("CSTR_TotalAllocatedSlot:\n %s" %self.CSTR_TotalAllocatedSlot)
        
    def _createCSTR_NumAttendee(self):
        """For each meeting, represent number of attendee as a unique constraint"""
        
        for k in xrange(self.NUM_SLOT):  # TODO: improve this to working hour only. (and make sure all meeting start and finish within working hour)            
            lcstr = []
            for l in xrange(self.NUM_ROOM):
                lcstr.append([])
                lcstr[l] = 0
                                     
            for m in xrange(self.NUM_MEETING):        
                k_m = []
                k_m = self.EAMS.getFeasibleStartTime(m, k)
                if k_m:
#                     logging.debug("Meeting %d starts at %s still on-going at time period %d" %(m, k_m, k))                        
                    for l in xrange(self.NUM_ROOM):
                        if l in self.EAMS.MR[m]:
                            for i in xrange(len(k_m)):
                                mlk = self.BDV_x_MLK_Dict.get(tuple([m, l, k_m[i]]))
#                                 logging.debug("MLK_%s" %mlk)                            
                                lcstr[l] += len(self.EAMS.ML[m].Attendees)*self.BDV_x_MLK[mlk[0]][mlk[1]][mlk[2]]
                            
            self.CSTR_NumAttendee.append([])
            for l in xrange(self.NUM_ROOM):
                rcstr = self.DAV_Attendee_LK[l][k]
#                     logging.debug("k:%d, l:%d, lcstr=%s" %(k,l,lcstr[l]))              
                name = ['CSTR_NumAttendee_LK', str(l), str(k)]
                name = '_'.join(name)  
                if lcstr[l]:
                    self.CSTR_NumAttendee[k].append(self.model.addConstr(lcstr[l] == rcstr, name))
                else:
                    self.CSTR_NumAttendee[k].append(self.model.addConstr(0 == rcstr, name))
                    
        self.model.update()
        logging.debug("CSTR_NumAttendee:\n %s" %self.CSTR_NumAttendee)
        
    def _createCSTR_AttendeeConflict(self):
        """Meetings which have the same attendee(s) should not be allocated into the same time period"""
                
        for k in xrange(self.NUM_SLOT):  # TODO: improve this to working hour only. (and make sure all meeting start and finish within working hour)
            logging.debug("k[%d] ----- " %(k))
            self.CSTR_AttendeeConflict.append([])
            
            for m in xrange(len(self.EAMS.MOM)):
                if self.EAMS.MOM[m] and self.EAMS.isInTimeWindows(m,k) > 0:
                    ml = [m]
                    ml.extend(self.EAMS.MOM[m])
                    
                    om = []
                    for i in xrange(len(ml)):
                        if self.EAMS.isInTimeWindows(ml[i],k) > 0:                        
                            logging.debug("at k[%d], meeting [%d] %s" %(k, ml[i], self.EAMS.getFeasibleStartTime(ml[i], k)))
                            om.append([ml[i], self.EAMS.getFeasibleStartTime(ml[i], k)])
                    
                    if len(om)>1: # more than 1 meeting
                        logging.debug("om: %s" %om)
                        lcstr = 0
                        for j in xrange(len(om)):    
                            logging.debug("om[%d]: %s" %(j,om[j]))    
                            logging.debug("om[%d][0]: %s" %(j, om[j][0]))
                            mk = om[j][1]
                            for p in xrange(len(mk)):
                                logging.debug("om[%d][1] [%d]: %s" %(j, p, mk[p]))      
                                         
                                for l in xrange(self.NUM_ROOM):
                                    mlk = self.BDV_x_MLK_Dict.get(tuple([om[j][0], l, mk[p]]))    
                                    logging.debug("MLK_%s" %mlk)
                                    if mlk:
                                        lcstr += self.BDV_x_MLK[mlk[0]][mlk[1]][mlk[2]]
                        logging.debug(lcstr)
                        name = ['CSTR_AttendeeConflict_K_CM', str(k), str(m)]
                        name = '_'.join(name)
                        self.CSTR_AttendeeConflict[k].append(self.model.addConstr(lcstr <= 1, name))
                    
        self.model.update()
        logging.debug("CSTR_AttendeeConflict:\n %s" %self.CSTR_AttendeeConflict)
                                  
    
    #===========================================================================
    # Constraints: HVAC
    #===========================================================================
    def _createCSTR_SupplyAirTemperature_LB_noStandbyMode(self):
        for l in xrange(self.NUM_ROOM):        
            self.CSTR_T_SA_LK.append([])
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_T_SA_LK', str(l), str(k)]
                name = '_'.join(name)                
                 
                lcstr = self.CDV_T_SA_LK[l][k]
                
                # Method 1:
#                 if self.EAMS.SH[k] == 1:
#                     rcstr = float(self.EAMS.TEMPERATURE_CONDITIONED_AIR) * self.BAV_z_LK[l][k] 
#                     self.CSTR_T_SA_LK[l].append(self.model.addConstr(lcstr >= rcstr, name))
#                 else:
#                     self.CSTR_T_SA_LK[l].append(self.model.addConstr(lcstr == 0, name))

                # Method 2:
                if self.EAMS.SH[k] == 1:
                    rcstr = float(self.EAMS.TEMPERATURE_CONDITIONED_AIR)
                    self.CSTR_T_SA_LK[l].append(self.model.addConstr(lcstr >= rcstr, name))
                else:
                    self.CSTR_T_SA_LK[l].append(self.model.addConstr(lcstr == 0, name))
                    
                # Method 3:
#                 rcstr = float(self.EAMS.TEMPERATURE_CONDITIONED_AIR) * self.BAV_z_LK[l][k]
#                 self.CSTR_T_SA_LK[l].append(self.model.addConstr(lcstr >= rcstr, name))

             
        self.model.update()
        logging.debug("CSTR_T_SA_LK:\n %s" %self.CSTR_T_SA_LK)
        
        
    def _createCSTR_SupplyAirTemperature_LB_hasStandbyMode(self):
        for l in xrange(self.NUM_ROOM):        
            self.CSTR_T_SA_LB_LK.append([])
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_T_SA_LB_LK', str(l), str(k)]
                name = '_'.join(name)               
                 
                lcstr = self.CDV_T_SA_LK[l][k]
                if self.EAMS.SH[k] == 1:
                    rcstr = float(self.EAMS.TEMPERATURE_CONDITIONED_AIR)
                    self.CSTR_T_SA_LB_LK[l].append(self.model.addConstr(lcstr >= rcstr, name))
                else:
                    lk = self.BDV_w_LK_Dict.get(tuple([l, k]))
                    rcstr = float(self.EAMS.TEMPERATURE_CONDITIONED_AIR) * self.BDV_w_LK[lk[0]][lk[1]]
                    self.CSTR_T_SA_LB_LK[l].append(self.model.addConstr(lcstr >= rcstr, name))
                             
        self.model.update()
        logging.debug("CSTR_T_SA_LB_LK:\n %s" %self.CSTR_T_SA_LB_LK)
        
    def _createCSTR_SupplyAirTemperature_UB_hasStandbyMode(self):
        for l in xrange(self.NUM_ROOM):        
            self.CSTR_T_SA_UB_LK.append([])
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_T_SA_UB_LK', str(l), str(k)]
                name = '_'.join(name)               
                 
                lcstr = self.CDV_T_SA_LK[l][k]
                # Not necessary to set the upper bound of SH==1, as it is the same as T_SA default UB
                if self.EAMS.SH[k] == 0: 
                    lk = self.BDV_w_LK_Dict.get(tuple([l, k]))
                    rcstr = float(self.EAMS.TEMPERATURE_SUPPLY_AIR_HIGH) * self.BDV_w_LK[lk[0]][lk[1]]
                    self.CSTR_T_SA_UB_LK[l].append(self.model.addConstr(lcstr <= rcstr, name))
                             
        self.model.update()
        logging.debug("CSTR_T_SA_UB_LK:\n %s" %self.CSTR_T_SA_UB_LK)
        
#--------------------------------------    
    def _createCSTR_SupplyAirFlowRate_LB_noStandbyMode(self):
        """For each location at each timestep, create a constraint for lower bound of air mass flow rate"""
        
        for l in xrange(self.NUM_ROOM):
            self.CSTR_A_SA_LB_LK.append([])
            
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_A_SA_LB_LK', str(l), str(k)]
                name = '_'.join(name)                
                
                lcstr = self.CDV_A_SA_LK[l][k]
                rcstr = self._getA_SA_LB(l,k)
                if self.EAMS.SH[k] == 1:                    
                    self.CSTR_A_SA_LB_LK[l].append(self.model.addConstr(lcstr >= rcstr, name))
                else:
                    self.CSTR_A_SA_LB_LK[l].append(self.model.addConstr(lcstr == rcstr, name))
                    
        self.model.update()
        logging.debug("CSTR_A_SA_LB_LK:\n %s" %self.CSTR_A_SA_LB_LK)
        
    def _createCSTR_SupplyAirFlowRate_LB_hasStandbyMode(self):
        """For each location at each timestep, create a constraint for lower bound of air mass flow rate"""
        
        for l in xrange(self.NUM_ROOM):
            self.CSTR_A_SA_LB_LK.append([])
            
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_A_SA_LB_LK', str(l), str(k)]
                name = '_'.join(name)                
                
                lcstr = self.CDV_A_SA_LK[l][k]
                if self.EAMS.SH[k] == 1:
                    rcstr = self._getA_SA_LB(l,k)
                else: 
                    #TODO:  as long as ASA_LB for sh[k]=0 is set to 0, this cstr can be removed.
                    lk = self.BDV_w_LK_Dict.get(tuple([l, k]))
                    rcstr = self._getA_SA_LB(l,k) * self.BDV_w_LK[lk[0]][lk[1]]
                self.CSTR_A_SA_LB_LK[l].append(self.model.addConstr(lcstr >= rcstr, name))
                    
        self.model.update()
        logging.debug("CSTR_A_SA_LB_LK:\n %s" %self.CSTR_A_SA_LB_LK)
        
    def _createCSTR_SupplyAirFlowRate_UB_hasStandbyMode(self):
        for l in xrange(self.NUM_ROOM):
            self.CSTR_A_SA_UB_LK.append([])            
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_A_SA_UB_LK', str(l), str(k)]
                name = '_'.join(name)                
                
                lcstr = self.CDV_A_SA_LK[l][k]
                if self.EAMS.SH[k] == 0: # Not necessary to set the upper bound of SH==1, as it is the same as A_SA default UB
                    lk = self.BDV_w_LK_Dict.get(tuple([l, k]))
                    rcstr = self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MAX * self.BDV_w_LK[lk[0]][lk[1]]
                    self.CSTR_A_SA_UB_LK[l].append(self.model.addConstr(lcstr <= rcstr, name))
                    
        self.model.update()
        logging.debug("CSTR_A_SA_UB_LK:\n %s" %self.CSTR_A_SA_UB_LK)
                
        
#--------------------------------------             
    def _createCSTR_RoomTemperature_LB(self):
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_LK_lb.append([])
            for k in xrange(self.NUM_SLOT):   
                
                if self.EAMS.WH[k] == 1:             
                    name = ['CSTR_T_LK_lb', str(l), str(k)]
                    name = '_'.join(name)                
                     
                    lcstr = self.CAV_T_LK[l][k]
                    rcstr = float(self.EAMS.TEMPERATURE_UNOCC_MIN) + float(self.EAMS.TEMPERATURE_OCC_COMFORT_RANGE_INCR)   
                    self.CSTR_T_LK_lb[l].append(self.model.addConstr(lcstr >= rcstr, name))
             
        self.model.update()
        logging.debug("CSTR_T_LK_lb:\n %s" %self.CSTR_T_LK_lb)
        
    def _createCSTR_RoomTemperature_UB(self):
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_LK_ub.append([])
            for k in xrange(self.NUM_SLOT):  
                
                if self.EAMS.WH[k] == 1:                 
                    name = ['CSTR_T_LK_ub', str(l), str(k)]
                    name = '_'.join(name)                
                     
                    lcstr = self.CAV_T_LK[l][k]
                    rcstr = float(self.EAMS.TEMPERATURE_UNOCC_MAX) - float(self.EAMS.TEMPERATURE_OCC_COMFORT_RANGE_DECR) 
                    self.CSTR_T_LK_ub[l].append(self.model.addConstr(lcstr <= rcstr, name))
             
        self.model.update()
        logging.debug("CSTR_T_LK_ub:\n %s" %self.CSTR_T_LK_ub)
    
    def _createCSTR_RoomTemperature(self):
        """For each location at each timestep, create a constraint for room temperature T(k, l)"""
        
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_LK.append([])
            
            A = self.EAMS.getRoomThermalConfig(l, "C")
            B1 =  self.EAMS.getRoomThermalConfig(l, "Rij")
            B2 =  self.EAMS.getRoomThermalConfig(l, "Rik")
            B3 =  self.EAMS.getRoomThermalConfig(l, "Ril")
            B4 =  self.EAMS.getRoomThermalConfig(l, "Rio")
            B5 =  self.EAMS.getRoomThermalConfig(l, "Rif")
            B6 =  self.EAMS.getRoomThermalConfig(l, "Ric")            
            #TODO: For the moment, only 1 wall could have window. Test with more windows
            B7 = self.EAMS.getRoomThermalConfig(l, "Rwij")            
            C = self.EAMS.AIR_HEAT_CAPACITY_AT_CONSTANT_PRESSURE            
            D = float(self.EAMS.SCHEDULING_INTERVAL)*60 / A            
            E1 = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (A*B1)
            E2 = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (A*B2)
            E3 = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (A*B3)
            E4 = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (A*B4)
            E5 = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (A*B5)
            E6 = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (A*B6)
            E7 = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (A*B7)
            F = D * self.EAMS.OCCUPANT_SENSIBLE_HEAT_GAIN
                
            for k in xrange(self.NUM_SLOT):          
                name = ['CSTR_T_LK', str(l), str(k)]
                name = '_'.join(name)
                
                if k != 0:
                    rcstr = (
                             (self.CAV_T_LK[l][k-1] - 
                             (D *
                              (
                              (self.CAV_T_LK[l][k-1] / B1) +
                            (self.CAV_T_LK[l][k-1] / B2) +
                            (self.CAV_T_LK[l][k-1] / B3) +
                            (self.CAV_T_LK[l][k-1] / B4) +
                            (self.CAV_T_LK[l][k-1] / B5) +
                            (self.CAV_T_LK[l][k-1] / B6) +
                            (self.CAV_T_LK[l][k-1] / B7) +
                              (C * self.CAV_A_SA_T_z_LK[l][k-1])
                              )
                             )
                             ) + 
                             (E1 * self.CAV_T_l_z1_LK[l][k-1]) +
                            (E2 * self.CAV_T_l_z2_LK[l][k-1]) +
                            (E3 * self.CAV_T_l_z3_LK[l][k-1]) +
                            (E4 * self.CAV_T_l_z4_LK[l][k-1]) +
                            (E5 * self.CAV_T_l_f_LK[l][k-1]) +
                            (E6 * self.CAV_T_l_c_LK[l][k-1]) +
                            (E7 * float(self.EAMS.OAT.values()[k-1])) +                             
                             (F * self.DAV_Attendee_LK[l][k-1]) + 
                             (D * C * self.CAV_A_SA_T_SA_LK[l][k-1]))
                    
                else: # no occupant at previous session (k=-1)
                    rcstr = self.EAMS.INITIAL_TEMPERATURE
                
                lcstr = self.CAV_T_LK[l][k]         
                self.CSTR_T_LK[l].append(self.model.addConstr(lcstr==rcstr, name))
                
        self.model.update()
        logging.debug("CSTR_T_LK:\n %s" %self.CSTR_T_LK)
        
   
    def _createCSTR_T_z1_l(self):        
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_z1_l_LK.append([])              
            
            nz = self.EAMS.RNL[l][0]
            A = float(self.EAMS.SCHEDULING_INTERVAL)*60 / self.EAMS.getRoomThermalConfig(l, "Cij")
            B = float(1)/self.EAMS.getRoomThermalConfig(l, "Rji")
            C = float(1)/self.EAMS.getRoomThermalConfig(l, "Rimj")
            D = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(l, "Cij") * self.EAMS.getRoomThermalConfig(l, "Rimj"))
            E = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(l, "Cij") * self.EAMS.getRoomThermalConfig(l, "Rji"))
            H = 1-(A*(B+C)) 
            
            logging.debug("Cij = %s" %(self.EAMS.getRoomThermalConfig(l, "Cij")))  
            logging.debug("A = %s" %(A))
            logging.debug("B = %s" %(B))
            logging.debug("C = %s" %(C))
            logging.debug("H = %s" %(H))
                                                 
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_T_z1_l_LK', str(l), str(k)]
                name = '_'.join(name)                
                 
                if k != 0:
                    if nz == N_OUTDOOR:
                        F = float(self.EAMS.OAT.values()[k-1])
                    elif nz == N_NOT_EXIST:
                        F = self.CAV_T_LK[l][k-1]
                    else:
                        F = self.CAV_T_LK[nz][k-1]
                    
                    G = self.EAMS.getRoomSolarGain(k-1, l, 0)
                        
                    rcstr = (
                             (H * self.CAV_T_z1_l_LK[l][k-1]) +
                             (D * self.CAV_T_l_z1_LK[l][k-1]) +
                             (E * F) +
                             (A * G)
                             )
                else:
                    rcstr = self.EAMS.INITIAL_TEMPERATURE
 
                lcstr = self.CAV_T_z1_l_LK[l][k]                 
                self.CSTR_T_z1_l_LK[l].append(self.model.addConstr(lcstr == rcstr, name))
              
        self.model.update()
        logging.debug("CSTR_T_z1_l_LK:\n %s" %self.CSTR_T_z1_l_LK)
        
    def _createCSTR_T_l_z1(self):
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_l_z1_LK.append([])
            
            A = float(self.EAMS.SCHEDULING_INTERVAL)*60 / self.EAMS.getRoomThermalConfig(l, "Cji")
            B = float(1)/self.EAMS.getRoomThermalConfig(l, "Rij")
            C = float(1)/self.EAMS.getRoomThermalConfig(l, "Rimj")
            D = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(l, "Cji") * self.EAMS.getRoomThermalConfig(l, "Rij"))
            E = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(l, "Cji") * self.EAMS.getRoomThermalConfig(l, "Rimj"))
            
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_T_l_z1_LK', str(l), str(k)]
                name = '_'.join(name)                
                 
                if k != 0:    
                    rcstr = (
                             ((1-A*(B+C))*self.CAV_T_l_z1_LK[l][k-1]) +
                             (D * self.CAV_T_LK[l][k-1]) +
                             (E * self.CAV_T_z1_l_LK[l][k-1])
                             )
                else:
                    rcstr = self.EAMS.INITIAL_TEMPERATURE 
                
                lcstr = self.CAV_T_l_z1_LK[l][k]
                self.CSTR_T_l_z1_LK[l].append(self.model.addConstr(lcstr == rcstr, name))
             
        self.model.update()
        logging.debug("CSTR_T_l_z1_LK:\n %s" %self.CSTR_T_l_z1_LK)
        
    def _createCSTR_T_z2_l(self):
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_z2_l_LK.append([])
            
            nz = self.EAMS.RNL[l][1]
            A = float(self.EAMS.SCHEDULING_INTERVAL)*60 / self.EAMS.getRoomThermalConfig(l, "Cik")
            B = float(1)/self.EAMS.getRoomThermalConfig(l, "Rki")
            C = float(1)/self.EAMS.getRoomThermalConfig(l, "Rimk")
            D = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(l, "Cik") * self.EAMS.getRoomThermalConfig(l, "Rimk"))
            E = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(l, "Cik") * self.EAMS.getRoomThermalConfig(l, "Rki"))
                                     
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_T_z2_l_LK', str(l), str(k)]
                name = '_'.join(name)                
                 
                if k != 0:
                    if nz == N_OUTDOOR:
                        F = float(self.EAMS.OAT.values()[k-1])
                    elif nz == N_NOT_EXIST:
                        F = self.CAV_T_LK[l][k-1]
                    else:
                        F = self.CAV_T_LK[nz][k-1]
                    
                    G = self.EAMS.getRoomSolarGain(k-1, l, 1)
                        
                    rcstr = (
                             ((1-A*(B+C))*self.CAV_T_z2_l_LK[l][k-1]) +
                             (D * self.CAV_T_l_z2_LK[l][k-1]) +
                             (E * F) +
                             (A * G)
                             )
                else:
                    rcstr = self.EAMS.INITIAL_TEMPERATURE
                    
#                 lcstr = self.CAV_T_l_z2_LK[l][k]  #BUG!!
                lcstr = self.CAV_T_z2_l_LK[l][k]
                self.CSTR_T_z2_l_LK[l].append(self.model.addConstr(lcstr == rcstr, name))
             
        self.model.update()
        logging.debug("CSTR_T_z2_l_LK:\n %s" %self.CSTR_T_z2_l_LK)
        
    def _createCSTR_T_l_z2(self):
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_l_z2_LK.append([])
            
            A = float(self.EAMS.SCHEDULING_INTERVAL)*60 / self.EAMS.getRoomThermalConfig(l, "Cki")
            B = float(1)/self.EAMS.getRoomThermalConfig(l, "Rik")
            C = float(1)/self.EAMS.getRoomThermalConfig(l, "Rimk")
            D = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(l, "Cki") * self.EAMS.getRoomThermalConfig(l, "Rik"))
            E = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(l, "Cki") * self.EAMS.getRoomThermalConfig(l, "Rimk"))
            
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_T_l_z2_LK', str(l), str(k)]
                name = '_'.join(name)                
                 
                if k != 0:    
                    rcstr = (
                             ((1-A*(B+C))*self.CAV_T_l_z2_LK[l][k-1]) +
                             (D * self.CAV_T_LK[l][k-1]) +
                             (E * self.CAV_T_z2_l_LK[l][k-1])
                             )
                else:
                    rcstr = self.EAMS.INITIAL_TEMPERATURE       
                 
                lcstr = self.CAV_T_l_z2_LK[l][k]
                self.CSTR_T_l_z2_LK[l].append(self.model.addConstr(lcstr == rcstr, name))
             
        self.model.update()
        logging.debug("CSTR_T_l_z2_LK:\n %s" %self.CSTR_T_l_z2_LK)
        
    def _createCSTR_T_z3_l(self):
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_z3_l_LK.append([])
            
            nz = self.EAMS.RNL[l][2]
            A = float(self.EAMS.SCHEDULING_INTERVAL)*60 / self.EAMS.getRoomThermalConfig(l, "Cil")
            B = float(1)/self.EAMS.getRoomThermalConfig(l, "Rli")
            C = float(1)/self.EAMS.getRoomThermalConfig(l, "Riml")
            D = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(l, "Cil") * self.EAMS.getRoomThermalConfig(l, "Riml"))
            E = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(l, "Cil") * self.EAMS.getRoomThermalConfig(l, "Rli"))
      
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_T_z3_l_LK', str(l), str(k)]
                name = '_'.join(name)        
                
                if k != 0:
                    if nz == N_OUTDOOR:
                        F = float(self.EAMS.OAT.values()[k-1])
                    elif nz == N_NOT_EXIST:
                        F = self.CAV_T_LK[l][k-1]
                    else:
                        F = self.CAV_T_LK[nz][k-1]
                    
                    G = self.EAMS.getRoomSolarGain(k-1, l, 2)
                        
                    rcstr = (
                             ((1-A*(B+C))*self.CAV_T_z3_l_LK[l][k-1]) +
                             (D * self.CAV_T_l_z3_LK[l][k-1]) +
                             (E * F) +
                             (A * G)
                             )
                else:
                    rcstr = self.EAMS.INITIAL_TEMPERATURE 
                 
                lcstr = self.CAV_T_z3_l_LK[l][k]                
                self.CSTR_T_z3_l_LK[l].append(self.model.addConstr(lcstr == rcstr, name))
             
        self.model.update()
        logging.debug("CSTR_T_z3_l_LK:\n %s" %self.CSTR_T_z3_l_LK)
        
    def _createCSTR_T_l_z3(self):
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_l_z3_LK.append([])
            
            A = float(self.EAMS.SCHEDULING_INTERVAL)*60 / self.EAMS.getRoomThermalConfig(l, "Cli")
            B = float(1)/self.EAMS.getRoomThermalConfig(l, "Ril")
            C = float(1)/self.EAMS.getRoomThermalConfig(l, "Riml")
            D = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(l, "Cli") * self.EAMS.getRoomThermalConfig(l, "Ril"))
            E = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(l, "Cli") * self.EAMS.getRoomThermalConfig(l, "Riml"))
            
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_T_l_z3_LK', str(l), str(k)]
                name = '_'.join(name)                
                 
                if k != 0:    
                    rcstr = (
                             ((1-A*(B+C))*self.CAV_T_l_z3_LK[l][k-1]) +
                             (D * self.CAV_T_LK[l][k-1]) +
                             (E * self.CAV_T_z3_l_LK[l][k-1])
                             )
                else:
                    rcstr = self.EAMS.INITIAL_TEMPERATURE       
                 
                lcstr = self.CAV_T_l_z3_LK[l][k]
                self.CSTR_T_l_z3_LK[l].append(self.model.addConstr(lcstr == rcstr, name))
             
        self.model.update()
        logging.debug("CSTR_T_l_z3_LK:\n %s" %self.CSTR_T_l_z3_LK)
             
    def _createCSTR_T_z4_l(self):
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_z4_l_LK.append([])
            
            nz = self.EAMS.RNL[l][3]
            A = float(self.EAMS.SCHEDULING_INTERVAL)*60 / self.EAMS.getRoomThermalConfig(l, "Cio")
            B = float(1)/self.EAMS.getRoomThermalConfig(l, "Roi")
            C = float(1)/self.EAMS.getRoomThermalConfig(l, "Rimo")
            D = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(l, "Cio") * self.EAMS.getRoomThermalConfig(l, "Rimo"))
            E = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(l, "Cio") * self.EAMS.getRoomThermalConfig(l, "Roi"))
      
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_T_z4_l_LK', str(l), str(k)]
                name = '_'.join(name)                
                 
                if k != 0:
                    if nz == N_OUTDOOR:
                        F = float(self.EAMS.OAT.values()[k-1])
                    elif nz == N_NOT_EXIST:
                        F = self.CAV_T_LK[l][k-1]
                    else:
                        F = self.CAV_T_LK[nz][k-1]
                    
                    G = self.EAMS.getRoomSolarGain(k-1, l, 3)
                        
                    rcstr = (
                             ((1-A*(B+C))*self.CAV_T_z4_l_LK[l][k-1]) +
                             (D * self.CAV_T_l_z4_LK[l][k-1]) +
                             (E * F) +
                             (A * G)
                             )
                else:
                    rcstr = self.EAMS.INITIAL_TEMPERATURE 
                    
                lcstr = self.CAV_T_z4_l_LK[l][k]                
                self.CSTR_T_z4_l_LK[l].append(self.model.addConstr(lcstr == rcstr, name))
             
        self.model.update()
        logging.debug("CSTR_T_z4_l_LK:\n %s" %self.CSTR_T_z4_l_LK)
        
    def _createCSTR_T_l_z4(self):
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_l_z4_LK.append([])
            
            A = float(self.EAMS.SCHEDULING_INTERVAL)*60 / self.EAMS.getRoomThermalConfig(l, "Coi")
            B = float(1)/self.EAMS.getRoomThermalConfig(l, "Rio")
            C = float(1)/self.EAMS.getRoomThermalConfig(l, "Rimo")
            D = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(l, "Coi") * self.EAMS.getRoomThermalConfig(l, "Rio"))
            E = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(l, "Coi") * self.EAMS.getRoomThermalConfig(l, "Rimo"))
            
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_T_l_z4_LK', str(l), str(k)]
                name = '_'.join(name)                
                 
                if k != 0:    
                    rcstr = (
                             ((1-A*(B+C))*self.CAV_T_l_z4_LK[l][k-1]) +
                             (D * self.CAV_T_LK[l][k-1]) +
                             (E * self.CAV_T_z4_l_LK[l][k-1])
                             )
                else:
                    rcstr = self.EAMS.INITIAL_TEMPERATURE                    
                 
                lcstr = self.CAV_T_l_z4_LK[l][k]                
                self.CSTR_T_l_z4_LK[l].append(self.model.addConstr(lcstr == rcstr, name))
             
        self.model.update()
        logging.debug("CSTR_T_l_z4_LK:\n %s" %self.CSTR_T_l_z4_LK)
        
    def _createCSTR_T_l_f(self):
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_l_f_LK.append([])
            
            A = float(self.EAMS.SCHEDULING_INTERVAL)*60 / self.EAMS.getRoomThermalConfig(l, "Cif")
            B = float(1)/self.EAMS.getRoomThermalConfig(l, "Rif")
            C = float(1)/self.EAMS.getRoomThermalConfig(l, "Rfi")
            D = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(l, "Cif") * self.EAMS.getRoomThermalConfig(l, "Rif"))
            E = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(l, "Cif") * self.EAMS.getRoomThermalConfig(l, "Rfi"))
            F = float(self.EAMS.SCHEDULING_INTERVAL)*60 / self.EAMS.getRoomThermalConfig(l, "Cfi")
       
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_T_l_f_LK', str(l), str(k)]
                name = '_'.join(name)                
                
                G = self.EAMS.getRoomSolarGain(k-1, l, 4)
                
                if k != 0:    
                    rcstr = (
                             ((1-A*(B+C))*self.CAV_T_l_f_LK[l][k-1]) +
                             (D * self.CAV_T_LK[l][k-1]) +
                             (E * self.CAV_T_LK[l][k-1]) +
                             (F * G)
                             )
                else:
                    rcstr = self.EAMS.INITIAL_TEMPERATURE     
                
                lcstr = self.CAV_T_l_f_LK[l][k]
                self.CSTR_T_l_f_LK[l].append(self.model.addConstr(lcstr == rcstr, name))
             
        self.model.update()
        logging.debug("CSTR_T_l_f_LK:\n %s" %self.CSTR_T_l_f_LK)
        
    def _createCSTR_T_l_c(self):
        for l in xrange(self.NUM_ROOM):
            self.CSTR_T_l_c_LK.append([])
            
            A = float(self.EAMS.SCHEDULING_INTERVAL)*60 / self.EAMS.getRoomThermalConfig(l, "Cic")
            B = float(1)/self.EAMS.getRoomThermalConfig(l, "Ric")
            C = float(1)/self.EAMS.getRoomThermalConfig(l, "Rci")
            D = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(l, "Cic") * self.EAMS.getRoomThermalConfig(l, "Ric"))
            E = float(self.EAMS.SCHEDULING_INTERVAL)*60 / (self.EAMS.getRoomThermalConfig(l, "Cic") * self.EAMS.getRoomThermalConfig(l, "Rci"))
            
            for k in xrange(self.NUM_SLOT):                
                name = ['CSTR_T_l_c_LK', str(l), str(k)]
                name = '_'.join(name)             
                
                if k != 0:    
                    rcstr = (
                             ((1-A*(B+C))*self.CAV_T_l_c_LK[l][k-1]) +
                             (D * self.CAV_T_LK[l][k-1]) +
                             (E * self.CAV_T_LK[l][k-1])
                             )
                else:
                    rcstr = self.EAMS.INITIAL_TEMPERATURE      
                 
                lcstr = self.CAV_T_l_c_LK[l][k]
                self.CSTR_T_l_c_LK[l].append(self.model.addConstr(lcstr == rcstr, name))
             
        self.model.update()
        logging.debug("CSTR_T_l_c_LK:\n %s" %self.CSTR_T_l_c_LK)        
        
#--------------------------------------------------
    def _createCSTR_A_SA_T_z_1_LK_looseboundedT_hasStandbyMode(self):
        T_LB    = float(self.EAMS.TEMPERATURE_UNOCC_MIN)
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_z_1_LK.append([])
                
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_z_1_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T       = self.CAV_T_LK[l][k]
                    A_SA    = self.CDV_A_SA_LK[l][k]
                    A_SA_LB = self._getA_SA_LB(l,k)                    
                    lcstr = self.CAV_A_SA_T_z_LK[l][k]
                    
                    rcstr = (A_SA_LB * T) + (T_LB * A_SA) - (A_SA_LB * T_LB)
                    self.CSTR_A_SA_T_z_1_LK[l].append(self.model.addQConstr(lcstr >= rcstr, name=name))
                        
        self.model.update()
        logging.debug("CSTR_A_SA_T_z_1_LK:\n %s" %self.CSTR_A_SA_T_z_1_LK)
        
    def _createCSTR_A_SA_T_z_2_LK_looseboundedT_hasStandbyMode(self):
        
        A_SA_UB = self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MAX
        T_UB    = float(self.EAMS.TEMPERATURE_UNOCC_MAX)        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_z_2_LK.append([])
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_z_2_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T = self.CAV_T_LK[l][k]                    
                    A_SA    = self.CDV_A_SA_LK[l][k]
                    
                    lcstr = self.CAV_A_SA_T_z_LK[l][k]
                    
                    rcstr = (A_SA_UB * T) + (T_UB * A_SA) - (A_SA_UB * T_UB)
                    self.CSTR_A_SA_T_z_2_LK[l].append(self.model.addQConstr(lcstr >= rcstr, name=name))
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_z_2_LK:\n %s" %self.CSTR_A_SA_T_z_2_LK)
        
        
    def _createCSTR_A_SA_T_z_3_LK_looseboundedT_hasStandbyMode(self):
        T_UB    = float(self.EAMS.TEMPERATURE_UNOCC_MAX)
        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_z_3_LK.append([])
                
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_z_3_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T       = self.CAV_T_LK[l][k]
                    A_SA    = self.CDV_A_SA_LK[l][k]
                    A_SA_LB = self._getA_SA_LB(l,k)
                    
                    lcstr = self.CAV_A_SA_T_z_LK[l][k]
                    
                    rcstr = (A_SA_LB * T) + (T_UB * A_SA) - (A_SA_LB * T_UB)
                    self.CSTR_A_SA_T_z_3_LK[l].append(self.model.addQConstr(lcstr <= rcstr, name=name))
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_z_3_LK:\n %s" %self.CSTR_A_SA_T_z_3_LK)
        
    def _createCSTR_A_SA_T_z_4_LK_looseboundedT_hasStandbyMode(self):
        
        A_SA_UB = self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MAX
        T_LB    = float(self.EAMS.TEMPERATURE_UNOCC_MIN)
        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_z_4_LK.append([])
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_z_4_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T       = self.CAV_T_LK[l][k]
                    A_SA    = self.CDV_A_SA_LK[l][k]                    
                    lcstr = self.CAV_A_SA_T_z_LK[l][k]
                    
                    rcstr = (A_SA_UB * T) + (T_LB * A_SA) - (A_SA_UB * T_LB)
                    self.CSTR_A_SA_T_z_4_LK[l].append(self.model.addQConstr(lcstr <= rcstr, name=name))
                    
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_z_4_LK:\n %s" %self.CSTR_A_SA_T_z_4_LK)
        
        
#---------------------------------------
    def _createCSTR_A_SA_T_z_1_LK_looseboundedT_noStandbyMode(self):
   
        T_LB    = float(self.EAMS.TEMPERATURE_UNOCC_MIN)
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_z_1_LK.append([])
                
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_z_1_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T       = self.CAV_T_LK[l][k]
                    A_SA    = self.CDV_A_SA_LK[l][k]     
                    A_SA_LB = self._getA_SA_LB(l,k)     
                    lcstr = self.CAV_A_SA_T_z_LK[l][k]
                    
                    if self.EAMS.SH[k] == 1:
                        rcstr = (A_SA_LB * T) + (T_LB * A_SA) - (A_SA_LB * T_LB)
                        self.CSTR_A_SA_T_z_1_LK[l].append(self.model.addQConstr(lcstr >= rcstr, name=name))
                    else:
                        self.CSTR_A_SA_T_z_1_LK[l].append(self.model.addQConstr(lcstr == 0, name=name))
                        
        self.model.update()
        logging.debug("CSTR_A_SA_T_z_1_LK:\n %s" %self.CSTR_A_SA_T_z_1_LK)
        
    def _createCSTR_A_SA_T_z_2_LK_looseboundedT_noStandbyMode(self):
        
        A_SA_UB = self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MAX
        T_UB    = float(self.EAMS.TEMPERATURE_UNOCC_MAX)
        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_z_2_LK.append([])
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_z_2_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T = self.CAV_T_LK[l][k]                    
                    A_SA    = self.CDV_A_SA_LK[l][k]
                    
                    lcstr = self.CAV_A_SA_T_z_LK[l][k]
                    
                    if self.EAMS.SH[k] == 1:
                        rcstr = (A_SA_UB * T) + (T_UB * A_SA) - (A_SA_UB * T_UB)
                        self.CSTR_A_SA_T_z_2_LK[l].append(self.model.addQConstr(lcstr >= rcstr, name=name))
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_z_2_LK:\n %s" %self.CSTR_A_SA_T_z_2_LK)
        
        
    def _createCSTR_A_SA_T_z_3_LK_looseboundedT_noStandbyMode(self):
        T_UB    = float(self.EAMS.TEMPERATURE_UNOCC_MAX)
        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_z_3_LK.append([])
                
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_z_3_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T       = self.CAV_T_LK[l][k]
                    A_SA    = self.CDV_A_SA_LK[l][k]
                    A_SA_LB = self._getA_SA_LB(l,k)
                    lcstr = self.CAV_A_SA_T_z_LK[l][k]
                    
                    if self.EAMS.SH[k] == 1:
                        rcstr = (A_SA_LB * T) + (T_UB * A_SA) - (A_SA_LB * T_UB)
                        self.CSTR_A_SA_T_z_3_LK[l].append(self.model.addQConstr(lcstr <= rcstr, name=name))
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_z_3_LK:\n %s" %self.CSTR_A_SA_T_z_3_LK)
        
    def _createCSTR_A_SA_T_z_4_LK_looseboundedT_noStandbyMode(self):
        
        A_SA_UB = self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MAX
        T_LB    = float(self.EAMS.TEMPERATURE_UNOCC_MIN)
        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_z_4_LK.append([])
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_z_4_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T       = self.CAV_T_LK[l][k]
                    A_SA    = self.CDV_A_SA_LK[l][k]                    
                    lcstr = self.CAV_A_SA_T_z_LK[l][k]
                    
                    if self.EAMS.SH[k] == 1:
                        rcstr = (A_SA_UB * T) + (T_LB * A_SA) - (A_SA_UB * T_LB)
                        self.CSTR_A_SA_T_z_4_LK[l].append(self.model.addQConstr(lcstr <= rcstr, name=name))
                    
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_z_4_LK:\n %s" %self.CSTR_A_SA_T_z_4_LK)

#-----------------------------------
        
    def _createCSTR_A_SA_T_SA_1_LK_hasStandbyMode(self):
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_SA_1_LK.append([])
                                
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_SA_1_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T_SA    = self.CDV_T_SA_LK[l][k]
                    T_SA_LB = self._get_T_SA_LB(l,k)
                    A_SA    = self.CDV_A_SA_LK[l][k]      
                    A_SA_LB = self._getA_SA_LB(l,k)
                                  
                    lcstr = self.CAV_A_SA_T_SA_LK[l][k]
                    
                    rcstr = (A_SA_LB * T_SA) + (T_SA_LB * A_SA) - (A_SA_LB * T_SA_LB)
                    self.CSTR_A_SA_T_SA_1_LK[l].append(self.model.addQConstr(lcstr >= rcstr, name=name))
                    
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_SA_1_LK:\n %s" %self.CSTR_A_SA_T_SA_1_LK)
        
    def _createCSTR_A_SA_T_SA_2_LK_hasStandbyMode(self):        
        A_SA_UB = self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MAX
        T_SA_UB = self.EAMS.TEMPERATURE_SUPPLY_AIR_HIGH
        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_SA_2_LK.append([])
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_SA_2_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T_SA    = self.CDV_T_SA_LK[l][k]   
                    A_SA    = self.CDV_A_SA_LK[l][k]
                    lcstr = self.CAV_A_SA_T_SA_LK[l][k]
                                        
                    rcstr = (A_SA_UB * T_SA) + (T_SA_UB * A_SA) - (A_SA_UB * T_SA_UB)
                    self.CSTR_A_SA_T_SA_2_LK[l].append(self.model.addQConstr(lcstr >= rcstr, name=name))
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_SA_2_LK:\n %s" %self.CSTR_A_SA_T_SA_2_LK)
        
        
    def _createCSTR_A_SA_T_SA_3_LK_hasStandbyMode(self):
        T_SA_UB = self.EAMS.TEMPERATURE_SUPPLY_AIR_HIGH        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_SA_3_LK.append([])
                                
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_SA_3_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T_SA    = self.CDV_T_SA_LK[l][k]
                    A_SA    = self.CDV_A_SA_LK[l][k]
                    A_SA_LB = self._getA_SA_LB(l,k)
                    
                    lcstr = self.CAV_A_SA_T_SA_LK[l][k]
                                        
                    rcstr = (A_SA_LB * T_SA) + (T_SA_UB * A_SA) - (A_SA_LB * T_SA_UB)
                    self.CSTR_A_SA_T_SA_3_LK[l].append(self.model.addQConstr(lcstr <= rcstr, name=name))
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_SA_3_LK:\n %s" %self.CSTR_A_SA_T_SA_3_LK)
        
    def _createCSTR_A_SA_T_SA_4_LK_hasStandbyMode(self):
        
        A_SA_UB = self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MAX
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_SA_4_LK.append([])
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_SA_4_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T_SA    = self.CDV_T_SA_LK[l][k]    
                    T_SA_LB = self._get_T_SA_LB(l,k)                   
                    A_SA    = self.CDV_A_SA_LK[l][k]                    
                    lcstr = self.CAV_A_SA_T_SA_LK[l][k]
                    
                    rcstr = (A_SA_UB * T_SA) + (T_SA_LB * A_SA) - (A_SA_UB * T_SA_LB)
                    self.CSTR_A_SA_T_SA_4_LK[l].append(self.model.addQConstr(lcstr <= rcstr, name=name))
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_SA_4_LK:\n %s" %self.CSTR_A_SA_T_SA_4_LK)   

#-----------------------------------
        
    def _createCSTR_A_SA_T_SA_1_LK_noStandbyMode(self):
        
        T_SA_LB = float(self.EAMS.TEMPERATURE_CONDITIONED_AIR)     
        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_SA_1_LK.append([])
                                
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_SA_1_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T_SA    = self.CDV_T_SA_LK[l][k]
                    A_SA    = self.CDV_A_SA_LK[l][k]
                    A_SA_LB = self._getA_SA_LB(l,k)
                    
                    lcstr = self.CAV_A_SA_T_SA_LK[l][k]
                    
                    if self.EAMS.SH[k] == 1:
                        rcstr = (A_SA_LB * T_SA) + (T_SA_LB * A_SA) - (A_SA_LB * T_SA_LB)
                        self.CSTR_A_SA_T_SA_1_LK[l].append(self.model.addQConstr(lcstr >= rcstr, name=name))
                    else:
                        self.CSTR_A_SA_T_SA_1_LK[l].append(self.model.addQConstr(lcstr == 0, name=name))
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_SA_1_LK:\n %s" %self.CSTR_A_SA_T_SA_1_LK)
        
    def _createCSTR_A_SA_T_SA_2_LK_noStandbyMode(self):
        
        A_SA_UB = self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MAX
        T_SA_UB = self.EAMS.TEMPERATURE_SUPPLY_AIR_HIGH
        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_SA_2_LK.append([])
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_SA_2_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T_SA    = self.CDV_T_SA_LK[l][k]   
                    A_SA    = self.CDV_A_SA_LK[l][k]
                    
                    lcstr = self.CAV_A_SA_T_SA_LK[l][k]
                    
                    if self.EAMS.SH[k] == 1:
                        rcstr = (A_SA_UB * T_SA) + (T_SA_UB * A_SA) - (A_SA_UB * T_SA_UB)
                        self.CSTR_A_SA_T_SA_2_LK[l].append(self.model.addQConstr(lcstr >= rcstr, name=name))
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_SA_2_LK:\n %s" %self.CSTR_A_SA_T_SA_2_LK)
        
        
    def _createCSTR_A_SA_T_SA_3_LK_noStandbyMode(self):
        T_SA_UB = self.EAMS.TEMPERATURE_SUPPLY_AIR_HIGH
        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_SA_3_LK.append([])
                                
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_SA_3_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T_SA    = self.CDV_T_SA_LK[l][k]
                    A_SA    = self.CDV_A_SA_LK[l][k]
                    A_SA_LB = self._getA_SA_LB(l,k)
                    
                    lcstr = self.CAV_A_SA_T_SA_LK[l][k]
                    
                    if self.EAMS.SH[k] == 1:
                        rcstr = (A_SA_LB * T_SA) + (T_SA_UB * A_SA) - (A_SA_LB * T_SA_UB)
                        self.CSTR_A_SA_T_SA_3_LK[l].append(self.model.addQConstr(lcstr <= rcstr, name=name))
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_SA_3_LK:\n %s" %self.CSTR_A_SA_T_SA_3_LK)
        
    def _createCSTR_A_SA_T_SA_4_LK_noStandbyMode(self):
        
        A_SA_UB = self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MAX
        T_SA_LB = float(self.EAMS.TEMPERATURE_CONDITIONED_AIR) 
        
        for l in xrange(self.NUM_ROOM):
                self.CSTR_A_SA_T_SA_4_LK.append([])
                for k in xrange(self.NUM_SLOT):
                    name = ['CSTR_A_SA_T_SA_4_LK', str(l), str(k)]
                    name = '_'.join(name)
                    
                    T_SA    = self.CDV_T_SA_LK[l][k]                       
                    A_SA    = self.CDV_A_SA_LK[l][k]                    
                    lcstr = self.CAV_A_SA_T_SA_LK[l][k]
                    
                    if self.EAMS.SH[k] == 1:
                        rcstr = (A_SA_UB * T_SA) + (T_SA_LB * A_SA) - (A_SA_UB * T_SA_LB)
                        self.CSTR_A_SA_T_SA_4_LK[l].append(self.model.addQConstr(lcstr <= rcstr, name=name))
                                    
        self.model.update()
        logging.debug("CSTR_A_SA_T_SA_4_LK:\n %s" %self.CSTR_A_SA_T_SA_4_LK)    
        
        
        
    #===========================================================================
    # Constraints: Energy Consumption
    #===========================================================================
    def _createCSTR_EnergyConsumption_Fan(self):
        """For each location at each timestep, create a constraint for e_fan(k, l)"""
        
        for l in xrange(self.NUM_ROOM):
            self.CSTR_E_FAN_LK.append([])
            for k in xrange(self.NUM_SLOT):
                
                name = ['CSTR_E_FAN_LK', str(l), str(k)]
                name = '_'.join(name)      
                
#                 cstr = float(self.EAMS.SCHEDULING_INTERVAL) * 60 * self.EAMS.BETA_FAN_POWER_CONSTANT * self.CDV_A_SA_LK[l][k]   
                cstr = self.EAMS.BETA_FAN_POWER_CONSTANT * self.CDV_A_SA_LK[l][k]
                
                e_fan = self.CAV_E_FAN_LK[l][k]
                self.CSTR_E_FAN_LK[l].append(self.model.addConstr(e_fan==cstr, name))
                
        self.model.update()
        logging.debug("CSTR_E_FAN_LK:\n %s" %self.CSTR_E_FAN_LK)
        
    def _createCSTR_EnergyConsumption_Conditioning(self):
        """For each location at each timestep, create a constraint for e_conditioning(k, l)"""
        
        for l in xrange(self.NUM_ROOM):
            self.CSTR_E_CONDITIONING_LK.append([])            
            for k in xrange(self.NUM_SLOT):               
                name = ['CSTR_E_CONDITIONING_LK', str(l), str(k)]
                name = '_'.join(name)    
                
                cstr = 0
                # NOTE: only when OAT > T_CA!!
                if (float(self.EAMS.OAT.values()[k]) > float(self.EAMS.TEMPERATURE_CONDITIONED_AIR)):            
                    cstr += self.CDV_A_SA_LK[l][k] * (
                                   ((float)(self.EAMS.AIR_HEAT_CAPACITY_AT_CONSTANT_PRESSURE) * (float)(self.EAMS.OAT.values()[k])) -
                                   ((float)(self.EAMS.AIR_HEAT_CAPACITY_AT_CONSTANT_PRESSURE) * (float)(self.EAMS.TEMPERATURE_CONDITIONED_AIR))
                                   )
#                     cstr += float(self.EAMS.SCHEDULING_INTERVAL) * 60 * self.CDV_A_SA_LK[l][k] * (
#                                    ((float)(self.EAMS.AIR_HEAT_CAPACITY_AT_CONSTANT_PRESSURE) * (float)(self.EAMS.OAT.values()[k])) -
#                                    ((float)(self.EAMS.AIR_HEAT_CAPACITY_AT_CONSTANT_PRESSURE) * (float)(self.EAMS.TEMPERATURE_CONDITIONED_AIR))
#                                    )
                
                e_conditioning = self.CAV_E_CONDITIONING_LK[l][k]
                self.CSTR_E_CONDITIONING_LK[l].append(self.model.addConstr(e_conditioning==cstr, name))
                
        self.model.update()
        logging.debug("CSTR_E_CONDITIONING_LK:\n %s" %self.CSTR_E_CONDITIONING_LK)
        
    def _createCSTR_EnergyConsumption_Heating(self):
        """For each location at each timestep, create a constraint for e_heating(k, l)"""
                
        for l in xrange(self.NUM_ROOM):
            self.CSTR_E_HEATING_LK.append([])
            for k in xrange(self.NUM_SLOT):
                
                name = ['CSTR_E_HEATING_LK', str(l), str(k)]
                name = '_'.join(name) 
                e_heating = self.CAV_E_HEATING_LK[l][k]
                
                cstr = (
                         (float(self.EAMS.AIR_HEAT_CAPACITY_AT_CONSTANT_PRESSURE) *
                         self.CAV_A_SA_T_SA_LK[l][k]
                         ) - 
                         (float(self.EAMS.AIR_HEAT_CAPACITY_AT_CONSTANT_PRESSURE) *
                         float(self.EAMS.TEMPERATURE_CONDITIONED_AIR) *
                         self.CDV_A_SA_LK[l][k]
                         )
                        )
                                
#                 cstr = (
#                         (float(self.EAMS.SCHEDULING_INTERVAL) * 60) * 
#                         (
#                          (float(self.EAMS.AIR_HEAT_CAPACITY_AT_CONSTANT_PRESSURE) *
#                          self.CAV_A_SA_T_SA_LK[l][k]
#                          ) - 
#                          (float(self.EAMS.AIR_HEAT_CAPACITY_AT_CONSTANT_PRESSURE) *
#                          float(self.EAMS.TEMPERATURE_CONDITIONED_AIR) *
#                          self.CDV_A_SA_LK[l][k]
#                          )
#                          )
#                         )
   
                self.CSTR_E_HEATING_LK[l].append(self.model.addConstr(e_heating==cstr, name)) 
                    
        self.model.update()
        logging.debug("CSTR_E_HEATING_LK:\n %s" %self.CSTR_E_HEATING_LK)
                    
                
        
    #===========================================================================
    # Diagnose
    #===========================================================================  
    
    def _getBDV_x_MLK(self, idx):
        for k,v in self.BDV_x_MLK_Dict.iteritems():
            if v == idx:
                return k        
            
    def _getBDV_w_LK(self, idx):
        for k,v in self.BDV_w_LK_Dict.iteritems():
            if v == idx:
                return k   
        
    def logSchedulingResults(self):        
        self._printSchedulingResults()
        
        self._printVar_BDV_x_MLK_MT_Summary()
#         self._printVar_BDV_x_MLK_Summary()
        
    def logHVACResults(self):
        self._printHVACResults()
        self._printVar_BDV_w_LK_Summary()
        self._printVar_Occupied_RoomTemperature_Summary()
#         self._printForExcel()
        self._calcNPrintEnergyConsumption()
        
    def logforGraph(self, logfile, logcase):     
        
        # Option 1: draw graph for seperate case - not
#         caseid = logcase.split('/')
#         caseid = caseid[1].split('.')                   
#         fstr = 'Output\\' + logfile + "_" + caseid[0]
        
        # Option 2: draw graph for all cases
        fstr = 'Output\\' + logfile
        
        f = open(fstr,'a')        
        for l in xrange(self.NUM_ROOM):    
            data = []
            data.append(logcase+"_loc_"+str(l))
            data.append(round(self.total_power_kJs[l],2))
            data.append(round(self.total_energy_kJ[l],2))
            data.append(round(self.total_energy_kWh[l],2))
            data.append(round(self.total_fan_energy_kWh[l],2))
            data.append(round(self.total_cond_energy_kWh[l],2))
            data.append(round(self.total_heat_energy_kWh[l],2))    
            f.write(" ".join(map(str,data)))
            f.write("\n")
        f.close()        
        
    def _printForExcel(self):
        logging.info("----------------------------------------------------------------")
        logging.info("Print for Excel ...........")            
        logging.info("----------------------------------------------------------------")
        for l in xrange(self.NUM_ROOM):
            res_asa = ['AirMassFlowRate']
            res_tsa = ['SupplyAirTemperature']
            res_t = ['RoomTemperature']
            res_asat = ['ASAxT']
            res_asatsa = ['ASAxTSA']
            
            for k in xrange(self.NUM_SLOT):                
                res_asa.append(str(self.CDV_A_SA_LK[l][k].x))
                res_tsa.append(str(self.CDV_T_SA_LK[l][k].x))
                res_t.append(str(self.CAV_T_LK[l][k].x))                
                res_asat.append(str(self.CAV_A_SA_T_z_LK[l][k].x))
                res_asatsa.append(str(self.CAV_A_SA_T_SA_LK[l][k].x))
                
            s = ' '.join(res_asa)
            logging.info(s)
            s = ' '.join(res_tsa)
            logging.info(s)
            s = ' '.join(res_t)
            logging.info(s)
            
            res_oat = ['OutdoorTemperature']
            for i in self.EAMS.OAT.itervalues():
                res_oat.append(str(i))
            s = ' '.join(res_oat)
            logging.info(s)
            
            s = ' '.join(res_asat)
            logging.info(s)
            s = ' '.join(res_asatsa)
            logging.info(s)
            
            self._printDetailedT()
            
            logging.info("")
            self._printDetailedASATz()
            self._printDetailedASATSA()
  
              
    def _calcNPrintEnergyConsumption(self):
        self.total_power_kJs = []
        self.total_energy_kJ = []
        self.total_energy_kWh = []
            
        self.final_total_fan_power_kJs = 0      # 1 kJs = 1 kW
        self.final_total_cond_power_kJs = 0
        self.final_total_heat_power_kJs = 0
        self.final_total_fan_energy_kJ = 0
        self.final_total_cond_energy_kJ = 0
        self.final_total_heat_energy_kJ = 0
        self.final_total_fan_energy_kWh = 0
        self.final_total_cond_energy_kWh = 0
        self.final_total_heat_energy_kWh = 0
        
        self.total_fan_power_kJs = []
        self.total_cond_power_kJs = []
        self.total_heat_power_kJs = []
        self.total_fan_energy_kJ = []
        self.total_cond_energy_kJ = []
        self.total_heat_energy_kJ = []
        self.total_fan_energy_kWh = []
        self.total_cond_energy_kWh = []
        self.total_heat_energy_kWh = []
        
        self.fan_power_kJs = []
        self.cond_power_kJs = []
        self.heat_power_kJs = []        
        self.fan_energy_kJ = []
        self.cond_energy_kJ = []
        self.heat_energy_kJ = []        
        self.fan_energy_kWh = []
        self.cond_energy_kWh = []
        self.heat_energy_kWh = []
        
        for l in xrange(self.NUM_ROOM):
            self.total_power_kJs.append([])
            self.total_energy_kJ.append([])
            self.total_energy_kWh.append([])
                        
            self.total_fan_power_kJs.append([])
            self.total_cond_power_kJs.append([])
            self.total_heat_power_kJs.append([])
            self.total_fan_energy_kJ.append([])
            self.total_cond_energy_kJ.append([])
            self.total_heat_energy_kJ.append([])
            self.total_fan_energy_kWh.append([])
            self.total_cond_energy_kWh.append([])
            self.total_heat_energy_kWh.append([])
            
            self.fan_power_kJs.append([])
            self.cond_power_kJs.append([])
            self.heat_power_kJs.append([])
            self.fan_energy_kJ.append([])
            self.cond_energy_kJ.append([])
            self.heat_energy_kJ.append([])            
            self.fan_energy_kWh.append([])
            self.cond_energy_kWh.append([])
            self.heat_energy_kWh.append([])
            
            loc_fan_power_kJs = 0
            loc_cond_power_kJs = 0
            loc_heat_power_kJs = 0        
            loc_fan_energy_kJ = 0
            loc_cond_energy_kJ = 0
            loc_heat_energy_kJ = 0        
            loc_fan_energy_kWh = 0
            loc_cond_energy_kWh = 0
            loc_heat_energy_kWh = 0
            
            for k in xrange(self.NUM_SLOT):
                # Power in kJ/s, equivalent to kW
                self.fan_power_kJs[l].append(self.CAV_E_FAN_LK[l][k].x)
                self.cond_power_kJs[l].append(self.CAV_E_CONDITIONING_LK[l][k].x)
                self.heat_power_kJs[l].append(self.CAV_E_HEATING_LK[l][k].x)                   
                loc_fan_power_kJs = loc_fan_power_kJs + self.CAV_E_FAN_LK[l][k].x
                loc_cond_power_kJs = loc_cond_power_kJs + self.CAV_E_CONDITIONING_LK[l][k].x
                loc_heat_power_kJs = loc_heat_power_kJs + self.CAV_E_HEATING_LK[l][k].x
                
                # Energy in kJ = Power  (kJ/s)*scheduling interval in seconds   
                fan_e_kJ = self.CAV_E_FAN_LK[l][k].x * self.EAMS.SCHEDULING_INTERVAL * 60
                cond_e_kJ = self.CAV_E_CONDITIONING_LK[l][k].x * self.EAMS.SCHEDULING_INTERVAL * 60
                heat_e_kJ = self.CAV_E_HEATING_LK[l][k].x * self.EAMS.SCHEDULING_INTERVAL * 60   
                self.fan_energy_kJ[l].append(fan_e_kJ)
                self.cond_energy_kJ[l].append(cond_e_kJ)
                self.heat_energy_kJ[l].append(heat_e_kJ)             
                loc_fan_energy_kJ = loc_fan_energy_kJ + fan_e_kJ
                loc_cond_energy_kJ = loc_cond_energy_kJ + cond_e_kJ
                loc_heat_energy_kJ = loc_heat_energy_kJ + heat_e_kJ    
                
                # Energy in kWh = Power (kJ/s) * scheduling interval in seconds *  0.00027777777777778 
                fan_e_kWh = fan_e_kJ * KJ_TO_KWh
                cond_e_kWh = cond_e_kJ * KJ_TO_KWh
                heat_e_kWh = heat_e_kJ * KJ_TO_KWh  
                self.fan_energy_kWh[l].append(fan_e_kWh)
                self.cond_energy_kWh[l].append(cond_e_kWh)
                self.heat_energy_kWh[l].append(heat_e_kWh) 
                loc_fan_energy_kWh = loc_fan_energy_kWh + fan_e_kWh
                loc_cond_energy_kWh = loc_cond_energy_kWh + cond_e_kWh
                loc_heat_energy_kWh = loc_heat_energy_kWh + heat_e_kWh 
                
                
            self.total_fan_power_kJs[l] = loc_fan_power_kJs
            self.total_cond_power_kJs[l] = loc_cond_power_kJs
            self.total_heat_power_kJs[l] = loc_heat_power_kJs
            self.total_fan_energy_kJ[l] = loc_fan_energy_kJ
            self.total_cond_energy_kJ[l] = loc_cond_energy_kJ
            self.total_heat_energy_kJ[l] = loc_heat_energy_kJ
            self.total_fan_energy_kWh[l] = loc_fan_energy_kWh
            self.total_cond_energy_kWh[l] = loc_cond_energy_kWh
            self.total_heat_energy_kWh[l] = loc_heat_energy_kWh
            
            self.total_power_kJs[l] = self.total_fan_power_kJs[l] + self.total_cond_power_kJs[l] + self.total_heat_power_kJs[l]
            self.total_energy_kJ[l] = self.total_fan_energy_kJ[l] + self.total_cond_energy_kJ[l] + self.total_heat_energy_kJ[l]
            self.total_energy_kWh[l] = self.total_fan_energy_kWh[l] + self.total_cond_energy_kWh[l] + self.total_heat_energy_kWh[l]
                      
            self.final_total_fan_power_kJs = self.final_total_fan_power_kJs + loc_fan_power_kJs
            self.final_total_cond_power_kJs = self.final_total_cond_power_kJs + loc_cond_power_kJs
            self.final_total_heat_power_kJs = self.final_total_heat_power_kJs + loc_heat_power_kJs
            self.final_total_fan_energy_kJ = self.final_total_fan_energy_kJ + loc_fan_energy_kJ
            self.final_total_cond_energy_kJ = self.final_total_cond_energy_kJ + loc_cond_energy_kJ
            self.final_total_heat_energy_kJ = self.final_total_heat_energy_kJ + loc_heat_energy_kJ
            self.final_total_fan_energy_kWh = self.final_total_fan_energy_kWh + loc_fan_energy_kWh
            self.final_total_cond_energy_kWh = self.final_total_cond_energy_kWh + loc_cond_energy_kWh
            self.final_total_heat_energy_kWh = self.final_total_heat_energy_kWh + loc_heat_energy_kWh
                
            s = ' '.join(map(str, ['fan_power_kJs', self.fan_power_kJs[l]]))
            logging.info(s)
            s = ' '.join(map(str, ['cond_power_kJs', self.cond_power_kJs[l]]))
            logging.info(s)
            s = ' '.join(map(str, ['heat_power_kJs', self.heat_power_kJs[l]]))
            logging.info(s)
               
            s = ' '.join(map(str, ['fan_energy_kJ', self.fan_energy_kJ[l]]))
            logging.info(s)
            s = ' '.join(map(str, ['cond_energy_kJ', self.cond_energy_kJ[l]]))
            logging.info(s)
            s = ' '.join(map(str, ['heat_energy_kJ', self.heat_energy_kJ[l]]))
            logging.info(s)
             
            s = ' '.join(map(str, ['fan_energy_kWh', self.fan_energy_kWh[l]]))
            logging.info(s)
            s = ' '.join(map(str, ['cond_energy_kWh', self.cond_energy_kWh[l]]))
            logging.info(s)
            s = ' '.join(map(str, ['heat_energy_kWh', self.heat_energy_kWh[l]]))
            logging.info(s)       
            
            logging.info('Location[%d] Total Fan Power (kJ/s or kW): %s' %(l, round(self.total_fan_power_kJs[l],2)))
            logging.info('Location[%d] Total Conditioning Power (kJ/s or kW): %s' %(l, round(self.total_cond_power_kJs[l],2)))
            logging.info('Location[%d] Total Heating Power (kJ/s or kW): %s' %(l, round(self.total_heat_power_kJs[l],2)))
               
            logging.info('Location[%d] Total Fan Energy (kJ): %s' %(l, round(self.total_fan_energy_kJ[l],2)))
            logging.info('Location[%d] Total Conditioning Energy (kJ): %s' %(l, round(self.total_cond_energy_kJ[l],2)))
            logging.info('Location[%d] Total Heating Energy (kJ): %s' %(l, round(self.total_heat_energy_kJ[l],2)))
              
            logging.info('Location[%d] Total Fan Energy (kWh): %s' %(l, round(self.total_fan_energy_kWh[l],2)))
            logging.info('Location[%d] Total Conditioning Energy (kWh): %s' %(l, round(self.total_cond_energy_kWh[l],2)))
            logging.info('Location[%d] Total Heating Energy (kWh): %s' %(l, round(self.total_heat_energy_kWh[l],2)))
                        
            logging.info('Location[%d] Total Power Consumption (kJ/s or kW): %s' %(l, round(self.total_power_kJs[l],2)))
            logging.info('Location[%d] Total Energy Consumption (kJ): %s' %(l, round(self.total_energy_kJ[l],2)))
            logging.info('Location[%d] Total Energy Consumption (kWh): %s' %(l, round(self.total_energy_kWh[l],2)))

                    
    def _printSchedulingResults(self):
#         self._printVar_BDV_x_MLK()
        self._printVar_BAV_z_LK()   
        self._printVar_DAV_Attendee_LK()
        
    def _printHVACResults(self):
        self._printVar_CDV_A_SA()
        self._printVar_CDV_T_SA()        
        self._printVar_CAV_T()
        self._printOAT()
        self._printVar_CAV_A_SA_T_z_LK()
        self._printVar_CAV_A_SA_T_SA_LK()
        self._printDetailedT()

          
    def _printVar_BDV_x_MLK(self):
        for m in xrange(self.NUM_MEETING):
            for l in xrange(len(self.BDV_x_MLK[m])):
                for k in xrange(len(self.BDV_x_MLK[m][l])):
#                     val = self.BDV_x_MLK[m][l][k].x
#                     print val,
#                     if val > self.EPSILON:
#                         print int(self.BDV_x_MLK[m][l][k].x),
                    print "MLK_", m, "_", l, "_", k, " [", self._getBDV_x_MLK([m,l,k]) ,"]=", (self.BDV_x_MLK[m][l][k].x)
                        
#                 print ''        
#             print ''
#         print ''

                    
        
    def _printVar_BAV_z_LK(self):
        print "BAV_z_LK:"
        logging.info("BAV_z_LK")
        
        for l in xrange(self.NUM_ROOM):
            print 'Location', l            
            res = []
            res.append("Location")
            res.append(str(l))
            res.append("|")
            for k in xrange(self.NUM_SLOT):
                val = self.BAV_z_LK[l][k].x
#                 print val,
                if val > self.EPSILON:
#                     print int(self.BAV_z_LK[l][k].x),
                    print (self.BAV_z_LK[l][k].x),  
                    res.append(str(self.BAV_z_LK[l][k].x))
                else:
                    print 0,
                    res.append(str(0))
            print ''
            s = ' '.join(res)
            logging.info(s)
        print ''
       
    def _printVar_DAV_Attendee_LK(self):        
        print "DAV_Attendee"
        logging.info("DAV_Attendee")
        
        for l in xrange(self.NUM_ROOM):
            print 'Location', l,'|',
            res = []
            res.append("Location")
            res.append(str(l))
            res.append("|")
            for k in xrange(self.NUM_SLOT):
                val = self.DAV_Attendee_LK[l][k].x
#                 print val,
                if val > self.EPSILON:
#                     print int(self.DAV_Attendee_LK[l][k].x),
                    print (self.DAV_Attendee_LK[l][k].x),   
                    res.append(str(self.DAV_Attendee_LK[l][k].x))                   
                else:
                    print 0,
                    res.append(str(0))
            print ''
            s = ' '.join(res)
            logging.info(s)
        print '' 
        
    def _printVar_CDV_A_SA(self):
        print "Air Mass Flow Rate"
        logging.info("Air Mass Flow Rate")
                    
        for l in xrange(self.NUM_ROOM):     
            print 'Location', l,'|',
            res = []
            res.append("Location")
            res.append(str(l))
            res.append("|")
            for k in xrange(self.NUM_SLOT):
                print self.CDV_A_SA_LK[l][k].x,
                res.append(str(self.CDV_A_SA_LK[l][k].x))
            print ''
            s = ' '.join(res)
            logging.info(s)
        print '' 
        
    def _printVar_CDV_T_SA(self):
        print "Supply Air Temperature"
        logging.info("Supply Air Temperature")
                    
        for l in xrange(self.NUM_ROOM):     
            print 'Location', l,'|',
            res = []
            res.append("Location")
            res.append(str(l))
            res.append("|")
            for k in xrange(self.NUM_SLOT):
                print self.CDV_T_SA_LK[l][k].x,
                res.append(str(self.CDV_T_SA_LK[l][k].x))
            print ''
            s = ' '.join(res)
            logging.info(s)
        print ''
            
    def _printVar_CAV_T(self):
        print "Room Temperature"
        logging.info("Room Temperature")
                      
        for l in xrange(self.NUM_ROOM):        
            print 'Location', l, '|',    
            res = []
            res.append("Location")
            res.append(str(l))
            res.append("|")
            for k in xrange(self.NUM_SLOT):
                print self.CAV_T_LK[l][k].x,
                res.append(str(self.CAV_T_LK[l][k].x))
            print ''
            s = ' '.join(res)
            logging.info(s)
        print ''
        
    def _printOAT(self):
        logging.info("Outdoor Temperature")        
        res = []
        for i in self.EAMS.OAT.itervalues():
            res.append(str(i))
        s = ' '.join(res)
        logging.info(s)
    
    def _printVar_CAV_A_SA_T_z_LK(self):
        print "Air Mass Flow Rate x Room Temperature"
        logging.info("Air Mass Flow Rate x Room Temperature")  
        
        for l in xrange(self.NUM_ROOM):        
            print 'Location', l, '|',           
            res = []
            res.append("Location")
            res.append(str(l))
            res.append("|")
            for k in xrange(self.NUM_SLOT):
                print self.CAV_A_SA_T_z_LK[l][k].x,
                res.append(str(self.CAV_A_SA_T_z_LK[l][k].x))
            print ''
            s = ' '.join(res)
            logging.info(s)
        print ''
        
    def _printVar_CAV_A_SA_T_SA_LK(self):
        print "Air Mass Flow Rate x Supply Air Temperature"
        logging.info("Air Mass Flow Rate x Supply Air Temperature")  
        
        for l in xrange(self.NUM_ROOM):        
            print 'Location', l, '|',  
            res = []
            res.append("Location")
            res.append(str(l))
            res.append("|") 
            for k in xrange(self.NUM_SLOT):
                print self.CAV_A_SA_T_SA_LK[l][k].x,
                res.append(str(self.CAV_A_SA_T_SA_LK[l][k].x))
            print ''
            s = ' '.join(res)
            logging.info(s)
        print ''  
        
    def _printVar_BDV_x_MLK_MT_Summary(self):        
        print "Summary BDV_x_MLK_MT:"  
        logging.info ("Summary BDV_x_MLK_MT:")          
            
        for m in xrange(self.NUM_MEETING_TYPE):
            alloc = []
            for l in xrange(len(self.BDV_x_MLK[m])):
                for k in xrange(len(self.BDV_x_MLK[m][l])):
                    val = self.BDV_x_MLK[m][l][k].x                    
#                     print k, "=", val
                    if val > self.EPSILON:
#                         print int(self.BDV_x_MLK[m][l][k].x),
                        [_,fl,fk] = self._getBDV_x_MLK([m,l,k]) 
                        alloc.append([fl,fk])
                        
            if len(alloc) != len(self.EAMS.MTYPE[m].MLS):
                logging.critical("Critical Error! Number of allocated slot =%d Required slot=%s is Different!" %(len(alloc), len(self.EAMS.MTYPE[m].MLS)))
            else:
                for i in xrange(len(self.EAMS.MTYPE[m].MLS)):
                    mid =  self.EAMS.MTYPE[m].MLS[i]
                    [fl,fk] = alloc[i]
                    print "Meeting Type",m,"[#",i,"]", ' [', self.EAMS.ML[mid].Key , '] |', 'Location', fl, '[', self.EAMS.RL[fl], '] | Start Slot', fk, '[', self.EAMS.TS.get(fk), ']'
                    logging.info("Meeting Type %d [#%d][%s]| Location %d [%s] | Start Slot %s [%s]" %(m, i, self.EAMS.ML[mid].Key, fl, self.EAMS.RL[fl], fk, self.EAMS.TS.get(fk)))
                                 
    def _printVar_BDV_x_MLK_Summary(self):        
        print "Summary BDV_x_MLK:"  
        logging.info ("Summary BDV_x_MLK:")          
            
        for m in xrange(self.NUM_MEETING):
            for l in xrange(len(self.BDV_x_MLK[m])):
                for k in xrange(len(self.BDV_x_MLK[m][l])):
                    val = self.BDV_x_MLK[m][l][k].x                    
#                     print k, "=", val
                    if val > self.EPSILON:
#                         print int(self.BDV_x_MLK[m][l][k].x),
                        [_,fl,fk] = self._getBDV_x_MLK([m,l,k])  
                        print '[mlk_', m, l, k,']=1: ', 'Meeting', m, ' [', self.EAMS.ML[m].Key , '] |', 'Location', fl, '[', self.EAMS.RL[fl], '] | Start Slot', fk, '[', self.EAMS.TS.get(fk), ']'
                        logging.info("Meeting %d [%s]| Location %d [%s] | Start Slot %s [%s]" %(m, self.EAMS.ML[m].Key, fl, self.EAMS.RL[fl], fk, self.EAMS.TS.get(fk)))
#                         break                
            print ""
        print ""
        
    def _printVar_BDV_w_LK_Summary(self):  
        print "Summary BDV_w_LK:"       
        if self.BDV_w_LK: 
            print "Summary BDV_w_LK:"  
            logging.info ("Summary BDV_w_LK:")          
                
            for l in xrange(len(self.BDV_w_LK)):
                for k in xrange(len(self.BDV_w_LK[l])):
                    val = self.BDV_w_LK[l][k].x
                    if val > self.EPSILON:
                        [fl,fk] = self._getBDV_w_LK([l,k])  
                        print '[lk_', l, k,']=1: ', 'Location', fl, '[', self.EAMS.RL[fl], '] | Start Slot', fk, '[', self.EAMS.TS.get(fk), ']',
                        logging.info("Location %d [%s] | Start Slot %s [%s]" %(l, self.EAMS.RL[fl], fk, self.EAMS.TS.get(fk)))                               
                print ""
        
    def _printVar_Occupied_RoomTemperature_Summary(self):
        print "Room Temperature when BAV_z_LK=1:"   
        logging.info("Room Temperature when BAV_z_LK=1:")     
        for l in xrange(self.NUM_ROOM):
            print 'Location', l
            logging.info("Location %s" %l)
            res = []
            for k in xrange(self.NUM_SLOT):            
                val = self.BAV_z_LK[l][k].x
#                 print k, "=", val, ", True?", (val > self.EPSILON)
                if val > self.EPSILON:                    
#                     print self.BAV_z_LK[l][k].x,
                    print self.CAV_T_LK[l][k].x,
                    res.append(str(self.CAV_T_LK[l][k].x))
            print ''
            s = ' '.join(res)
            logging.info(s)
        print ''
    
    def logTemperatures(self, logcase):
        try:
            
            fstr = 'Output\\' + logcase + '_temperatures'
            f = open(fstr,'a')   
            
            # Log timeslot
            f.write(",".join(map(str,self.EAMS.TS.values())))            
            f.write("\n")
            
            # Log outdoor temperature
            f.write(",".join(map(str,self.EAMS.OAT.values())))  
            f.write("\n")
            
            # Log number of rooms
            f.write(str(self.NUM_ROOM))
            f.write("\n")
              
            # Log room temperature, TSA, ASA            
            for r in xrange(self.NUM_ROOM):
                T = []
                TSA = []
                ASA = []
                for k in xrange(self.NUM_SLOT):   
                    T.append(self.CAV_T_LK[r][k].x)
                    TSA.append(self.CDV_T_SA_LK[r][k].x)
                    ASA.append(self.CDV_A_SA_LK[r][k].x)
                                    
                f.write(",".join(map(str,T)))
                f.write("\n")
                f.write(",".join(map(str,TSA)))
                f.write("\n")
                f.write(",".join(map(str,ASA)))
                f.write("\n")
            
            f.close()      
            
        except (ValueError), e:
            logging.critical('%s' % (e))  
    
    def logSchedules(self, logcase):
        try:
            
            fstr = 'Output\\' + logcase + '_schedules'
            f = open(fstr,'a')   
            
            # Log timeslot
            f.write(",".join(map(str,self.EAMS.TS.values())))            
            f.write("\n")
            
            # Log number of rooms
            f.write(str(self.NUM_ROOM))
            f.write("\n")
              
            # Log room allocation            
            for r in xrange(self.NUM_ROOM):
                vz = []                      
                for k in xrange(self.NUM_SLOT):    
                    if self.BAV_z_LK[r][k].x > self.EPSILON:   
                        vz.append(1)
                    else:
                        vz.append(0)
                                                                  
                vw = []                    
                if self.EAMS.STANDBY_MODE != '0':     
                    vwidx = 0      
                    for k in xrange(len(self.BDV_w_LK[r])):
                        [_,fk] = self._getBDV_w_LK([r,k])                    
                        if fk > vwidx:
                            vw.extend([str(0)] * (fk-vwidx))
                            
                        if self.BDV_w_LK[r][k].x > self.EPSILON:
                            vw.extend(str(1))
                        else:
                            vw.extend(str(0))
                                                    
                        vwidx = len(vw)
                    
                f.write(",".join(map(str,vz)))
                f.write("\n")
                f.write(",".join(map(str,vw)))
                f.write("\n")
                
            f.close()      
            
        except (ValueError), e:
            logging.critical('%s' % (e))  
    
            
    def logStatistics(self, logfile, logcase):
        try:
            logging.info("Status: %s", self.STATUS[self.model.getAttr(GRB.attr.Status)])
            logging.info("Model name: %s", self.model.getAttr(GRB.attr.ModelName))
            logging.info("Objective: %s", self.model.getAttr(GRB.attr.ObjVal))
            logging.info("Number variables: %s", self.model.getAttr(GRB.attr.NumVars))
            logging.info("Number constraints: %s", self.model.getAttr(GRB.attr.NumConstrs))
            logging.info("Number iterations: %s", self.model.getAttr(GRB.attr.IterCount))
            if self.model.getAttr(GRB.attr.IsMIP) == 1:
                logging.info("Number B&B nodes: %s", self.model.getAttr(GRB.attr.NodeCount))
            logging.info("Runtime: %s", self.model.getAttr(GRB.attr.Runtime))
            logging.info("Solve time:%f" %self.solveTime)
            
            gap = (self.model.getAttr(GRB.attr.ObjVal) - self.model.getAttr(GRB.attr.ObjBound))/ self.model.getAttr(GRB.attr.ObjVal) * 100
            logging.info("Num Solution Found:%d" %self.model.getAttr(GRB.attr.SolCount))
            logging.info("Best Bound:%f" %self.model.getAttr(GRB.attr.ObjBound))
            logging.info("Best Objective Value:%f" %self.model.getAttr(GRB.attr.ObjVal))
            logging.info("Optimality Gap (%%):%f" %(gap))
            
            fstr = 'Output\\' + logfile + '_stats'
            f = open(fstr,'a')   
            data = []
            data.append(logcase)
            data.append(self.STATUS[self.model.getAttr(GRB.attr.Status)])
            data.append(self.model.getAttr(GRB.attr.ObjVal))            
            data.append(self.model.getAttr(GRB.attr.NumVars))
            data.append(self.model.getAttr(GRB.attr.NumConstrs))
            data.append(self.model.getAttr(GRB.attr.IterCount))
            data.append(self.model.getAttr(GRB.attr.NodeCount))
            data.append(self.model.getAttr(GRB.attr.Runtime))
            data.append(self.solveTime)
            data.append(self.model.getAttr(GRB.attr.SolCount))            
            data.append(self.model.getAttr(GRB.attr.ObjBound))
            data.append(self.model.getAttr(GRB.attr.ObjVal))                        
            data.append(gap)
            f.write(" ".join(map(str,data)))
            f.write("\n")
            f.close()      
            
        except (ValueError), e:
            logging.critical('%s' % (e))  
        
    def _printDetailedASATSA(self):         
        res_diff = []   
        res_actual = []     
        for l in xrange(self.NUM_ROOM):            
            for k in xrange(self.NUM_SLOT):    
                a = self.CAV_A_SA_T_SA_LK[l][k].x
                b = self.CDV_A_SA_LK[l][k].x * self.CDV_T_SA_LK[l][k].x
                res_actual.append(b)
                if b == 0:
                    diff = 0
                else:
                    diff = round((a-b)/b*100,2)
                res_diff.append(diff)
        
        logging.info("ASA_TSA_Actual: %s" %res_actual)
        logging.info("ASA_TSA_ApproxErr: %s " %res_diff)
        
    def _printDetailedASATz(self):         
        res_diff = []        
        res_actual = [] 
        for l in xrange(self.NUM_ROOM):            
            for k in xrange(self.NUM_SLOT):    
                a = self.CAV_A_SA_T_z_LK[l][k].x
                b = self.CDV_A_SA_LK[l][k].x * self.CAV_T_LK[l][k].x
                res_actual.append(b)                
                if b == 0:
                    diff = 0
                else:
                    diff = round((a-b)/b*100,2)                    
                res_diff.append(diff)
                
        logging.info("ASA_Tz_Actual: %s" %res_actual)
        logging.info("ASA_Tz_ApproxErr: %s" %res_diff)
        
    def _printDetailedT(self):        
        T = []
        T_plus_1 = []
        T_plus_1_actual = []
        T_l_z1 = []
        T_l_z2 = []
        T_l_z3 = []
        T_l_z4 = []
        T_l_f = []
        T_l_c = []
        T_l_oat = []        
        Qr = []
        Qp = []
        Qh = []
        Qh_actual = []
        
        for l in xrange(self.NUM_ROOM):
            A = self.EAMS.getRoomThermalConfig(l, "C")
            B1 =  self.EAMS.getRoomThermalConfig(l, "Rij")
            B2 =  self.EAMS.getRoomThermalConfig(l, "Rik")
            B3 =  self.EAMS.getRoomThermalConfig(l, "Ril")
            B4 =  self.EAMS.getRoomThermalConfig(l, "Rio")
            B5 =  self.EAMS.getRoomThermalConfig(l, "Rif")
            B6 =  self.EAMS.getRoomThermalConfig(l, "Ric")  
            B7 = self.EAMS.getRoomThermalConfig(l, "Rwij")            
            C = self.EAMS.AIR_HEAT_CAPACITY_AT_CONSTANT_PRESSURE            
            D = (float)(self.EAMS.SCHEDULING_INTERVAL)*60 / A            
            E1 = (float)(self.EAMS.SCHEDULING_INTERVAL)*60 / (A*B1)
            E2 = (float)(self.EAMS.SCHEDULING_INTERVAL)*60 / (A*B2)
            E3 = (float)(self.EAMS.SCHEDULING_INTERVAL)*60 / (A*B3)
            E4 = (float)(self.EAMS.SCHEDULING_INTERVAL)*60 / (A*B4)
            E5 = (float)(self.EAMS.SCHEDULING_INTERVAL)*60 / (A*B5)
            E6 = (float)(self.EAMS.SCHEDULING_INTERVAL)*60 / (A*B6)
            E7 = (float)(self.EAMS.SCHEDULING_INTERVAL)*60 / (A*B7)
            F = D * self.EAMS.OCCUPANT_SENSIBLE_HEAT_GAIN   
            
            B = ((1/B1) + (1/B2) + (1/B3) + (1/B4) + (1/B5) + (1/B6) + (1/B7))
            
            T.append([])
            T_plus_1.append([])
            T_l_z1.append([])
            T_l_z2.append([])
            T_l_z3.append([])
            T_l_z4.append([])
            T_l_f.append([])
            T_l_c.append([])
            T_l_oat.append([])
            Qr.append([])
            Qp.append([])
            Qh.append([])
            Qh_actual.append([])            
            
            for k in xrange(self.NUM_SLOT):              
                T[l].append(round((self.CAV_T_LK[l][k].x),4))
                T_l_z1[l].append(self.CAV_T_l_z1_LK[l][k].x)
                T_l_z2[l].append(self.CAV_T_l_z2_LK[l][k].x)
                T_l_z3[l].append(self.CAV_T_l_z3_LK[l][k].x)
                T_l_z4[l].append(self.CAV_T_l_z4_LK[l][k].x)
                T_l_f[l].append(self.CAV_T_l_f_LK[l][k].x)
                T_l_c[l].append(self.CAV_T_l_c_LK[l][k].x)
                T_l_oat[l].append(float(self.EAMS.OAT.values()[k]))                
                E = ((E1 * self.CAV_T_l_z1_LK[l][k].x) +
                     (E2 * self.CAV_T_l_z2_LK[l][k].x) +
                     (E3 * self.CAV_T_l_z3_LK[l][k].x) +
                     (E4 * self.CAV_T_l_z4_LK[l][k].x) +
                     (E5 * self.CAV_T_l_f_LK[l][k].x) +
                     (E6 * self.CAV_T_l_c_LK[l][k].x) +
                     (E7 * float(self.EAMS.OAT.values()[k]))
                    )                
                
                res_qr = round((E-(D*B*self.CAV_T_LK[l][k].x)),4)
                Qr[l].append(res_qr)
                
                res_qp = round((F * self.DAV_Attendee_LK[l][k].x),4)
                Qp[l].append(res_qp)
                
                res_qh = round((D*C*self.CAV_A_SA_T_SA_LK[l][k].x) - (D*C*self.CAV_A_SA_T_z_LK[l][k].x),4)
                Qh[l].append(res_qh)
                
                res_qh_actual = round(
                                      (D * C * self.CDV_A_SA_LK[l][k].x * self.CDV_T_SA_LK[l][k].x) - 
                                      (D * C * self.CDV_A_SA_LK[l][k].x * self.CAV_T_LK[l][k].x),4)
                Qh_actual[l].append(res_qh_actual)
                
                res_t1 = round((self.CAV_T_LK[l][k].x + Qr[l][k] + Qp[l][k] + Qh[l][k]),4)
                T_plus_1[l].append(res_t1)
                
                res_t1_actual = round((self.CAV_T_LK[l][k].x + Qr[l][k] + Qp[l][k] + Qh_actual[l][k]),4)
                T_plus_1_actual.append(res_t1_actual)
                
        
        logging.info("T  %s" %T)
        logging.info("Qr %s" %Qr)
        logging.info("Qp %s" %Qp)
        logging.info("Qh %s" %Qh)
        logging.info("T+1 %s" %T_plus_1)
        logging.info("Above is the Detailed Breakdown of Temperature Change with MacCormick Relaxation Term in Qh:")
        logging.info("")
        logging.info("Below is the Detailed Breakdown of Temperature Change with Actual ASAxTSA, ASAxT in Qh:")
        logging.info("T  %s" %T)
        logging.info("Qr %s" %Qr)
        logging.info("Qp %s" %Qp)
        logging.info("Qh_actual %s" %Qh_actual)
        logging.info("T+1_actual %s" %T_plus_1_actual)
    
        
    #===========================================================================
    # Graph Plotting
    #===========================================================================  
    def _populateRoomAlloc(self):
        self.RA = np.array(np.empty((self.NUM_ROOM, self.NUM_SLOT)), dtype='object')
        self.RA.fill(-1)
        
        for l in xrange(self.NUM_ROOM):
            for m in xrange(self.NUM_MEETING):                
                for k in xrange(self.NUM_SLOT):
                    mlk = self.BDV_x_MLK_Dict.get(tuple([m, l, k]))
                    if mlk:
                        if int(self.BDV_x_MLK[mlk[0]][mlk[1]][mlk[2]].x * self.BAV_z_LK[l][k].x) == 1:
                            self.RA[l][k] = m
#         print str(self.RA)
          
    def plotGraphs(self):        
        T = {}
        T_SA = {}
        A_SA = {}
        E_FAN = {}
        E_CONDITIONING = {}
        E_HEATING = {}
        self._populateRoomAlloc()
        
        for r in xrange(self.NUM_ROOM):
            T[r] = {'Time': [], 'Celcius': []}
            A_SA[r] = {'Time': [], 'Kg/s': []}
            T_SA[r] = {'Time': [], 'Celcius': []}
            E_FAN[r] = {'Time': [], 'kW': [], 'kJ':[], 'kWh':[]}
            E_CONDITIONING[r] = {'Time': [], 'kW': [], 'kJ':[], 'kWh':[]}
            E_HEATING[r] = {'Time': [], 'kW': [], 'kJ':[], 'kWh':[]}
            
        for r in xrange(self.NUM_ROOM):
            for k in xrange(self.NUM_SLOT):   
                ts_str =  self.EAMS.TS.get(k)
                T[r].get('Time').append(ts_str) 
                T[r].get('Celcius').append(self.CAV_T_LK[r][k].x)
                
                T_SA[r].get('Time').append(ts_str)
                T_SA[r].get('Celcius').append(self.CDV_T_SA_LK[r][k].x)
                
                A_SA[r].get('Time').append(ts_str)
                A_SA[r].get('Kg/s').append(self.CDV_A_SA_LK[r][k].x)
                
#                 self.A_SA_LB.append(self.CAV_A_SA_Room_L[r].x + self.CAV_A_SA_MaxPeople_L[r].x)
                [width, length, height] = self.EAMS.getRoomThermalConfig(r, "Dim")
                self.A_SA_LB.append(self.EAMS.ALPHA_IAQ_FACTOR_OF_SAFETY*(
                                                        (self.EAMS.MASS_AIR_FLOW_OUTSIDE_AIR_PER_METER_SQUARE * width * length * height) /
                                                        (1-self.EAMS.MASS_AIR_FLOW_RETURN_AIR_RATIO)))
             
                
                E_FAN[r].get('Time').append(ts_str)
                E_FAN[r].get('kW').append(self.fan_power_kJs[r][k])
                E_FAN[r].get('kJ').append(self.fan_energy_kJ[r][k])
                E_FAN[r].get('kWh').append(self.fan_energy_kWh[r][k]) 
                
                E_CONDITIONING[r].get('Time').append(ts_str)
                E_CONDITIONING[r].get('kW').append(self.cond_power_kJs[r][k])
                E_CONDITIONING[r].get('kJ').append(self.cond_energy_kJ[r][k])
                E_CONDITIONING[r].get('kWh').append(self.cond_energy_kWh[r][k])
                                
                E_HEATING[r].get('Time').append(ts_str)
                E_HEATING[r].get('kW').append(self.heat_power_kJs[r][k])
                E_HEATING[r].get('kJ').append(self.heat_energy_kJ[r][k])
                E_HEATING[r].get('kWh').append(self.heat_energy_kWh[r][k])
        
        
                
#         print T[r].get('Time')
#         print self.EAMS.OAT.values()
                                          
        for r in xrange(self.NUM_ROOM):              
            GraphPlot().plotTemperatureZoom(self.CFG_IDX,
                                            self.EAMS.ZOOMPLOT_INTERVAL,
                                            self.EAMS.ZOOMPLOT_STEP,
                                            self.EAMS.RL[r],
                                            self.EAMS.ROOM_CONFIG_DATA,
                                            self.EAMS.MEETINGS_CONFIG_DATA,
                                            self.EAMS.ZOOMPLOT_START_DATETIME,   
                                            self.EAMS.ZOOMPLOT_END_DATETIME,
                                            T[r])

#             GraphPlot().plotTemperatureNAirMassZoom(self.CFG_IDX, 
#                                                     self.EAMS.RL[r], 
#                                                     self.EAMS.PLOT_INTERVAL, 
#                                                     self.EAMS.PLOT_STEP, 
#                                                     T[r], 
#                                                     self.EAMS.OAT, 
#                                                     T_SA[r], 
#                                                     A_SA[r], 
#                                                     self.EAMS.ZOOMPLOT_START_DATETIME, 
#                                                     self.EAMS.ZOOMPLOT_END_DATETIME)
            
            print T[r].get('Celcius')
            print T_SA[r].get('Celcius')
            print A_SA[r].get('Kg/s')
             
            GraphPlot().plotTemperatureNAirMass(self.CFG_IDX,
                                                self.EAMS.PLOT_INTERVAL,
                                               self.EAMS.PLOT_STEP,
                                               self.EAMS.RL[r],
                                               self.EAMS.PROB_CFG,
                                               self.EAMS.ROOM_CONFIG_DATA,
                                               self.EAMS.MEETINGS_CONFIG_DATA,
                                               self.EAMS.OUTDOOR_TEMP_DATA,
                                               self.EAMS.PROB_CFG,
                                               self.EAMS.INITIAL_TEMPERATURE,
                                               self.EAMS.TEMPERATURE_UNOCC_MIN,
                                               self.EAMS.TEMPERATURE_OCC_COMFORT_RANGE_INCR,
                                               self.EAMS.TEMPERATURE_UNOCC_MAX,
                                               self.EAMS.TEMPERATURE_OCC_COMFORT_RANGE_DECR,
                                               self.A_SA_LB[r],
                                               self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MAX,
                                               self.EAMS.TEMPERATURE_CONDITIONED_AIR,
                                               self.EAMS.TEMPERATURE_SUPPLY_AIR_HIGH,
                                               T[r],
                                               self.EAMS.OAT,
                                               self.RA[r],
                                               T_SA[r],   
                                               A_SA[r]                                            
                                               )
               
#             GraphPlot().plotEnergyConsumption(self.CFG_IDX, self.EAMS.PLOT_INTERVAL, 
#                                               self.EAMS.PLOT_STEP,
#                                               self.EAMS.RL[r],
#                                               self.EAMS.ROOM_CONFIG_DATA,
#                                               self.EAMS.MEETINGS_CONFIG_DATA,
#                                               self.EAMS.OUTDOOR_TEMP_DATA,
#                                               E_FAN[r],
#                                               E_CONDITIONING[r],
#                                               E_HEATING[r],                                   
#                                               self.total_fan_power_kJs,
#                                               self.total_cond_power_kJs,
#                                               self.total_heat_power_kJs,
#                                               self.total_fan_energy_kWh,
#                                               self.total_cond_energy_kWh,
#                                               self.total_heat_energy_kWh,
#                                               self.total_fan_energy_kJ,
#                                               self.total_cond_energy_kJ,
#                                               self.total_heat_energy_kJ,
#                                               self.total_power_kJs,
#                                               self.total_energy_kWh,
#                                               self.total_energy_kJ)
               
#             GraphPlot().plotTemperatureNEnergy(self.CFG_IDX,
#                                                self.EAMS.PLOT_INTERVAL,
#                                    self.EAMS.PLOT_STEP,
#                                    self.EAMS.RL[r],
#                                    self.EAMS.ROOM_CONFIG_DATA,
#                                    self.EAMS.MEETINGS_CONFIG_DATA,
#                                    self.EAMS.OUTDOOR_TEMP_DATA,
#                                    self.EAMS.PROB_CFG,
#                                    self.EAMS.INITIAL_TEMPERATURE,
#                                    self.EAMS.TEMPERATURE_UNOCC_MIN,
#                                    self.EAMS.TEMPERATURE_OCC_COMFORT_RANGE_INCR,
#                                    self.EAMS.TEMPERATURE_UNOCC_MAX,
#                                    self.EAMS.TEMPERATURE_OCC_COMFORT_RANGE_DECR,                                  
#                                    self.A_SA_LB[r],
#                                    self.EAMS.MASS_AIR_FLOW_SUPPLY_AIR_MAX,
#                                    self.EAMS.TEMPERATURE_CONDITIONED_AIR,
#                                    self.EAMS.TEMPERATURE_SUPPLY_AIR_HIGH,
#                                    T[r],
#                                    self.EAMS.OAT,
#                                    self.RA[r],
#                                    T_SA[r],                                            
#                                    E_FAN[r],
#                                    E_CONDITIONING[r],
#                                    E_HEATING[r],
#                                    self.total_fan_power_kJs,
#                                    self.total_cond_power_kJs,
#                                    self.total_heat_power_kJs,
#                                    self.total_fan_energy_kWh,
#                                    self.total_cond_energy_kWh,
#                                    self.total_heat_energy_kWh,
#                                    self.total_power_kJs,
#                                    self.total_energy_kWh
#                                    )

    def plotPatternGraphs(self):
        T = []  
        for k in xrange(self.NUM_SLOT):
            ts_str =  self.EAMS.TS.get(k)
            T.append(ts_str) 
            
        GraphPlot().plotOutdoor(self.EAMS.PLOT_INTERVAL,
                                self.EAMS.PLOT_STEP,                                               
                                self.EAMS.OUTDOOR_TEMP_DATA,
                                self.EAMS.PROB_CFG,
                                self.EAMS.INITIAL_TEMPERATURE,
                                self.EAMS.TEMPERATURE_UNOCC_MIN,
                                self.EAMS.TEMPERATURE_OCC_COMFORT_RANGE_INCR,
                                self.EAMS.TEMPERATURE_UNOCC_MAX,
                                self.EAMS.TEMPERATURE_OCC_COMFORT_RANGE_DECR,
                                T,
                                self.EAMS.OAT)




