######## CellVelocityField.py ##########
#                                      #
# Plots the velocity field for the     #
# cells in the growth zone             #
#                                      #
# sdhester June 2014                   #
########################################

import numpy as np
import matplotlib.pyplot as plt
from math import sqrt

# soa =np.array( [[0,0,3,2], [0,0,1,1],[0,0,9,9]]) 
# X,Y,U,V = zip(*soa)
# plt.figure()
# ax = plt.gca()
# ax.quiver(X,Y,U,V,angles='xy',scale_units='xy',scale=1)
# ax.set_xlim([-1,10])
# ax.set_ylim([-1,10])
# plt.draw()
# plt.show()

#####################
# a=np.array([[1,2,3,4],[2,3,4,5]])
# b=np.array([[3,4,5,6]])
# vec_array=np.concatenate((a,b),axis=0)
# X,Y,U,V=zip(*vec_array)
# plt.figure()
# vecplot=plt.gca()
# vecplot.quiver(X,Y,U,V,angles='xy',scale_units='xy',scale=1)
# vecplot.set_xlim([-10,10])
# vecplot.set_ylim([-10,10])
# plt.draw()
# plt.show()

##########################
x_min=230
x_max=522
y_post=1090
y_lastseg=785
x_center=(x_max-x_min)/2 + x_min
yGZ_center=(y_post-y_lastseg)/2 + y_lastseg
V_p=3
step=20

vel_array=np.array([[0,0,0,0]])

xCM=x_min - step
while xCM <= x_max:
   xCM+=step
   yCM=y_lastseg - step
   print 'xCM=' + str(xCM)
   while yCM <= y_post:
      yCM+=step
      print 'yCM=' + str(yCM)
      d = sqrt((xCM - x_center)**2 + (yCM - (y_post))**2)
      if d < (y_post - (y_lastseg + 50)):
         d2 = sqrt((xCM - x_center)**2 + (yCM - yGZ_center)**2)
         if d2 >= 0.60*(y_post - yGZ_center):
            V_x = 2*V_p*((xCM - x_center)/d)*(1-(yCM-y_lastseg)/(y_post-y_lastseg))
            V_y = V_p*((yCM - y_post)/d)*(1-(yCM-y_lastseg)/(y_post-y_lastseg))
         else:
            V_x = V_p*((xCM - x_center)/d)*(1-(yCM-y_lastseg)/(y_post-y_lastseg))
            V_y=0
      else:
         V_x = V_p*((xCM - x_center)/d)*(1-(yCM-y_lastseg)/(y_post-y_lastseg))
         V_y = -V_p*((yCM - y_post)/d)*(1-(yCM-y_lastseg)/(y_post-y_lastseg))
         
      cell_vel=np.array([[xCM,yCM,-5*V_x,-5*V_y]])
      vel_array=np.concatenate((vel_array,cell_vel),axis=0)
      # print cell_vel

X,Y,U,V=zip(*vel_array)
plt.figure()
plt.axis('equal')
vecplot=plt.gca()
vecplot.quiver(X,Y,U,V,angles='xy',scale_units='xy',scale=1,lw=1.25)
vecplot.set_xlim([x_min-10,x_max+10])
vecplot.set_ylim([y_lastseg-10,y_post+10])
plt.draw()
plt.show()