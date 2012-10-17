from optparse import OptionParser
from datetime import datetime
from vtk import *
import os

from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeTemporalPython import *
from libvtkGRASSBridgeCommonPython import *

from RothCEqulibriumRun import *
    
###############################################################################

class PlotModelData:
    def __init__(self, list):
        self.date = datetime(year=int(float(list[0])), month=int(float(list[1])), day=1)
        self.temp = float(list[2])
        self.precip = float(list[3])
        self.rad = float(list[4])
        self.typeFert = int(float(list[5]))
        self.fertDryMatter = float(list[6])
        self.fertCInput = float(list[7])
        self.cropType = int(float(list[8]))
        self.cropFreshMatter = float(list[9])
        self.cropCInput = float(list[10])

    def __str__(self):
        string = ""
        string += "\n    date:........... " + str(self.date)
        string += "\n    temp:........... " + str(self.temp)
        string += "\n    precip:......... " + str(self.precip)
        string += "\n    rad:............ " + str(self.rad)
        string += "\n    typeFert:....... " + str(self.typeFert)
        string += "\n    fertDryMatter:.. " + str(self.fertDryMatter)
        string += "\n    fertCInput:..... " + str(self.fertCInput)
        string += "\n    cropType:....... " + str(self.cropType)
        string += "\n    cropFreshMatter: " + str(self.cropFreshMatter)
        string += "\n    cropCInput:..... " + str(self.cropCInput)
        return string
    
###############################################################################
        
class Plot:
    def __init__(self, list):
        self.extract_plot_data(list)
        
    def extract_plot_data(self, list):
        self.name = list[0]
        self.start = datetime(year=int(float(list[1])), month=int(float(list[2])), day=1)
        self.end = datetime(year=int(float(list[3])), month=int(float(list[4])), day=1)
        self.x = float(list[6])
        self.y =float(list[7])
        self.depth = float(list[13])/100.0
        self.initCorg = float(list[16])
        self.finalCorg = float(list[17])
        self.bulkDensity = float(list[23])
        self.sand = float(list[24])
        self.silt = float(list[25])
        self.clay = float(list[26])
        self.Norg = float(list[18])
        self.cropTypeEqui = float(list[27])
    
    def __str__(self):
        string = ""
        string += "\n  name:........ " + str(self.name)
        string += "\n  start:....... " + str(self.start)
        string += "\n  end:......... " + str(self.end)
        string += "\n  x:........... " + str(self.x)
        string += "\n  y:........... " + str(self.y)
        string += "\n  depth:....... " + str(self.depth)
        string += "\n  initCorg:.... " + str(self.initCorg)
        string += "\n  finalCorg:... " + str(self.finalCorg)
        string += "\n  bulkDensity:. " + str(self.bulkDensity)
        string += "\n  sand:........ " + str(self.sand)
        string += "\n  silt:........ " + str(self.silt)
        string += "\n  clay:........ " + str(self.clay)
        string += "\n  Norg:........ " + str(self.Norg)
        string += "\n  cropTypeEqui: " + str(self.cropTypeEqui)
        
        return string
    
###############################################################################
        
class Site:
    def __init__(self, gid, filename, directory):
        self.gid = int(gid)
        self.filename = filename
        self.directory = directory
        self.plots = []
        self.timeSeriesData = {}
        self.extract_site(gid, filename, directory)
        
    def extract_site(self, gid=None, filename=None, directory=None):
        if gid:
            self.gid = int(gid)
        if filename:
            self.filename = filename
        if directory:
            self.directory = directory
            
        # Read the site specific data
        file = open(filename, "r")
        lines = file.readlines()
        file.close()
        
        # Parse the input file and extract the group site data
        for line in lines[2:]:
            list = line.split(";")
            if int(list[9]) == self.gid:
                plot = Plot(list)
                self.plots.append(plot)
        
        # Read the plot model data for each group member
        for plot in self.plots:
            self.timeSeriesData[plot.name] = []
            filepath = os.path.join(self.directory, plot.name + ".inp")
            file = open(filepath, "r")
            lines = file.readlines()
            for line in lines[1:]:
                list = line.split("\t")
                self.timeSeriesData[plot.name].append(PlotModelData(list))
                
                
    def __str__(self):
        string = ""
        string += "Group " + str(self.gid)
        for plot in self.plots:
            string += "\n" + str(plot)
            for plot_data in self.timeSeriesData[plot.name]:
                string += "\n"
                string += str(plot_data)
        return string
    
