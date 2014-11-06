import sys,time
from os import environ
from os import getcwd
import string
sys.path.append(environ["PYTHON_MODULE_PATH"])

## Global Parameters

# Initial length of the cell's side, so d^2 gives area (volume) and d*4 gives circumference (surface area)
global d; 

# Cell's target volume (area) and surface area (circumference) -- i.e. its steady-state size
global target_V; global target_S; global lambda_V; global lambda_S

# Cell growth parameters
global range_phase; global T_double; 

# Growth-signaling parameters
global grow_sig_flag; global y_grow_sig; global grow_stim; global grow_repr

# Cell division parameters
global V_div; global divOrientation

# Cell labeling parameters
global y_dye; global x_dye; global w_dye

# Motility parameters
global HighMotility; global LowMotility; global GradedMotility_flag
global lambda_V_high; global lambda_V_low; global lambda_S_high
global lambda_S_low; global y_c
global sd_ratio_low; global sd_ratio_high
global signal_flag

# Segmention parameters
global T_segment; global y_segment; global y0_seg; global segment_flag

# Dimension parameters
global Lx; global Ly; global Lz; global Dx
global Dy; global Dz; global x_margin; global y_top_margin
global y_bottom_margin; global N_seg; global GZ_x; global GZ_y
global GZ_flag

#  Potts T parameter (temperature?)
global T; 

# Neighbor order
global nOrder

## Cell-field initialization parameters
# pifName="InitializationPiffs/Initial4.piff"

## Cell size parameters
d = 10             # cell's side?
target_V = d**2      # Cell's target value -- its typical volume
target_S = int(4*d)  # Cell's target circumference -- its typical circumference

## Initial segment size parameters
Lx =  19*d # for Oncopeltus #25*d # for Tribolium
Ly =  9*d # for Oncopeltus #10*d # for Tribolium
N_seg = 2

## Growth-zone size parameters
GZ_flag = 1
GZ_x = Lx
GZ_y = 35*d #28*d #20*d #2*Ly

## Growth signal parameters
grow_sig_flag= 1  ## 0 to turn off growth or growth-repression signaling
grow_stim=1       ## 1 to turn on growth-stimulating "signal" from posterior
grow_repr=0       ## 1 to turn on growth-repressing "signal" from anterior
y_grow_sig= 20*d #15*d #Ly



## Cell Growth parameters
range_phase = 1  # range over which cell-cycle phases are distributed, from 0 (no spread) to 1 (complete spread)
T_double = 2000 # 1000 # time it takes for a cell to grow to doubling size, in MCB (e.g., cycle time)

## Cell division parameters
V_div = 1.8*target_V # minimum volume at which a cell can divide
## Choose one (and ONLY ONE) of the following for cell division orientation to leave uncommented
divOrientation="Random"
# divOrientation="MajorAxis"
# divOrientation="MinorAxis"
# divOrientation="VectorBased"

## Simulation dimensions
x_margin = 30*d
y_top_margin = 9*Ly
y_bottom_margin = 3*Ly

Dx = Lx+2*x_margin
Dy = N_seg*Ly+GZ_flag*GZ_y+y_top_margin+y_bottom_margin
Dz = 1

# Segmention parameters
segment_flag=0 # set to nonzero to run segmentation
T_segment = 900 # 1200 # segmentation period
y_segment = 8*d # length of a newly-formed segment
y0_seg = y_top_margin+2*Ly  # bottom of initial segments

# Cell-labeling parameters
y_dye = y_top_margin+3*Ly
x_dye = int(Dx/2)
w_dye = 4*d

## Potts parameters
T = 50
nOrder = 1

## Motility parameters - set ONE of the following flags to one
HighMotility=1
LowMotility=0
GradedMotility_flag=0

if HighMotility:
   lambda_V = 2. #5. # Lambda volume -- volume constraint
   lambda_S = 2. #5. 
elif LowMotility:
   lambda_S = 25.
   lambda_V = 25.
elif GradedMotility_flag:
   lambda_V_low=2.
   lambda_V_high=25.
   lambda_S_low=2.
   lambda_S_high=25.
   lambda_V=25.
   lambda_S=25.
   sd_ratio_low=3
   sd_ratio_high=7
   signal_flag=1
   
   
   
def configureSimulation(sim):
## Potts variables and simulation dimensions
   import CompuCellSetup
   from XMLUtils import ElementCC3D
   cc3d=ElementCC3D("CompuCell3D")
   potts=cc3d.ElementCC3D("Potts")
   potts.ElementCC3D("Dimensions",{"x":Dx,"y":Dy,"z":Dz})
   potts.ElementCC3D("Steps",{},20000)
   potts.ElementCC3D("Anneal",{},1)
   potts.ElementCC3D("Temperature",{},int(T))
   potts.ElementCC3D("NeighborOrder",{},nOrder)
   potts.ElementCC3D("Flip2DimRatio",{},1)      # Very low flipping
   
