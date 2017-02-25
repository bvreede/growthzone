'''
Script for Fig 1 violin plots
'''

import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("/home/barbara/Dropbox/pandasdata.csv")

df_gz = df[df["Item"]=="gz"]


#growthzone length
sns.violinplot(x="Stage",y="Length", data=df_gz,palette="muted",order=range(1,9),scale="count",inner="stick")
plt.show()


