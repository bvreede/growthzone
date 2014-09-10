
from PySteppables import *
import CompuCell
import sys
import math

class jeremyVector:
    def __init__(self,_x,_y):
        self.x = float(_x)
        self.y = float(_y)
        self.distance = float(math.sqrt(_x**2 + _y**2))

    def x(self): return self.x
    def y(self): return self.y
    def set_x(self, _x):
        self.x = _x
        self.distance = math.sqrt(_x**2 + _y**2)
    def set_y(self, _y):
        self.y = _y
        self.distance = math.sqrt(_x**2 + _y**2)

    def scream(self): raise NameError("Vector x = {}, y = {}".format(self.x,self.y))

    def normalize(self):
        if self.distance > 0:
            self.x /= self.distance
            self.y /= self.distance
            self.distance = 1
        else:
            self.x = 0
            self.y = 0
    def normalVector(self):
        newVec = copy.deepcopy(self)
        newVec.normalize()
        return newVec

    def add(self, vec):
        self.x += vec.x
        self.y += vec.y
    def scale(self, scaleFactor):
        self.x *= scaleFactor
        self.y *= scaleFactor

    @classmethod
    def vecBetweenPoints(cls, _start_x, _start_y, _end_x, _end_y):
        x_disp = _end_x - _start_x
        y_disp = _end_y - _start_y
        return jeremyVector(x_disp, y_disp)
    @classmethod
    def addVecs(cls,_vecs):
        newVec = jeremyVector(0,0)
        for vec in _vecs: newVec.add(vec)
        return newVec

class VolumeStabilizer(SteppableBasePy):
    def __init__(self,_simulator,_frequency=1):
        SteppableBasePy.__init__(self,_simulator,_frequency)

    def start(self):
        for cell in self.cellList:
            cell.targetVolume = cell.volume
            cell.targetSurface = cell.surface

            # This above code prevents the cells from immediately shrinking to nothing.

            cell.lambdaVolume = 50.0 # A high lambdaVolume makes the cells resist changing volume.
            cell.lambdaSurface = 2.0 # However, a low lambdaSurface still allows them to move easily.

            # In effect, these two lines allow the cells to travel without squeezing, which would be unrealistic.
            
class AssignCellAddresses(SteppableBasePy): # this steppable assigns each cell an address along the AP axis
    def __init__(self,_simulator,_frequency):
        SteppableBasePy.__init__(self,_simulator,_frequency)

        self.height = 0
        self.posteriormost_cell_y = None
        self.anteriormost_cell_y = None
        self.anteriormost_cell = None
        
    def evaluateEmbryoDimensions(self):
        self.posteriormost_cell_y = 999
        self.anteriormost_cell_y = 0

        for cell in self.cellList:
            if cell.yCOM < self.posteriormost_cell_y:
                self.posteriormost_cell_y = cell.yCOM
            elif cell.yCOM > self.anteriormost_cell_y:
                self.anteriormost_cell_y = cell.yCOM
                self.anteriormost_cell = cell
            
        self.height = abs(self.posteriormost_cell_y - self.anteriormost_cell_y)

    def percentBodyLengthFromAnteriorToCell(self, target_cell): # delete me if not needed!
        distance_from_anterior = abs(self.posteriormost_cell_y - target_cell.yCOM)
        return distance_from_anterior / self.height

    def yCoordOfPercentBodyLengthFromAnterior(self, percent_body_length): # delete me if not needed!
        if 0 > percent_body_length or 1 < percent_body_length: raise NameError("Paramater limits of yCoordOfPercentBodyLengthFromAnterior function exceeded")
        return self.anteriormost_cell_y + self.height*percent_body_length

    def assignRelativeAddresses(self, cell):
        CompuCell.getPyAttrib(cell)["CELL_AP_ADDRESS"] = self.percentBodyLengthFromAnteriorToCell(cell)

    def immobilizeAnteriorLobe(self,cell):
        address = CompuCell.getPyAttrib(cell)["CELL_AP_ADDRESS"]
        if address < 0.2:
            cell.lambdaSurface += (0.2 - address) * 100

    def start(self):
        self.evaluateEmbryoDimensions()
        for cell in self.cellList:
            self.assignRelativeAddresses(cell)
            #self.immobilizeAnteriorLobe(cell) #experimental code to preserve the shape of the anterior lobe

