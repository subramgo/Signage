"""
    Object Tracking Algorithm

    For continuous online usage
"""

import time
import random

class ObjectTracker:
    """ Manages identification and tracking of objects 
        across multiple frames over time.
        Gives random IDs but forgets objects when they aren't seen again. """
    
    def __init__(self,cfg):        
        self.known = set()

        self.iou_threshold = cfg['iou_threshold']
        self.min_secs_live = cfg['min_secs_live']

    def track(self,faces):
        """ Assume all windows are from the same frame dimensions """
        seen_time = time.time()
        uknwn_faces = [TrackingObject(gen_iduid(),face.window,seen_time) for face in faces]
        return self._track(uknwn_faces)

    def _track(self,objects):
        """ General-purpose tracking based on TrackingObject class """
        known = set()
        ids = []
        live_times = []

        for obj in objects:
            idd = self.recognize(obj)
            if idd:
                idd.last_seen   = obj.last_seen
                idd.last_coords = obj.last_coords
                obj = idd
            
            known.add(obj)
            ids.append(obj.iduid)
            live_times.append(obj.time_alive)

        self.known = known
        return ids,live_times

    def recognize(self,obj):
        for kno in self.known:
            if self.object_match(obj,kno):
                return kno
        else:
            return None

    def object_match(self,objA,objB):
        """ Given two TrackingObjects, return Boolean match.
            Assume all coords are from the same frame dimensions. """
        # TODO add momentum estimates etc. for more sophisticated tracking
        boxA = objA.last_coords
        boxB = objB.last_coords
        try:
            xA = max(boxA[0], boxB[0])
            yA = max(boxA[1], boxB[1])
            xB = min(boxA[2], boxB[2])
            yB = min(boxA[3], boxB[3])
            
            interArea = max(0,xB-xA+1) * max(0,yB-yA+1)
            boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
            boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
            iou = interArea / float(boxAArea + boxBArea - interArea)
            if iou>self.iou_threshold:
                return True
        except:
            pass
        return False

class TrackingObject:
    @property
    def time_alive(self):
        return int(self.last_seen - self.first_seen)

    def __init__(self,iduid,coords,seen_time):
        self.iduid = iduid
        self.last_coords = coords
        self.first_seen = seen_time
        self.last_seen = seen_time
    
    def __repr__(self):
        coords = ','.join([str(x) for x in self.last_coords])
        report = "ID: {} - lived {} secs - coords: {}".format(self.iduid,self.time_alive,coords)
        return report

def gen_iduid():
    """ Inter-dimensionally Unique IDentifier! """
    return int(random.random()*10**15)
