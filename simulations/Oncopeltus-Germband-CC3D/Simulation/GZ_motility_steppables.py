from PySteppables import *
import CompuCell
from CompuCell import getPyAttrib
from PySteppablesExamples import MitosisSteppableBase
from PlayerPython import *
import random
from math import sqrt
from copy import deepcopy
import sys,time

# Initializes the volume and surface area of all cells.  Runs once.
class InitVolSur(SteppablePy):
   def __init__(self,_simulator,_frequency,_LamV,_LamS,_tV,_tS):
      SteppablePy.__init__(self,_frequency)
      self.simulator=_simulator
      self.inventory=self.simulator.getPotts().getCellInventory()
      self.cellList=CellList(self.inventory)
      self.LamV=_LamV; self.LamS=_LamS; self.tV=_tV; self.tS=_tS
      
   # Interate through each cell and set its initial V and S
   def start(self):          
      for cell in self.cellList:
         if cell:
            cell.targetVolume=cell.volume; cell.lambdaVolume=self.LamV
            cell.targetSurface=cell.surface; cell.lambdaSurface=self.LamS
            
            # cell.targetVolume=self.tV; cell.lambdaVolume=self.LamV
            # cell.targetSurface=self.tS; cell.lambdaSurface=self.LamS
            
# Controls the growth of all cells. Runs at each step.
# There are 2 parameters that control cell growth, only 1 of which should be non-zero
#   pixPerMCS -- pixels per MCS will be >= 1 if the cell should grow by more than 1 pixel per MCS
#   mcsPerPix -- MCSs per pixel will be >= 1 if the cell should grown by 1 pixel every MCS cycles
class CellGrowth(SteppablePy):
   # Parameters
   # tV : target volumne
   # tS : target surface area
   # T_double:  time in MCS it takes a growing cell to double in volume
   def __init__(self,_simulator,_frequency,_tV,_tS,_T_double,_range_phase):
      SteppablePy.__init__(self,_frequency)
      self.simulator=_simulator
      self.potts=self.simulator.getPotts()
      self.inventory=self.potts.getCellInventory()
      self.cellList=CellList(self.inventory)
      self.tV=_tV; self.tS=_tS; self.range_phase=_range_phase
      self.T_double=_T_double

      # Calculate pixels to add per MCS
      # E.g., If target_volume = 100 and T_double = 100, this will be 1
      self.pixPerMCS=self.tV/float(self.T_double)   # number of pixels added to growing cell volume per MCS
      if self.pixPerMCS >= 1:
         self.pixPerMCS = int(self.pixPerMCS+0.5) # Rounds up
         self.mcsPerPix=0

      # If the pixPerMCS is below 1, then calculate how many MCSs to run before adding a pixel
      else:
         self.mcsPerPix=int(1./self.pixPerMCS+0.5)
         self.pixPerMCS = 0
         

   def start(self):
      print "Starting CellGrowth"
   ## Attach a growth timer to cells that grow less than 1 pixel per MCS
      count = 0
      if self.mcsPerPix:             # If mcsPerPix > 0
         for cell in self.cellList:
            if cell:
               if cell.type == 3:          # Only allow GZ cells to proliferate
                  cellDict=CompuCell.getPyAttrib(cell)
                  cellDict["growth_timer"] = 0
                  count += 1
      print " >> Attached a growth_timer to " + str(count) + " cells"
                  
   ## Attach a phase timer to all dividing cells. This timer will count down before a cell begins to grow.
      count = 0
      for cell in self.cellList:
         if cell.type==3:  # add phase timer to GZ cells only
            timerRange = self.range_phase*self.T_double # range, in MCS, of phase offsets
            phase = int(random.randrange(0,timerRange,1))  # phase offset of cell, in MCS
            cellDict=CompuCell.getPyAttrib(cell)
            cellDict["phaseCountdown"]=phase  # attach phase offset countdown timer as a dictionary item
            count+=1
      print " >> Attached a phase countdown to " + str(count) + " cells"
      
   def step(self,mcs):
   ## count down through initial phase offset for each GZ cell
      cells_to_grow=[]  # list of cells to evaluate for growth
      if mcs <= self.T_double:
         for cell in self.cellList:
            if cell.type==3: # GZ cells
               cellDict=CompuCell.getPyAttrib(cell)
               if cellDict["phaseCountdown"]==0:  # if cell has reached or surpassed its initial phase offset
                  cells_to_grow.append(cell)  # add cell to list of cells to evaluate for growth
               else:
                  cellDict["phaseCountdown"]-=1  # count down phase offset
      else:
         for cell in self.cellList:
            if cell.type==3: # GZ cells
               cells_to_grow.append(cell)
                  
   ## Grow each cell that meets criteria for growth by increasing target volume and surface parameters:
      count=0
      if self.pixPerMCS:
         for cell in cells_to_grow:
            cell.targetVolume+=self.pixPerMCS
            cell.targetSurface=int(4*sqrt(cell.volume)+0.5)
            count+=1
      else:
         count_timer=0
         for cell in cells_to_grow:
            cellDict=CompuCell.getPyAttrib(cell)
            if cellDict["growth_timer"] < self.mcsPerPix: # if cell has not reached time to grow
               cellDict["growth_timer"] += 1  # add to growth timer
               count_timer+=1
            else:  # if cell has reached time to grow, increase target volume and surface
               cell.targetVolume+=1
               cell.targetSurface=int(4*sqrt(cell.volume)+0.5)
               cellDict["growth_timer"] = 0
               count+=1
         # print " >> Incremented " + str(count_timer) + " growth timers."
      # print " >> Grew " + str(count) + " cells."

