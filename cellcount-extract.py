'''
Written to extract cell count data from xls files.
'''

import os

rootdir = "/home/barbara/Dropbox/shared_work/growthzone/cell_count_sample/"
out = open("%s/results.csv" %rootdir, "w")

ids,data = [],[]
for subdir,dirs,files in os.walk(rootdir):
	for f in files:
		#check if this is an xls result file
		if f.split('.')[-1] != 'xls':
			continue
		#this should not be a problem, but just in case: check if the word 'area' appears in the filename
		try:
			fname,area = f.split('_area')
			area = area[0]
		except IndexError:
			continue
		#what channel was used?
		if f.lower().find('dapi') >= 0:
			channel = 'DAPI'
		elif f.lower().find('gfp') >= 0:
			channel = 'GFP'
		else:
			channel = 'unknown'
		#now open the file and retrieve the number of counts (i.e. number of cells)
		xlsfile = open("%s/%s" %(subdir,f))
		for line in xlsfile:
			ncells = line.split()[0]
		xlsfile.close()
		ids.append(fname)
		data.append([fname,channel,area,ncells])

#write the data to file.
ids = set(ids)
out.write("ID,area1-dapi,area1-gfp,area2-dapi,area2-gfp,area3-dapi,area3-gfp\n")
for i in ids:
	line = [i,0,0,0,0,0,0]
	for d in data:
		if d[0] != i:
			continue
		if d[1] == 'DAPI':
			if d[2] == '1':
				line[1] = d[3]
			elif d[2] == '2':
				line[3] = d[3]
			elif d[2] == '3':
				line[5] = d[3]
		elif d[1] == 'GFP':
			if d[2] == '1':
				line[2] = d[3]
			elif d[2] == '2':
				line[4] = d[3]
			elif d[2] == '3':
				line[6] = d[3]
	line_text = ''
	for l in line:
		line_text += str(l)
		line_text += ','
	out.write("%s\n" %line_text[:-1])
