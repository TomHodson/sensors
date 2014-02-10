import time, math
from datetime import datetime as dt
from tempodb import Client, DataPoint

nodeIDs = {1:'my room temp', 2:'kitchen', 3:'water', 4:'parents room'}
path = "/home/pi/logs"
#path = '.'

def temp(x):
	val = x / 1023.0
	if val == 1: val = 0.999
	res = 9840.0 / (1 - val) - 9840.0
	t = 1.0 / (1.0/298.15 + 1/3977.0 * math.log(res / 10000.0)) - 273.15
	#print "resistance: {:.1f}K , temp: {}C".format(res/1000.0, t)
	return t

data = open("{}/sensordata".format(path)).readlines()

try:
	last_sent = dt.fromtimestamp(float(open("{}/last_sent_to_tempodb".format(path)).read()))
except:
	last_sent = dt.fromtimestamp(float(0))

data = [dict(i.split('=') for i in d.strip('\n').split(', ')) for d in data]
new_data = [d for d in data if dt.fromtimestamp(int(d['time'])) >= last_sent]
for d in new_data:
	d['temp'] = temp(int(d['temp']))
	d['id'] = int(d['id'])
	d['vcc'] = float(d['vcc'])
	d['pipe'] = int(d['pipe'])
	d['tries'] = int(d['tries'])
	d['time'] = dt.fromtimestamp(int(d['time']))

print len(new_data)
sorted_by_id = {}
for d in new_data:
	key = nodeIDs.get(d['id']) or str(d['id'])
	p = DataPoint(d['time'], d['temp'])
	try:
		sorted_by_id[key].append(p)
	except:
		sorted_by_id[key] = [p]

print sorted_by_id


#print data[5:10]
#plot([d['time'].tm_hour + d['time'].tm_min / 59.0 for d in data], [d['temp'] for d in data])

#time_dict = {d['time'] : d for d in data}
#show()
# Modify these with your credentials found at: http://tempo-db.com/manage/
API_KEY = 'f3c71667bab7425fb9ac728409d22f1e'
API_SECRET = '1b72a21ad76247e8afc2b00ba46df329'

if len(sorted_by_id) > 0:
	client = Client(API_KEY, API_SECRET)
	for key in sorted_by_id:
		print "sent {} under key {}".format(sorted_by_id[key], key)
		client.write_key(key,sorted_by_id[key])
	open("{}/last_sent_to_tempodb".format(path), 'w').write(str(time.time()))

