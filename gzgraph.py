'''
This script can be used to convert a csv table with measurement data to a given set
of graphs. It is adjusted to growth zone measurements made in ImageJ with an .ijm macro
that can be found in the same git repo (bvreede/growthzone).
When in doubt, check the conditions below (in comment sections before indvidual modules
in the script) for the precise file set-up that is required for the script to function well,
and the results to not lie to you.
Author: Barbara Vreede
Contact: b.vreede@gmail.com
Date: 5 November 2014
'''

import os, csv, numpy
import matplotlib.pyplot as plt


'''
Specify input parameters: input/output folders and files.

'''
folder = "/home/barbara/Dropbox/shared_work/growthzone"
data = "output.csv"
outfolder = "plots_underconstruction"
readmefile = "README.txt"

'''
Make outputfolder (if necessary) and open readme file.
'''
if os.path.exists("%s/%s" %(folder,outfolder)):
	pass
else:
	os.system("mkdir %s/%s" %(folder,outfolder))
readme = open("%s/%s/%s" %(folder,outfolder,readmefile), "w")

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
readme.write("order of measurements:\t\t'w1'\t'w2'\t'w3'\t'w4'\t'l5'\t'l6'\t'l7'\t'l8'\t'a9'\t'a10'\t'a11'\n")
readme.write("corresponding to [data]:\t2   \t3   \t4   \t5   \t6   \t7   \t8   \t9   \t10  \t11   \t12\n\n")
readme.write("These correspond to the following measurements in the macro:\n")
readme.write("w1/[2]:\tThe width of the growthzone at its widest part\n") 
readme.write("w2/[3]:\tWidth of the first stripe\n")
readme.write("w3/[4]:\tWidth of the second stripe\n")
readme.write("w4/[5]:\tWidth of the third stripe\n") 
readme.write("l5/[6]:\tThe tip of the growthzone to the first stripe\n")
readme.write("l6/[7]:\tThe tip of the growthzone to the middle of the cross section of the growth zone (w1)\n")
readme.write("l7/[8]:\tLength between the first and second stripe\n")
readme.write("l8/[9]:\tLength between the second and third stripe\n") 
readme.write("a9/[10]:\tThe area of the growthzone up to the first stripe\n")
readme.write("a10/[11]:\tThe area of the growthzone between the first and second stripe\n")
readme.write("a11/[12]:\tThe area of the growthzone between the second and third stripe\n\n")
mlabels = ['age','segments','growthzone width','stripe 1 width','stripe 2 width', 'stripe 3 width', 'growthzone length', 'growthzone top half length','1st segment length','2nd segment length','growthzone area','1st segment area','2nd segment area']

### HOW TO MAKE THE PLOTS ###
plotcount = 0

