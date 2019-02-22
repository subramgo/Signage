
"""
	## Linear Model Assumption
	    Area_face ~ -(Distance * FOV)

	Where Area_face is relative to image frame size.

	Add contants for estimation:
		Distance = ( Pseudo-FOV - Area_face ) / Pseudo-FCL

	## Inverse-square Model
	...necessary?
"""

"""
	HP All-In-One Measurements via utils/calibrate.py

	2ft: Face Proportionate-Area: 0.1604296875
	3ft: Face Proportionate-Area: 0.0762011718
	4ft: Face Proportionate-Area: 0.0369140625
	5ft: Face Proportionate-Area: 0.0254947916
	6ft: Face Proportionate-Area: 0.0178255208

	Linear model: D = 78.0 - A_f * 336.6
"""

class DistanceMeasurer:
	def __init__(self,camfig):
		self.pseudo_fov = camfig.get('p_fov',78.0)
		self.pseudo_fcl = camfig.get('p_fcl',336.6)

	def _distance(self,face_area):
		distance = self.pseudo_fov - (self.pseudo_fcl * face_area)
		return distance

	def measure(self,faces,frame):
		A_frame = frame.size[0]*frame.size[1]
		windows = [float(face.size[0]*face.size[1])/A_frame for face in faces]
		return [self._distance(window) for window in windows]