###############################################################################

class SiteToVTK:
    def __init__(self, site):
        self.site = site
        self.datasets = []
        self.convert()
    
    def convert(self, site=None):
        if site:
            self.site = site
            
        for i in xrange(len(self.site.timeSeriesData[self.site.plots[0].name])):
            
            num = len(self.site.plots)
            
            GlobalRadiationArray = vtkDoubleArray()
            GlobalRadiationArray.SetNumberOfTuples(num)
            GlobalRadiationArray.SetName("GlobalRadiation")
            
            MeanTemperatureArray = vtkDoubleArray()
            MeanTemperatureArray.SetNumberOfTuples(num)
            MeanTemperatureArray.SetName("MeanTemperature")
            
            PrecipitationArray = vtkDoubleArray()
            PrecipitationArray.SetNumberOfTuples(num)
            PrecipitationArray.SetName("Precipitation")
            
            SoilCoverArray = vtkDoubleArray()
            SoilCoverArray.SetNumberOfTuples(num)
            SoilCoverArray.SetName("SoilCover")
            
            ClayArray = vtkDoubleArray()
            ClayArray.SetNumberOfTuples(num)
            ClayArray.SetName("Clay")
            
            FertilizerCarbonArray = vtkDoubleArray()
            FertilizerCarbonArray.SetNumberOfTuples(num)
            FertilizerCarbonArray.SetName("FertilizerCarbon")

            
            type_ = vtkIntArray()
            type_.SetNumberOfTuples(num)
            type_.SetName("type")
            
            # Point ids for poly vertex cell
            points = vtkPoints()
     
            ETpot = vtkPolyData()
            ETpot.Allocate(num, num)
      
            WaterBudget = vtkPolyData()
            WaterBudget.Allocate(num, num)
            
            RothC = vtkPolyData()
            RothC.Allocate(num, num)
                      
            SoilCarbonArray = vtkDoubleArray()
            SoilCarbonArray.SetNumberOfTuples(num)
            SoilCarbonArray.SetName("SoilCarbon")
            
            if i == 0:
                InitialSoilCarbonArray = vtkDoubleArray()
                InitialSoilCarbonArray.SetNumberOfTuples(num)
                InitialSoilCarbonArray.SetName("InitialCarbon")
            
            ResidualsArray = vtkDoubleArray()
            ResidualsArray.SetNumberOfTuples(num)
            ResidualsArray.SetName("Residuals")
            
            Residuals = vtkPolyData()
            Residuals.Allocate(num, num)
        
            if i == 0:
                SoilCarbon = vtkPolyData()
                SoilCarbon.Allocate(num, num)
          
            count = 0
            for plot in self.site.plots:
                ids = vtkIdList()
                ids.InsertNextId(points.InsertNextPoint(plot.x, plot.y, 0))
                ids.InsertNextId(points.InsertNextPoint(plot.x, plot.y, plot.depth))
                ETpot.InsertNextCell(vtk.VTK_LINE, ids)
                WaterBudget.InsertNextCell(vtk.VTK_LINE, ids)
                RothC.InsertNextCell(vtk.VTK_LINE, ids)
                Residuals.InsertNextCell(vtk.VTK_LINE, ids)
                SoilCarbon.InsertNextCell(vtk.VTK_LINE, ids)
                
                GlobalRadiationArray.SetValue(count, self.site.timeSeriesData[plot.name][i].rad)
                MeanTemperatureArray.SetValue(count, self.site.timeSeriesData[plot.name][i].temp)
                PrecipitationArray.SetValue(count, self.site.timeSeriesData[plot.name][i].precip)
                
                soilCover = self.site.timeSeriesData[plot.name][i].cropType
                if int(soilCover) == 9999:
                    SoilCoverArray.SetValue(count, False)
                else:
                    SoilCoverArray.SetValue(count, True)
                    
                ClayArray.SetValue(count, plot.clay)
                FertilizerCarbonArray.SetValue(count, self.site.timeSeriesData[plot.name][i].fertCInput)
                
                if i == 0:
                    InitialSoilCarbonArray.SetValue(count, plot.initCorg)
                
                SoilCarbonArray.SetValue(count, plot.initCorg)
                
                ResidualsArray.SetValue(count, self.site.timeSeriesData[plot.name][i].cropCInput)
                count += 1
                
                #print i, "rad", self.site.timeSeriesData[plot.name][i].rad, \
                #      "temp", self.site.timeSeriesData[plot.name][i].temp, \
                #      "precip", self.site.timeSeriesData[plot.name][i].precip, \
                #      "cropType", self.site.timeSeriesData[plot.name][i].cropType, \
                #      "fertCInput", self.site.timeSeriesData[plot.name][i].fertCInput, \
                #      "cropCInput", self.site.timeSeriesData[plot.name][i].cropCInput, \
                #      "plot.initCorg", plot.initCorg
    
            ETpot.GetCellData().AddArray(GlobalRadiationArray)
            ETpot.GetCellData().AddArray(MeanTemperatureArray)
            ETpot.SetPoints(points)    
            
            WaterBudget.GetCellData().AddArray(PrecipitationArray)
            WaterBudget.GetCellData().AddArray(SoilCoverArray)
            WaterBudget.GetCellData().AddArray(ClayArray)
            WaterBudget.SetPoints(points) 
               
            RothC.GetCellData().AddArray(ClayArray) 
            if i == 0:
                RothC.GetCellData().AddArray(InitialSoilCarbonArray) 
            RothC.GetCellData().AddArray(SoilCoverArray) 
            RothC.GetCellData().AddArray(MeanTemperatureArray)
            RothC.GetCellData().AddArray(ResidualsArray)
            RothC.GetCellData().AddArray(FertilizerCarbonArray)
            RothC.SetPoints(points)

            Residuals.GetCellData().SetScalars(ResidualsArray)
            Residuals.SetPoints(points)    
        
            if i == 0:
                SoilCarbon.GetCellData().SetScalars(SoilCarbonArray)
                SoilCarbon.SetPoints(points)              
        
            ds = {}
            ds["ETpot"] = ETpot
            ds["WaterBudget"] = WaterBudget
            ds["RothC"] = RothC
            ds["Residuals"] = Residuals
            ds["SoilCarbon"] = SoilCarbon
            self.datasets.append(ds)
    
