import re
from temp import temp

#maps an id to a name
#nodeIDs = {1:'my room temp', 2:'kitchen', 3:'water', 4:'parents room'}
#maps and id to a field number
field = {1:1, 2:2, 3:4, 4:3}

for line in open("./sensordata"):
	line = dict(entry.split('=') for entry in line.split(', '))
	print "{}{}{}".format(
		line['time'][:-1],
		field[int(line['id'])] * ',',
		temp(int(line['temp']))
		)
	