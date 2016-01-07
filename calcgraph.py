import pandas as pd
from math import sqrt
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("/home/barbara/Dropbox/shared_work/growthzone/tidy_measurements.csv")
style = "white"
context= "talk"
sns.set_context(context)
sns.set_style(style)

plt.xlim((1,10))

x = range(2,10) #stages for which growth is calculated

y,s = [],[] #means and standard deviations of the growth
y_,s_ = [],[]
yy,ss = [],[]
for n in range(8):
	#make calculations for area
	ya = df['a1_m'][n+1]+df['a2_m'][n+1]-df['a1_m'][n] #area_gz[stage_n] + area_seg1[stage_n] - area_gz[stage_n-1]
	va = df['a1_v'][n+1]+df['a2_v'][n+1]+df['a1_v'][n] #variances of all three distributions added up
	sa = sqrt(va)
	y.append(ya)
	s.append(sa)
	#make calculations for area in another way
	ya = df['a4_m'][n+1]-df['a1_m'][n] #area_gz[stage_n] + area_seg1[stage_n] - area_gz[stage_n-1]
	va = df['a4_v'][n+1]+df['a1_v'][n] #variances of all three distributions added up
	sa = sqrt(va)
	yy.append(ya)
	ss.append(sa)
	#make calculations for length
	ya = df['l5_m'][n+1]+df['l7_m'][n+1]-df['l5_m'][n] #area_gz[stage_n] + area_seg1[stage_n] - area_gz[stage_n-1]
	va = df['l5_v'][n+1]+df['l7_v'][n+1]+df['l5_v'][n] #variances of all three distributions added up
	sa = sqrt(va)
	y_.append(ya)
	s_.append(sa)

#plt.errorbar(x,y_,yerr=s_) #length plot
plt.errorbar(x,y,yerr=s) #area plot
#plt.errorbar(x,yy,yerr=ss) #area plot with different standard dev
sns.despine()

plt.savefig("/home/barbara/Dropbox/growth-bystage.png")
plt.show()
