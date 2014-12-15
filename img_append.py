import os, re
img = re.compile('(.+)\.(jpg|jpeg)')
images = [re.match(img, fn) for fn in os.listdir('./') if re.match(img, fn)]

with open('README.md', 'r+') as f:
	readme = f.read()
	print readme
	for a in images:
		if a.group(0) not in readme:
			s = "\n![{}]({}?raw=true)\n".format(a.group(1), a.group(0))
			print "writing {}".format(s)
			f.write(s)
