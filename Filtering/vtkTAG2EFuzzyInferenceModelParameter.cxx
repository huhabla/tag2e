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
#include "vtkTAG2EFuzzyInferenceModelParameter.h"
#include <vtkXMLDataParser.h>
#include "tag2eFIS.h"
#include <sstream>

vtkCxxRevisionMacro(vtkTAG2EFuzzyInferenceModelParameter, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2EFuzzyInferenceModelParameter);

//----------------------------------------------------------------------------

vtkTAG2EFuzzyInferenceModelParameter::vtkTAG2EFuzzyInferenceModelParameter()
{
  this->NumberOfFactors = 0;
  this->NumberOfRules = 0;
}

//----------------------------------------------------------------------------

vtkTAG2EFuzzyInferenceModelParameter::~vtkTAG2EFuzzyInferenceModelParameter()
{
  ;
}

//----------------------------------------------------------------------------

bool vtkTAG2EFuzzyInferenceModelParameter::GenerateXMLFromInternalScheme()
{
  unsigned int i, j;

  vtkXMLDataElement *fis = vtkXMLDataElement::New();
  fis->SetName("FuzzyInferenceScheme");
  fis->SetAttribute("name", this->FIS.name.c_str());
  fis->SetAttribute("xmlns",
      "http://tag2e.googlecode.com/files/FuzzyInferenceScheme");
  fis->SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance");
  fis->SetAttribute("xsi:schemaLocation",
      "http://tag2e.googlecode.com/files/FuzzyInferenceScheme http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme.xsd");

  for (i = 0; i < this->FIS.Factors.size(); i++)
    {
    FuzzyFactor &Factor = this->FIS.Factors[i];
    vtkXMLDataElement *factor = vtkXMLDataElement::New();

    std::ostringstream factmin;
    std::ostringstream factmax;
    factmin << setprecision(20) << Factor.min;
    factmax << setprecision(20) << Factor.max;
    factor->SetName("Factor");
    factor->SetAttribute("name", Factor.name.c_str());
    factor->SetAttribute("min", factmin.str().c_str());
    factor->SetAttribute("max", factmax.str().c_str());
    factor->SetIntAttribute("portId", Factor.portId);

    for (j = 0; j < Factor.Sets.size(); j++)
      {
      FuzzySet &Set = Factor.Sets[j];
      vtkXMLDataElement *set = vtkXMLDataElement::New();

      set->SetName("Set");
      set->SetIntAttribute("const", (int) Set.constant);

      if (Set.position == FUZZY_SET_POISITION_LEFT)
        set->SetAttribute("position", "left");
      if (Set.position == FUZZY_SET_POISITION_RIGHT)
        set->SetAttribute("position", "right");
      if (Set.position == FUZZY_SET_POISITION_INT)
        set->SetAttribute("position", "intermediate");

      set->SetIntAttribute("priority", (int) Set.priority);

      if (Set.type == FUZZY_SET_TYPE_TRIANGULAR)
        set->SetAttribute("type", "Triangular");
      if (Set.type == FUZZY_SET_TYPE_CRISP)
        set->SetAttribute("type", "Crisp");
      if (Set.type == FUZZY_SET_TYPE_BELL_SHAPE)
        set->SetAttribute("type", "BellShape");

      if (Set.type == FUZZY_SET_TYPE_TRIANGULAR)
        {
        vtkXMLDataElement *triangular = vtkXMLDataElement::New();

        triangular->SetName("Triangular");
        std::ostringstream value1;
        std::ostringstream value2;
        std::ostringstream value3;
        value1 << setprecision(20) << Set.Triangular.center;
        triangular->SetAttribute("center", value1.str().c_str());
        value2 << setprecision(20) << Set.Triangular.left;
        triangular->SetAttribute("left", value2.str().c_str());
        value3 << setprecision(20) << Set.Triangular.right;
        triangular->SetAttribute("right", value3.str().c_str());

        set->AddNestedElement(triangular);
        triangular->Delete();
        }
      if (Set.type == FUZZY_SET_TYPE_CRISP)
        {
        vtkXMLDataElement *crisp = vtkXMLDataElement::New();

        crisp->SetName("Crisp");
        std::ostringstream value1;
        std::ostringstream value2;
        value1 << setprecision(20) << Set.Crisp.right;
        crisp->SetAttribute("right", value1.str().c_str());
        value2 << setprecision(20) << Set.Crisp.left;
        crisp->SetAttribute("left", value2.str().c_str());

        set->AddNestedElement(crisp);
        crisp->Delete();
        }
      if (Set.type == FUZZY_SET_TYPE_BELL_SHAPE)
        {
        vtkXMLDataElement *bellshape = vtkXMLDataElement::New();

        bellshape->SetName("BellShape");
        std::ostringstream value1;
        std::ostringstream value2;
        std::ostringstream value3;
        value1 << setprecision(20) << Set.BellShape.center;
        bellshape->SetAttribute("center", value1.str().c_str());
        value2 << setprecision(20) << Set.BellShape.sdLeft;
        bellshape->SetAttribute("sdLeft", value2.str().c_str());
        value3 << setprecision(20) << Set.BellShape.sdRight;
        bellshape->SetAttribute("sdRight", value3.str().c_str());

        set->AddNestedElement(bellshape);
        bellshape->Delete();
        }
      factor->AddNestedElement(set);
      set->Delete();
      }
    fis->AddNestedElement(factor);
    factor->Delete();
    }

  vtkXMLDataElement *responses = vtkXMLDataElement::New();

  std::ostringstream respmin;
  std::ostringstream respmax;
  respmin << setprecision(20) << this->FIS.Responses.min;
  respmax << setprecision(20) << this->FIS.Responses.max;
  responses->SetName("Responses");
  responses->SetAttribute("min", respmin.str().c_str());
  responses->SetAttribute("max", respmax.str().c_str());

  for (i = 0; i < this->FIS.Responses.Responses.size(); i++)
    {
    FuzzyResponse &Response = this->FIS.Responses.Responses[i];
    vtkXMLDataElement *response = vtkXMLDataElement::New();

    response->SetName("Response");
    response->SetIntAttribute("const", (int) Response.constant);
    response->SetDoubleAttribute("sd", Response.sd);
    std::ostringstream value;
    value << setprecision(20) << Response.value;
    response->SetCharacterData(value.str().c_str(), value.str().size());

    responses->AddNestedElement(response);
    response->Delete();
    }

  fis->AddNestedElement(responses);
  responses->Delete();

  this->XMLRoot->DeepCopy(fis);
  fis->Delete();

  return true;
}

