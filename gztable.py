import os

folder = "/home/barbara/Dropbox/shared_work/growthzone/"
msfile = "temp/"
outputdb = open("%soutput.csv" %(folder),"w")


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

'''
read individual files to produce one output file
with all measurements as well as averages.
'''
outputdb.write("filename,devt_time,segments,repeat,w1,w2,w3,w4,l5,l6,l7,l8,a1,a2,a3\n")
for img in filelist:
	metafile = open("%s%s%s.%s_meta.txt" %(folder,msfile,img,jpgdict[img]))
	meta = metafile.readlines()
	segm = int(meta[1].strip().split()[1]) # takes 2nd line, 2nd element of meta file: segment number
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
		outputdb.write("%s.%s,%s,%s,%s," %(img,jpgdict[img],img[:5],segm,i))# collect image filename to measurement number
		w1 = float(length[1].split()[8])/cr #8th item depends on formatting imagej! pay attention!
		if segm == 0:
			w2=w3=w4=l5=l7=l8=a1=a2=a3=""
			l6 = float(length[2].split()[8])/cr
		elif segm == 1:
			w3=w4=l7=l8=a2=a3=""
			w2=float(length[2].split()[8])/cr
			l5=float(length[3].split()[8])/cr
			l6=float(length[4].split()[8])/cr
			a1=float(area[1].split()[2])/(cr*cr)
		elif segm == 2:
			w4=l8=a3=""
			w2=float(length[2].split()[8])/cr
			w3=float(length[3].split()[8])/cr
			l5=float(length[4].split()[8])/cr
			l6=float(length[5].split()[8])/cr
			l7=float(length[6].split()[8])/cr
			a1=float(area[1].split()[2])/(cr*cr)
			a2=float(area[2].split()[2])/(cr*cr)
		else:
			w2=float(length[2].split()[8])/cr
			w3=float(length[3].split()[8])/cr
			w4=float(length[4].split()[8])/cr
			l5=float(length[5].split()[8])/cr
			l6=float(length[6].split()[8])/cr
			l7=float(length[7].split()[8])/cr
			l8=float(length[8].split()[8])/cr
			a1=float(area[1].split()[2])/(cr*cr)
			a2=float(area[2].split()[2])/(cr*cr)
			a3=float(area[3].split()[2])/(cr*cr)
		outputdb.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" %(w1,w2,w3,w4,l5,l6,l7,l8,a1,a2,a3))
	#collect averages: how about a list and then averaging its items?