class SarrazinForces01(SteppableBasePy):

    def __init__(self,_simulator,_frequency, _y_target_offset, _pull_force_magnitude, _pinch_force_relative_center, _pinch_force_mag, _pinch_force_falloff_sharpness):
        SteppableBasePy.__init__(self,_simulator,_frequency)
        self.y_target_offset = _y_target_offset # 15
        self.pull_force_magnitude = _pull_force_magnitude # 75
        self.pinch_force_relative_center = _pinch_force_relative_center # 0.3
        self.pinch_force_mag = _pinch_force_mag # 50
        self.pinch_force_falloff_sharpness = _pinch_force_falloff_sharpness #5


        self.anteriormost_cell = None

    def start(self):
        self.anteriormost_cell = self.getSteppableByClassName('AssignCellAddresses').anteriormost_cell

    def step(self,mcs):

        target_coord_x = 160
        target_coord_y = self.anteriormost_cell.yCOM - self.y_target_offset
        # the 15 pixels is the offset of the target from the anterior most cell

        for cell in self.cellList:
            cell.lambdaVecX = 0; cell.lambdaVecY = 0 #reset forces from the MCS
            body_address = CompuCell.getPyAttrib(cell)["CELL_AP_ADDRESS"] # figure out where the cell lies along the AP axis

            ##******** Here, we'll apply the pull force: ********##

            newVec = jeremyVector.vecBetweenPoints(cell.xCOM, cell.yCOM, target_coord_x,target_coord_y) # find the direction vector
            newVec.normalize() # make the vector into a unit vector
            newVec.scale(self.pull_force_magnitude) # scale it to a standard length, so that the field has a uniform, substantial magnitude

            # Finally, apply the pull force

            cell.lambdaVecX -= newVec.x
            cell.lambdaVecY -= newVec.y * body_address

            # this previous line of code scales the component parallel to the AP axis
            # as a function of each cell's location on that axis.

             ##******** And here, the pinch force ********##

            direction_vec = (160 - cell.xCOM) # First, find the vector between the cell and the AP axis.
            try: direction_vec = direction_vec/abs(direction_vec) # normalize this vector...
            except: direction_vec = 0   # unless we get a divide by zero error, in which it must be a zero vector.

            #Here, we configure the variables that govern the pinch force

            rc = self.pinch_force_relative_center # where along the AP axis, as a percentage of body length from the posterior, should this force be most active
            f = self.pinch_force_mag # the value of the force at its greatest value
            s = self.pinch_force_falloff_sharpness # sharpness of the falloff from its strongest point

            # Beyond this point lies mathy stuff

            min_zenith_loc = 1/s
            max_zenith_loc = s - min_zenith_loc
            zenith_range = max_zenith_loc - min_zenith_loc
            o = min_zenith_loc + (zenith_range * rc)
            mag = (((-1) * (s*body_address - o)**2) + 1) * f
            if mag < 0: mag = 0

            # Finally, apply the pinch force

            cell.lambdaVecX -= direction_vec * mag


class SarrazinVisualizer(SteppableBasePy):
    def __init__(self, _simulator, _frequency):
        SteppableBasePy.__init__(self, _simulator, _frequency)
        self.vectorCLField = self.createVectorFieldCellLevelPy("Sarrazin_Force")

    def step(self, mcs):
        self.vectorCLField.clear()
        for cell in self.cellList:
            self.vectorCLField[cell] = [cell.lambdaVecX * -1, cell.lambdaVecY * -1, 0]