class Mitosis(MitosisSteppableBase):
   def __init__(self,_simulator,_frequency=1,_V_div=180,_divType="Random"):
      MitosisSteppableBase.__init__(self,_simulator, _frequency)
      
      self.V_div=_V_div; self.divType=_divType
      
   def step(self,mcs):
   ## make a list of cells that will divide
      count=0
      cells_to_divide=[]
      for cell in self.cellList:
         if cell.type==3: # GZ cells
            if cell.volume>=self.V_div:
               cells_to_divide.append(cell)
               count+=1
      # print " >> Added " + str(count) + " cells to division list."
      
   ## Iterate through cell-division list and perform mitosis
      for cell in cells_to_divide:
         if self.divType=="Random":
            self.divideCellRandomOrientation(cell)
         elif self.divType=="MajorAxis":
            self.divideCellAlongMajorAxis(cell)
         elif self.divType=="MinorAxis":
            self.divideCellAlongMinorAxis(cell)
         else:
            self.divideCellOrientationVectorBased(cell,0,1,0)
            
   # UpdateAttributes is inherited from MitosisSteppableBase
   #  and it is called automatically by the divideCell() function
   # It sets the attributes of the parent and daughter cells:      
   def updateAttributes(self):
      parentCell=self.mitosisSteppable.parentCell
      childCell=self.mitosisSteppable.childCell
            
      childCell.targetVolume = childCell.volume
      childCell.lambdaVolume = parentCell.lambdaVolume
      childCell.targetSurface = childCell.surface
      childCell.lambdaSurface = parentCell.lambdaSurface
      parentCell.targetVolume = parentCell.volume
      parentCell.targetSurface = parentCell.surface
      childCell.type = parentCell.type
      
      parentDict=CompuCell.getPyAttrib(parentCell)
      childDict=CompuCell.getPyAttrib(childCell)
      parentDict["growth_timer"]=0
   ### Make a copy of the parent cell's dictionary and attach to child cell   
      for key, item in parentDict.items():
         childDict[key]=deepcopy(parentDict[key])
         
### Controls segmentation
class Segmentation(SteppablePy):
   def __init__(self,_simulator,_frequency,_T_seg,_y_seg,_y0):
      SteppablePy.__init__(self,_frequency)
      self.simulator=_simulator
      self.inventory=self.simulator.getPotts().getCellInventory()
      self.cellList=CellList(self.inventory)
      
      self.T_seg=int(_T_seg); self.y_seg=_y_seg; self.y0=_y0
      self.segNum=1

   def step(self,mcs):
      if (mcs%self.T_seg==0 and mcs>1):
      # if (mcs >= 201 and (mcs-200)%self.T_seg==0):
         print " >> Making new segment #" + str(self.segNum) + "..."
      ### Determine segment border (y-value)
         y_lastseg=0
         for cell in self.cellList:
            if cell.type==2 or cell.type==1: # Segment cell
               yCM=cell.yCM/float(cell.volume)
               if yCM>y_lastseg:
                  y_lastseg=yCM      
         y_border = y_lastseg + self.y_seg
      
         # y_border = self.y0 + self.segNum*self.y_seg  ## <-- old way of finding new segment border
         
      ### Determine type of segment and increase segment # counter(segments alternate adhesion properties)
         segType=self.segNum%2
         self.segNum+=1
      ### Make a list of cells to add to new segment
         cells_for_segment=[]
         count=0
         for cell in self.cellList:
            if cell.type==3: ## growth-zone cells
               yCM=cell.yCM/float(cell.volume)
               if yCM <= y_border:
                  cells_for_segment.append(cell)
                  count+=1
      ### Change cell's types to add them to new segment:
         if segType==1:
            for cell in cells_for_segment:
               cell.type=1  # change cell type to Seg01
         else:
            for cell in cells_for_segment:
               cell.type=2 # change cell type to Seg02
         print " >> Segment contains " + str(count) + " cells."
                    

##   def step(self,mcs):
##      if (mcs%self.T_seg==0 and mcs>1):
##      # if (mcs >= 201 and (mcs-200)%self.T_seg==0):
##         print " >> Making new segment #" + str(self.segNum) + "..."
##      ### Determine segment border (y-value)
##         y_border = self.y0 + self.segNum*self.y_seg
##      ### Determine type of segment and increase segment # counter(segments alternate adhesion properties)
##         segType=self.segNum%2
##         self.segNum+=1
##      ### Locate the maximum and minimum x positions of future segment and last segment
##         count=0
##         ys_max=0
##         xs_min=0
##         xs_max=999
##         for cell in self.cellList:
##            if cell.type==1 or cell.type==2: # most recent segment added
##               yCM=cell.yCM/float(cell.volume)
##               if yCM<ys_max:
##                  ys_max=yCM
##         for cell in self.cellList:
##             if cell.type==3:
##                 yCM=cell.yCM/float(cell.volume)
##                 if yCM <= ys_max and yCM >= (ys_max - 80):
##                     xCM=cell.xCM/float(cell.volume)
##                     if xCM>xs_max:
##                         xCM=xs_max
##                     elif xCM<xs_min:
##                         xCM=xs_min
##      ### Make a list of cells to add to new segment
##         cells_for_segment=[]
##         for cell in self.cellList:
##            if cell.type==3: ## growth-zone cells
##               yCM=cell.yCM/float(cell.volume)
##               if yCM <= y_border:
##                   cells_for_segment.append(cell)
##                   count+=1
##         xb_min=0
##         xb_max=999
##         for  cell in cells_for_segment:
##             if cell.type==3:
##                 xCM=cell.xCM/float(cell.volume)
##                 if xCM>xb_max:
##                     xb_max=xCM
##                 if xCM<xb_min:
##                     xb_min=xCM
##      ### Change cell's types to add them to new segment
##         xxb_min=xb_min
##         xxb_max=xb_max
##         xxs_min=xs_min
##         xxs_max=xs_max
##         if (xxb_max - xxb_min) <= (xxs_max - xxs_min):
##            if segType==1:
##                for cell in cells_for_segment:
##                    cell.type=1  # change cell type to Seg01
##
##            else:
##                for cell in cells_for_segment:
##                    cell.type=2 # change cell type to Seg02
##
##         print " >> Segment contains " + str(count) + " cells."
##                    

