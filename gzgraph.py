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
infile = "gzdata_noheaders.csv"
outfolder = "plots"
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
Read data & write 'data' db, and 'segments' and 'age' lists
'''
csvin = csv.reader(open("%s/%s" %(folder,infile)))

data = []
segments = []
age = []
for line in csvin:
	# start a list to collect all the info in the correct format
	addlist = []
	for a in range(len(line)):
		if a <= 1:
			addlist.append(int(line[a])) # first two are categories; int not float
		else:
			addlist.append(float(line[a])) # all measurements are floats.
	data.append(addlist)
	age.append(int(line[0]))
	segments.append(int(line[1]))

age = list(set(age))
segments = list(set(segments))

'''
module that calculates data averages and standard deviations.
Input is two numbers, corresponding to columns in the data matrix
(first number is the category, the second number is the data for which
averages etc. need to be calculated)
output is a matrix where each line contains the category, then the average
of datapoints for all instances in that category, and then the standard
deviation of those observations.
'''
def avgmatrix(cat,dat):
	global data
	matrix = []
	# collect all categories
	datacat = []
	for i in data:
		datacat.append(i[cat])
	datacat = list(set(datacat))
	# collect all data per category
	for j in datacat:
		dcoll = []
		for i in data:
			if i[dat] == 0.0:
				continue
			if i[cat] == j:
				dcoll.append(i[dat])
		if sum(dcoll) == 0.0:
			continue
		davg = numpy.mean(dcoll)
		dstd = numpy.std(dcoll)
		line = [j,davg,dstd]
		matrix.append(line)
	return matrix


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

def plotmakr(x,y,title,descr,calc,xlab='segments'):
	# calculate the averages:
	xavg = list(set(x)) #collect all distinct x values in the dataset
	xavg.sort()
	yavg = []
	y_bp = []
	for n in range(min(xavg)-1):
		y_bp.append([])
	for xval in xavg:
		ycoll = []
		for p,q in zip(x,y):
			if p == xval:
				ycoll.append(q)
		yval = sum(ycoll)/len(ycoll)
		yavg.append(yval)
		y_bp.append(ycoll)

	# open figure, apply labels, set graph limits
	plt.figure()
	plt.xlabel(xlab)
	#plt.ylabel(ylab)
	plt.xlim([0,10])
	#plt.ylim([0,4])
	plt.title(title)

	# name the plot & write the readme description
	global plotcount
	plotcount += 1
	name = 'plot' + str(plotcount)
	readme.write("%s:\t%s\n\t%s\n\t%s\n\n" %(name,title,descr,calc))

	# plot the actual data
	plt.plot(x,y,'r.') #optional for multiple plots in 1 fig: label='label'
	#plt.legend() #when applying a label
	plt.savefig('%s/%s/%s-basic.svg' %(folder,outfolder,name)) #save the plot without the trendline
	plt.savefig('%s/%s/%s-basic.png' %(folder,outfolder,name)) #also save a .png

	# calculate and plot the trendline/average
	z = numpy.polyfit(xavg, yavg, 6) #calculate trendline as 6-degree polynomial
	p = numpy.poly1d(z)
	plt.plot(xavg,p(xavg),"k--")
	plt.plot(xavg,yavg,'ko')
	plt.savefig('%s/%s/%s-trend.svg' %(folder,outfolder,name))#save the plot with the trendline
	plt.savefig('%s/%s/%s-trend.png' %(folder,outfolder,name))#also save a .png
	plt.clf()
	plt.close()

	# boxplot with the data
	plt.figure()
	plt.xlabel(xlab)
	#plt.ylabel(ylab)
	plt.xlim([0,10])
	#plt.ylim([0,4])
	plt.title(title)
	plt.boxplot(y_bp)
	#plt.savefig('%s/%s/%s-boxplot.svg' %(folder,outfolder,name))#save the plot with the trendline
	plt.savefig('%s/%s/%s-boxplot.png' %(folder,outfolder,name))#also save a .png
	plt.clf()
	plt.close()
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
	title = mlabels[i]
	descr = '%s in the different segmental stages' %mlabels[i]
	calc = 'data[%s] by data[1]' %i
	x,y = plotmakr(x,y,title,descr,calc)
	

## PLOT: GZ WIDTH/GZ LENGTH ##
for line in data:
	y.append(line[2]/line[6])
	x.append(line[1])

title = 'GZ width / GZ length'
descr = 'width of GZ divided by length of GZ, in the different segmental stages'
calc = 'data[2]/data[6] by data[1]'
x,y = plotmakr(x,y,title,descr,calc)


## PLOT: GZ LENGTH/GZ TIP ##
for line in data:
	y.append(line[6]/line[7])
	x.append(line[1])

title = 'GZ length / top GZ'
descr = 'length of GZ divided by length of GZ until crossing point of the length/width measurements in the different segmental stages'
calc = 'data[6]/data[7] by data[1]'
x,y = plotmakr(x,y,title,descr,calc)


## PLOT: GZ WIDTH / 1st SEG WIDTH ##
for line in data:
	y.append(line[2]/line[3])
	x.append(line[1])

title = 'GZ width / 1st segment width'
descr = 'Width of GZ divided by width of 1st segment in the different segmental stages.'
calc = 'data[2]/data[3] by data[1]'
x,y = plotmakr(x,y,title,descr,calc)


## PLOT: LENGTH 1st/2nd ##
## NB not all measurements have 2nd segment!
for line in data:
	if line[9] == 0.0:
		continue
	y.append(line[8]/line[9])
	x.append(line[1])

title = '1st segment length / 2nd segment length'
descr = 'Length of first segment divided by length of 2nd segment in the different segmental stages'
calc = 'data[8]/data[9] by data[1]'
x,y = plotmakr(x,y,title,descr,calc)

## PLOT: AREA 1st/2nd ##
## NB not all measurements have 2nd segment!
for line in data:
	if line[12] == 0.0:
		continue
	y.append(line[11]/line[12])
	x.append(line[1])

title = '1st segment area / 2nd segment area'
descr = 'Size of 1st segment divided by size of 2nd segment in the different segmental stages'
calc = 'data[11]/data[12] by data[1]'
x,y = plotmakr(x,y,title,descr,calc)


## PLOT: DELTA GZ (2 variants) ##
gzmatrix = avgmatrix(1,10)

for n in range(1,len(gzmatrix)):
	x.append(gzmatrix[n][0])
	y.append((gzmatrix[n][1])-(gzmatrix[n-1][1]))

title = 'delta growthzone area'
descr = 'average GZ size of embryos with X segments minus average GZ size of embryos with X-1 segments'
calc = 'avg(data[10]) in s - avg(data[10]) in s-1 by data[1]'
x,y = plotmakr(x,y,title,descr,calc)

for n in range(1,len(gzmatrix)):
	x.append(gzmatrix[n][0])
	y.append((gzmatrix[n][1])/(gzmatrix[n-1][1]))

title = 'percentage decrease of growthzone area'
descr = 'average GZ size of embryos with X segments divided by average GZ size of embryos with X-1 segments'
calc = 'avg(data[10]) in s / avg(data[10]) in s-1 by data[1]'
x,y = plotmakr(x,y,title,descr,calc)


## PLOT: DELTA SEGMENTS (2x2 variants) ##
## NB not all measurements have 1st/2nd segment!

fsmatrix = avgmatrix(1,11)
for n in range(1,len(fsmatrix)):
	x.append(fsmatrix[n][0])
	y.append((fsmatrix[n][1])-(fsmatrix[n-1][1]))

title = 'delta 1st segment (area)'
descr = 'change in latest ("first") segment size in the different segmental stages'
calc = 'avg(data[11]) in s - avg(data[11]) in s-1 by data[1]'
x,y = plotmakr(x,y,title,descr,calc)

for n in range(1,len(fsmatrix)):
	x.append(fsmatrix[n][0])
	y.append((fsmatrix[n][1])/(fsmatrix[n-1][1]))

title = 'percentage change 1st segment (area)'
descr = 'change in latest ("first") segment size in the different segmental stages'
calc = 'avg(data[11]) in s / avg(data[11]) in s-1 by data[1]'
x,y = plotmakr(x,y,title,descr,calc)

ssmatrix = avgmatrix(1,12)
for n in range(1,len(ssmatrix)):
	x.append(ssmatrix[n][0])
	y.append((ssmatrix[n][1])-(ssmatrix[n-1][1]))

title = 'delta 2nd segment (area)'
descr = 'change in second segment size in the different segmental stages'
calc = 'avg(data[12]) in s - avg(data[12]) in s-1 by data[1]'
x,y = plotmakr(x,y,title,descr,calc)

for n in range(1,len(ssmatrix)):
	x.append(ssmatrix[n][0])
	y.append((ssmatrix[n][1])/(ssmatrix[n-1][1]))

title = 'percentage change 2nd segment (area)'
descr = 'change in second segment size in the different segmental stages'
calc = 'avg(data[12]) in s / avg(data[12]) in s-1 by data[1]'
x,y = plotmakr(x,y,title,descr,calc)


## PLOT: DO SEGMENTS CHANGE IN SIZE? ##
## USE the fsmatrix and ssmatrix calculated before.
## these are the average sizes of each segment (first or second)

for n in range(3,len(segments)):
	### segment 1 in cat 2,3,4,5,6,7,8
	### segment 2 in cat 3,4,5,6,7,8,9
	# get category n
	x.append(n)
	# get segment 2 in category n
	for line in ssmatrix:
		if line[0] == n:
			segtwo = line[1]
	# get segment 1 in category n-1
	for line in fsmatrix:
		if line[0] == n-1:
			segone = line[1]
	y.append(segtwo/segone)

title = 'segment area change post-formation'
descr = 'change in the size of a segment as it transitions from being segment 1 to being segment 2'
calc = 'avg(data[12]) in s / avg(data[11]) in s-1 by data[1]'
x,y = plotmakr(x,y,title,descr,calc)


## PLOT: IS GROWTH DIFFERENT BETWEEN SEGMENT ADDITIONS? ##
## USE gzmatrix, fsmatrix calculated before
## y = x + g where y = gz+first segment at t = 1; x = gz at t = 0; g = growth

## on y axis: g = gz + seg1 at s=0 - gz at s=-1
## for s = 2,3,4,5,6,7,8,9

for n in range(2,len(segments)):
	# get category n
	x.append(n)
	# get segment 1 in category n
	for line in fsmatrix:
		if line[0] == n:
			segone = line[1]
	# get gz in category n
	# get gz in category n-1
	for line in gzmatrix:
		if line[0] == n:
			gz = line[1]
		elif line[0] == n-1:
			gzprev = line[1]
	# calculate growth: (gz+seg)t=0 - (gz)t=-1
	y.append(gz+segone-gzprev)

title = 'gz growth (gz + segment1 - gz in previous stage)'
descr = 'growthzone + segment 1 minus growthzone in the previous segmental stage'
calc = 'avg(data[11])+avg(data[10] in s - avg(data[10]) in s-1, by data[1]'
x,y = plotmakr(x,y,title,descr,calc)

for n in range(2,len(segments)):
	# get category n
	x.append(n)
	# get segment 1 in category n
	for line in fsmatrix:
		if line[0] == n:
			segone = line[1]
	# get gz in category n
	# get gz in category n-1
	for line in gzmatrix:
		if line[0] == n:
			gz = line[1]
		elif line[0] == n-1:
			gzprev = line[1]
	# calculate growth: (gz+seg)t=0 - (gz)t=-1
	y.append((gz+segone)/gzprev)

title = 'growth  ((gz + segment1) / gz in previous stage)'
descr = 'growth in percentagegrowthzone + segment 1 divided by growthzone in the previous segmental stage'
calc = '(avg(data[11])+avg(data[10] in s) / avg(data[10]) in s-1, by data[1]'
x,y = plotmakr(x,y,title,descr,calc)

for n in range(2,len(segments)):
	# get category n
	x.append(n)
	# get segment 1 in category n
	for line in fsmatrix:
		if line[0] == n:
			segone = line[1]
	# get gz in category n
	# get gz in category n-1
	for line in gzmatrix:
		if line[0] == n:
			gz = line[1]
		elif line[0] == n-1:
			gzprev = line[1]
	# calculate growth: (gz+seg)t=0 - (gz)t=-1
	y.append(gz/(gzprev-segone))

title = 'gz growth ( gz / (gz in prev stage - segment1))'
descr = ''
calc = ' avg(data[10] in s) / (avg(data[10] in s-1)-avg(data[11] in s), by data[1]'
x,y = plotmakr(x,y,title,descr,calc)
			

## PLOT: GZ AREA DIVIDED BY LENGTH X WIDTH ##
for line in data:
	y.append(line[10]/(line[2]*line[6]))
	x.append(line[1])

title = 'GZ area / (GZ length x GZ width)'
descr = 'GZ area divided by the product of GZ length and width'
calc = 'data[10]/(data[2]*data[6]) by data[1]'
x,y = plotmakr(x,y,title,descr,calc)

## PLOT: GZ AREA DIVIDED BY GZ LENGTH ##
for line in data:
	y.append(line[10]/line[2])
	x.append(line[1])

title = 'GZ area / length'
descr = 'GZ area divided by GZ length'
calc = 'data[10]/data[2] by data[1]'
x,y = plotmakr(x,y,title,descr,calc)

## PLOT: GZ AREA DIVIDED GZ WIDTH ##
for line in data:
	y.append(line[10]/line[6])
	x.append(line[1])

title = 'GZ area / width'
descr = 'GZ area divided by GZ width'
calc = 'data[10]/data[6] by data[1]'
x,y = plotmakr(x,y,title,descr,calc)


## PLOT: AGE BY SEGMENTS ##
for line in data:
	y.append(line[0])
	x.append(line[1])

title = 'Age by segments'
descr = 'Age in hours by segment (stripe) number'
calc = 'data[0] by data[1]'
x,y = plotmakr(x,y,title,descr,calc)

readme.close()

'''
Notes for update:
- Error bars can be added with: plt.errorbar(x,y,yerr=e) where e is the matrix of error bars.
- plots by age (plus: segments by age, and delta segments by age)
'''


