class DistanceMeasure:
	def __init__(self):
		self.resol_A = 160641.0
		self.resol_B = 28800.0

	def _distance(self, windows):


		x_min = windows[0]
		y_min = windows[1]
		x_max = windows[2]
		y_max = windows[3]

		area  = (x_max - x_min) * (y_max - y_min)
		distance = (self.resol_A - area) / (1.0 * self.resol_B)
		return distance

	def process(self, no_faces, windows_string):
		windows = windows_string.split(',')

		if len(windows) < 4:
			return [0]

		windows =[int(w) * 1.0 for w in windows]

		start_index = 0
		end_index = 4

		distances =[]
		for i in range(no_faces):
			distance = self._distance(windows[start_index:end_index])
			start_index+=4
			end_index+=4
			distances.append(distance)

		return distances

def find_distance(json_data):

    tracker = DistanceMeasure()
    frames = []

    for frame in json_data:
    	distances = tracker.process(frame['no_faces'], frame['windows'])
    	frame['distances'] = distances
    	frames.append(frame)

    return frames


