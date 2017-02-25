'''
This script can be used to convert a csv table with measurement data to a prettier
csv table that can then be fed into a new script (gzgraph.py) to make
graphs. It is adjusted to growth zone measurements made in ImageJ with an .ijm macro
that can be found in the same git repo (bvreede/growthzone).
When in doubt, check the conditions below (in comment sections before indvidual modules
in the script) for the precise file set-up that is required for the script to function well,
and the results to not lie to you.
Author: Barbara Vreede
Contact: b.vreede@gmail.com
Date: 26 November 2014
'''

import csv

'''
Specify input parameters: input/output folders and files.

'''
folder = "/home/barbara/Dropbox/"
data = "output2.csv"
outdata = "gzdata2"

'''
Read input file and import the data to memory.
This works with a flat csv table with the columns in the following order:
- [unspecified]
- developmental time window (e.g. '50-52')
- segment number (e.g. '3'); must be an integer
- measurement count (for a total of 3 measurements per image); must be 1, 2, or 3
- [n measurements; must be floats]
Do check the 'data explained' bit, for info that goes onto headers, etc.
'''
csvdata = csv.reader(open("%s/%s" %(folder,data)))
devt_time = []
segments = []
temp = [] #temporary dataset: collects the three measurements done on each image, before averaging
data = [] #the final dataset, with measurements averaged
for line in csvdata:
	#get devt_time categories
	devt_time.append(line[1])
	#get segment number categories
	try:
		segments.append(int(line[2])) #only append values that can be integers to segment number list
	except ValueError:
		continue
	#get measurements 1-3 per image.
	if (line[3] == '1') or (line[3] == '2'): #save the first two measurement entries of a photo
		temp.append(line)
	elif line[3] == '3': #the third and final measurement entry of the photo
		temp.append(line)
		#test if three measurements are from the same image
		if temp[0][0] != temp[1][0] or temp[1][0] != temp[2][0]:
			print "Error: measurements not in order on image" + line[0]
			break
		#test if there are three measurements in total.
		if len(temp) != 3:
			print "Error: total measurements on photo %s is not 3. Adjust script or measurements; results invalid." %line[0]
			break
		devt1 = float(line[1][:2])
		devt2 = float(line[1][-2:])
		avg_age = (devt1+devt2)/2
		td = [line[0],avg_age,int(line[2])] # enter the age bracket and segment number to the dataset
		for i in range(4,len(temp[0])): #for all measured parameters:
			try:
				k = [float(temp[0][i]),float(temp[1][i]),float(temp[2][i])]
			except ValueError: #this happens if there are no measurement entries; in that case the value is 0 for each measurement
				k = [0.0,0.0,0.0]
			d = sum(k)/3
			td.append(d)
		data.append(td)	
		temp = []

#organize all segment numbers into a list:
segments = list(set(segments)) #make a list of unique 'segments' entries
segments.sort()

#organize all ages into a dictionary (number as key; category as value)
#nb, this is not used at the moment, but can be at a later stage
devt_time = list(set(devt_time[1:])) #make a list of unique 'devt_time' entries, except the header
devt_time.sort()
agedict = {}
for k in devt_time:
	agedict[int(k[:2])+1] = k

### DATA EXPLAINED: ###
## order of measurements:\t\t'w1'\t'w2'\t'w3'\t'w4'\t'l5'\t'l6'\t'l7'\t'l8'\t'a9'\t'a10'\t'a11'\n")
## corresponding to [data]:\t2   \t3   \t4   \t5   \t6   \t7   \t8   \t9   \t10  \t11   \t12\n\n")
## These correspond to the following measurements in the macro:\n")
## w1/[2]:\tThe width of the growthzone at its widest part\n") 
## w2/[3]:\tWidth of the first stripe\n")
## w3/[4]:\tWidth of the second stripe\n")
## w4/[5]:\tWidth of the third stripe\n") 
## l5/[6]:\tThe tip of the growthzone to the first stripe\n")
## l6/[7]:\tThe tip of the growthzone to the middle of the cross section of the growth zone (w1)\n")
## l7/[8]:\tLength between the first and second stripe\n")
## l8/[9]:\tLength between the second and third stripe\n") 
## a9/[10]:\tThe area of the growthzone up to the first stripe\n")
## a10/[11]:\tThe area of the growthzone between the first and second stripe\n")
## a11/[12]:\tThe area of the growthzone between the second and third stripe\n\n")
mlabels = ['filename','age (in hrs)','segments','growthzone width','stripe 1 width','stripe 2 width', 'stripe 3 width', 'growthzone length', 'growthzone top half length','1st segment length','2nd segment length','growthzone area','1st segment area','2nd segment area','gz+1st_segment']


'''
Now, it's time to write the data to a new file. Rejoice!
'''

# open the output file
out = open("%s/%s.csv" %(folder,outdata), "w")
out_nohead = open("%s/%s_noheaders.csv" %(folder,outdata), "w")

# write the headers
head = ''
for m in mlabels:
	head += str(m)
	head += ','
out.write("%s\n" %head[:-1])

# write the data
for line in data:
	wl = ""
	for i in line:
		wl += str(i)
		wl += ','
	out.write("%s\n" %wl[:-1])
	out_nohead.write("%s\n" %wl[:-1])

out.close()
out_nohead.close()