//----------------------------------------------------------------------------

bool vtkTAG2EFuzzyInferenceModelParameter::SetParameter(unsigned int index,
    double value)
{
  unsigned int i, j;
  unsigned int count = 0;

  for (i = 0; i < this->FIS.Factors.size(); i++)
    {
    FuzzyFactor &Factor = this->FIS.Factors[i];

    for (j = 0; j < Factor.Sets.size(); j++)
      {
      FuzzySet &Set = Factor.Sets[j];

      // Const values are not counted
      if (Set.constant == false)
        {

        if (Set.type == FUZZY_SET_TYPE_TRIANGULAR)
          {
          if (index == count)
            {
            this->UpdateParameterState(index, Set.Triangular.center, value);
            // Assign the value
            Set.Triangular.center = value;

            // This is the distance between the old and new center
            double dx = (value - this->ParameterValue);

            // We need to change the size of the left slope of the right neighbouring triangle
            // and the right slope of the current triangle 
            // The size of booth triangle must be identical
            if (Set.position == FUZZY_SET_POISITION_LEFT
                || Set.position == FUZZY_SET_POISITION_INT)
              {
              Factor.Sets[j + 1].Triangular.left -= dx;
              Set.Triangular.right -= dx;
              }
            // We need to change the size of the right slope of the left neighbouring triangle
            // and the left slope of the current triangle 
            // The size of booth triangle must be identical
            if (Set.position == FUZZY_SET_POISITION_RIGHT
                || Set.position == FUZZY_SET_POISITION_INT)
              {
              Factor.Sets[j - 1].Triangular.right += dx;
              Set.Triangular.left += dx;
              }
            // Check for correct fuzzy factor and fuzzy sets
            return tag2eFIS::CheckFuzzyFactor(Factor);
            }
          count++;
          }
        if (Set.type == FUZZY_SET_TYPE_CRISP)
          {
          if (index == count)
            {
            this->UpdateParameterState(index, Set.Crisp.left, value);
            Set.Crisp.left = value;
            return tag2eFIS::CheckFuzzyFactor(Factor);
            }
          count++;
          if (index == count)
            {
            this->UpdateParameterState(index, Set.Crisp.right, value);
            Set.Crisp.right = value;
            return tag2eFIS::CheckFuzzyFactor(Factor);
            }
          count++;
          }
        if (Set.type == FUZZY_SET_TYPE_BELL_SHAPE)
          {
          if (index == count)
            {
            this->UpdateParameterState(index, Set.BellShape.center, value);
            Set.BellShape.center = value;
            return tag2eFIS::CheckFuzzyFactor(Factor);
            }
          count++;
          }
        }
      }
    }

  for (i = 0; i < this->FIS.Responses.Responses.size(); i++)
    {
    FuzzyResponse &Response = this->FIS.Responses.Responses[i];
    if (index == count && Response.constant == false)
      {
      this->UpdateParameterState(index, Response.value, value);
      Response.value = value;
      return true;
      }
    count++;
    }

  return false;
}