class GradedMotility(SteppablePy):
   def __init__(self,_simulator,_frequency,_ls_high,_ls_low,_lv_high,_lv_low,_T_seg,_sdrh,_sdrl,_sigflag):
      SteppablePy.__init__(self,_frequency)
      self.simulator=_simulator
      self.inventory=self.simulator.getPotts().getCellInventory()
      self.cellList=CellList(self.inventory)
      
      self.lambda_V_high=_lv_high
      self.lambda_V_low=_lv_low
      self.lambda_S_high=_ls_high
      self.lambda_S_low=_ls_low
      self.T_seg=_T_seg
      self.cs_high=_sdrh
      self.cs_low=_sdrl
      self.signal_flag=_sigflag
           
   def step(self,mcs):
      if mcs%100==0:
         if self.signal_flag:
            y_sig=0
            x_min=999
            x_max=0
            for cell in self.cellList:
               if cell.type==3:
                  yCM=cell.yCM/float(cell.volume)
                  xCM=cell.xCM/float(cell.volume)
                  if yCM>y_sig:
                     y_sig=yCM
                  if xCM>x_max:
                     x_max=xCM
                  elif xCM<x_min:
                     x_min=xCM
            x_sig=(x_max-x_min)/2 + x_min
            distance_max=0
            for cell in self.cellList:
               yCM=cell.yCM/float(cell.volume)
               xCM=cell.xCM/float(cell.volume)
               distance=sqrt((y_sig-yCM)**2+(x_sig-xCM)**2)
               if distance>distance_max:
                  distance_max=distance
         else:   
   ## Find the minimum and maximum yCM for the growth-zone cells
            y_min=999
            y_max=0
            for cell in self.cellList:
               if cell.type==3: # growth zone cells
                  yCM=cell.yCM/float(cell.volume)
                  if yCM<y_min:
                     y_min=yCM
                  elif yCM>y_max:
                     y_max=yCM
                     x_signal=cell.xCM/float(cell.volume)
   ## Set motility (lambda values) for each cell based on its position
   ## Based on distance from signal
         if self.signal_flag:
            for cell in self.cellList:
               if cell.type==3:
                  yCM=cell.yCM/float(cell.volume)
                  xCM=cell.xCM/float(cell.volume)
                  distance=sqrt((y_sig-yCM)**2+(x_sig-xCM)**2)
                  cell.lambdaSurface=distance*(self.lambda_S_high-self.lambda_S_low)/distance_max + self.lambda_S_low
                  cs=distance*(self.cs_low-self.cs_high)/distance_max + self.cs_high
                  d=sqrt(float(cell.targetVolume))
                  surface=int(cs*d+0.5)
                  cell.targetSurface=surface
               elif (cell.type==1 or cell.type==2):
                  # cell.lambdaVolume=self.lambda_V_high
                  cell.lambdaSurface=self.lambda_S_high
                  d=sqrt(float(cell.targetVolume))
                  surface=int(self.cs_low*d+0.5)
                  cell.targetSurface=surface
         else:
      ## Based on y-position only
            for cell in self.cellList:
               if cell.type==3: # growth zone cells
                  yCM=cell.yCM/float(cell.volume)
               #   cell.lambdaVolume=(yCM-y_min)*(self.lambda_V_low-self.lambda_V_high)/(y_max-y_min) + self.lambda_V_high
                  cell.lambdaSurface=(yCM-y_min)*(self.lambda_S_low-self.lambda_S_high)/(y_max-y_min) + self.lambda_S_high
                  cs=(yCM-y_min)*(self.cs_high-self.cs_low)/(y_max-y_min)+self.cs_low
                  d=sqrt(float(cell.targetVolume))
                  surface=int(cs*d+0.5)
                  cell.targetSurface=surface
               elif (cell.type==1 or cell.type==2):
                  # cell.lambdaVolume=self.lambda_V_high
                  cell.lambdaSurface=self.lambda_S_high
                  d=sqrt(float(cell.targetVolume))
                  surface=int(self.cs_low*d+0.5)
                  cell.targetSurface=surface