## Specify cell types
   cellType=cc3d.ElementCC3D("Plugin",{"Name":"CellType"})
   cellType.ElementCC3D("CellType", {"TypeName":"Medium","TypeId":"0"})
   cellType.ElementCC3D("CellType", {"TypeName":"Seg01","TypeId":"1"})
   cellType.ElementCC3D("CellType", {"TypeName":"Seg02","TypeId":"2"})
   cellType.ElementCC3D("CellType", {"TypeName":"GZ","TypeId":"3"})
   
   ## Specify contact energies (adhesion penalty) between cell types
   contact=cc3d.ElementCC3D("Plugin",{"Name":"Contact"})
   contact.ElementCC3D("Energy", {"Type1":"Medium", "Type2": "Medium"},0)
   contact.ElementCC3D("Energy", {"Type1":"Medium", "Type2": "Seg01"},50) # 20
   contact.ElementCC3D("Energy", {"Type1":"Medium", "Type2": "Seg02"},50) # 20
   contact.ElementCC3D("Energy", {"Type1":"Medium", "Type2": "GZ"},30) # 30
   contact.ElementCC3D("Energy", {"Type1":"Seg01", "Type2": "Seg01"},5) 
   contact.ElementCC3D("Energy", {"Type1":"Seg01", "Type2": "Seg02"},20) # 10
   contact.ElementCC3D("Energy", {"Type1":"Seg01", "Type2": "GZ"},20) # 10
   contact.ElementCC3D("Energy", {"Type1":"Seg02", "Type2": "Seg02"},5)
   contact.ElementCC3D("Energy", {"Type1":"Seg02", "Type2": "GZ"},20) # 10
   contact.ElementCC3D("Energy", {"Type1":"GZ", "Type2": "GZ"},5)
   contact.ElementCC3D("NeighborOrder",{},nOrder)
   
## Impose a penalty on cell fragmentation using the built-in
## CC3D "Connectivity" plugin   
   connectivity = cc3d.ElementCC3D("Plugin",{"Name":"Connectivity"})
   connectivity.ElementCC3D("Penalty",{},10000)
   
   # volume=cc3d.ElementCC3D("Plugin",{"Name":"Volume"})
   # volume.ElementCC3D("TargetVolume",{},target_V)
   # volume.ElementCC3D("LambdaVolume",{},lambda_V)
   
   # surface=cc3d.ElementCC3D("Plugin",{"Name":"Surface"})
   # surface.ElementCC3D("TargetSurface",{},target_S)
   # surface.ElementCC3D("LambdaSurface",{},lambda_S)
   
## Initialize plugins for accessing/manipulating cell properties
   ptrpd = cc3d.ElementCC3D("Plugin",{"Name":"PixelTracker"})
   vlfpd = cc3d.ElementCC3D("Plugin",{"Name":"VolumeLocalFlex"})
   slfpd = cc3d.ElementCC3D("Plugin",{"Name":"SurfaceLocalFlex"})
   ntpd = cc3d.ElementCC3D("Plugin",{"Name":"NeighborTracker"})
   comtpd = cc3d.ElementCC3D("Plugin",{"Name":"CenterOfMass"})

   
## MUST INITIALIZE EXTERNAL POTENTIAL PLUGIN
   # extPotential=cc3d.ElementCC3D("Plugin",{"Name":"ExternalPotential"})   
   
## Initialize cell field from piff file:
   # piffinit = cc3d.ElementCC3D("Steppable",{"Type":"PIFInitializer"})
   # piffinit.ElementCC3D("PIFName",{},pifName)
  
