def temp(x):
	val = x / 1023.0
	if val == 1: val = 0.999
	res = 9840.0 / (1 - val) - 9840.0
	t = 1.0 / (1.0/298.15 + 1/3977.0 * math.log(res / 10000.0)) - 273.15
	#print "resistance: {:.1f}K , temp: {}C".format(res/1000.0, t)
	return t