//----------------------------------------------------------------------------

bool vtkTAG2EFuzzyInferenceModelParameter::CreateParameterIndex()
{
  unsigned int i, j;
  unsigned int count = 0;

  // ATTENTION:
  // The count mechanism of CreateParameterIndex and SetParemter must be identical

  this->ParameterIndex.clear();

  // We start to count the fuzzy sets, then the responses and at last the weight

  for (i = 0; i < this->FIS.Factors.size(); i++)
    {
    FuzzyFactor &Factor = this->FIS.Factors[i];

    for (j = 0; j < Factor.Sets.size(); j++)
      {
      FuzzySet &Set = Factor.Sets[j];
      // Count only non-constant fuzzy sets
      if (Set.constant == false)
        {

        if (Set.type == FUZZY_SET_TYPE_TRIANGULAR)
          {
          this->AppendParameterState(count, Set.Triangular.center, Factor.min,
              Factor.max);
          count++;
          }
        if (Set.type == FUZZY_SET_TYPE_CRISP)
          {
          this->AppendParameterState(count, Set.Crisp.left, Factor.min,
              Factor.max);
          count++;
          this->AppendParameterState(count, Set.Crisp.right, Factor.min,
              Factor.max);
          count++;
          }
        if (Set.type == FUZZY_SET_TYPE_BELL_SHAPE)
          {
          this->AppendParameterState(count, Set.BellShape.center, Factor.min,
              Factor.max);
          count++;
          }
        }
      }
    }

  for (i = 0; i < this->FIS.Responses.Responses.size(); i++)
    {
    FuzzyResponse &Response = this->FIS.Responses.Responses[i];
    if (Response.constant == false)
      {
      this->AppendParameterState(count, Response.value, this->FIS.Responses.min,
          this->FIS.Responses.max);
      }
    count++;
    }

  return true;
}

//----------------------------------------------------------------------------