class ExtPotConverge(SteppablePy): # Places an external potential on cells
   def __init__(self,_simulator,_frequency,_V_p,_y_comp):
      SteppablePy.__init__(self,_frequency)
      self.simulator=_simulator
      self.inventory=self.simulator.getPotts().getCellInventory()
      self.cellList=CellList(self.inventory)
      self.V_p=_V_p
      self.y_comp=_y_comp
                         
   def step(self,mcs):
   ## find y-position of poster-most GZ cell and center of growth zone
      y_post=0
      x_min=999
      x_max=0
      xs_min=999
      xs_max=0
      y_lastseg=0
      for cell in self.cellList:
         if cell.type==3: # GZ cell
            yCM=cell.yCM/float(cell.volume)
            xCM=cell.xCM/float(cell.volume)
            if yCM>y_post:
               y_post=yCM
            if xCM>x_max:
               x_max=xCM
            elif xCM<x_min:
               x_min=xCM
      x_center=x_min + (x_max-x_min)/2.
      for cell in self.cellList:
          if cell.type==2 or cell.type==1: # Segment cell
              yCM=cell.yCM/float(cell.volume)
              xCM=cell.xCM/float(cell.volume)
              if yCM>y_lastseg:
                  y_lastseg=yCM
      for cell in self.cellList:
          yCM=cell.yCM/float(cell.volume)
          xCM=cell.xCM/float(cell.volume)
          if yCM < y_lastseg  and yCM > (y_lastseg - 70): # Segment cell
              if xCM>xs_max:
                   xs_max=xCM
              elif xCM<xs_min:
                   xs_min=xCM
      print ">> y_lastseg: %.2f" %(y_lastseg)
              
      for cell in self.cellList:
         if cell.type==3:
             xx_min = xs_min
             xx_max = xs_max
             yy_lastseg = y_lastseg
             yCM=cell.yCM/float(cell.volume)
             xCM=cell.xCM/float(cell.volume)
             if yCM >= (-13*(xCM-552) + 241):
                 yCM=cell.yCM/float(cell.volume)
                 xCM=cell.xCM/float(cell.volume)
                 d = sqrt((xCM - x_center)**2 + (yCM - (y_post))**2)
                 if yCM >= (yy_lastseg + 80):
                    V_y= self.V_p*((yCM - y_post)/d)*(1-((yCM-yy_lastseg)/(y_post-yy_lastseg))**2)
                    V_x= 2*self.V_p*((xCM - x_center)/d)*(1-((yCM-yy_lastseg)/(y_post-yy_lastseg))**2)
                 else:
                    V_y = 5
                    V_x= 3*self.V_p*((xCM - x_center)/d)*(1-((yCM-yy_lastseg)/(y_post-yy_lastseg))**2)
                 cell.lambdaVecX = V_x
                 cell.lambdaVecY = V_y
             elif yCM >= (13*(xCM-298) + 241):
                 yCM=cell.yCM/float(cell.volume)
                 xCM=cell.xCM/float(cell.volume)
                 d = sqrt((xCM - x_center)**2 + (yCM - (y_post))**2)
                 if yCM >= (yy_lastseg +80):
                    V_y= self.V_p*((yCM - y_post)/d)*(1-((yCM-yy_lastseg)/(y_post-yy_lastseg))**2)
                    V_x= 2*self.V_p*((xCM - x_center)/d)*(1-((yCM-yy_lastseg)/(y_post-yy_lastseg))**2)
                 else:
                    V_y = 5
                    V_x= 3*self.V_p*((xCM - x_center)/d)*(1-((yCM-yy_lastseg)/(y_post-yy_lastseg))**2)                                                       
                 cell.lambdaVecX = V_x
                 cell.lambdaVecY = V_y
             elif yCM <= (13*(xCM-298) + 241) and yCM <= (-13*(xCM-552) + 241):
                 V_x = 5
                 V_y = -2
                 cell.lambdaVecX = V_x
                 cell.lambdaVecY = V_y
                
      print ">> Posterior most y value is %.2f" %(y_post)
      print ">> xx_max: %.2f" %(xx_max)
      print ">> xs_max: %.2f" %(xs_max)
      print ">> xx_min: %.2f" %(xx_min)
      print ">> xs_min: %.2f" %(xs_min)
      print ">> x_min: %.2f" %(x_min)
      print ">> x_max: %.2f" %(x_max)
            
               
class ExtPotMedialZone(SteppablePy): # Places an external potential on cells
   def __init__(self,_simulator,_frequency,_V_p,_y_comp):
      SteppablePy.__init__(self,_frequency)
      self.simulator=_simulator
      self.inventory=self.simulator.getPotts().getCellInventory()
      self.cellList=CellList(self.inventory)
      self.V_p=_V_p
      self.y_comp=_y_comp
                         
   def step(self,mcs):
   ## find y-position of poster-most GZ cell and center of growth zone
      y_post=0
      x_min=999
      x_max=0
      xs_min=999
      xs_max=0
      y_lastseg=0
      for cell in self.cellList:
         if cell.type==3: # GZ cell
            yCM=cell.yCM/float(cell.volume)
            xCM=cell.xCM/float(cell.volume)
            if yCM>y_post:
               y_post=yCM
            if xCM>x_max:
               x_max=xCM
            elif xCM<x_min:
               x_min=xCM
      x_center=x_min + (x_max-x_min)/2.
      for cell in self.cellList:
          if cell.type==2 or cell.type==1: # Segment cell
              yCM=cell.yCM/float(cell.volume)
              if yCM>y_lastseg:
                  y_lastseg=yCM
      for cell in self.cellList:
          yCM=cell.yCM/float(cell.volume)
          xCM=cell.xCM/float(cell.volume)
          if yCM < y_lastseg  and yCM > (y_lastseg - 70): # Segment cell
              if xCM>xs_max:
                   xs_max=xCM
              elif xCM<xs_min:
                   xs_min=xCM
              
      for cell in self.cellList:
         if cell.type==3:
             xx_min = xs_min
             xx_max = xs_max
             yy_lastseg = y_lastseg
             yCM=cell.yCM/float(cell.volume)
             xCM=cell.xCM/float(cell.volume)
             if xCM < xx_min  :
                 yCM=cell.yCM/float(cell.volume)
                 xCM=cell.xCM/float(cell.volume)
                 d = sqrt((xCM - x_center)**2 + (yCM - (y_post))**2)
                 V_x= self.V_p*((xCM - x_center)/d) 
                 V_y= 1*self.V_p*((yCM - y_post)/d)
                 cell.lambdaVecX = V_x
                 cell.lambdaVecY = V_y
             elif xCM > xx_max :
                 yCM=cell.yCM/float(cell.volume)
                 xCM=cell.xCM/float(cell.volume)
                 d = sqrt((xCM - x_center)**2 + (yCM - (y_post))**2)
                 V_x= self.V_p*((xCM - x_center)/d) 
                 V_y= 1*self.V_p*((yCM - y_post)/d)
                 cell.lambdaVecX = V_x
                 cell.lambdaVecY = V_y
             else:
                 V_x = 0
                 V_y = 2
                 cell.lambdaVecX = V_x
                 cell.lambdaVecY = V_y
                
      print ">> Posterior most y value is %.2f" %(y_post)
      print ">> xx_max: %.2f" %(xx_max)
      print ">> xs_max: %.2f" %(xs_max)
      print ">> xx_min: %.2f" %(xx_min)
      print ">> xs_min: %.2f" %(xs_min)
      print ">> x_min: %.2f" %(x_min)
      print ">> x_max: %.2f" %(x_max)

