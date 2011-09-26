#include the VTK and vtkGRASSBridge Python libraries
from vtk import *
from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeIOPython import *
from libvtkGRASSBridgeCommonPython import *
from libvtkGRASSBridgeTemporalPython import *

inputName = "precipitation_autumn_prev3gwa3fert3.xml"
outputName = "precipitation_autumn_prev3gwa3fert3.vti"

# Read the XML fuzzy inference parameter
reader = vtkXMLDataParser()
reader.SetFileName(inputName)
reader.Parse()

xmlRoot = vtkXMLDataElement()
xmlRoot.DeepCopy(reader.GetRootElement())

# Set up the parameter and the model
parameter = vtkTAG2EFuzzyInferenceModelParameter()
parameter.SetXMLRepresentation(xmlRoot)

# Set up the fuzzy inference parameter to image data filter
fim = vtkTAG2EFuzzyInferenceModelParameterToImageData()
fim.SetFuzzyModelParameter(parameter)
fim.SetXAxisExtent(50)
fim.SetYAxisExtent(50)
fim.SetZAxisExtent(50)
fim.Update()

# Write the output
iwriter = vtkXMLImageDataWriter()
iwriter.SetFileName(outputName)
iwriter.SetInput(fim.GetOutput())
iwriter.Write()