bool vtkTAG2EFuzzyInferenceModelParameter::GenerateInternalSchemeFromXML()
{
  vtkXMLDataElement *root = this->XMLRoot;
  unsigned int i;

  // Check for correct name
  if (strncasecmp(root->GetName(), "FuzzyInferenceScheme",
      strlen("FuzzyInferenceScheme")) != 0)
    {
    vtkErrorMacro(
        "The model parameter does not contain a valid fuzzy inference WFIS");
    return false;
    }

  if (root->GetAttribute("name") != NULL)
    {
    this->FIS.name = root->GetAttribute("name");
    } else
    {
    vtkErrorMacro(
        << "Attribute \"name\" is missing in WeightedFuzzyInferenceScheme element");
    return false;
    }

  if (!this->ParseFactors(root))
    return false;

  vtkXMLDataElement *Responses = root->FindNestedElementWithName("Responses");
  if (Responses != NULL)
    this->ParseResponses(Responses);

  // Compute the number of rules and number of factors
  this->NumberOfRules = FIS.Factors[0].Sets.size();
  this->NumberOfFactors = FIS.Factors.size();

  for (i = 0; i < this->NumberOfFactors; i++)
    {
    FuzzyFactor &Factor = FIS.Factors[i];

    if (i > 0)
      this->NumberOfRules *= Factor.Sets.size();
    }

  //  cout << "Number of Rules " << this->NumberOfRules << endl;
  //  cout << "Number of Factors " << this->NumberOfFactors << endl;

  // cout << this->FIS.name << endl;

  this->CreateParameterIndex();

  this->SetNumberOfCalibratableParameter(this->ParameterIndex.size());

  return true;
}

//----------------------------------------------------------------------------

bool vtkTAG2EFuzzyInferenceModelParameter::ParseFactors(
    vtkXMLDataElement *XMLFIS)
{
  int i;

  this->FIS.Factors.clear();

  for (i = 0; i < XMLFIS->GetNumberOfNestedElements(); i++)
    {
    vtkXMLDataElement *XMLFactor = XMLFIS->GetNestedElement(i);

    if (strncasecmp(XMLFactor->GetName(), "Factor", strlen("Factor")) != 0)
      {
      continue;
      }

    FuzzyFactor Factor;

    if (XMLFactor->GetAttribute("name") != NULL)
      {
      Factor.name = XMLFactor->GetAttribute("name");
      } else
      {
      vtkErrorMacro(
          << "Attribute \"name\" is missing in Factor element: " << i);
      return false;
      }

    if (XMLFactor->GetAttribute("portId") != NULL)
      {
      Factor.portId = atoi(XMLFactor->GetAttribute("portId"));
      } else
      {
      vtkErrorMacro(
          << "Attribute \"portId\" is missing in Factor element: " << i);
      return false;
      }

    if (XMLFactor->GetAttribute("min") != NULL)
      {
      Factor.min = atof(XMLFactor->GetAttribute("min"));
      } else
      {
      vtkErrorMacro(
          << "Attribute \"min\" is missing in Factor element: " << i);
      return false;
      }

    if (XMLFactor->GetAttribute("max") != NULL)
      {
      Factor.max = atof(XMLFactor->GetAttribute("max"));
      } else
      {
      vtkErrorMacro(
          << "Attribute \"max\" is missing in Factor element: " << i);
      return false;
      }

    this->ParseFuzzySets(Factor, XMLFactor);

    //    cout << "Add Factor " << Factor.name << " with portId " << Factor.portId
    //      << " min  " << Factor.min << " max " << Factor.max << endl;

    this->FIS.Factors.push_back(Factor);

    if (tag2eFIS::CheckFuzzyFactor(Factor) != true)
      {
      vtkErrorMacro(
          << "Factor " << Factor.name.c_str() << " has incorrect fuzzy sets");
      return false;
      }
    }

  return true;
}

//----------------------------------------------------------------------------

