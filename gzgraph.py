'''
This script can be used to convert a csv table with measurement data to a given set
of graphs. It is adjusted to growth zone measurements made with an .ijm macro
that can be found in the same git repo (bvreede/growthzone).
When in doubt, check the conditions below for the precise file set-up that is required
for the script to function well!
Author: Barbara Vreede
Contact: b.vreede@gmail.com
Date: 5 November 2014
'''

import csv

'''
Specify input parameters: input folder and file.

'''
folder = "/home/barbara/Dropbox/shared_work/growthzone"
data = "output.csv"

'''
Read input file and import the data to memory.
This works with a flat csv table with the columns in the following order:
- [unspecified]
- developmental time window (e.g. '50-52')
- segment number (e.g. '3'); must be an integer
- measurement count (for a total of 3 measurements per image); must be 1, 2, or 3
- [n measurements; must be floats]
'''
csvdata = csv.reader(open("%s/%s" %(folder,data)))
devt_time = []
segments = []
temp = [] #temporary dataset: collects the three measurements done on each image
data = [] #the final dataset
for line in csvdata:
	devt_time.append(line[1])
	try:
		segments.append(int(line[2])) #only append values that can be integers to segment number list
	except ValueError:
		continue
	if (line[3] == '1') or (line[3] == '2'): #save the first two measurement entries of a photo
		temp.append(line)
	elif line[3] == '3': #the third and final measurement entry of the photo
		temp.append(line)
		if len(temp) != 3:
			print "Error: total measurements on photo %s is not 3. Adjust script or measurements; results invalid." %line[0]
			break
		td = [line[1],int(line[2])] # enter the age bracket and segment number to the dataset
		for i in range(4,len(temp[0])): #for all measured parameters:
			try:
				k = [float(temp[0][i]),float(temp[1][i]),float(temp[2][i])]
			except ValueError: #this happens if there are no entries; in that case the value is 0 for each measurement
				k = [0.0,0.0,0.0]
			d = sum(k)/3
			td.append(d)
		data.append(td)	
		temp = []

devt_time = list(set(devt_time[1:])) #make a list of unique devt_time entries, except the header
segments = list(set(segments)) #make a list of unique segments entries
devt_time.sort()
segments.sort


### PLOTS ###
'''
1. width of GZ divided by length of GZ, in the different segmental stages.
2. length of GZ divided by length of GZ until crossing point of the length/width measurements -   in the different segmental stages.
3. change in GZ / first segment / second segment size iin the different segmental stages.
4. width of GZ divided by width of 1st segment in the different segmental stages.
5. length of first segment divided by length of 2nd seg' in the different segmental stages.
6. size of 1st segment divided by size of 2nd seg' in the different segmental stages.
7. size of GZ in embryos with X segments devided by size of GZ in embryos with X+1 segments 
'''
