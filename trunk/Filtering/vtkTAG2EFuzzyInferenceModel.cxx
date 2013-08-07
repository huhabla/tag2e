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
#include <vtkCellData.h>
#include <vtkIntArray.h>
#include <vtkDoubleArray.h>
#include <vtkStringArray.h>
#include <vtkDataSet.h>
#include <vtkInformation.h>
#include <vtkInformationVector.h>
#include <vtkDataSetAttributes.h>
#include <vtkDataSetAlgorithm.h>
#include <vtkObjectFactory.h>
#include "vtkTAG2EFuzzyInferenceModel.h"
#include "vtkTAG2EFuzzyInferenceModelParameter.h"

vtkCxxRevisionMacro ( vtkTAG2EFuzzyInferenceModel, "$Revision: 1.0 $" );
vtkStandardNewMacro ( vtkTAG2EFuzzyInferenceModel );

//----------------------------------------------------------------------------

vtkTAG2EFuzzyInferenceModel::vtkTAG2EFuzzyInferenceModel()
{
  this->SetNumberOfOutputPorts ( 1 );
  this->FuzzyModelParameter = NULL;
  this->InputPorts = vtkIntArray::New();
  this->ArrayNames = vtkStringArray::New();
  this->ModelAssessmentFactor = 1;
  this->ApplicabilityRuleLimit = 2;
  this->CreateDOFArray = 0;
  this->ComputeSigma = 0;
}

//----------------------------------------------------------------------------

vtkTAG2EFuzzyInferenceModel::~vtkTAG2EFuzzyInferenceModel()
{
  this->InputPorts->Delete();
  this->ArrayNames->Delete();
}

//----------------------------------------------------------------------------

int vtkTAG2EFuzzyInferenceModel::FillInputPortInformation (
  int vtkNotUsed ( port ),
  vtkInformation* info )
{
  info->Set ( vtkAlgorithm::INPUT_REQUIRED_DATA_TYPE(), "vtkDataSet" );
  return 1;
}

//----------------------------------------------------------------------------
int vtkTAG2EFuzzyInferenceModel::FillOutputPortInformation (
  int vtkNotUsed ( port ), vtkInformation* info )
{
  // now add our info
  info->Set ( vtkDataObject::DATA_TYPE_NAME(), "vtkDataSet" );
  return 1;
}

//----------------------------------------------------------------------------

void vtkTAG2EFuzzyInferenceModel::SetModelParameter (
  vtkTAG2EAbstractModelParameter* modelParameter )
{
  int i = 0;

  this->Superclass::SetModelParameter ( modelParameter );

  this->ArrayNames->Initialize();
  this->InputPorts->Initialize();

  // Check if the ModelParameter is of correct type
  if ( this->ModelParameter->IsA ( "vtkTAG2EFuzzyInferenceModelParameter" ) )
    {
      this->FuzzyModelParameter =
        static_cast<vtkTAG2EFuzzyInferenceModelParameter *> ( this->ModelParameter );
    }
  else
    {
      vtkErrorMacro (
        << "The ModelParameter is not of type vtkTAG2EFuzzyInferenceModelParameter" );
      this->SetModelParameter ( NULL );
      return;
    }

  // Generate the internal representation
  this->FuzzyModelParameter->GenerateInternalSchemeFromXML();

  FuzzyInferenceScheme &FIS = this->FuzzyModelParameter->GetInternalScheme();

  // Count the input ports and array names
  for ( i = 0; i < this->FuzzyModelParameter->GetNumberOfFactors(); i++ )
    {
      this->InputPorts->InsertValue ( i, FIS.Factors[i].portId );
      this->ArrayNames->InsertValue ( i, FIS.Factors[i].name );
    }

  double *range = this->InputPorts->GetRange();
  // Ports from 0 ... n must be used
  this->SetNumberOfInputPorts ( ( int ) ( range[1] + 1 ) );

  this->Modified();
}

//----------------------------------------------------------------------------

#define MAX_RULE_NUMBER 1024

