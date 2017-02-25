import os
import numpy as np

folder = "/home/barbara/Dropbox/"
msfile = "rawdata/"
outputdb = open("%soutput2.csv" %(folder),"w")
#out_tt = open("%stidy_measurements-bystage.csv" %(folder),"w")
#out_tt_a = open("%stidy_measurements-byage.csv" %(folder),"w")

### CONVERSION RATE: 1 PIXEL = ?? MICROMETER
cr=0.048

'''
read inputfolder and find all unique identifiers;
save to create a list of all images that have
been measured.
Also makes dictionary of extensions. WARNING!
WILL GIVE TROUBLE IF EXTENSIONS ARE LONGER THAN 3
CHARACTERS!
'''
filelist_long = []
jpgdict = {}
for filename in os.listdir(folder + msfile): # directory: e.g. 'temp' directory (msfile) in the 'growthzone' folder (folder)
	fn = filename.split('.')[0] # takes only the first indicator (prior to .jpg) to add to the filelist
	filelist_long.append(fn)
	jpgdict[fn] = filename.split('.')[1][:3] # makes a dictionary of the image extensions
fileset = set(filelist_long) # removes duplicates
filelist = list(fileset)

'''
check that all files in the filelist are indeed
complete. If any measurement of length is
missing, the image name will be deleted from the
list of images for further processing.
NOTE! Area measurements are NOT checked (if there are
0 segments, there will not be area measurements).
'''
removelist = []
for img in filelist:
	for i in range(1,4):
		if os.path.exists("%s%s%s.%s%s_len.txt" %(folder,msfile,img,jpgdict[img],i)):
			continue
		else:
			print "not all measurements completed for", img
			removelist.append(img)
	if os.path.exists("%s%s%s.JPG_meta.txt" %(folder,msfile,img)):
		continue
	else:
		print "meta information mising for", img
		removelist.append(img)
removeset = set(removelist) # removes duplicates
for rem in removeset:
	filelist.remove(rem) # chuck all items that have incomplete measurements

#prepare lists for averages and standarddev
#name_meas = ['w1','w2','w3','w4','l5','l6','l7','l8','a1','a2','a3','a4']
#collect_meas = [[[] for x in range(9)] for m in name_meas]
#mean_meas = [['' for x in range(9)] for m in name_meas]
#var_meas = [['' for x in range(9)] for m in name_meas]

#first set with ages
#ages = ['44-46','46-48','48-50','50-52','52-54','54-56']
#second set with ages
#for i in range(44,56):
#	a = '%s-%s' %(str(i),str(i+1))
#	ages.append(a)

#name_meas_a = name_meas + ['stage']
#collect_meas_a = [[[] for x in range(len(ages))] for m in name_meas_a]
#mean_meas_a = [['' for x in range(len(ages))] for m in name_meas_a]
#var_meas_a = [['' for x in range(len(ages))] for m in name_meas_a]


'''
read individual files to produce one output file
with all measurements.
'''
#NB!! CHECK THE OUTPUT FILE FOR THE CORRECT LOCATION OF MEASUREMENT DATA
## where is the segment number found in the meta file?
## NOTE these are python indices; so 0 is the first line, etc.
# line
ms_l = 1
# element in line
ms_e = 1

## where is the first length measurement found in the length file?
# line
lm_l = 1
# element in line
lm_e = 8

## where is the first area measurement found in the area file?
# line
am_l = 1
# element in line
am_e = 2