bool vtkTAG2EFuzzyInferenceModelParameter::ParseFuzzySets(FuzzyFactor &Factor,
    vtkXMLDataElement *XMLFactor)
{

  int i;

  Factor.Sets.clear();

  for (i = 0; i < XMLFactor->GetNumberOfNestedElements(); i++)
    {
    vtkXMLDataElement *XMLFuzzySet = XMLFactor->GetNestedElement(i);

    FuzzySet Set;

    if (XMLFuzzySet->GetAttribute("type") != NULL)
      {
      const char *type = XMLFuzzySet->GetAttribute("type");
      if (strncasecmp(type, "Triangular", strlen(type)) == 0)
        Set.type = FUZZY_SET_TYPE_TRIANGULAR;
      if (strncasecmp(type, "Crisp", strlen(type)) == 0)
        Set.type = FUZZY_SET_TYPE_CRISP;
      if (strncasecmp(type, "BellShape", strlen(type)) == 0)
        Set.type = FUZZY_SET_TYPE_BELL_SHAPE;
      } else
      {
      vtkErrorMacro(
          << "Attribute \"type\" is missing in FuzzySet element: " << i);
      return false;
      }

    if (XMLFuzzySet->GetAttribute("priority") != NULL)
      {
      Set.priority = atoi(XMLFuzzySet->GetAttribute("priority"));
      } else
      {
      vtkErrorMacro(
          << "Attribute \"priority\" is missing in FuzzySet element: " << i);
      return false;
      }

    if (XMLFuzzySet->GetAttribute("const") != NULL)
      {
      int val = atoi(XMLFuzzySet->GetAttribute("const"));
      if (val == 0)
        Set.constant = false;
      else
        Set.constant = true;
      } else
      {
      vtkErrorMacro(
          << "Attribute \"const\" is missing in FuzzySet element: " << i);
      return false;
      }

    if (XMLFuzzySet->GetAttribute("position") != NULL)
      {
      const char *type = XMLFuzzySet->GetAttribute("position");
      if (strncasecmp(type, "left", strlen(type)) == 0)
        Set.position = FUZZY_SET_POISITION_LEFT;
      if (strncasecmp(type, "intermediate", strlen(type)) == 0)
        Set.position = FUZZY_SET_POISITION_INT;
      if (strncasecmp(type, "right", strlen(type)) == 0)
        Set.position = FUZZY_SET_POISITION_RIGHT;
      } else
      {
      vtkErrorMacro(
          << "Attribute \"position\" is missing in FuzzySet element: " << i);
      return false;
      }

    // Now fetch the Fuzzy shapes

    if (Set.type == FUZZY_SET_TYPE_TRIANGULAR)
      {
      vtkXMLDataElement *Triangular = XMLFuzzySet->FindNestedElementWithName(
          "Triangular");

      if (Triangular != NULL)
        {
        if (Triangular->GetAttribute("left") != NULL)
          {
          Set.Triangular.left = atof(Triangular->GetAttribute("left"));
          } else
          {
          vtkErrorMacro(
              << "Attribute \"left\" is missing in Triangular element: " << i);
          return false;
          }
        if (Triangular->GetAttribute("right") != NULL)
          {
          Set.Triangular.right = atof(Triangular->GetAttribute("right"));
          } else
          {
          vtkErrorMacro(
              << "Attribute \"right\" is missing in Triangular element: " << i);
          return false;
          }
        if (Triangular->GetAttribute("center") != NULL)
          {
          Set.Triangular.center = atof(Triangular->GetAttribute("center"));
          } else
          {
          vtkErrorMacro(
              << "Attribute \"center\" is missing in Triangular element: " << i);
          return false;
          }
        } else
        {
        vtkErrorMacro(
            << "Element \"Triangular\" is missing in FuzzySet element: " << i);
        return false;
        }

      //      cout << "Added Trinagular center " << Set.Triangular.center << " left "
      //        << Set.Triangular.left << " right " << Set.Triangular.right << endl;
      }

    if (Set.type == FUZZY_SET_TYPE_CRISP)
      {
      vtkXMLDataElement *Crisp = XMLFuzzySet->FindNestedElementWithName(
          "Crisp");

      if (Crisp != NULL)
        {
        if (Crisp->GetAttribute("left") != NULL)
          {
          Set.Crisp.left = atof(Crisp->GetAttribute("left"));
          } else
          {
          vtkErrorMacro(
              << "Attribute \"left\" is missing in Crisp element: " << i);
          return false;
          }
        if (Crisp->GetAttribute("right") != NULL)
          {
          Set.Crisp.right = atof(Crisp->GetAttribute("right"));
          } else
          {
          vtkErrorMacro(
              << "Attribute \"right\" is missing in Crisp element: " << i);
          return false;
          }
        } else
        {
        vtkErrorMacro(
            << "Element \"Crisp\" is missing in FuzzySet element: " << i);
        return false;
        }

      //      cout << "Added Crispt left " << Set.Crisp.left << " right " << Set.Crisp.right << endl;
      }

    if (Set.type == FUZZY_SET_TYPE_BELL_SHAPE)
      {
      vtkXMLDataElement *BellShape = XMLFuzzySet->FindNestedElementWithName(
          "BellShape");

      if (BellShape != NULL)
        {
        if (BellShape->GetAttribute("sdLeft") != NULL)
          {
          Set.BellShape.sdLeft = atof(BellShape->GetAttribute("sdLeft"));
          } else
          {
          vtkErrorMacro(
              << "Attribute \"sdLeft\" is missing in BellShape element: " << i);
          return false;
          }
        if (BellShape->GetAttribute("sdRight") != NULL)
          {
          Set.BellShape.sdRight = atof(BellShape->GetAttribute("sdRight"));
          } else
          {
          vtkErrorMacro(
              << "Attribute \"sdRight\" is missing in BellShape element: " << i);
          return false;
          }
        if (BellShape->GetAttribute("center") != NULL)
          {
          Set.BellShape.center = atof(BellShape->GetAttribute("center"));
          } else
          {
          vtkErrorMacro(
              << "Attribute \"center\" is missing in BellShape element: " << i);
          return false;
          }
        } else
        {
        vtkErrorMacro(
            << "Element \"BellShape\" is missing in FuzzySet element: " << i);
        return false;
        }

      //      cout << "Added BellShape center " << Set.Triangular.center << " left "
      //        << Set.Triangular.left << " right " << Set.Triangular.right << endl;
      }

    //    cout << "Add FuzzySet " << Set.type << " with priority " << Set.priority
    //      << " constant  " << Set.constant << " position " << Set.position << endl;

    // Add the FuzzySet to the Factor
    Factor.Sets.push_back(Set);
    }

  return true;
}

