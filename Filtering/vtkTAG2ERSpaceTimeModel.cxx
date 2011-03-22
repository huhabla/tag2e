/*
 *  Toolkit for Agriculture Greenhouse Gas Emission Estimation TAG2E
 *
 * Authors: Soeren Gebbert, soeren.gebbert@vti.bund.de
 *          Rene Dechow, rene.dechow@vti.bund.de
 *
 * Copyright:
 *
 * Johann Heinrich von Thünen-Institut
 * Institut für Agrarrelevante Klimaforschung
 *
 * Phone: +49 (0)531 596 2601
 *
 * Fax:+49 (0)531 596 2699
 *
 * Mail: ak@vti.bund.de
 *
 * Bundesallee 50
 * 38116 Braunschweig
 * Germany
 *
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; version 2 of the License.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 */
#include <vtkCommand.h>
#include <vtkCompositeDataPipeline.h>
#include <vtkDataSet.h>
#include <vtkPointData.h>
#include <vtkIntArray.h>
#include <vtkDoubleArray.h>
#include <vtkStringArray.h>
#include <vtkTemporalDataSet.h>
#include <vtkInformation.h>
#include <vtkInformationVector.h>
#include <vtkRInterfaceSpaceTime.h>
#include <vtkDataSetAlgorithm.h>
#include <vtkObjectFactory.h>
#include <vtkDataArrayCollection.h>
#include "vtkTAG2ERSpaceTimeModel.h"
#include "vtkTAG2EModelMonteCarloVariationAnalyser.h"

vtkCxxRevisionMacro(vtkTAG2ERSpaceTimeModel, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2ERSpaceTimeModel);

//----------------------------------------------------------------------------

vtkTAG2ERSpaceTimeModel::vtkTAG2ERSpaceTimeModel()
{
    this->InputArrayNames = vtkStringArray::New();
    this->OutputArrayNames = vtkStringArray::New();
    this->RInterface = vtkRInterfaceSpaceTime::New();
    this->SetNumberOfOutputPorts(1);

    this->RString = NULL;
    this->RVariable = NULL;
    this->StartDate = NULL;
    this->Proj4String = NULL;

    this->SetStartDate("2007-12-25");
}

//----------------------------------------------------------------------------

vtkTAG2ERSpaceTimeModel::~vtkTAG2ERSpaceTimeModel()
{
    this->InputArrayNames->Delete();
    this->OutputArrayNames->Delete();
    this->RInterface->Delete();

    if(this->RString)
        delete [] this->RString;
    if(this->RVariable)
        delete [] this->RVariable;
    if(this->StartDate)
        delete [] this->StartDate;
}

//----------------------------------------------------------------------------

int
vtkTAG2ERSpaceTimeModel::FillInputPortInformation(
                                                  int vtkNotUsed(port),
                                                  vtkInformation* info)
{
    info->Set(vtkAlgorithm::INPUT_REQUIRED_DATA_TYPE(), "vtkTemporalDataSet");
    return 1;
}


//----------------------------------------------------------------------------

int
vtkTAG2ERSpaceTimeModel::RequestUpdateExtent(
                                             vtkInformation *vtkNotUsed(request),
                                             vtkInformationVector **inputVector,
                                             vtkInformationVector *outputVector)
{
    int numInputs = this->GetNumberOfInputPorts();
    vtkInformation *outInfo = outputVector->GetInformationObject(0);

    // Remove any existing output UPDATE_TIME_STEPS, beacuse we will set them from
    // the first input
    if (outInfo->Has(vtkStreamingDemandDrivenPipeline::UPDATE_TIME_STEPS()))
        outInfo->Remove(vtkStreamingDemandDrivenPipeline::UPDATE_TIME_STEPS());

    if (!outInfo->Has(vtkStreamingDemandDrivenPipeline::UPDATE_TIME_STEPS()))
    {
        int i;
        double *timeSteps = inputVector[0]->GetInformationObject(0)->Get(vtkStreamingDemandDrivenPipeline::TIME_STEPS());
        int numTimeSteps = inputVector[0]->GetInformationObject(0)->Length(vtkStreamingDemandDrivenPipeline::TIME_STEPS());

        // We request for each input the same number of update timesteps as for the first input
        for (i = 1; i < numInputs; i++)
        {
            inputVector[i]->GetInformationObject(0)->Set(vtkStreamingDemandDrivenPipeline::UPDATE_TIME_STEPS(), timeSteps, numTimeSteps);
        }

        outInfo->Set(vtkStreamingDemandDrivenPipeline::UPDATE_TIME_STEPS(), timeSteps, numTimeSteps);
    }

    return 1;
}



