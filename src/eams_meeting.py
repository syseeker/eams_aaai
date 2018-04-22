import logging
from datetime import datetime
from operator import itemgetter
from collections import namedtuple

from eams_error import EAMS_Error

class Meeting:        
    # Meeting class consists of {Key, TimeWindows, Duration, Room, Attendees}
    def __init__(self):        
        self.mlist = []
        self.mdesc = namedtuple('Meeting_Desc', 'Key TimeWindows Duration Room Attendees')
    
    def _validateOverlappedTimeWindows(self, twlist, s, e):
        for i in xrange(len(twlist)):
            if twlist[i][0] == s and twlist[i][1] == e:
                return EAMS_Error().eams_meeting_overlapped_time_windows()
        return 0
    
    def populateMeetingsForRoomAllocNSchedule(self, meetings):
        """Populate meetings from configuration files"""
        for k, v in meetings.iteritems():
            tw = []
            for sk, sv in v.iteritems():                
                if sk.startswith("W"):
                    st = datetime.strptime(sv.get('Start'), "%Y-%m-%d %H:%M")
                    et = datetime.strptime(sv.get('End'), "%Y-%m-%d %H:%M")
                    if et < st:
                        logging.critical("Meeting[%s] Invalid time windows [%s]. End Time earlier than Start Time." %(k,sk))
                        return EAMS_Error().eams_meeting_invalid_time_windows()
                    elif self._validateOverlappedTimeWindows(tw, st, et) < 0:
                        logging.critical("Meeting[%s] Invalid time windows [%s]. Duplicate time windows." %(k,sk))
                        return EAMS_Error().eams_meeting_overlapped_time_windows()
                    else:
                        tw.append([st,et])      
            
            stw = sorted(tw, key=itemgetter(0))                
            if 'Preferred_Room' in v:
                self.mlist.append(self.mdesc(k, stw, int(v['Duration']), v['Preferred_Room'], v['Attendees']))                
            else:
                self.mlist.append(self.mdesc(k, stw, int(v['Duration']), "", v['Attendees']))
                
        
        # debug only
        logging.debug(self.mlist)   
        for i in xrange(len(self.mlist)):
            logging.debug("Meeting [%s]" %(self.mlist[i].Key))
            for j in xrange(len(self.mlist[i].TimeWindows)):
                logging.debug(self.mlist[i].TimeWindows[j])
                                 
        return 0
    
    def getMeetingsList(self):
        return self.mlist

            
            
#     def populateMeetingsWithFixedSchedule(self, meetings):      
#         """Populate meetings and convert Start/End time from string to datetime"""  
#         logging.info("Populate meetings and convert Start/End time from string to datetime")
#         for k, v in meetings.iteritems():
#             self.meetings[k]={'Start':datetime.strptime(v['Start'], "%Y-%m-%d %H:%M"), 
#                               'End':datetime.strptime(v['End'], "%Y-%m-%d %H:%M"),
#                               'Room':None,
#                               'Duration':None,
#                               'Attendees':v['Attendees']}                        
#         logging.debug("Meetings: %s" %self.meetings)
#         
#     def populateMeetingsWithDynamicSchedule(self, meetings):      
#         """Populate meetings and convert Start/End time from string to datetime"""  
#         logging.info("Populate meetings and convert Start/End time from string to datetime")
#         for k, v in meetings.iteritems():
#             self.meetings[k]={'Start':datetime.strptime(v['Start'], "%Y-%m-%d %H:%M"), 
#                               'End':datetime.strptime(v['End'], "%Y-%m-%d %H:%M"),
#                               'Room':None, 
#                               'Duration': v['Duration'],
#                               'Attendees':v['Attendees']}                        
#         logging.debug("Meetings: %s" %self.meetings)
#     
#     def sortMeetingsListByStartTime(self):        
#         logging.info("Sort meetings based on Start Time")
#         if (len(self.meetings)==0):
#             logging.error("Empty meeting. Expected? Else call populateMeetings() first")
#             return -1
#                     
#         m = list()        
#         for k, v in self.meetings.iteritems():
#             m.append(self.mdesc(k, v['Start'], v['End'], v['Duration'], v['Room'], v['Attendees']))
#             sm = sorted(m , key=attrgetter('Start'), reverse=False)
#         logging.debug("Sorted Meetings: %s" %sm)                    
#         self.smlist = sm
            