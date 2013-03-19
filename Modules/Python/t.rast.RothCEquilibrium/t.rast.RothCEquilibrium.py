#!/usr/bin/env python
#
# Toolkit for Agriculture Greenhouse Gas Emission Estimation TAG2E
#
# Program: t.rast.RothCEquilibrium
#
# Purpose: Compute a weighted fuzzy inference model based on raster data
#
# Authors: Soeren Gebbert, soeren.gebbert@vti.bund.de
#          Rene Dechow, rene.dechow@vti.bund.de
#
# Copyright:
#
# Johann Heinrich von Thuenen-Institut
# Institut fuer Agrarrelevante Klimaforschung
#
# Phone: +49 (0)531 596 2601
#
# Fax:+49 (0)531 596 2699
#
# Mail: ak@vti.bund.de
#
# Bundesallee 50
# 38116 Braunschweig
# Germany
#
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; version 2 of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

import sys
import grass.script as grass
import grass.temporal as tgis
import os
#include the VTK and vtkGRASSBridge Python libraries
from vtk import *
import libvtkTAG2EFilteringPython
from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeIOPython import *
from libvtkGRASSBridgeCommonPython import *
from RothCEqulibriumRun import *

################################################################################
################################################################################
################################################################################

def main():
    # Initiate GRASS
    init = vtkGRASSInit()
    init.Init("t.rast.RothCEquilibrium")
    init.ExitOnErrorOn()

    module = vtkGRASSModule()
    module.SetDescription("Compute the RothC soil carbon equilibrium using Brents method")
    module.AddKeyword("temporal")
    module.AddKeyword("RothC")
    
    temperature = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    temperature.SetKey("temperature")
    temperature.SetDescription("Space time raster dataset with long "
                               "term monthly temperature mean [degree C] (exactly 12 months)"
                               ". This dataset will be used to temporally sample all other.")
    
    precipitation = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    precipitation.SetKey("precipitation")
    precipitation.SetDescription("Space time raster dataset with long term "
                                 "monthly accumulated precipitation [mm] (exactly 12 months)")
    
    radiation = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    radiation.SetKey("radiation")
    radiation.SetDescription("Space time raster dataset with long term monthly "
                             "global radiation [J/(cm^2 * day)] (exactly 12 months)")
    
    # Space time raster datasets
    soilCover = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    soilCover.SetKey("soilcover")
    soilCover.SetDescription("Space time raster dataset with long term monthly soil cover (exactly 12 months)")
                       
    # Raster map input
    clayContent = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType())
    clayContent.SetKey("claycontent")
    clayContent.SetDescription("Raster map with clay content in percent [%]")
    
    soilCarbon = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType())
    soilCarbon.SetKey("soc")
    soilCarbon.SetDescription("Raster map with target SOC [tC/ha]")

    residuals = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType())
    residuals.SetKey("residuals")
    residuals.SetDescription("Raster map with the initial residuals of the RothC model [tC/ha] "
                             "applied in august of each model year")
    
    output = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterOutputType())
    output.SetDescription("The model soil organic carbon result at equilibrium")
    
    poolDPM = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterOutputType())
    poolDPM.SetKey("dpmpool")
    poolDPM.SetDescription("The model DPM pool result at equilibirum")
        
    poolRPM = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterOutputType())
    poolRPM.SetKey("rpmpool")
    poolRPM.SetDescription("The model RPM pool result at equilibirum")
        
    poolHUM = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterOutputType())
    poolHUM.SetKey("humpool")
    poolHUM.SetDescription("The model HUM pool result at equilibirum")
        
    poolBIO = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterOutputType())
    poolBIO.SetKey("biopool")
    poolBIO.SetDescription("The model BIO pool result at equilibirum")
        
    poolIOM = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterOutputType())
    poolIOM.SetKey("iompool")
    poolIOM.SetDescription("The model IOM pool result at equilibirum")
    
    convergence = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterOutputType())
    convergence.SetKey("convergence")
    convergence.SetDescription("Convergence flag for each pixel. 1 convence, 0 no convergence")
    
    squaredResiduals = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterOutputType())
    squaredResiduals.SetKey("squaredresiduals")
    squaredResiduals.SetDescription("The squared residuals of the Brent optimization for each pixel")
    """
    Model input start
      * Temperature STRDS name
      * Precipitation STRDS name
      * Radiation STRDS name
      * SoilCover STRDS name
      * Fertilizer STRDS name
      * Residuals STRDS name
    """
    
    modelTemperature = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    modelTemperature.SetKey("mtemperature")
    modelTemperature.RequiredOff()
    modelTemperature.SetDescription("Space time raster dataset with monthly temperature mean [degree C]"
                               ". This dataset will be used to temporally sample all other.")
    
    modelPrecipitation = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    modelPrecipitation.SetKey("mprecipitation")
    modelPrecipitation.RequiredOff()
    modelPrecipitation.SetDescription("Space time raster dataset with "
                                      "accumulated precipitation [mm]")
    
    modelRadiation = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    modelRadiation.SetKey("mradiation")
    modelRadiation.RequiredOff()
    modelRadiation.SetDescription("Space time raster dataset with monthly "
                             "global radiation [J/(cm^2 * day)]")
    
    modelResiduals = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    modelResiduals.SetKey("mresiduals")
    modelResiduals.RequiredOff()
    modelResiduals.SetDescription("Space time raster dataset with monthly "
                             "residuals tC/ha")
    
    modelFertilizer = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    modelFertilizer.SetKey("mfertilizer")
    modelFertilizer.RequiredOff()
    modelFertilizer.SetDescription("Space time raster dataset with monthly "
                             "fertilizer tC/ha")
    
    # Space time raster datasets
    modelSoilCover = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    modelSoilCover.SetKey("msoilcover")
    modelSoilCover.RequiredOff()
    modelSoilCover.SetDescription("Space time raster dataset with monthly soil cover")
    
    """
    Model input end
    """

    residualsOut = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterOutputType())
    residualsOut.SetKey("resout")
    residualsOut.SetDescription("The computed residuals to reach equilibirum")
        
    iterations = vtkGRASSOption()
    iterations.SetKey("iterations")
    iterations.MultipleOff()
    iterations.RequiredOff()
    iterations.SetDefaultAnswer("20")
    iterations.SetDescription("The maximum number of iterations to find the equilibrium")
    iterations.SetTypeToInteger()

    years = vtkGRASSOption()
    years.SetKey("years")
    years.MultipleOff()
    years.RequiredOff()
    years.SetDefaultAnswer("300")
    years.SetDescription("The number of years of the provided temporal cycle")
    years.SetTypeToInteger()

    ax = vtkGRASSOption()
    ax.SetKey("ax")
    ax.MultipleOff()
    ax.RequiredOff()
    ax.SetDefaultAnswer("0")
    ax.SetDescription("The lower limit of the residual range")
    ax.SetTypeToDouble()
    
    cx = vtkGRASSOption()
    cx.SetKey("cx")
    cx.MultipleOff()
    cx.RequiredOff()
    cx.SetDefaultAnswer("15")
    cx.SetDescription("The upper limit of the residual range")
    cx.SetTypeToDouble()
    
    
    yearly = vtkGRASSFlag()
    yearly.SetDescription("Compute yearly aggregates for equilibrium run")
    yearly.SetKey('y')
    
    # INIT
    paramter = vtkStringArray()
    for arg in sys.argv:
        paramter.InsertNextValue(str(arg))

    if init.Parser(paramter) == False:
        return -1
    # We need to modify the environment settings so that the
    # overwrite flag will be recognized
    os.environ["GRASS_OVERWRITE"] = str(init.Overwrite())
    os.environ["GRASS_VERBOSE"] = str(init.Verbosity())

    tgis.init()
    messages = vtkGRASSMessagingInterface()

    messages.VerboseMessage("Reading raster maps into memory")

    # We define the line length as 30cm
    lineLengths = vtkDoubleArray()
    lineLengths.InsertNextValue(0.30)
    
    names = vtkStringArray()
    names.InsertNextValue(clayContent.GetAnswer())
    clayReader = vtkGRASSMultiRasterPolyDataLineReader()
    clayReader.SetRasterNames(names)
    clayReader.SetDataName("Clay")
    clayReader.SetLineLengths(lineLengths)
    clayReader.Update()
    
    # We are using the target SOC as initial SOC
    names = vtkStringArray()
    names.InsertNextValue(soilCarbon.GetAnswer())
    InitialCarbon = vtkGRASSMultiRasterPolyDataLineReader()
    InitialCarbon.SetRasterNames(names)
    InitialCarbon.SetDataName("InitialCarbon")
    InitialCarbon.SetLineLengths(lineLengths)
    InitialCarbon.Update()
    
    names = vtkStringArray()
    names.InsertNextValue(soilCarbon.GetAnswer())
    soilCarbonReader = vtkGRASSMultiRasterPolyDataLineReader()
    soilCarbonReader.SetRasterNames(names)
    soilCarbonReader.SetDataName("SoilCarbon")
    soilCarbonReader.SetLineLengths(lineLengths)
    soilCarbonReader.Update()
    
    names = vtkStringArray()
    names.InsertNextValue(residuals.GetAnswer())
    residualsReader = vtkGRASSMultiRasterPolyDataLineReader()
    residualsReader.SetRasterNames(names)
    residualsReader.SetDataName("Residuals")
    residualsReader.SetLineLengths(lineLengths)
    residualsReader.Update()
        
    inputNames = "%s,%s,%s"%(precipitation.GetAnswer(), radiation.GetAnswer(),
                            soilCover.GetAnswer())
    
    mapmatrix = tgis.sample_stds_by_stds_topology("strds", "strds", inputNames,
                                           temperature.GetAnswer(), False,
                                 "|", "equal", False, True)

    dataInputs = []
    
    if len(mapmatrix) > 0:
        
        if len(mapmatrix[0]) < 12:
            messages.FatalError("You must provide at least 12 months of data")
        
        for j in range(12):
            
            dsList = []
            
            for i in range(len(mapmatrix)):
                
                entry = mapmatrix[i][j]
                
                samples = entry["samples"]
                granule = entry["granule"]
                
                if len(samples) > 1:
                    messages.Warning("More than one maps found in sample. "
                                     "Using the first one only.")
                    for sample in samples:
                        print sample.get_id()
                    
                sample = samples[0]
                
                if sample.get_id() == None:
                    messages.FatalError("Gaps are not allowed")
                
                if i == 0:
                    id = sample.get_id()
                    names = vtkStringArray()
                    names.InsertNextValue(id)
                    reader = vtkGRASSMultiRasterPolyDataLineReader()
                    reader.SetRasterNames(names)
                    reader.SetDataName("Precipitation")
                    reader.SetLineLengths(lineLengths)
                    reader.Update()
                    
                    dsList.append(reader.GetOutput())

                if i == 1:
                    id = sample.get_id()
                    names = vtkStringArray()
                    names.InsertNextValue(id)
                    reader = vtkGRASSMultiRasterPolyDataLineReader()
                    reader.SetRasterNames(names)
                    reader.SetDataName("GlobalRadiation")
                    reader.SetLineLengths(lineLengths)
                    reader.Update()
                    
                    dsList.append(reader.GetOutput())

                if i == 2:
                    id = sample.get_id()
                    names = vtkStringArray()
                    names.InsertNextValue(id)
                    reader = vtkGRASSMultiRasterPolyDataLineReader()
                    reader.SetRasterNames(names)
                    reader.SetDataName("SoilCover")
                    reader.SetLineLengths(lineLengths)
                    reader.Update()
                    
                    dsList.append(reader.GetOutput())

            entry = mapmatrix[0][j]
            map = entry["granule"]
            id = map.get_id()
            
            names = vtkStringArray()
            names.InsertNextValue(id)
            reader = vtkGRASSMultiRasterPolyDataLineReader()
            reader.SetRasterNames(names)
            reader.SetDataName("MeanTemperature")
            reader.SetLineLengths(lineLengths)
            reader.Update()
            
            dsList.append(reader.GetOutput())
            
            join = vtkTAG2EDataSetJoinFilter()
            join.AddInput(clayReader.GetOutput())
            join.AddInput(InitialCarbon.GetOutput())
            
            for ds in dsList:
                join.AddInput(ds)
            join.Update()
            
            dataInputs.append(join.GetOutput())
    
    # Create the module input dictionary
    
    """
    Model input start
      * Temperature STRDS name
      * Precipitation STRDS name
      * Radiation STRDS name
      * SoilCover STRDS name
      * Fertilizer STRDS name
      * Residuals STRDS name
    """
    
    ModelRunNames = None

    if modelTemperature.GetAnswer() and \
        modelPrecipitation.GetAnswer() and \
        modelRadiation.GetAnswer() and \
        modelResiduals.GetAnswer() and \
        modelFertilizer.GetAnswer() and \
        modelSoilCover.GetAnswer():
        ModelRunNames = {}
        
        ModelRunNames["Temperature"] = modelTemperature.GetAnswer()
        ModelRunNames["Precipitation"] = modelPrecipitation.GetAnswer()
        ModelRunNames["Radiation"] = modelRadiation.GetAnswer()
        ModelRunNames["SoilCover"] = modelSoilCover.GetAnswer()
        ModelRunNames["Fertilizer"] = modelFertilizer.GetAnswer()
        ModelRunNames["Residuals"] = modelResiduals.GetAnswer()
        ModelRunNames["ClayContent"] = clayContent.GetAnswer()
            
            
    runType = "monthly"
    if yearly.GetAnswer():
        runType = "yearly"
        
                
    new_ds, res_ds = RothCEquilibriumRun(Inputs=dataInputs, 
                                 ResidualsInput=residualsReader.GetOutput(), 
                                 SoilCarbonInput=soilCarbonReader.GetOutput(), 
                                 Years=int(years.GetAnswer()), 
                                 NumberOfRuns=int(iterations.GetAnswer()),
                                 ax=float(ax.GetAnswer()), cx=float(cx.GetAnswer()), 
                                 ModelRunNames=ModelRunNames, runType=runType)

    # The layer array needs to be added
    new_ds.GetCellData().AddArray(soilCarbonReader.GetOutput().GetCellData().GetArray("Layer"))