class ExtPotMedialGrad(SteppablePy): # Places an external potential on cells
   def __init__(self,_simulator,_frequency,_V_p,_y_comp):
      SteppablePy.__init__(self,_frequency)
      self.simulator=_simulator
      self.inventory=self.simulator.getPotts().getCellInventory()
      self.cellList=CellList(self.inventory)
      self.V_p=_V_p
      self.y_comp=_y_comp
      
   def step(self,mcs):
   ## find y-position of poster-most GZ cell and center of growth zone. Find the y-position of the posterior most segment cell
      y_post=0
      x_min=999
      x_max=0
      y_lastseg=0
      for cell in self.cellList:
         if cell.type==3: # GZ cell
            yCM=cell.yCM/float(cell.volume)
            xCM=cell.xCM/float(cell.volume)
            if yCM>y_post:
               y_post=yCM
            if xCM>x_max:
               x_max=xCM
            elif xCM<x_min:
               x_min=xCM
      x_center=x_min + (x_max-x_min)/2.
      for cell in self.cellList: #Finding the maximum y-value of all segment cells
          if cell.type==2 or cell.type==1: 
              yCM=cell.yCM/float(cell.volume)
              if yCM > y_lastseg:
                  y_lastseg=yCM
      
      for cell in self.cellList:
          if cell.type==3: #Growth Zone cells
             yCM=cell.yCM/float(cell.volume)
             xCM=cell.xCM/float(cell.volume)
             yy_lastseg = y_lastseg
             V_x = self.V_p*(xCM - x_center) #x component of force is proportional to the distance from midline
             V_y = self.y_comp*(1-((yCM-yy_lastseg)/(y_post-yy_lastseg))**2)
             cell.lambdaVecX = V_x
             cell.lambdaVecY = V_y

class ExtPotSarrazin(SteppablePy): # Places an external potential on cells
   def __init__(self,_simulator,_frequency,_V_p,_y_comp):
      SteppablePy.__init__(self,_frequency)
      self.simulator=_simulator
      self.inventory=self.simulator.getPotts().getCellInventory()
      self.cellList=CellList(self.inventory)
      self.V_p=_V_p
      self.y_comp=_y_comp
      
   def step(self,mcs):
   ## find y-position of poster-most GZ cell and center of growth zone. Find the y-position of the posterior most segment cell
      y_post=0
      x_min=999
      x_max=0
      y_lastseg=0
      for cell in self.cellList:
         if cell.type==3: # GZ cell
            yCM=cell.yCM/float(cell.volume)
            xCM=cell.xCM/float(cell.volume)
            if yCM>y_post:
               y_post=yCM
            if xCM>x_max:
               x_max=xCM
            elif xCM<x_min:
               x_min=xCM
      x_center=x_min + (x_max-x_min)/2.
      for cell in self.cellList:
         yy_lastseg = y_lastseg
         if cell.type==2 or cell.type==1: # Segment cell
            yCM=cell.yCM/float(cell.volume)
            if yCM>y_lastseg:
               y_lastseg=yCM
      for cell in self.cellList:
         if cell.type==3:
            yy_lastseg = y_lastseg
            if yCM >= (yy_lastseg + 80):
               yCM=cell.yCM/float(cell.volume)
               xCM=cell.xCM/float(cell.volume)
               d = sqrt((xCM - x_center)**2 + (yCM - (y_post))**2)
               V_x = 2*self.V_p*((xCM - x_center)/d)*(1-(yCM-yy_lastseg)/(y_post-yy_lastseg)) #new 1/2 
               V_y = self.V_p*((yCM - y_post)/d)*(1-(yCM-yy_lastseg)/(y_post-yy_lastseg)) #new 1/2
               cell.lambdaVecX = V_x
               cell.lambdaVecY = V_y
            elif yCM <= (yy_lastseg + 80):
               yCM=cell.yCM/float(cell.volume)
               xCM=cell.xCM/float(cell.volume)
               d = sqrt((xCM - x_center)**2 + (yCM - (y_post))**2)
               V_x = self.V_p*((xCM - x_center)/d)*(1-(yCM-yy_lastseg)/(y_post-yy_lastseg)) 
               V_y = -self.V_p*((yCM - y_post)/d)*(1-(yCM-yy_lastseg)/(y_post-yy_lastseg)) #new 5/2
               cell.lambdaVecX = V_x
               cell.lambdaVecY = V_y
         if cell.type==1 or cell.type==2:
            yCM=cell.yCM/float(cell.volume)
            xCM=cell.xCM/float(cell.volume)
            V_y = 8 #new, was 2
            cell.lambdaVecY = V_y            
            if yCM <= yy_lastseg and yCM >= (yy_lastseg -80):
               V_x = 0
            else:
               V_x = 0
            cell.lambdaVecX = V_x