int vtkTAG2EFuzzyInferenceModel::RequestData (
  vtkInformation * vtkNotUsed ( request ), vtkInformationVector **inputVector,
  vtkInformationVector *outputVector )
{
  int numberOfRules = 0;
  int numberOfFactors = 0;
  int i, j;
  int observationCount = 0;
  int port;
  double dof_values[MAX_RULE_NUMBER];
  double fuzzyInput[MAX_RULE_NUMBER];
  
  // Check for model parameter
  if ( this->ModelParameter == NULL )
    {
      vtkErrorMacro ( "Model parameter not set or invalid." );
      return -1;
    }

  FuzzyInferenceScheme &FIS = this->FuzzyModelParameter->GetInternalScheme();

  // Compute the number of rules and number of factors
  numberOfRules = this->FuzzyModelParameter->GetNumberOfRules();
  numberOfFactors = this->FuzzyModelParameter->GetNumberOfFactors();
  
  if(numberOfRules > MAX_RULE_NUMBER)
  {
      vtkErrorMacro (
          << "Number of rules exceedes limit of " <<  MAX_RULE_NUMBER);
      return -1;
  }
  if(numberOfFactors > MAX_RULE_NUMBER)
  {
      vtkErrorMacro (
          << "Number of factors exceedes limit of " <<  MAX_RULE_NUMBER);
      return -1;
  }
  

  // Create the rule code matrix
  std::vector < std::vector<int>
  > RuleCodeMatrix ( numberOfRules, std::vector<int> ( numberOfFactors ) );
  std::vector<double> DOFVector ( numberOfRules );
  std::vector<double> DOFSumVector ( numberOfRules );

  /* Initialize the degree of fulfillment vectors */
  for ( i = 0; i < numberOfRules; i++ )
    {
      DOFVector[i] = 0;
      DOFSumVector[i] = 0;
    }

  // Compute the rule code matrix entries
  tag2eFIS::ComputeRuleCodeMatrixEntries ( RuleCodeMatrix, numberOfRules, FIS );

  // get the info objects
  vtkInformation *inInfo = inputVector[0]->GetInformationObject ( 0 );
  vtkInformation *outInfo = outputVector->GetInformationObject ( 0 );

  // get the first input and the output
  vtkDataSet *firstInput = vtkDataSet::SafeDownCast (
                             inInfo->Get ( vtkDataObject::DATA_OBJECT() ) );

  vtkDataSet *output = vtkDataSet::SafeDownCast (
                         outInfo->Get ( vtkDataObject::DATA_OBJECT() ) );

  output->DeepCopy ( firstInput );

  // Result array
  vtkDoubleArray *result = vtkDoubleArray::New();
  vtkDoubleArray *dof = NULL;
  vtkDoubleArray *sigma = NULL;

  result->SetNumberOfComponents ( 0 );
  result->SetName ( this->ResultArrayName );
  if ( this->UseCellData )
    result->SetNumberOfTuples ( firstInput->GetNumberOfCells() );
  else
    result->SetNumberOfTuples ( firstInput->GetNumberOfPoints() );
  result->FillComponent ( 0, 0.0 );

  // This is used to store the needed arrays pointer to collect the
  // data for fuzzy computation
  std::vector<vtkDataArray *> Data;

  // Get the arrays for each input port and factor
  for ( i = 0; i < this->InputPorts->GetNumberOfTuples(); i++ )
    {

      port = this->InputPorts->GetValue ( i );
      //cerr << "Processing input port " << port << " at time step " << timeStep << endl;

      // Get the correct input port for the input
      vtkInformation *activeInputInfo = inputVector[port]->GetInformationObject (
                                          0 );

      // Check if the input port was filled with data
      if ( activeInputInfo == NULL )
        {
          vtkErrorMacro (
            << "No dataset information available at input port " << port );
          return -1;
        }

      vtkDataSet *activeInput = vtkDataSet::SafeDownCast (
                                  activeInputInfo->Get ( vtkDataObject::DATA_OBJECT() ) );

      // Check if a dataset is present
      if ( activeInput == NULL )
        {
          vtkErrorMacro ( << "No dataset available at input port " << port );
          return -1;
        }

      // Check if the number of points and cells in the active input are identical with the first input
      if ( firstInput->GetNumberOfPoints() != activeInput->GetNumberOfPoints()
           || firstInput->GetNumberOfCells() != activeInput->GetNumberOfCells() )
        {
          vtkErrorMacro (
            << "The number of points or cells differ between the inputs "
            "at port 0 and port " << port );
          return -1;
        }

      vtkDataSetAttributes *inputData;

      if ( this->UseCellData )
        inputData = activeInput->GetCellData();
      else
        inputData = activeInput->GetPointData();
      // Get the array and

      // Check if the array exists in the current input
      if ( !inputData->HasArray ( this->ArrayNames->GetValue ( i ) ) )
        {
          vtkErrorMacro (
            << "Array " << this->ArrayNames->GetValue ( i ) << " is missing in input. Wrong reference in the model parameter" );
          return -1;
        }

      // Put the array pointer into the vector template
      Data.push_back ( inputData->GetArray ( this->ArrayNames->GetValue ( i ) ) );
    }

  int num;
  if ( this->UseCellData )
    num = firstInput->GetNumberOfCells();
  else
    num = firstInput->GetNumberOfPoints();
  
  if ( this->ComputeSigma == 1 )
      sigma = vtkDoubleArray::New();
  
  if ( this->CreateDOFArray == 1 )
      dof = vtkDoubleArray::New();
  
  if ( dof )
    {
      dof->SetName ( "DOF" );
      dof->SetNumberOfComponents ( numberOfRules );
      dof->SetNumberOfTuples ( num );
      dof->FillComponent ( 0, 0.0 );
    }

  if ( sigma )
    {
      sigma->SetName ( "Sigma" );
      sigma->SetNumberOfComponents ( 1 );
      sigma->SetNumberOfTuples ( num );
      sigma->FillComponent ( 0, 0.0 );
    }

  /* We need to adjust the value range in case of a none-calibration model run */
  for ( i = 0; i < this->FuzzyModelParameter->GetNumberOfFactors(); i++ )
    {

      if ( strcmp ( FIS.Factors[i].name.c_str(), Data[i]->GetName() ) != 0 )
        {
          vtkErrorMacro (
            << "Array names of the inputs do not match the FuzzyModelParamter "
            "names. Unable to adjust data range." );
          return -1;
        }
      double min = FIS.Factors[i].min;
      double max = FIS.Factors[i].max;
      double value = 0.0;

      for ( j = 0; j < num; j++ )
        {
          value = Data[i]->GetTuple1 ( j );
          if ( value != this->NullValue && value < min )
            Data[i]->SetTuple1 ( j, min );
          if ( value != this->NullValue && value > max )
            Data[i]->SetTuple1 ( j, max );
        }
    }

  for ( i = 0; i < num; i++ )
    {
      bool isNull = false;


      for ( j = 0; j < numberOfFactors; j++ )
        {
          Data[j]->GetTuple ( i, &fuzzyInput[j] );

          if ( fuzzyInput[j] == this->NullValue )
            {
              isNull = true;
              break;
            }
        }

      // In case one of the factors is null, we skip the processing
      if ( isNull )
        {
          result->SetValue ( i, this->NullValue );
          continue;
        }

      double val = tag2eFIS::ComputeFISResult ( fuzzyInput, numberOfRules,
                   RuleCodeMatrix, FIS, DOFVector );

      /* Summarize the dof's for punishment function */
      for ( unsigned int k = 0; k < DOFSumVector.size(); k++ )
        {
          DOFSumVector[k] += DOFVector[k];
        }

      if ( sigma )
        {
          double s = 0.0;
          for ( unsigned int k = 0; k < DOFSumVector.size(); k++ )
            {
              s += DOFVector[k] * FIS.Responses.Responses[k].sd;
            }
            sigma->SetValue(i, s);
        }
        if ( dof )
        {
            for ( unsigned int k = 0; k < DOFSumVector.size(); k++ )
            {
                dof_values[k] = DOFVector[k];
            }
            dof->SetTuple(i, dof_values);
        }

      result->SetValue ( i, val );
      observationCount++;
    }

  if ( this->UseCellData )
    {
      output->GetCellData()->AddArray ( result );
      if(sigma)
          output->GetCellData()->AddArray ( sigma );
      if(dof)
          output->GetCellData()->AddArray ( dof );
      output->GetCellData()->SetActiveScalars ( result->GetName() );
    }
  else
    {
        output->GetPointData()->AddArray ( result );
        if(sigma)
            output->GetCellData()->AddArray ( dof );
        if(dof)
            output->GetCellData()->AddArray ( dof );
      output->GetPointData()->SetActiveScalars ( result->GetName() );
    }
  result->Delete();

  /* Compute punishment function */
  double v = observationCount * this->ApplicabilityRuleLimit / 100.0;
  //double v = 0.1 * (double)observationCount/(double)numberOfRules;
  this->ModelAssessmentFactor = 1;

  for ( unsigned int rule = 0; rule < DOFSumVector.size(); rule++ )
    {
      // cout << "Rule " << rule << " DOF sum " << DOFSumVector[rule] << endl;
      double value = 0;
      value = ( v - DOFSumVector[rule] ) / v;
      // cout << "Value " << value << endl;
      /* Continue if fullfilled */
      if ( value < 0 )
        continue;
      /* assign the punishment for the current rule */
      this->ModelAssessmentFactor *= 1 + value;
      // cout << "Model assessment " << this->ModelAssessmentFactor << endl;
    }

  return 1;
}

//----------------------------------------------------------------------------

void vtkTAG2EFuzzyInferenceModel::PrintSelf ( ostream& os, vtkIndent indent )
{
  this->Superclass::PrintSelf ( os, indent );
}