# Write the resulting pools
    writer = vtkGRASSMultiRasterPolyDataLineWriter()
    writer.SetRasterMapName(output.GetAnswer())
    writer.SetArrayName("SoilCarbon")
    writer.SetLayer(1)
    writer.SetInput(new_ds)
    writer.Update()
    
    writer = vtkGRASSMultiRasterPolyDataLineWriter()
    writer.SetRasterMapName(poolDPM.GetAnswer())
    writer.SetArrayName("DPM")
    writer.SetLayer(1)
    writer.SetInput(new_ds)
    writer.Update()
    
    writer = vtkGRASSMultiRasterPolyDataLineWriter()
    writer.SetRasterMapName(poolRPM.GetAnswer())
    writer.SetArrayName("RPM")
    writer.SetLayer(1)
    writer.SetInput(new_ds)
    writer.Update()
    
    writer = vtkGRASSMultiRasterPolyDataLineWriter()
    writer.SetRasterMapName(poolHUM.GetAnswer())
    writer.SetArrayName("HUM")
    writer.SetLayer(1)
    writer.SetInput(new_ds)
    writer.Update()
    
    writer = vtkGRASSMultiRasterPolyDataLineWriter()
    writer.SetRasterMapName(poolBIO.GetAnswer())
    writer.SetArrayName("BIO")
    writer.SetLayer(1)
    writer.SetInput(new_ds)
    writer.Update()
    
    writer = vtkGRASSMultiRasterPolyDataLineWriter()
    writer.SetRasterMapName(poolIOM.GetAnswer())
    writer.SetArrayName("IOM")
    writer.SetLayer(1)
    writer.SetInput(new_ds)
    writer.Update()
    
    writer = vtkGRASSMultiRasterPolyDataLineWriter()
    writer.SetRasterMapName(residualsOut.GetAnswer())
    writer.SetArrayName("Residuals")
    writer.SetLayer(1)
    writer.SetInput(res_ds)
    writer.Update()
    
    writer = vtkGRASSMultiRasterPolyDataLineWriter()
    writer.SetRasterMapName(convergence.GetAnswer())
    writer.SetArrayName("Convergence")
    writer.SetLayer(1)
    writer.SetInput(new_ds)
    writer.Update()
    
    writer = vtkGRASSMultiRasterPolyDataLineWriter()
    writer.SetRasterMapName(squaredResiduals.GetAnswer())
    writer.SetArrayName("SquaredResiduals")
    writer.SetLayer(1)
    writer.SetInput(new_ds)
    writer.Update()
################################################################################
################################################################################
################################################################################

if __name__ == "__main__":
    main()
