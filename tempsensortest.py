import serial, time, math
from datetime import datetime as dt
from tempodb import Client, DataPoint
from pylab import *

def temp(x):
	val = x / 1023.0
	res = 9840.0 / (1 - val) - 9840.0
	t = 1.0 / (1.0/298.15 + 1/3977.0 * math.log(res / 10000.0)) - 273.15
	#print "resistance: {:.1f}K , temp: {}C".format(res/1000.0, t)
	return t

data = open("./sensordata").readlines()

try:
	last_sent = dt.fromtimestamp(float(open("./last_sent_to_tempodb").read()))
except:last_sent = 0

data = [dict(i.split('=') for i in d.strip('\n').split(', ')) for d in data]
for d in data:
	d['temp'] = temp(int(d['temp']))
	d['id'] = int(d['id'])
	d['vcc'] = float(d['vcc'])
	d['pipe'] = int(d['pipe'])
	d['tries'] = int(d['tries'])
	d['time'] = dt.fromtimestamp(int(d['time']))

new_data = [d for d in data if d['time'] >= last_sent]
print len(new_data)



#print data[5:10]
#plot([d['time'].tm_hour + d['time'].tm_min / 59.0 for d in data], [d['temp'] for d in data])

#time_dict = {d['time'] : d for d in data}
#show()

temp_data = [DataPoint(d['time'],d['temp'] ) for d in data]
print temp_data
# Modify these with your credentials found at: http://tempo-db.com/manage/
API_KEY = 'f3c71667bab7425fb9ac728409d22f1e'
API_SECRET = '1b72a21ad76247e8afc2b00ba46df329'
SERIES_KEY = 'my room temp'

client = Client(API_KEY, API_SECRET)
client.write_key(SERIES_KEY,temp_data)

open("./last_sent_to_tempodb", 'w').write(str(time.time()))

