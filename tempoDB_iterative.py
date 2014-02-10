import time, math
from datetime import datetime as dt
from tempodb import Client, DataPoint
from temp import temp

nodeIDs = {1:'my room temp', 2:'kitchen', 3:'water', 4:'parents room'}
path = "/home/pi/logs"
#path = '.'

import os

def reversed_lines(file):
    "Generate the lines of file in reverse order."
    part = ''
    for block in reversed_blocks(file):
        for c in reversed(block):
            if c == '\n' and part:
                yield part[::-1]
                part = ''
            part += c
    if part: yield part[::-1]

def reversed_blocks(file, blocksize=4096):
    "Generate blocks of file's contents in reverse order."
    file.seek(0, os.SEEK_END)
    here = file.tell()
    while 0 < here:
        delta = min(blocksize, here)
        here -= delta
        file.seek(here, os.SEEK_SET)
        yield file.read(delta)

data = open("{}/sensordata".format(path))

try:
	last_sent = dt.fromtimestamp(float(open("{}/last_sent_to_tempodb".format(path)).read()))
except:
	last_sent = dt.fromtimestamp(float(0))

for line in reversed_lines(data):
	d = dict(i.split('=') for i in line.strip('\n').split(', '))
	d['temp'] = temp(int(d['temp']))
	d['id'] = int(d['id'])
	d['vcc'] = float(d['vcc'])
	d['pipe'] = int(d['pipe'])
	d['tries'] = int(d['tries'])
	d['time'] = dt.fromtimestamp(int(d['time']))
	if d['time'] <= last_sent: break

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