//----------------------------------------------------------------------------

int
vtkTAG2ERSpaceTimeModel::RequestData(
                                     vtkInformation * vtkNotUsed(request),
                                     vtkInformationVector **inputVector,
                                     vtkInformationVector *outputVector)
{
    unsigned int timeStep, array, i;
    vtkDoubleArray *timeSteps = vtkDoubleArray::New();
    vtkDataArrayCollection *collection = vtkDataArrayCollection::New();

    // get the info objects
    vtkInformation *inInfo = inputVector[0]->GetInformationObject(0);
    vtkInformation *outInfo = outputVector->GetInformationObject(0);

    // Check for model parameter
    if (this->ModelParameter == NULL)
    {
        vtkErrorMacro("Model parameter not set or invalid.");
        return -1;
    }

    // Parse the XML content
    if(this->BuildArrays() == false)
      return -1;

    // get the first input and ouptut
    vtkTemporalDataSet *Input = vtkTemporalDataSet::SafeDownCast(
                        inInfo->Get(vtkDataObject::DATA_OBJECT()));

    vtkTemporalDataSet *Output = vtkTemporalDataSet::SafeDownCast(
                        outInfo->Get(vtkDataObject::DATA_OBJECT()));

    Output->SetNumberOfTimeSteps(Input->GetNumberOfTimeSteps());

    timeSteps->SetName("time");
    timeSteps->SetNumberOfValues(Input->GetNumberOfTimeSteps());

    double *timeValues = inputVector[0]->GetInformationObject(0)->Get(vtkStreamingDemandDrivenPipeline::TIME_STEPS());

    // Check if the input point data arrays exists
    for (timeStep = 0; timeStep < Input->GetNumberOfTimeSteps(); timeStep++) {
        vtkDataSet *InputDataSet = vtkDataSet::SafeDownCast(Input->GetTimeStep(timeStep));
        vtkDataSetAttributes *data = InputDataSet->GetPointData();

        double time = timeValues[timeStep];
        //cout << "Attach time " << time << endl;
        timeSteps->SetValue(timeStep, time);

        for(array = 0; array < this->InputArrayNames->GetNumberOfValues(); array++)
        {
            vtkStdString name = this->InputArrayNames->GetValue(array);
            if(!data->HasArray(name.c_str())) {
                vtkErrorMacro(<<"Requested input array " << name.c_str() <<
                                " not found in input data set at time step " << timeStep);
                return -1;
            }
        }
    }

    // Set the projection if known
    if(this->Proj4String)
        this->RInterface->SetProj4String(this->Proj4String);

    // Create the R STFDF object
    this->RInterface->AssignVTKTemporalDataSetToRSTFDF(Input, this->RVariable, timeSteps, this->StartDate);

    // Run the R script
    this->RInterface->EvalRscript(this->RString, true);


    // Copy the output arrays from R
    // The arrays contain the results forall time steps
    for(array = 0; array < this->OutputArrayNames->GetNumberOfValues(); array++) {
        vtkStdString name = this->OutputArrayNames->GetValue(array);
        // Get the array from the R instance
        vtkDataArray *a = this->RInterface->AssignRVariableToVTKDataArray(name);
        if(a) {
            a->SetName(name);
            collection->AddItem(a);
        } else {
            vtkErrorMacro(<< "Unable to attach R variable " << name << " as vtkDataArray to the output");
            return -1;
        }
    }

    // Attach the content of the result arrays to the temporal output data set
    int count = 0;
    for (timeStep = 0; timeStep < Output->GetNumberOfTimeSteps(); timeStep++) {
        vtkDataSet *InputDataSet = vtkDataSet::SafeDownCast(Input->GetTimeStep(timeStep));
        vtkDataSet *OutputDataSet = InputDataSet->NewInstance();
        OutputDataSet->CopyStructure(InputDataSet);

        // For each output array
        for(array = 0; array < (unsigned int)collection->GetNumberOfItems(); array++) {
            vtkDataArray *resultArray  = collection->GetItem(array);
            vtkDataArray *outArray = resultArray->NewInstance();
            outArray->SetName(resultArray->GetName());
            outArray->SetNumberOfComponents(resultArray->GetNumberOfComponents());

            // Extract the point data tuple for each time step
            for(i = 0; i < OutputDataSet->GetNumberOfPoints(); i++) {
                outArray->InsertNextTuple(resultArray->GetTuple(count + i));
            }

            // Add the array to the active data set
            OutputDataSet->GetPointData()->AddArray(outArray);

            outArray->Delete();
        }

        // Increase the counter
        count += OutputDataSet->GetNumberOfPoints();

        // Attach a time step data set with result data
        Output->SetTimeStep(timeStep, OutputDataSet);
        
        OutputDataSet->Delete();
    }

    collection->Delete();

    return 1;
}