class ExtPotSarrazin02(SteppablePy): # Places an external potential on cells
   def __init__(self,_simulator,_frequency,_V_p,_y_comp):
      SteppablePy.__init__(self,_frequency)
      self.simulator=_simulator
      self.inventory=self.simulator.getPotts().getCellInventory()
      self.cellList=CellList(self.inventory)
      self.V_p=_V_p
      self.y_comp=_y_comp
      
   def step(self,mcs):
   ## find y-position of poster-most GZ cell and center of growth zone. Find the y-position of the posterior most segment cell
      y_post=0
      x_min=999
      x_max=0
      y_lastseg=0
      for cell in self.cellList:
         if cell.type==3: # GZ cell
            yCM=cell.yCM/float(cell.volume)
            xCM=cell.xCM/float(cell.volume)
            if yCM>y_post:
               y_post=yCM
            if xCM>x_max:
               x_max=xCM
            elif xCM<x_min:
               x_min=xCM
      x_center=x_min + (x_max-x_min)/2.
      for cell in self.cellList:
         yy_lastseg = y_lastseg
         if cell.type==2 or cell.type==1: # Segment cell
            yCM=cell.yCM/float(cell.volume)
            if yCM>y_lastseg:
               y_lastseg=yCM
      for cell in self.cellList:
         if cell.type==3:
            yy_lastseg = y_lastseg
            d = sqrt((xCM - x_center)**2 + (yCM - (y_post))**2)
            yCM=cell.yCM/float(cell.volume)
            xCM=cell.xCM/float(cell.volume)
            if d < (y_post - (yy_lastseg + 80)):
               yCM=cell.yCM/float(cell.volume)
               xCM=cell.xCM/float(cell.volume)
               yGZ_center = yy_lastseg + (y_post - yy_lastseg)/2
               d2 = sqrt((xCM - x_center)**2 + (yCM - yGZ_center)**2)
               if d2 >= 0.60*(y_post - yGZ_center):
                  V_x = 2*self.V_p*((xCM - x_center)/d)*(1-(yCM-yy_lastseg)/(y_post-yy_lastseg)) #new 1/2 
                  V_y = self.V_p*((yCM - y_post)/d)*(1-(yCM-yy_lastseg)/(y_post-yy_lastseg)) #new 1/2
                  cell.lambdaVecX = V_x
                  cell.lambdaVecY = V_y
               else:
                  V_x = self.V_p*((xCM - x_center)/d)*(1-(yCM-yy_lastseg)/(y_post-yy_lastseg)) 
                  V_y = -self.V_p*((yCM - y_post)/d)*(1-(yCM-yy_lastseg)/(y_post-yy_lastseg)) #new 5/2
                  cell.lambdaVecX = V_x
                  cell.lambdaVecY = V_y                  
            elif d >= (y_post - (yy_lastseg + 80)):
               yCM=cell.yCM/float(cell.volume)
               xCM=cell.xCM/float(cell.volume)
               d = sqrt((xCM - x_center)**2 + (yCM - (y_post))**2)
               V_x = self.V_p*((xCM - x_center)/d)*(1-(yCM-yy_lastseg)/(y_post-yy_lastseg)) 
               V_y = -self.V_p*((yCM - y_post)/d)*(1-(yCM-yy_lastseg)/(y_post-yy_lastseg)) #new 5/2
               cell.lambdaVecX = V_x
               cell.lambdaVecY = V_y
         if cell.type==1 or cell.type==2:
            yCM=cell.yCM/float(cell.volume)
            xCM=cell.xCM/float(cell.volume)
            V_y = 5 #new, was 2
            cell.lambdaVecY = V_y            
            if yCM <= yy_lastseg and yCM >= (yy_lastseg -80):
               V_x = 0
            else:
               V_x = 0
            cell.lambdaVecX = V_x
            