## Initialize cell field
   uipd = cc3d.ElementCC3D("Steppable",{"Type":"UniformInitializer"})
   region = uipd.ElementCC3D("Region")
   region.ElementCC3D("BoxMin",{"x":x_margin,  "y":y_top_margin,  "z":0})
   region.ElementCC3D("BoxMax",{"x":x_margin+Lx,  "y":y_top_margin+Ly,  "z":1})
   region.ElementCC3D("Types",{}, "Seg01" )
   region.ElementCC3D("Width", {}, d)
   # region.ElementCC3D("Gap", {}, int(d/2))

   region = uipd.ElementCC3D("Region")
   region.ElementCC3D("BoxMin",{"x":x_margin,  "y":y_top_margin+Ly,  "z":0})
   region.ElementCC3D("BoxMax",{"x":x_margin+Lx,  "y":y_top_margin+2*Ly,  "z":1})
   region.ElementCC3D("Types",{}, "Seg02" )
   region.ElementCC3D("Width", {}, d)
   # region.ElementCC3D("Gap", {}, int(d/2))

   region = uipd.ElementCC3D("Region")
   region.ElementCC3D("BoxMin",{"x":x_margin,  "y":y_top_margin+2*Ly,  "z":0})
   region.ElementCC3D("BoxMax",{"x":x_margin+GZ_x,  "y":y_top_margin+2*Ly+GZ_y,  "z":1})
   region.ElementCC3D("Types",{}, "GZ" )
   region.ElementCC3D("Width", {}, d)
  
  
   CompuCellSetup.setSimulationXMLDescription(cc3d)
   
import CompuCellSetup
sim,simthread = CompuCellSetup.getCoreSimulationObjects()
configureSimulation(sim)

import CompuCell
CompuCellSetup.initializeSimulationObjects(sim,simthread)
pyAttributeAdder,dictAdder=CompuCellSetup.attachDictionaryToCells(sim)

#Add Python steppables here
steppableRegistry=CompuCellSetup.getSteppableRegistry()
changeWatcherRegistry=CompuCellSetup.getChangeWatcherRegistry(sim)
stepperRegistry=CompuCellSetup.getStepperRegistry(sim)

from GZ_genesis_steppables import InitVolSur
initVolSur=InitVolSur(_simulator=sim,_frequency=1,_LamV=lambda_V,_LamS=lambda_S,_tV=target_V,_tS=target_S)
steppableRegistry.registerSteppable(initVolSur)

from GZ_genesis_steppables import CellCounts
cellCounts=CellCounts(_simulator=sim,_frequency=100)
steppableRegistry.registerSteppable(cellCounts)

# from GZ_genesis_steppables import CellGrowth
# cellGrowth=CellGrowth(_simulator=sim,_frequency=1,_tV=target_V,_tS=target_S,_T_double=T_double,_range_phase=range_phase)
# steppableRegistry.registerSteppable(cellGrowth)

from GZ_genesis_steppables import Mitosis
mitosis=Mitosis(_simulator=sim,_frequency=1,_V_div=V_div,_divType=divOrientation)
steppableRegistry.registerSteppable(mitosis)

# from GZ_genesis_steppables import ExternalPotentialExample
# extPot=ExternalPotentialExample(_simulator=sim,_frequency=1,_V_p=V_p,_y_comp=y_comp)
# steppableRegistry.registerSteppable(extPot)

if segment_flag:
   from GZ_genesis_steppables import Segmentation
   segmentation=Segmentation(_simulator=sim,_frequency=1,_T_seg=T_segment,_y_seg=y_segment,_y0=y0_seg)
   steppableRegistry.registerSteppable(segmentation)

if GradedMotility_flag:
   from GZ_genesis_steppables import GradedMotility
   motility=GradedMotility(_simulator=sim,_frequency=1,_ls_high=lambda_S_high,_ls_low=lambda_S_low,_lv_high=lambda_V_high,_lv_low=lambda_V_low,_T_seg=T_segment,_sdrh=sd_ratio_high,_sdrl=sd_ratio_low,_sigflag=signal_flag)
   steppableRegistry.registerSteppable(motility)

if grow_sig_flag:
   if grow_repr:
      from GZ_genesis_steppables import GrowthSignaling_repression
      cellGrowth=GrowthSignaling_repression(_simulator=sim,_frequency=1,_tV=target_V,_tS=target_S,_T_double=T_double,_range_phase=range_phase,_y_sig=y_grow_sig)
      steppableRegistry.registerSteppable(cellGrowth)
   else:
      from GZ_genesis_steppables import GrowthSignaling_stimulating02
      cellGrowth=GrowthSignaling_stimulating02(_simulator=sim,_frequency=1,_tV=target_V,_tS=target_S,_T_double=T_double,_range_phase=range_phase,_y_sig=y_grow_sig)
      steppableRegistry.registerSteppable(cellGrowth)
else:
   from GZ_genesis_steppables import CellGrowth
   cellGrowth=CellGrowth(_simulator=sim,_frequency=1,_tV=target_V,_tS=target_S,_T_double=T_double,_range_phase=range_phase)
   steppableRegistry.registerSteppable(cellGrowth)
  
from GZ_motility_steppables import CellCounts
cellCounts=CellCounts(_simulator=sim,_frequency=100)
steppableRegistry.registerSteppable(cellCounts)
  
CompuCellSetup.mainLoop(sim,simthread,steppableRegistry)