//----------------------------------------------------------------------------

bool
vtkTAG2ERSpaceTimeModel::BuildArrays()
{
    int i = 0;
    this->InputArrayNames->Initialize();
    this->OutputArrayNames->Initialize();

    vtkXMLDataElement *root = this->ModelParameter->GetXMLRoot();

    // Check for correct
    
    if (strncasecmp(root->GetName(), "RSpaceTimeModelDescription", strlen("RSpaceTimeModelDescription")) != 0)
    {
        vtkErrorMacro("The model parameter does not contain a valid R space time scheme");
        return false;
    }

    if (root->GetAttribute("name") != NULL)
    {
        this->SetRVariable(root->GetAttribute("name"));
    }
    else
    {
        vtkErrorMacro( << "Attribute \"name\" is missing in RSpaceTimeModelScheme element");
        return false;
    }

    // Fetch the R script value.
    vtkXMLDataElement *rscript = root->FindNestedElementWithName("RScript");

    if (rscript == NULL)
    {
        vtkErrorMacro( << "Element \"RScript\" is missing");
        return false;
    }
    else
    {
      cout << rscript->GetCharacterData() << endl;
        this->SetRString(rscript->GetCharacterData());
    }

    vtkXMLDataElement *inputs = root->FindNestedElementWithName("InputArrays");

    if (inputs != NULL)
    {
        for (i = 0; i < inputs->GetNumberOfNestedElements(); i++)
        {
            vtkXMLDataElement *element = inputs->GetNestedElement(i);
            // Check for Coefficient elements
            if (strncasecmp(element->GetName(), "ArrayName", strlen("ArrayName")) == 0)
            {
                this->InputArrayNames->InsertNextValue(element->GetCharacterData());
                //cout << "Input array " << element->GetCharacterData() << endl;
            }
        }
    }

    vtkXMLDataElement *outputs = root->FindNestedElementWithName("OutputArrays");

    if (outputs != NULL)
    {
        for (i = 0; i < outputs->GetNumberOfNestedElements(); i++)
        {
            vtkXMLDataElement *element = outputs->GetNestedElement(i);
            // Check for Coefficient elements
            if (strncasecmp(element->GetName(), "ArrayName", strlen("ArrayName")) == 0)
            {
                this->OutputArrayNames->InsertNextValue(element->GetCharacterData());
                //cout << "Output array " << element->GetCharacterData() << endl;
            }
        }
    }

    return true;
}

//----------------------------------------------------------------------------

void
vtkTAG2ERSpaceTimeModel::PrintSelf(ostream& os, vtkIndent indent)
{
    this->Superclass::PrintSelf(os, indent);
    os << indent << "RScript: " << this->RString << endl;
    os << indent << "RVariable:" << this->RVariable << endl;
    os << indent << "Input array names:" << endl;
    this->InputArrayNames->PrintSelf(os, indent.GetNextIndent());
    os << indent << "Output array names:" << endl;
    this->OutputArrayNames->PrintSelf(os, indent.GetNextIndent());
}