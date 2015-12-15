import csv

cr=csv.reader(open("/home/barbara/Dropbox/oncopeltus/playground/gzdata.csv"))
out = open("/home/barbara/Dropbox/shared_work/growthzone/pandasdata.csv", "w")

#write headers to outfile
out.write("Stage,Item,Width,Length,Area\n")

def writeinfo(seg,itID,w,l,a):
	if l == '0.0':
		l = 'NaN'
	if a == '0.0':
		a = 'NaN'
	out.write("%s,%s,%s,%s,%s\n" %(seg,itID,w,l,a))

#make all emtpy values NaN
#label stripes: keep stages, but switch '1st' etc to stripe identity

#	1	2	3 (stripe order P-A)
#stripe
#count
# 1	A	-	-
# 2	B	A	-
# 3	C	B	A
# 4	D	C	B
# 5	E	D	C
# 6	F	E	D
# 7	G	F	E
# 8	H	G	F
# 9	I	H	G

stripeID = {'11': 'A', '12': 'B', '13':'C', '14':'D', '15':'E', '16': 'F', '17':'G', '18':'H', '19':'I', '22': 'A', '23': 'B', '24':'C', '25':'D', '26':'E', '27': 'F', '28':'G', '29':'H', '33': 'A', '34': 'B', '35':'C', '36':'D', '37':'E', '38': 'F', '39':'G'}

####### Original:
#0	'age (in hrs)'
#1	'segments'
#2	'growthzone width'
#3	'stripe 1 width'
#4	'stripe 2 width'
#5	'stripe 3 width'
#6	'growthzone length
#7	'growthzone top half length'
#8	'1st segment length'
#9	'2nd segment length'
#10	'growthzone area'
#11	'1st segment area'
#12	'2nd segment area'

####### Goal:
#1	'segments'
#2	'item ID' (=gz, segment A, B, C, etc.)
#3	'width'
#4	'length'
#5	'area'

for line in cr:
	if line[0][:3] == "age": #first line, headers
		continue
	seg = line[1]
	# first assess gz
	itID = 'gz'
	w = line[2]
	l = line[6]
	a = line[10]
	writeinfo(seg,itID,w,l,a) # write info to file
	# then assess first seg
	itID = stripeID['1' + seg]
	w = line[3]
	l = line[8]
	a = line[11]
	writeinfo(seg,itID,w,l,a)# write info to file
	if int(seg) < 2:
		continue
	# then assess second seg
	itID = stripeID['2' + seg]
	w = line[4]
	l = line[9]
	a = line[12]
	writeinfo(seg,itID,w,l,a)# write info to file
	if int(seg) < 3:
		continue
	# then assess third seg
	itID = stripeID['3' + seg]
	w = line[5]
	l = "NaN"
	a = "NaN"
	writeinfo(seg,itID,w,l,a)# write info to file

out.close()