def plotmakr(x,y,title,descr,calc,xlab=segments):
	# calculate the averages:
	xavg = list(set(x)) #collect all distinct x values in the dataset
	xavg.sort()
	yavg = []
	for xval in xavg:
		ycoll = []
		for p,q in zip(x,y):
			if p == xval:
				ycoll.append(q)
		yval = sum(ycoll)/len(ycoll)
		yavg.append(yval)

	# apply labels, set graph limits
	plt.xlabel(xlab)
	#plt.ylabel(ylab)
	plt.xlim([0,10])
	#plt.ylim([0,4])
	plt.title(title)

	# name the plot & write the readme description
	plotcount += 1
	name = 'plot' + str(plotcount)
	readme.write("%s:\t%s\n\t%s\n\t%s\n\n" %(name,title,descr,calc)

	# plot the actual data
	plt.plot(x,y,'y.') #optional for multiple plots in 1 fig: label='label'
	#plt.legend() #when applying a label
	plt.savefig('%s/%s/%s-basic.svg' %(folder,outfolder,name)) #save the plot without the trendline
	plt.savefig('%s/%s/%s-basic.png' %(folder,outfolder,name)) #also save a .png

	# calculate and plot the trendline/average
	z = numpy.polyfit(xavg, yavg, 7) #calculate trendline as 7-degree polynomial
	p = numpy.poly1d(z)
	plt.plot(xavg,p(xavg),"k--")
	plt.plot(xavg,yavg,'ko')
	plt.savefig('%s/%s/%s-trend.svg' %(folder,outfolder,name))#save the plot with the trendline
	plt.savefig('%s/%s/%s-trend.png' %(folder,outfolder,name))#also save a .png

	# close matplotlib to clear the data for the next plot; return empty lists for new x/y collection
	plt.close()
	plt.clf()
	return [],[]


### PLOTS ###

## basic measurement plots ##
x,y=[],[]

for i in range(2,len(data[0])):
	for line in data:
		if line[i] == 0.0:
			continue
		y.append(line[i])
		x.append(line[1])
	plname,x,y = plotmakr(x,y,,mlabels[i])
	

## PLOT: GZ WIDTH/GZ LENGTH ##
for line in data:
	y.append(line[2]/line[6])
	x.append(line[1]) 

plname,x,y = plotmakr(x,y,'segment number','GZ width / GZ length','plot1')
readme.write("%s:\twidth of GZ divided by length of GZ, in the different segmental stages.\n" %name)
readme.write("\tdata[2]/data[6] by data[1]\n\n")


## PLOT 2 ##
readme.write("Plot2:\tlength of GZ divided by length of GZ until crossing point of the length/width measurements in the different segmental stages\n")
readme.write("\tdata[6]/data[7] by data[1]\n\n")

for line in data:
	y.append(line[6]/line[7])
	x.append(line[1])
plname,x,y = plotmakr(x,y,'segment number','GZ length / top GZ','plot2')

'''
## PLOT 3 ##
readme.write("\n")
readme.write("\n\n")
#3. change in GZ / first segment / second segment size in the different segmental stages.
## ???
## NB not all measurements have 2nd segment!


## PLOT 4 ##
readme.write("Plot4:\twidth of GZ divided by width of 1st segment in the different segmental stages.\n")
readme.write("\tdata[2]/data[3] by data[1]\n\n")

for line in data:
	y.append(line[2]/line[3])
	x.append(line[1])
x,y = plotmakr(x,y,'segment number','GZ width / 1st segment width','plot4')

## PLOT 5 ##
readme.write("Plot5:\tlength of first segment divided by length of 2nd seg' in the different segmental stages.\n")
readme.write("\tdata[8]/data[9] by data[1]\n\n")
## NB not all measurements have 2nd segment!

for line in data:
	if line[9] == 0.0:
		continue
	y.append(line[8]/line[9])
	x.append(line[1])
x,y = plotmakr(x,y,'segment number','1st segment length / 2nd segment length','plot5')

## PLOT 6 ##
readme.write("Plot6:\tsize of 1st segment divided by size of 2nd seg' in the different segmental stages.\n")
readme.write("\tdata[11]/data[12] by data[1]\n\n")
## NB not all measurements have 2nd segment!

for line in data:
	if line[12] == 0.0:
		continue
	y.append(line[11]/line[12])
	x.append(line[1])
x,y = plotmakr(x,y,'segment number','1st segment area / 2nd segment area','plot6')

## PLOT 7 ##
readme.write("Plot7:\tsize of GZ in embryos with X segments devided by size of GZ in embryos with X+1 segments \n")
readme.write("\ttotal(data[10])_segment/total(data[10])_segment+1 by segments\n\n")

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
			
x,y = plotmakr(x,y,'segment number','GZ size (X) / GZ size (X+1)','plot7')

## PLOT ##
readme.write("\n")
readme.write("\n\n")
#8. GZ area by segment number

## PLOT ##
readme.write("\n")
readme.write("\n\n")
#9a. delta GZ area by segment number (absolute size, not percentage)
#9b. 1st segment area number by age
#9c. 2nd segment area number by age(these three can be on one plot, different colour for each one)

## PLOT ##
readme.write("\n")
readme.write("\n\n")
#10. segments per age

## PLOT ##
readme.write("\n")
readme.write("\n\n")
#11. delta segments per age

## PLOT ##
readme.write("\n")
readme.write("\n\n")
#12. y = x + g where y = gz+first segment at t = 1; x = gz at t = 0; g = growth
##is growth different between different segment additions?

## PLOT ##
readme.write("\n")
readme.write("\n\n")
#13. segment 2 in t = 1 - segment 1 in t =0)
##do the segments, once formed, change in size?

'''


readme.close()

