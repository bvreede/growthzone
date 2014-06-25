import sys,time
from os import environ
from os import getcwd
import string
sys.path.append(environ["PYTHON_MODULE_PATH"])

## DECLARE GLOBAL PARAMETERS

# Potts parameters
global T  ## effective simulation temperature; effects the amount of "noise"
global nOrder  ## neighbor order; sets the degree of neighbor considered during contact
               ## energy calculations

# Simulation dimension parameters
global Dx; global Dy; global Dz  ## x, y and z dimensions of the simulation lattice

# Cell size constraint parameters
global d  ## approximately equal to cell diameter; used to calculate surface and volume targets
global targetSurface; global targetVolume ## target volume and surface values
global lambdaSurface; global lambdaVolume ## set the strength of the surface and volume constraints

# Cell blob dimension parameters
global blobRadius ## sets the radius of the initial cell blob

## SET PARAMETER VALUES

# Potts parameters
T = 50
nOrder = 1

# Simulation dimension parameters
Dx = 200
Dy = 200
Dz = 1

# Cell size constraint parameters
d = 10
targetSurface = 4*d
targetVolume = d**2
lambdaSurface = 2.5 ## Note: higher lambdaSurface causes less motile cells
lambdaVolume = 2.0

# Cell blob dimension parameters
blobRadius = 5*d

## CONFIGURE THE SIMULATION 

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
   potts.ElementCC3D("Flip2DimRatio",{},1)
   potts.ElementCC3D("Boundary_x",{},"Periodic")
   
## Specify cell types
   cellType=cc3d.ElementCC3D("Plugin",{"Name":"CellType"})
   cellType.ElementCC3D("CellType", {"TypeName":"Medium","TypeId":"0"})
   cellType.ElementCC3D("CellType", {"TypeName":"Cell1","TypeId":"1"})
   cellType.ElementCC3D("CellType", {"TypeName":"CellJ","TypeId":"2"})

## Specify contact energies (adhesion penalty) between cell types
   contact=cc3d.ElementCC3D("Plugin",{"Name":"Contact"})
   contact.ElementCC3D("Energy", {"Type1":"Medium", "Type2": "Medium"},0)
   contact.ElementCC3D("Energy", {"Type1":"Medium", "Type2": "Cell1"},20)
   contact.ElementCC3D("Energy", {"Type1":"Medium", "Type2": "CellJ"},40)
   contact.ElementCC3D("Energy", {"Type1":"Cell1", "Type2": "Cell1"},5)
   contact.ElementCC3D("Energy", {"Type1":"Cell1", "Type2": "CellJ"},10)
   contact.ElementCC3D("Energy", {"Type1":"CellJ", "Type2": "CellJ"},5)
   contact.ElementCC3D("NeighborOrder",{},nOrder)
   
## Impose a penalty on cell fragmentation using the built-in
## CC3D "Connectivity" plugin   
   connectivity = cc3d.ElementCC3D("Plugin",{"Name":"Connectivity"})
   connectivity.ElementCC3D("Penalty",{},10000)
   
#########Set volume constraints uniformly for all cells in the simulation
   # volume=cc3d.ElementCC3D("Plugin",{"Name":"Volume"})
   # volume.ElementCC3D("TargetVolume",{},targetVolume)
   # volume.ElementCC3D("LambdaVolume",{},lambdaVolume)
   
#########Set surface constraints uniformly for all cells in the simulation
   # surface=cc3d.ElementCC3D("Plugin",{"Name":"Surface"})
   # surface.ElementCC3D("TargetSurface",{},targetSurface)
   # surface.ElementCC3D("LambdaSurface",{},lambdaSurface) 
   
## Initialize plugins for accessing/manipulating cell properties
   # ptrpd = cc3d.ElementCC3D("Plugin",{"Name":"PixelTracker"})
   vlfpd = cc3d.ElementCC3D("Plugin",{"Name":"VolumeLocalFlex"})
   slfpd = cc3d.ElementCC3D("Plugin",{"Name":"SurfaceLocalFlex"})
   # ntpd = cc3d.ElementCC3D("Plugin",{"Name":"NeighborTracker"})
   # comtpd = cc3d.ElementCC3D("Plugin",{"Name":"CenterOfMass"})
   
## MUST INITIALIZE EXTERNAL POTENTIAL PLUGIN
   extPotential=cc3d.ElementCC3D("Plugin",{"Name":"ExternalPotential"})
      
## Initialize simulation with a "blob" of cells
   blobInit=cc3d.ElementCC3D("Steppable",{"Type":"BlobInitializer"})
   blobInit.ElementCC3D("Gap",{},0)
   blobInit.ElementCC3D("Width",{},d)
   blobInit.ElementCC3D("CellSortInit",{},"Yes")
   blobInit.ElementCC3D("Radius",{},blobRadius)
   
   CompuCellSetup.setSimulationXMLDescription(cc3d)
   
import CompuCellSetup
sim,simthread = CompuCellSetup.getCoreSimulationObjects()
configureSimulation(sim)   
   
import CompuCell
CompuCellSetup.initializeSimulationObjects(sim,simthread)
# pyAttributeAdder,dictAdder=CompuCellSetup.attachDictionaryToCells(sim)

#Add Python steppables here
steppableRegistry=CompuCellSetup.getSteppableRegistry()
changeWatcherRegistry=CompuCellSetup.getChangeWatcherRegistry(sim)
stepperRegistry=CompuCellSetup.getStepperRegistry(sim)

from Intro_Steppables import VolumeSurfaceExample
volSurEx=VolumeSurfaceExample(_simulator=sim,_frequency=10,_LamV=lambdaVolume,_LamS=lambdaSurface,_tV=targetVolume,_tS=targetSurface,_extremeSmall=10,_extremeBig=500)
steppableRegistry.registerSteppable(volSurEx)

from Intro_Steppables import TestOutput
testOutput=TestOutput(_simulator=sim,_frequency=100)
steppableRegistry.registerSteppable(testOutput)

CompuCellSetup.mainLoop(sim,simthread,steppableRegistry)