###############################################################################            
            
def run(ETpotInputs, WaterBudgetInputs, RothCInputs, ResidualsInput,
        RothCParameter=None, NullValue=-99999):
    """!Compute the RothC soil carbon equilibrium
    
       @param ETpotInputs: A list of inputs, each the long term parameter
                          for ETpot computation.
                          - Long term monthly temperature mean [degree C]
                          - Long term monthly global radiation [J/(cm^2 * day)]
       
       @param WaterBudgetInputs: A list of inputs, each the long term 
                          parameter for Water Budget computation.
                          - Long term monthly accumulated precipitation [mm]
                          - Long term monthly soil cover (0 or 1) [-]
                          - Clay content in percent [%]
       
       param RothCInputs: A list of vtkPolyData inputs, each the long term
                          parameter of the RothC model
                          - Clay content in percent [%]
                          - Long term monthly soil cover (0 or 1) [-]
                          - Long term monthly temperature mean [degree C]
                          - Long term monthly fertilizer carbon (should be 0)
                          - Initial C-org
       
       param ResidualsInput:  A list of vtkPolyData inputs representing
                          the residuals for the RothC model [tC/ha]
                                             
       @param RothCParameter: The parameter object for the RothC Model
       @param NullValue: The Null value that represents unknown values
       
       @return A vtkPolyDataSet with RothC pools and initial Carbon
    """
    
    # Compute potential evapo-transpiration
    ETpot = vtkTAG2ETurcETPotModel()
    ETpot.SetNullValue(NullValue)
    
    # Soil moisture computation
    SoilMoisture = vtkTAG2ERothCWaterBudgetModel()
    SoilMoisture.SetNullValue(NullValue)
    
    # Residual distribution
    Residuals = vtkTAG2ERothCResidualFilter()
    Residuals.SetNullValue(NullValue)
    
    # RothC model computation
    if not RothCParameter:
        RothCParameter = vtkTAG2ERothCModelParameter()

    RothC = vtkTAG2ERothCModel()
    RothC.SetModelParameter(RothCParameter)
    RothC.AddCPoolsToOutputOn()
    RothC.CPoolsInitiatedOn()
    RothC.SetNullValue(NullValue)
    
    dc1 = vtkTAG2EDataSetJoinFilter()
    dc2 = vtkTAG2EDataSetJoinFilter()
    
    for i in xrange(len(ETpotInputs)):
        print "Month", i                
        ETpot.SetInput(ETpotInputs[i])
        ETpot.SetTimeInterval(30)
        
        # Soil moisture input
        dc1.RemoveAllInputs()
        dc1.AddInputConnection(ETpot.GetOutputPort())
        dc1.AddInput(WaterBudgetInputs[i])
        
        SoilMoisture.SetInputConnection(dc1.GetOutputPort())
        
        Residuals.SetInput(ResidualsInput[i])
        
        dc2.RemoveAllInputs()
        dc2.AddInput(RothCInputs[i])
        dc2.AddInputConnection(SoilMoisture.GetOutputPort())
        dc2.AddInputConnection(Residuals.GetOutputPort())

        RothC.SetInputConnection(dc2.GetOutputPort())
        RothC.Update()
        
        cd = RothC.GetOutput().GetCellData()
        #for id in xrange(RothC.GetOutput().GetNumberOfCells()):
        #    print cd.GetArray("SoilCarbon").GetValue(id), cd.GetArray("DPM").GetValue(id), \
        #          cd.GetArray("RPM").GetValue(id), cd.GetArray("BIO").GetValue(id), \
        #          cd.GetArray("HUM").GetValue(id), cd.GetArray("IOM").GetValue(id)

    # Return the output of RothC
    output = vtkPolyData()
    output.ShallowCopy(RothC.GetOutput())
    
    return output
    