outputdb.write("filename,devt_time,segments,repeat,w1,w2,w3,w4,l5,l6,l7,l8,a1,a2,a3,a4\n")
for img in filelist:
#	cur_meas = [[] for m in name_meas]
	metafile = open("%s%s%s.%s_meta.txt" %(folder,msfile,img,jpgdict[img]))
	meta = metafile.readlines()
	segm = int(meta[ms_l].strip().split()[ms_e]) # takes 2nd line, 2nd element of meta file: segment number
	age = img[:5]
	for i in range(1,4): # for each measurement (1-3):
		#opening result files...
		lenfile = open("%s%s%s.%s%s_len.txt" %(folder,msfile,img,jpgdict[img],i))
		length = lenfile.readlines()
		if os.path.exists("%s%s%s.%s%s_area.txt" %(folder,msfile,img,jpgdict[img],i)): #areafile does not always exist(eg 0 segments)
			areafile = open("%s%s%s.%s%s_area.txt" %(folder,msfile,img,jpgdict[img],i))
			area = areafile.readlines()
		else:
			if segm != 0: # this means an area file is missing, but not for a good reason!
				print "not all area measurements done for", img
				break

		outputdb.write("%s.%s,%s,%s,%s," %(img,jpgdict[img],age,segm,i))# collect image filename to measurement number

		w1 = float(length[lm_l].split()[lm_e])*cr
		if segm == 0: #no segments, so only w1 and l6 are known
			l6 = float(length[lm_l+1].split()[lm_e])*cr
			w2=w3=w4=l5=l7=l8=a1=a2=a3=a4="" #a4 is added, it's the total of gz area and 1st segment area
		if segm == 1: #one segment, so only w1,w2,l5,l6, and a1 are known
			w2=float(length[lm_l+1].split()[lm_e])*cr
			l5=float(length[lm_l+2].split()[lm_e])*cr
			l6=float(length[lm_l+3].split()[lm_e])*cr
			a1=float(area[am_l].split()[am_e])*(cr*cr)
			w3=w4=l7=l8=a2=a3=a4=""
		if segm == 2: #two segments, so w1,w2,w3,l5,l6,l7,a1,a2, and a4 are known
			w2=float(length[lm_l+1].split()[lm_e])*cr
			w3=float(length[lm_l+2].split()[lm_e])*cr
			l5=float(length[lm_l+3].split()[lm_e])*cr
			l6=float(length[lm_l+4].split()[lm_e])*cr
			l7=float(length[lm_l+5].split()[lm_e])*cr
			a1=float(area[am_l].split()[am_e])*(cr*cr)
			a2=float(area[am_l+1].split()[am_e])*(cr*cr)
			a4=a1+a2
			w4=l8=a3=""
		if segm >= 3:
			w2=float(length[lm_l+1].split()[lm_e])*cr
			w3=float(length[lm_l+2].split()[lm_e])*cr
			w4=float(length[lm_l+3].split()[lm_e])*cr
			l5=float(length[lm_l+4].split()[lm_e])*cr
			l6=float(length[lm_l+5].split()[lm_e])*cr
			l7=float(length[lm_l+6].split()[lm_e])*cr
			l8=float(length[lm_l+7].split()[lm_e])*cr
			a1=float(area[am_l].split()[am_e])*(cr*cr)
			a2=float(area[am_l+1].split()[am_e])*(cr*cr)
			a3=float(area[am_l+2].split()[am_e])*(cr*cr)
			a4=a1+a2
		outputdb.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" %(w1,w2,w3,w4,l5,l6,l7,l8,a1,a2,a3,a4))
#		for k,measurement in enumerate((w1,w2,w3,w4,l5,l6,l7,l8,a1,a2,a3,a4)):#iterate through measurements and add them to the list
#			if measurement == "": #empty measurement, don't add it
#				continue
#			cur_meas[k].append(measurement)
	#now add the average to the collection of averages at the right stage
#	for n,mlist in enumerate(cur_meas):
#		stage = segm-1 #the ID in the list is the number of stripes minus one (because it starts counting at 0, obv)
#		agei = ages.index(age) #the ID in the list of ages
#		if mlist == []: #empty measurement, don't add anything
#			continue
#		am = np.mean(mlist)
#		collect_meas[n][stage].append(am)
#		collect_meas_a[n][agei].append(am)
#	collect_meas_a[-1][agei].append(segm)

#now add the averages and variances to the appropriate lists for stages
#for m in range(len(name_meas)): #m is the measurement
#	for s in range(9): #s is the stage
#		if collect_meas[m][s]==[]:
#			continue
#		mean=np.mean(collect_meas[m][s])
#		var=np.var(collect_meas[m][s])
#		mean_meas[m][s]=mean
#		var_meas[m][s]=var

#now add the averages and variances to the appropriate lists for ages
#for m in range(len(name_meas_a)): #m is the measurement
#	for a in range(len(ages)): #a is the age
#		if collect_meas_a[m][a]==[]:
#			continue
#		mean=np.mean(collect_meas_a[m][a])
#		var=np.var(collect_meas_a[m][a])
#		mean_meas_a[m][a]=mean
#		var_meas_a[m][a]=var


#write the results to a tidy table
#out_tt.write("stage,w1_m,w1_v,w2_m,w2_v,w3_m,w3_v,w4_m,w4_v,l5_m,l5_v,l6_m,l6_v,l7_m,l7_v,l8_m,l8_v,a1_m,a1_v,a2_m,a2_v,a3_m,a3_v,a4_m,a4_v\n")
'''
for k in range(9):
	out_tt.write("%s" %str(k+1))
	for n in range(len(name_meas)):
		out_tt.write(",%s,%s" %(mean_meas[n][k],var_meas[n][k]))
	out_tt.write("\n")
out_tt.close()

#write the results to a tidy table, by age
out_tt_a.write("age,w1_m,w1_v,w2_m,w2_v,w3_m,w3_v,w4_m,w4_v,l5_m,l5_v,l6_m,l6_v,l7_m,l7_v,l8_m,l8_v,a1_m,a1_v,a2_m,a2_v,a3_m,a3_v,a4_m,a4_v,stage_m, stage_v\n")
for k,a in enumerate(ages):
	out_tt_a.write(a)
	for n in range(len(name_meas_a)):
		out_tt_a.write(",%s,%s" %(mean_meas_a[n][k],var_meas_a[n][k]))
	out_tt_a.write("\n")
out_tt_a.close()
'''