//----------------------------------------------------------------------------

bool vtkTAG2EFuzzyInferenceModelParameter::ParseResponses(
    vtkXMLDataElement *XMLResponses)
{
  int i;

  this->FIS.Responses.Responses.clear();

  if (XMLResponses->GetAttribute("min") != NULL)
    {
    this->FIS.Responses.min = atof(XMLResponses->GetAttribute("min"));
    } else
    {
    vtkErrorMacro( << "Attribute \"min\" is missing in Responses element");
    return false;
    }

  if (XMLResponses->GetAttribute("max") != NULL)
    {
    this->FIS.Responses.max = atof(XMLResponses->GetAttribute("max"));
    } else
    {
    vtkErrorMacro( << "Attribute \"max\" is missing in Responses element");
    return false;
    }

  for (i = 0; i < XMLResponses->GetNumberOfNestedElements(); i++)
    {
    vtkXMLDataElement *XMLResponse = XMLResponses->GetNestedElement(i);

    FuzzyResponse Response;

    int constant;

    if (XMLResponse->GetAttribute("const") != NULL)
      {
      constant = atoi(XMLResponse->GetAttribute("const"));
      if (constant == 0)
        Response.constant = false;
      else
        Response.constant = true;
      } else
      {
      vtkErrorMacro(
          << "Attribute \"const\" is missing in Response element: " << i);
      return false;
      }

    if (XMLResponse->GetAttribute("sd") != NULL)
      {
      Response.sd = atof(XMLResponse->GetAttribute("sd"));
      } else
      {
      vtkErrorMacro(
          << "Attribute \"sd\" is missing in Response element: " << i);
      return false;
      }

    if (XMLResponse->GetCharacterData() != NULL)
      {
      Response.value = atof(XMLResponse->GetCharacterData());
      } else
      {
      vtkErrorMacro(
          << "Attribute \"sd\" is missing in Response element: " << i);
      return false;
      }

    this->FIS.Responses.Responses.push_back(Response);

    //    cout << "Added Response const " << Response.constant << " sd " << Response.sd
    //      << " value " << Response.value << endl;

    }

  //  cout << "Added Responses min " << this->FIS.Responses.min
  //    << " max " << this->FIS.Responses.max << endl;

  return true;
}