class ExtPotSarrazin03(SteppablePy): # Places an external potential on cells
   def __init__(self,_simulator,_frequency,_V_p):
      SteppablePy.__init__(self,_frequency)
      self.simulator=_simulator
      self.inventory=self.simulator.getPotts().getCellInventory()
      self.cellList=CellList(self.inventory)
      self.V_p=_V_p
      
   def step(self,mcs):
   ## find y-position of poster-most GZ cell and center of growth zone. Find the y-position of the posterior most segment cell
      y_post=0
      x_min=999
      x_max=0
      y_lastseg=0
      for cell in self.cellList:
         if cell.type==3: # GZ cell
            yCM=cell.yCM/float(cell.volume)
            xCM=cell.xCM/float(cell.volume)
            if yCM>y_post:
               y_post=yCM  # finds posterior-most y coordinate for growth zone
            if xCM>x_max:
               x_max=xCM   # finds maximum x position for GZ cell
            elif xCM<x_min: 
               x_min=xCM   # finds minimum x position for GZ cell
      x_center=x_min + (x_max-x_min)/2.  # finds midline (x-coordinate) of GZ
      ## finds posterior-most position of last segment
      for cell in self.cellList:
         if cell.type==2 or cell.type==1: # Segment cell
            yCM=cell.yCM/float(cell.volume)
            if yCM>y_lastseg:
               y_lastseg=yCM
      #### finds the y-coordinate for the center of the GZ
      yGZ_center = y_lastseg + (y_post - y_lastseg)/2
      ## CALCULATES AND APPLIES POSITION-DEPENDENT POTENTIAL ON CELLS         
      for cell in self.cellList:
         if cell.type==3:  #GZ cell
            yCM=cell.yCM/float(cell.volume)
            xCM=cell.xCM/float(cell.volume)
            d = sqrt((xCM - x_center)**2 + (yCM - (y_post))**2)   # finds cell distance from midpoint of posterior of GZ
            if d < (y_post - (y_lastseg + 50)):#80)):
               d2 = sqrt((xCM - x_center)**2 + (yCM - yGZ_center)**2)
               if d2 >= 0.60*(y_post - yGZ_center):
                  V_x = 2*self.V_p*((xCM - x_center)/d)*(1-(yCM-y_lastseg)/(y_post-y_lastseg)) #new 1/2 
                  # V_x = self.V_p*((xCM - x_center)/d)*(1-(yCM-y_lastseg)/(y_post-y_lastseg))
                  V_y = self.V_p*((yCM - y_post)/d)*(1-(yCM-y_lastseg)/(y_post-y_lastseg)) #new 1/2
                  cell.lambdaVecX = V_x
                  cell.lambdaVecY = V_y
               else:
                  V_x = self.V_p*((xCM - x_center)/d)*(1-(yCM-y_lastseg)/(y_post-y_lastseg)) 
                  V_y=0
                  # V_y = -self.V_p*((yCM - y_post)/d)*(1-(yCM-y_lastseg)/(y_post-y_lastseg)) #new 5/2
                  cell.lambdaVecX = V_x
                  cell.lambdaVecY = V_y                  
            else:
               V_x = self.V_p*((xCM - x_center)/d)*(1-(yCM-y_lastseg)/(y_post-y_lastseg)) 
               V_y = -self.V_p*((yCM - y_post)/d)*(1-(yCM-y_lastseg)/(y_post-y_lastseg)) #new 5/2
               cell.lambdaVecX = V_x
               cell.lambdaVecY = V_y
         elif cell.type==1 or cell.type==2:
            # yCM=cell.yCM/float(cell.volume)
            # xCM=cell.xCM/float(cell.volume)
            V_y = 5 #new, was 2
            cell.lambdaVecY = V_y     
            cell.lambdaVecX=0
            # if yCM <= y_lastseg and yCM >= (y_lastseg -80):
               # V_x = 0
            # else:
               # V_x = 0
            # cell.lambdaVecX = V_x            
            
# Counts GZ cells every freq MCS
class CellCounts(SteppablePy):
   def __init__(self,_simulator,_frequency):
      SteppablePy.__init__(self,_frequency)
      self.simulator=_simulator
      self.inventory=self.simulator.getPotts().getCellInventory()
      self.cellList=CellList(self.inventory)
   def start(self):
      folder='C:/CompuCell3D/Simulations/GZ_Motility_Force_July2013_PaperParameters/OutputFiles/'
      Time=time.localtime()
      Year=str(Time[0]); Month=str(Time[1]); Day=str(Time[2]); Hour=str(Time[3])
      Minute=str(Time[4]); Second=str(Time[5])
      timeTag=Month+"_"+Day+"_"+Year+"_"+Hour+"_"+Minute+"_"+Second
      filename=folder+'cell_counts'+timeTag+'.csv'
      self.file=open(filename,'w')
      self.file.write('MCS,GZ cell count\n')
   def step(self,mcs):
      cellcount=0
      for cell in self.cellList:
         if cell.type==3: ##GZ cell
            cellcount+=1
      print '++++++++++++++\nMCS=' + str(mcs) + '\nNumber of Growth Zone cells= ' + str(cellcount) + '\n++++++++++++++++++'
      self.file.write('\n'+str(mcs)+','+str(cellcount))
   def finish(self):
      self.file.close()
      
