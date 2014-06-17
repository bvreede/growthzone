import os

folder = "/home/barbara/Dropbox/growthzone/"
msfile = "temp/"
outputdb = open("%soutput.csv" %(folder),"w")

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
complete. If any item (1-3, len, area, meta) is
missing, the image name will be deleted from the
list of images for further processing.
'''
removelist = []
for img in filelist:
	for i in range(1,3):
		for tp in ("len","area"):
			if os.path.exists("%s%s%s.%s%s_%s.txt" %(folder,msfile,img,jpgdict[img],i,tp)):
				continue
			else:
				print "not all", tp, "measurements completed for", img
				removelist.append(img)
	if os.path.exists("%s%s%s.JPG_meta.txt" %(folder,msfile,img)):
		continue
	else:
		print "meta information mising for", img
		removelist.append(img)
removeset = set(removelist) # removes duplicates
for rem in removeset:
	filelist.remove(rem)

'''
read individual files to produce one output file
with all measurements as well as averages.
'''
outputdb.write("filename,devt_time,segments,measurement,l1,l2,l3,l4,b1,b2,b3,a1,a2,a3\n")
for img in filelist:
	metafile = "%s%s%s.%s_meta.txt" %(folder,msfile,img,jpgdict[img])
	meta = open(metafile)
	for i in range(1,3):	# for each measurement (1-3):
		outputdb.write("%s.jpg,%s," %(img,img[:5],))# collect image filename
	# collect developmental time
	# collect segment number
	# collect length + width data (depending on # segments)
	# collect area data
