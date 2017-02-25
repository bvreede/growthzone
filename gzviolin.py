'''
Script for Fig 1 violin plots
'''

import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("/home/barbara/Dropbox/pandasdata.csv")
df_gz = df[df["Item"]=="gz"]
df_seg = df[df["Item"]!="gz"]
df_seg = df_seg.sort_values(by="Item")

sns.set_style("whitegrid")

"""
#growthzone length
plt.ylim(0,50)
sns.violinplot(x="Stage",y="Length", data=df_gz,palette="Blues",order=range(1,9),scale="area",inner="stick",hue="Item")
plt.savefig("/home/barbara/Dropbox/gzlength.svg")
plt.clf()
plt.close()

#growthzone width
plt.ylim(0,40)
sns.violinplot(x="Stage",y="Width", data=df_gz,palette="Blues",order=range(1,9),scale="area",inner="stick",hue="Item")
plt.savefig("/home/barbara/Dropbox/gzwidth.svg")
plt.clf()
plt.close()

#growthzone area
plt.ylim(0,1400)
sns.violinplot(x="Stage",y="Area", data=df_gz,palette="Blues",order=range(1,9),scale="area",inner="stick",hue="Item")
plt.savefig("/home/barbara/Dropbox/gzarea.svg")
plt.clf()
plt.close()


#segments length
plt.ylim(0,13)
sns.violinplot(x="Stage",y="Length", data=df_seg,palette="Set1",order=range(1,9),scale="area",inner="stick",hue="Item")
plt.savefig("/home/barbara/Dropbox/seglength.svg")
plt.clf()
plt.close()
"""
#segments width
plt.ylim(0,30)
sns.violinplot(x="Stage",y="Width", data=df_seg,palette="Set1",order=range(4,7),scale="area",inner="stick",hue="Item")
plt.savefig("/home/barbara/Dropbox/segwidth2.svg")
plt.clf()
plt.close()
"""
#segments area
plt.ylim(0,180)
sns.violinplot(x="Stage",y="Area", data=df_seg,palette="Set1",order=range(1,9),scale="area",inner="stick",hue="Item")
plt.savefig("/home/barbara/Dropbox/segarea.svg")
plt.clf()
plt.close()
"""