###############################################################################

def main(options, args):    
    # Parse the site specific file for a specific group
    site = Site(options.group_id, options.filename, options.directory)
    ds = SiteToVTK(site)    
    # Equilibrium run

    ETpotInputs = []
    WaterBudgetInputs = []
    RothCInputs = []
    
    res = vtkPolyData()
    res.DeepCopy(ds.datasets[8]["Residuals"])
    
    for id in xrange(res.GetNumberOfCells()):
        res.GetCellData().GetArray("Residuals").SetTuple1(id, 1)
    
    ResidualsInput = res
    SoilCarbonInput = ds.datasets[0]["SoilCarbon"]
    
    for month in range(0, 12):
        ETpotInputs.append(ds.datasets[month]["ETpot"])
        WaterBudgetInputs.append(ds.datasets[month]["WaterBudget"])
        RothCInputs.append(ds.datasets[month]["RothC"])
    
    new_ds = RothCEquilibriumRun(ETpotInputs, WaterBudgetInputs, RothCInputs, 
                      ResidualsInput, SoilCarbonInput, 300, 100,
                      None, 9999)
        
    writer = vtkPolyDataWriter()
    writer.SetInput(new_ds)
    writer.SetFileName("/tmp/RothCEqulibirumEqui.vtk")
    writer.Write()

    ETpotInputs = []
    WaterBudgetInputs = []
    RothCInputs = []
    ResidualsInput = []
    
    for i in range(len(ds.datasets)):
        ETpotInputs.append(ds.datasets[i]["ETpot"])
        WaterBudgetInputs.append(ds.datasets[i]["WaterBudget"])
        RothCInputs.append(ds.datasets[i]["RothC"])
        ResidualsInput.append(ds.datasets[i]["Residuals"])
            
    
    # Append the pools to the first RothC input dataset
    for id in xrange(new_ds.GetCellData().GetNumberOfArrays()):
        RothCInputs[0].GetCellData().AddArray(new_ds.GetCellData().GetArray(id))
      
    new_ds = run(ETpotInputs, WaterBudgetInputs, RothCInputs, ResidualsInput)
    
    writer = vtkPolyDataWriter()
    writer.SetInput(new_ds)
    writer.SetFileName("/tmp/RothCEqulibirumRun.vtk")
    writer.Write()
    
###############################################################################
    
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="The SOC main text file", metavar="FILE")
    parser.add_option("-d", "--directory", dest="directory",
                  help="The directory containing the SOC inp files", metavar="DIR")    
    parser.add_option("-i", "--id", dest="group_id",
                  help="The group id of the site to convert")
    parser.add_option("-o", "--outfile", dest="outfilename",
                      help="The resulting site specific output VTK file name", metavar="FILE")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")
    
    (options, args) = parser.parse_args()
    
    if not options.filename or not options.directory or not options.group_id:
        parser.error("You need to specify filename and directory")
    
    cProfile.run(main(options, args)
