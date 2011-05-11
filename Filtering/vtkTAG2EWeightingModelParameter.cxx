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

#include <vtkObjectFactory.h>
#include "vtkTAG2EWeightingModelParameter.h"
#include <vtkXMLDataParser.h>
#include "tag2eFIS.h"
#include <sstream>

vtkCxxRevisionMacro(vtkTAG2EWeightingModelParameter, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2EWeightingModelParameter);

//----------------------------------------------------------------------------

vtkTAG2EWeightingModelParameter::vtkTAG2EWeightingModelParameter()
{
  ;
}

//----------------------------------------------------------------------------

vtkTAG2EWeightingModelParameter::~vtkTAG2EWeightingModelParameter()
{
  ;
}

//----------------------------------------------------------------------------

bool vtkTAG2EWeightingModelParameter::GenerateXMLFromInternalScheme()
{
  unsigned int i;

  vtkXMLDataElement *w = vtkXMLDataElement::New();
  w->SetName("Weighting");
  w->SetAttribute("name", this->W.name.c_str());
  w->SetAttribute("xmlns", "http://tag2e.googlecode.com/files/Weighting");
  w->SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance");
  w->SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/Weighting http://tag2e.googlecode.com/files/Weighting.xsd");

  vtkXMLDataElement *weights = vtkXMLDataElement::New();
  weights->SetName("Weights");

  for (i = 0; i < this->W.Weights.size(); i++) {
    WeightingWeight &Weight = this->W.Weights[i];
    vtkXMLDataElement *weight = vtkXMLDataElement::New();
    weight->SetName("Weight");
    weight->SetIntAttribute("active", (int) Weight.active);
    weight->SetIntAttribute("const", (int) Weight.constant);
    weight->SetIntAttribute("id", Weight.id);
    weight->SetDoubleAttribute("max", Weight.max);
    weight->SetDoubleAttribute("min", Weight.min);
    std::ostringstream value;
    value << setprecision(15) << Weight.value;
    weight->SetCharacterData(value.str().c_str(), value.str().size());

    weights->AddNestedElement(weight);

  }

  vtkXMLDataElement *factor = vtkXMLDataElement::New();
  factor->SetName("Factor");
  factor->SetAttribute("name", this->W.Factor.name.c_str());
  
  w->AddNestedElement(factor);
  w->AddNestedElement(weights);

  this->XMLRoot->DeepCopy(w);
  w->Delete();

  return true;
}

//----------------------------------------------------------------------------

bool vtkTAG2EWeightingModelParameter::SetParameter(unsigned int index, double value)
{
  unsigned int count = 0;
  unsigned int i;

  for (i = 0; i < this->W.Weights.size(); i++) {
    WeightingWeight &Weight = this->W.Weights[i];
    if (Weight.constant == false) {
      if (count == index) {

        this->UpdateParameterState(index, Weight.value, value);
        Weight.value = value;
        return true;
      }
      count++;
    }
  }

  return false;
}

//----------------------------------------------------------------------------

bool vtkTAG2EWeightingModelParameter::CreateParameterIndex()
{
  unsigned int i;
  unsigned int count = 0;

  // ATTENTION:
  // The count mechanism of CreateParameterIndex and SetParemter must be identical

  this->ParameterIndex.clear();

  for (i = 0; i < this->W.Weights.size(); i++) {
    WeightingWeight &Weight = this->W.Weights[i];

    if (Weight.constant == false) {

      this->AppendParameterState(count, Weight.value, Weight.min, Weight.max);
      count++;
    }
  }

  return true;
}

//----------------------------------------------------------------------------

bool vtkTAG2EWeightingModelParameter::GenerateInternalSchemeFromXML()
{
  vtkXMLDataElement *root = this->XMLRoot;
  int i;

  // Check for correct name
  if (strncasecmp(root->GetName(), "Weighting", strlen("Weighting")) != 0) {
    vtkErrorMacro("The model parameter does not contain a valid Weighting scheme");
    return false;
  }

  if (root->GetAttribute("name") != NULL) {
    this->W.name = root->GetAttribute("name");
  } else {
    vtkErrorMacro( << "Attribute \"name\" is missing in Weighting element");
    return false;
  }
  
  vtkXMLDataElement *factor = root->FindNestedElementWithName("Factor");
  if (factor != NULL) {

    if (root->GetAttribute("name") != NULL) {
      this->W.Factor.name = factor->GetAttribute("name");
    } else {
      vtkErrorMacro( << "Attribute \"name\" is missing in Factor element");
      return false;
    }
  }

  vtkXMLDataElement *weights = root->FindNestedElementWithName("Weights");
  if(weights != NULL){
      for (i = 0; i < weights->GetNumberOfNestedElements(); i++) {
        vtkXMLDataElement *weight = weights->GetNestedElement(i);
        WeightingWeight Weight;
        this->ParseWeight(weight, Weight);
        this->W.Weights.push_back(Weight);
      }
  }
  
  this->CreateParameterIndex();

  this->SetNumberOfCalibratableParameter(this->ParameterIndex.size());

  return true;
}


//----------------------------------------------------------------------------

bool vtkTAG2EWeightingModelParameter::ParseWeight(vtkXMLDataElement *XMLWeight, WeightingWeight &Weight)
{
  int active;

  ;

  int constant = 0;
  active = 0;

  if (XMLWeight->GetAttribute("const") != NULL) {
    constant = atoi(XMLWeight->GetAttribute("const"));
    if (constant == 0)
      Weight.constant = false;
    else
      Weight.constant = true;
  } else {
    vtkErrorMacro( << "Attribute \"const\" is missing in Weight element");
    return false;
  }

  if (XMLWeight->GetAttribute("active") != NULL) {
    active = atoi(XMLWeight->GetAttribute("active"));
    if (active == 0)
      Weight.active = false;
    else
      Weight.active = true;
  } else {
    vtkErrorMacro( << "Attribute \"active\" is missing in Weight element");
    return false;
  }

  if (XMLWeight->GetAttribute("min") != NULL) {
    Weight.min = atof(XMLWeight->GetAttribute("min"));
  } else {
    vtkErrorMacro( << "Attribute \"min\" is missing in Weight element");
    return false;
  }

  if (XMLWeight->GetAttribute("id") != NULL) {
    Weight.id = atoi(XMLWeight->GetAttribute("id"));
  } else {
    vtkErrorMacro( << "Attribute \"id\" is missing in Weight element");
    return false;
  }

  if (XMLWeight->GetAttribute("max") != NULL) {
    Weight.max = atof(XMLWeight->GetAttribute("max"));
  } else {
    vtkErrorMacro( << "Attribute \"max\" is missing in Weight element");
    return false;
  }

  if (XMLWeight->GetCharacterData() != NULL) {
    Weight.value = atof(XMLWeight->GetCharacterData());
  } else {
    vtkErrorMacro( << "Attribute \"sd\" is missing in Weight element");
    return false;
  }

    cout << "Added Weight const " << Weight.constant
      << " value " << Weight.value << " min " << Weight.min
      << " max " << Weight.max << " active " << Weight.active 
      << " id " << Weight.id << endl;

  return true;
}
