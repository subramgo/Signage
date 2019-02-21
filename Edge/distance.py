

class DistanceMeasurer:
	def __init__(self):
		self.resol_A = 79777.0
		self.resol_B = 1898.0

	def _distance(self, windows):
		x_min = windows[0]
		y_min = windows[1]
		x_max = windows[2]
		y_max = windows[3]

		area  = (x_max - x_min) * (y_max - y_min)
		distance = (self.resol_A - area) / (1.0 * self.resol_B)
		return distance

	def measure(self, faces):
		return [self._distance(face.window) for face in faces]