##
##class MotilityTracker(SteppablePy):
##   def __init__(self,_simulator,_frequency,_t0,_dt,_filename):
##      SteppablePy.__init__(self,_frequency)
##      self.simulator=_simulator
##      self.inventory=self.simulator.getPotts().getCellInventory()
##      self.cellList=CellList(self.inventory)               
##      
##      self.t0=_t0
##      self.dt=_dt
##      self.filename=_filename
##      
##   def step(self,mcs):
##      if mcs == self.t0:
##      ##### find posterior tip of growth zone
##         y_pos=0
##         x_min=9999
##         x_max=0
##         for cell in self.cellList:
##            if cell.type==3: # GZ cell
##               yCM = cell.yCM/float(cell.volume)
##               xCM = cell.xCM/float(cell.volume)
##               if yCM > y_pos:
##                  y_pos = yCM
##               if xCM > x_max:
##                  x_max = xCM
##               elif xCM < x_min:
##                  x_min = xCM
##         x_pos = x_min + (x_max - x_min)/2
##      
##      ##### store cells' initial information as a dictionary item
##         for cell in self.cellList:
##            if cell: ## if not medium
##               xCM = cell.xCM/float(cell.volume)
##               yCM = cell.yCM/float(cell.volume)
##               cellDict=CompuCell.getPyAttrib(cell)
##               x = xCM - x_pos
##               y = y_pos - yCM
##               cellDict["x0"]=str(x)
##               cellDict["y0"]=str(y)
##               cellDict["xCM0"]=xCM
##               cellDict["yCM0"]=yCM
##      elif mcs == (self.t0 + self.dt):     
##      #### create file and write header
##         motilityFile=open(self.filename,'w')
##         motilityFile.write('cell id,cell type,x0,y0,dx,dy,dt\n')
##      #### calculate and write info for all cells
##         dt = str(self.dt)
##         for cell in self.cellList:
##            if cell: # if not Medium
##               cellDict=CompuCell.getPyAttrib(cell)
##               xCM = cell.xCM/float(cell.volume)
##               yCM = cell.yCM/float(cell.volume)
##               x0 = cellDict["x0"]
##               y0 = cellDict["y0"]
##               dx = str(xCM - cellDict["xCM0"])
##               dy = str(yCM - cellDict["yCM0"])
##               id = str(cell.id)
##               type = str(cell.type)
##               motilityFile.write(id+','+type+','+x0+','+y0+','+dx+','+dy+','+dt+'\n')
##         motilityFile.close()
##         
##class LengthTracker(SteppablePy):
##   def __init__(self,_simulator,_frequency,_filename):
##      SteppablePy.__init__(self,_frequency)
##      self.simulator=_simulator
##      self.inventory=self.simulator.getPotts().getCellInventory()
##      self.cellList=CellList(self.inventory)      
##      
##      self.filename=_filename
##      
##   def start(self):
##      ## create file and write header
##      lengthFile=open(self.filename,'w')
##      lengthFile.write('mcs,length\n')
##      ## calculate length of simulated germ band
##      ## find max and min y
##      y_max=0
##      y_min=9999
##      for cell in self.cellList:
##         if cell: # if not Medium
##            yCM=cell.yCM/float(cell.volume)
##            if yCM < y_min:
##               y_min=yCM
##            elif yCM > y_max:
##               y_max=yCM
##      length = y_max - y_min
##      ## write length onto file
##      lengthFile.write('0,'+str(length)+'\n')
##      lengthFile.close()
##      
##   def step(self,mcs):
##      if mcs>0:
##      ## calculate length of simulated germ band
##      ## find max and min y
##         y_max=0
##         y_min=9999
##         for cell in self.cellList:
##            if cell: # if not Medium
##               yCM=cell.yCM/float(cell.volume)
##               if yCM < y_min:
##                  y_min=yCM
##               elif yCM > y_max:
##                  y_max=yCM
##         length = y_max - y_min
##         ## write length onto file
##         lengthFile=open(self.filename,'a')
##         lengthFile.write(str(mcs)+','+str(length)+'\n')
##         lengthFile.close()
##  

            
# class GradedMotility(SteppablePy):
   # def __init__(self,_simulator,_frequency,_ls_high,_ls_low,_lv_high,_lv_low,_T_seg):
      # SteppablePy.__init__(self,_frequency)
      # self.simulator=_simulator
      # self.inventory=self.simulator.getPotts().getCellInventory()
      # self.cellList=CellList(self.inventory)
      
      # self.lambda_V_high=_lv_high
      # self.lambda_V_low=_lv_low
      # self.lambda_S_high=_ls_high
      # self.lambda_S_low=_ls_low
      # self.T_seg=_T_seg
      
   # def start(self):
   # Find the minimum and maximum yCM for the growth-zone cells
      # y_min=999
      # y_max=0
      # for cell in self.cellList:
         # if cell.type==3: # growth zone cells
            # yCM=cell.yCM/float(cell.volume)
            # if yCM<y_min:
               # y_min=yCM
            # elif yCM>y_max:
               # y_max=yCM
   # Set motility (lambda values) for each cell based on its position
   # Linear:
      # for cell in self.cellList:
         # if cell.type==3: # growth zone cells
            # yCM=cell.yCM/float(cell.volume)
            # cell.lambdaVolume=(yCM-y_min)*(self.lambda_V_low-self.lambda_V_high)/(y_max-y_min) + self.lambda_V_high
            # cell.lambdaSurface=(yCM-y_min)*(self.lambda_S_low-self.lambda_S_high)/(y_max-y_min) + self.lambda_S_high      
      
   # def step(self,mcs):
      # if (mcs>2 and (mcs-1)%self.T_seg==0):
   # Find the minimum and maximum yCM for the growth-zone cells
         # y_min=999
         # y_max=0
         # for cell in self.cellList:
            # if cell.type==3: # growth zone cells
               # yCM=cell.yCM/float(cell.volume)
               # if yCM<y_min:
                  # y_min=yCM
               # elif yCM>y_max:
                  # y_max=yCM
   # Set motility (lambda values) for each cell based on its position
   # Linear:
         # for cell in self.cellList:
            # if cell.type==3: # growth zone cells
               # yCM=cell.yCM/float(cell.volume)
               # cell.lambdaVolume=(yCM-y_min)*(self.lambda_V_low-self.lambda_V_high)/(y_max-y_min) + self.lambda_V_high
               # cell.lambdaSurface=(yCM-y_min)*(self.lambda_S_low-self.lambda_S_high)/(y_max-y_min) + self.lambda_S_high
            # elif (cell.type==1 or cell.type==2):
               # cell.lambdaVolume=self.lambda_V_high
               # cell.lambdaSurface=self.lambda_S_high
            
