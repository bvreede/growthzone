from PySteppables import *
import CompuCell
from CompuCell import getPyAttrib
from PySteppablesExamples import MitosisSteppableBase
from PlayerPython import *
import random
import math
from copy import deepcopy
import sys,time

# Initializes the volume and surface area of all cells at the beginning of the simulation
# and varies volume and surface throughout runtime
class VolumeSurfaceExample(SteppablePy):
   def __init__(self,_simulator,_frequency,_LamV,_LamS,_tV,_tS,_extremeSmall,_extremeBig):
      SteppablePy.__init__(self,_frequency)
      self.simulator=_simulator
      self.inventory=self.simulator.getPotts().getCellInventory()
      self.cellList=CellList(self.inventory)
      self.LamV=_LamV; self.LamS=_LamS; self.tV=_tV; self.tS=_tS
      self.eSmall = _extremeSmall; self.eBig = _extremeBig
      
   # Iterate through each cell and set its initial V and S
   def start(self):          
      for cell in self.cellList:
         if cell:
            cell.targetVolume=cell.volume; cell.lambdaVolume=self.LamV
            cell.targetSurface=cell.surface; cell.lambdaSurface=self.LamS
            
   def step(self,mcs):
      for cell in self.cellList:
         if cell: 
            # cell.targetVolume = 50 #100 + 100*math.sin(10*mcs)
            cell.lambdaVecX = 500 #500*math.sin(10*mcs)
            
            
            # print "I'm being called!!"
            # targetVolume=cell.targetVolume
            # if targetVolume < self.eBig:
               # cell.targetVolume -= 10
            # elif targetVolume > self.eSmall:
               # cell.targetVolume += 10
   