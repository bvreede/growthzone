##******** Simulation Flags ********##

# general simulation flags
global batch; global speed_up_sim

# sarrazin force flags
global y_target_offset; global pull_force_magnitude; global pinch_force_relative_center
global pinch_force_mag; global pinch_force_falloff_sharpness

##******** Configure Simulation Flags ********##

speed_up_sim = False
batch = False

## configure the sarrazin force steppable. Comments show default values

y_target_offset = 15 # 15
pull_force_magnitude = 75 #75
pinch_force_relative_center = 0.3 #0.3
pinch_force_mag = 30 #30
pinch_force_falloff_sharpness = 5 #5

##******** Batch Run Configuration ********##

if batch == True:
    speed_up_sim = True
    file = open("variables.txt", "r") # note, this should be relative to the location command from which the CC3D program was opened
    pinch_center, pinch_girth = [float(i) for i in file.readlines()[0:2]] # this loads in a document with each variable to a line, in the order as seen on the left

def configureSimulation(sim):
    import CompuCellSetup
    from XMLUtils import ElementCC3D
    
    CompuCell3DElmnt=ElementCC3D("CompuCell3D",{"Revision":"20140724","Version":"3.7.2"})
    PottsElmnt=CompuCell3DElmnt.ElementCC3D("Potts")
    
    # Basic properties of CPM (GGH) algorithm
    PottsElmnt.ElementCC3D("Dimensions",{"x":"320","y":"480","z":"1"})
    PottsElmnt.ElementCC3D("Steps",{},"900")
    PottsElmnt.ElementCC3D("Temperature",{},"10.0")
    PottsElmnt.ElementCC3D("NeighborOrder",{},"1")
    
    PluginElmnt=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"CellType"}) # Listing all cell types in the simulation
    PluginElmnt.ElementCC3D("CellType",{"TypeId":"0","TypeName":"Medium"})
    PluginElmnt.ElementCC3D("CellType",{"TypeId":"1","TypeName":"AnteriorLobe"})
    PluginElmnt.ElementCC3D("CellType",{"TypeId":"2","TypeName":"Segment"})
    PluginElmnt.ElementCC3D("CellType",{"TypeId":"3","TypeName":"GZ"})
    
    PluginElmnt_1=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"Volume"}) # Cell property trackers and manipulators
    PluginElmnt_2=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"Surface"})
    extPotential=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"ExternalPotential"})
    PluginElmnt_4=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"CenterOfMass"})
    
    PluginElmnt_5=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"Contact"}) # Specification of adhesion energies
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"Medium","Type2":"Medium"},"100.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"Medium","Type2":"AnteriorLobe"},"100.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"Medium","Type2":"Segment"},"100.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"Medium","Type2":"GZ"},"100.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"AnteriorLobe","Type2":"AnteriorLobe"},"10.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"AnteriorLobe","Type2":"Segment"},"10.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"AnteriorLobe","Type2":"GZ"},"10.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"Segment","Type2":"Segment"},"10.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"Segment","Type2":"GZ"},"10.0")
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"GZ","Type2":"GZ"},"10.0")
    PluginElmnt_5.ElementCC3D("NeighborOrder",{},"1")
    
    SteppableElmnt=CompuCell3DElmnt.ElementCC3D("Steppable",{"Type":"PIFInitializer"})
    
    # Initial layout of cells using PIFF file. Piff files can be generated using PIFGEnerator
    SteppableElmnt.ElementCC3D("PIFName",{},"Simulation/newStart.piff")

    CompuCellSetup.setSimulationXMLDescription(CompuCell3DElmnt)
            
import sys
from os import environ
from os import getcwd
import string

sys.path.append(environ["PYTHON_MODULE_PATH"])

##******** Configure Simulation Flags ********##

import CompuCellSetup
sim,simthread = CompuCellSetup.getCoreSimulationObjects()
configureSimulation(sim)
CompuCellSetup.initializeSimulationObjects(sim,simthread)
steppableRegistry=CompuCellSetup.getSteppableRegistry()
from RewrittenSarrazinSteppables import *

s1 = VolumeStabilizer(sim,_frequency = 1)
s2 = AssignCellAddresses(sim,_frequency = 1)
s3 = SarrazinForces01(sim,_frequency = 1, _y_target_offset = y_target_offset, _pull_force_magnitude = pull_force_magnitude,
                      _pinch_force_relative_center = pinch_force_relative_center, _pinch_force_mag = pinch_force_mag,
                      _pinch_force_falloff_sharpness = pinch_force_falloff_sharpness)

steps = [s1,s2,s3]
for step in steps: steppableRegistry.registerSteppable(step)

if speed_up_sim == False: # Disable the superfluous code for runs where time is of the essense
    SV = SarrazinVisualizer(sim, _frequency = 1)
    
    from RewrittenSarrazinSteppables import SarrazinCloneVisualizer
    SCV = SarrazinCloneVisualizer(sim, _frequency = 1, _cell_locs =  [jeremyVector(_x = 160, _y = 275),
                                                  jeremyVector(_x = 120, _y = 250),
                                                  jeremyVector(_x = 113, _y = 240),
                                                  jeremyVector(_x = 106, _y = 210),
                                                  jeremyVector(_x = 210, _y = 250),
                                                  jeremyVector(_x = 207, _y = 240),
                                                  jeremyVector(_x = 214, _y = 210)])
                                                  
    super_steppables = [SV, SCV]
    for steppable in super_steppables: steppableRegistry.registerSteppable(steppable)                                                 

CompuCellSetup.mainLoop(sim,simthread,steppableRegistry)
        
        