'''
This script can be used to convert a csv table with measurement data to a given set
of graphs. It is adjusted to growth zone measurements made in ImageJ with an .ijm macro
that can be found in the same git repo (bvreede/growthzone).
When in doubt, check the conditions below (in comment sections before indvidual modules
in the script) for the precise file set-up that is required for the script to function well!
Author: Barbara Vreede
Contact: b.vreede@gmail.com
Date: 5 November 2014
'''

import csv, pylab

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
		td = [line[1],int(line[2])] # enter the age bracket and segment number to the dataset
		for i in range(4,len(temp[0])): #for all measured parameters:
			try:
				k = [float(temp[0][i]),float(temp[1][i]),float(temp[2][i])]
			except ValueError: #this happens if there are no measurement entries; in that case the value is 0 for each measurement
				k = [0.0,0.0,0.0]
			d = sum(k)/3
			td.append(d)
		data.append(td)	
		temp = []

devt_time = list(set(devt_time[1:])) #make a list of unique 'devt_time' entries, except the header
segments = list(set(segments)) #make a list of unique 'segments' entries
devt_time.sort()
segments.sort()

### DATA EXPLAINED: ###
### order of measurements:  'w1', 'w2', 'w3', 'w4', 'l5', 'l6', 'l7', 'l8', 'a1', 'a2', 'a3'
### corresponding to [data]: 2     3     4     5     6     7     8     9     10    11    12
### Which correspond to the following measurements in the macro:
##### w1/[2]: The width of the growthzone at its widest part
##### w2/[3]: Width of the first stripe
##### w3/[4]: Width of the second stripe
##### w4/[5]: Width of the third stripe
##### l5/[6]: The tip of the growthzone to the first stripe
##### l6/[7]: The tip of the growthzone to the middle of the cross section of the growth zone (w1)
##### l7/[8]: Length between the first and second stripe
##### l8/[9]: Length between the second and third stripe
##### l9/[10]: The area of the growthzone up to the first stripe
##### l10/[11]: The area of the growthzone between the first and second stripe
##### l11/[12]: The area of the growthzone between the second and third stripe

def plotmakr(x,y,xlab,ylab,name,clr):
	pylab.xlabel(xlab)
	pylab.ylabel(ylab)
	pylab.xlim([0,10])
	pylab.title('%s by %s' %(ylab,xlab))
	pylab.plot(x,y,clr)
	pylab.savefig('%s.png' %name)
	#pylab.close()
	#pylab.clf()
	return [],[]


### PLOTS ###
#1. width of GZ divided by length of GZ, in the different segmental stages.
## data[2]/data[6] by data[1]

x,y=[],[]
for line in data:
	y.append(line[2]/line[6])
	x.append(line[1]) 
x,y = plotmakr(x,y,'segment number','GZ width / GZ length','plot1','c.')

#2. length of GZ divided by length of GZ until crossing point of the length/width measurements in the different segmental stages
## data[6]/data[7] by data[1]

for line in data:
	y.append(line[6]/line[7])
	x.append(line[1])
x,y = plotmakr(x,y,'segment number','GZ length / top GZ','plot2','b.')

#3. change in GZ / first segment / second segment size in the different segmental stages.
## ???
## NB not all measurements have 2nd segment!

#4. width of GZ divided by width of 1st segment in the different segmental stages.
## data[2]/data[3] by data[1]
for line in data:
	y.append(line[2]/line[3])
	x.append(line[1])
x,y = plotmakr(x,y,'segment number','GZ width / 1st segment width','plot4','r.')

#5. length of first segment divided by length of 2nd seg' in the different segmental stages.
## data[8]/data[9] by data[1]
## NB not all measurements have 2nd segment!
for line in data:
	if line[9] == 0.0:
		continue
	y.append(line[8]/line[9])
	x.append(line[1])
x,y = plotmakr(x,y,'segment number','1st segment length / 2nd segment length','plot5','g.')

#6. size of 1st segment divided by size of 2nd seg' in the different segmental stages.
## data[11]/data[12] by data[1]
## NB not all measurements have 2nd segment!
for line in data:
	if line[12] == 0.0:
		continue
	y.append(line[11]/line[12])
	x.append(line[1])
x,y = plotmakr(x,y,'segment number','1st segment area / 2nd segment area','plot6','mx')

#7. size of GZ in embryos with X segments devided by size of GZ in embryos with X+1 segments 
## total(data[10])_segment/total(data[10])_segment+1 by segments
gzsize = {}
for s in segments:
	sl = []
	for line in data:
		if line[1] == s:
			sl.append(line[10])
	gzsize[s] = sum(sl)/len(sl)
for i in range(1,len(segments)):
	x.append(i)
	y.append(gzsize[i]/gzsize[i+1])
			
x,y = plotmakr(x,y,'segment number','GZ size (X) / GZ size (X+1)','plot7','k.')
