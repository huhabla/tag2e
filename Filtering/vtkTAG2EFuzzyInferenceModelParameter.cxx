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
#include "tag2eWFIS.h"

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

bool vtkTAG2EFuzzyInferenceModelParameter::GenerateXMLFromInternalScheme()
{
  unsigned int i, j;

  vtkXMLDataElement *root = vtkXMLDataElement::New();
  root->SetName("WeightedFuzzyInferenceScheme");
  root->SetAttribute("name", this->WFIS.name.c_str());

  this->XMLRoot->DeepCopy(root);

  cout << this->WFIS.name << endl;

  for (i = 0; i < this->WFIS.FIS.Factors.size(); i++) {
    FuzzyFactor &Factor = this->WFIS.FIS.Factors[i];
    cout << " " << Factor.name << endl;
    cout << " " << Factor.min << endl;
    cout << " " << Factor.max << endl;
    for (j = 0; j < Factor.Sets.size(); j++) {
      FuzzySet &Set = Factor.Sets[j];
      cout << "  " << Set.constant << endl;
      cout << "  " << Set.position << endl;
      cout << "  " << Set.priority << endl;
      cout << "  " << Set.type << endl;
      if (Set.type == FUZZY_SET_TYPE_TRIANGULAR) {
        cout << "   " << Set.Triangular.center << endl;
        cout << "   " << Set.Triangular.left << endl;
        cout << "   " << Set.Triangular.right << endl;
      }
      if (Set.type == FUZZY_SET_TYPE_CRISP) {
        cout << "   " << Set.Crisp.left << endl;
        cout << "   " << Set.Crisp.right << endl;
      }
      if (Set.type == FUZZY_SET_TYPE_BELL_SHAPE) {
        cout << "   " << Set.BellShape.center << endl;
        cout << "   " << Set.BellShape.sdLeft << endl;
        cout << "   " << Set.BellShape.sdRight << endl;
      }
    }
  }

  cout << this->WFIS.FIS.Responses.min << endl;
  cout << this->WFIS.FIS.Responses.max << endl;

  for (i = 0; i < this->WFIS.FIS.Responses.Responses.size(); i++) {
    FuzzyResponse &Response = this->WFIS.FIS.Responses.Responses[i];
    cout << " " << Response.constant << endl;
    cout << " " << Response.sd << endl;
    cout << " " << Response.value << endl;
  }

  cout << " " << WFIS.Weight.active << endl;
  cout << " " << WFIS.Weight.constant << endl;
  cout << " " << WFIS.Weight.max << endl;
  cout << " " << WFIS.Weight.min << endl;
  cout << " " << WFIS.Weight.name << endl;
  cout << " " << WFIS.Weight.value << endl;


  return true;
}

bool vtkTAG2EFuzzyInferenceModelParameter::GenerateInternalSchemeFromXML()
{
  vtkXMLDataElement *root = this->GetXMLRoot();
  int i;

  // Check for correct name
  if (strncasecmp(root->GetName(), "WeightedFuzzyInferenceScheme", strlen("WeightedFuzzyInferenceScheme")) != 0) {
    vtkErrorMacro("The model parameter does not contain a valid weighted fuzzy inference WFIS");
    return false;
  }

  if (root->GetAttribute("name") != NULL) {
    this->WFIS.name = root->GetAttribute("name");
  } else {
    vtkErrorMacro( << "Attribute \"name\" is missing in WeightedFuzzyInferenceScheme element");
    return false;
  }

  // Get the Fuzzy inference WFIS
  vtkXMLDataElement *XMLFIS = root->FindNestedElementWithName("FuzzyInferenceScheme");

  // Parse the Factors and the responses
  if (XMLFIS != NULL) {

    this->ParseFactors(XMLFIS);

    vtkXMLDataElement *Responses = XMLFIS->FindNestedElementWithName("Responses");
    if (Responses != NULL)
      this->ParseResponses(Responses);
  }

  // Get the Fuzzy inference WFIS
  vtkXMLDataElement *Weight = root->FindNestedElementWithName("Weight");

  // Parse the Factors and the responses
  if (Weight != NULL) {
    this->ParseWeights(Weight);
  }
  
  // Compute the number of rules and number of factors
  this->NumberOfRules = WFIS.FIS.Factors[0].Sets.size();
  this->NumberOfFactors = WFIS.FIS.Factors.size();

  for (i = 0; i < this->NumberOfFactors; i++) {
    FuzzyFactor &Factor = WFIS.FIS.Factors[i];
    
    if (i > 0)
      this->NumberOfRules *= Factor.Sets.size();
  }

//  cout << "Number of Rules " << this->NumberOfRules << endl;
//  cout << "Number of Factors " << this->NumberOfFactors << endl;
  
  cout << this->WFIS.name << endl;

  return true;
}

bool vtkTAG2EFuzzyInferenceModelParameter::ParseFactors(vtkXMLDataElement *XMLFIS)
{
  int i;
  
  this->WFIS.FIS.Factors.clear();

  for (i = 0; i < XMLFIS->GetNumberOfNestedElements(); i++) {
    vtkXMLDataElement *XMLFactor = XMLFIS->GetNestedElement(i);

    if (strncasecmp(XMLFactor->GetName(), "Factor", strlen("Factor")) != 0) {
      continue;
    }

    FuzzyFactor Factor;

    if (XMLFactor->GetAttribute("name") != NULL) {
      Factor.name = XMLFactor->GetAttribute("name");
    } else {
      vtkErrorMacro( << "Attribute \"name\" is missing in Factor element: " << i);
      return false;
    }

    if (XMLFactor->GetAttribute("portId") != NULL) {
      Factor.portId = atoi(XMLFactor->GetAttribute("portId"));
    } else {
      vtkErrorMacro( << "Attribute \"portId\" is missing in Factor element: " << i);
      return false;
    }

    if (XMLFactor->GetAttribute("min") != NULL) {
      Factor.min = atof(XMLFactor->GetAttribute("min"));
    } else {
      vtkErrorMacro( << "Attribute \"min\" is missing in Factor element: " << i);
      return false;
    }

    if (XMLFactor->GetAttribute("max") != NULL) {
      Factor.max = atof(XMLFactor->GetAttribute("max"));
    } else {
      vtkErrorMacro( << "Attribute \"max\" is missing in Factor element: " << i);
      return false;
    }

    this->ParseFuzzySets(Factor, XMLFactor);

//    cout << "Add Factor " << Factor.name << " with portId " << Factor.portId
//      << " min  " << Factor.min << " max " << Factor.max << endl;

    this->WFIS.FIS.Factors.push_back(Factor);
  }

  return true;
}

bool vtkTAG2EFuzzyInferenceModelParameter::ParseFuzzySets(FuzzyFactor &Factor, vtkXMLDataElement *XMLFactor)
{

  int i;
  
  Factor.Sets.clear();

  for (i = 0; i < XMLFactor->GetNumberOfNestedElements(); i++) {
    vtkXMLDataElement *XMLFuzzySet = XMLFactor->GetNestedElement(i);

    FuzzySet Set;

    if (XMLFuzzySet->GetAttribute("type") != NULL) {
      const char *type = XMLFuzzySet->GetAttribute("type");
      if (strncasecmp(type, "Triangular", strlen(type)) == 0)
        Set.type = FUZZY_SET_TYPE_TRIANGULAR;
      if (strncasecmp(type, "Crisp", strlen(type)) == 0)
        Set.type = FUZZY_SET_TYPE_CRISP;
      if (strncasecmp(type, "BellShape", strlen(type)) == 0)
        Set.type = FUZZY_SET_TYPE_BELL_SHAPE;
    } else {
      vtkErrorMacro( << "Attribute \"type\" is missing in FuzzySet element: " << i);
      return false;
    }

    if (XMLFuzzySet->GetAttribute("priority") != NULL) {
      Set.priority = atoi(XMLFuzzySet->GetAttribute("priority"));
    } else {
      vtkErrorMacro( << "Attribute \"priority\" is missing in FuzzySet element: " << i);
      return false;
    }

    if (XMLFuzzySet->GetAttribute("const") != NULL) {
      int val = atoi(XMLFuzzySet->GetAttribute("priority"));
      if (val == 0)
        Set.constant = false;
      else
        Set.constant = true;
    } else {
      vtkErrorMacro( << "Attribute \"const\" is missing in FuzzySet element: " << i);
      return false;
    }


    if (XMLFuzzySet->GetAttribute("position") != NULL) {
      const char *type = XMLFuzzySet->GetAttribute("position");
      if (strncasecmp(type, "left", strlen(type)) == 0)
        Set.position = FUZZY_SET_POISITION_LEFT;
      if (strncasecmp(type, "intermediate", strlen(type)) == 0)
        Set.position = FUZZY_SET_POISITION_INT;
      if (strncasecmp(type, "right", strlen(type)) == 0)
        Set.position = FUZZY_SET_POISITION_RIGHT;
    } else {
      vtkErrorMacro( << "Attribute \"position\" is missing in FuzzySet element: " << i);
      return false;
    }

    // Now fetch the Fuzzy shapes

    if (Set.type == FUZZY_SET_TYPE_TRIANGULAR) {
      vtkXMLDataElement *Triangular = XMLFuzzySet->FindNestedElementWithName("Triangular");

      if (Triangular != NULL) {
        if (Triangular->GetAttribute("left") != NULL) {
          Set.Triangular.left = atof(Triangular->GetAttribute("left"));
        } else {
          vtkErrorMacro( << "Attribute \"left\" is missing in Triangular element: " << i);
          return false;
        }
        if (Triangular->GetAttribute("right") != NULL) {
          Set.Triangular.right = atof(Triangular->GetAttribute("right"));
        } else {
          vtkErrorMacro( << "Attribute \"right\" is missing in Triangular element: " << i);
          return false;
        }
        if (Triangular->GetAttribute("center") != NULL) {
          Set.Triangular.center = atof(Triangular->GetAttribute("center"));
        } else {
          vtkErrorMacro( << "Attribute \"center\" is missing in Triangular element: " << i);
          return false;
        }
      } else {
        vtkErrorMacro( << "Element \"Triangular\" is missing in FuzzySet element: " << i);
        return false;
      }

//      cout << "Added Trinagular center " << Set.Triangular.center << " left "
//        << Set.Triangular.left << " right " << Set.Triangular.right << endl;
    }

    if (Set.type == FUZZY_SET_TYPE_CRISP) {
      vtkXMLDataElement *Crisp = XMLFuzzySet->FindNestedElementWithName("Crisp");

      if (Crisp != NULL) {
        if (Crisp->GetAttribute("left") != NULL) {
          Set.Crisp.left = atof(Crisp->GetAttribute("left"));
        } else {
          vtkErrorMacro( << "Attribute \"left\" is missing in Crisp element: " << i);
          return false;
        }
        if (Crisp->GetAttribute("right") != NULL) {
          Set.Crisp.right = atof(Crisp->GetAttribute("right"));
        } else {
          vtkErrorMacro( << "Attribute \"right\" is missing in Crisp element: " << i);
          return false;
        }
      } else {
        vtkErrorMacro( << "Element \"Crisp\" is missing in FuzzySet element: " << i);
        return false;
      }

//      cout << "Added Crispt left " << Set.Crisp.left << " right " << Set.Crisp.right << endl;
    }


    if (Set.type == FUZZY_SET_TYPE_BELL_SHAPE) {
      vtkXMLDataElement *BellShape = XMLFuzzySet->FindNestedElementWithName("BellShape");

      if (BellShape != NULL) {
        if (BellShape->GetAttribute("sdLeft") != NULL) {
          Set.BellShape.sdLeft = atof(BellShape->GetAttribute("sdLeft"));
        } else {
          vtkErrorMacro( << "Attribute \"sdLeft\" is missing in BellShape element: " << i);
          return false;
        }
        if (BellShape->GetAttribute("sdRight") != NULL) {
          Set.BellShape.sdRight = atof(BellShape->GetAttribute("sdRight"));
        } else {
          vtkErrorMacro( << "Attribute \"sdRight\" is missing in BellShape element: " << i);
          return false;
        }
        if (BellShape->GetAttribute("center") != NULL) {
          Set.BellShape.center = atof(BellShape->GetAttribute("center"));
        } else {
          vtkErrorMacro( << "Attribute \"center\" is missing in BellShape element: " << i);
          return false;
        }
      } else {
        vtkErrorMacro( << "Element \"BellShape\" is missing in FuzzySet element: " << i);
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

bool vtkTAG2EFuzzyInferenceModelParameter::ParseResponses(vtkXMLDataElement *XMLResponses)
{
  int i;
  
  this->WFIS.FIS.Responses.Responses.clear();

  if (XMLResponses->GetAttribute("min") != NULL) {
    this->WFIS.FIS.Responses.min = atof(XMLResponses->GetAttribute("min"));
  } else {
    vtkErrorMacro( << "Attribute \"min\" is missing in Responses element");
    return false;
  }

  if (XMLResponses->GetAttribute("max") != NULL) {
    this->WFIS.FIS.Responses.max = atof(XMLResponses->GetAttribute("max"));
  } else {
    vtkErrorMacro( << "Attribute \"max\" is missing in Responses element");
    return false;
  }

  for (i = 0; i < XMLResponses->GetNumberOfNestedElements(); i++) {
    vtkXMLDataElement *XMLResponse = XMLResponses->GetNestedElement(i);

    FuzzyResponse Response;

    int constant;

    if (XMLResponse->GetAttribute("const") != NULL) {
      constant = atoi(XMLResponse->GetAttribute("const"));
      if (constant == 0)
        Response.constant = false;
      else
        Response.constant = true;
    } else {
      vtkErrorMacro( << "Attribute \"const\" is missing in Response element: " << i);
      return false;
    }

    if (XMLResponse->GetAttribute("sd") != NULL) {
      Response.sd = atof(XMLResponse->GetAttribute("sd"));
    } else {
      vtkErrorMacro( << "Attribute \"sd\" is missing in Response element: " << i);
      return false;
    }

    if (XMLResponse->GetCharacterData() != NULL) {
      Response.value = atof(XMLResponse->GetCharacterData());
    } else {
      vtkErrorMacro( << "Attribute \"sd\" is missing in Response element: " << i);
      return false;
    }

    this->WFIS.FIS.Responses.Responses.push_back(Response);

//    cout << "Added Response const " << Response.constant << " sd " << Response.sd
//      << " value " << Response.value << endl;

  }

//  cout << "Added Responses min " << this->WFIS.FIS.Responses.min
//    << " max " << this->WFIS.FIS.Responses.max << endl;


  return true;
}

bool vtkTAG2EFuzzyInferenceModelParameter::ParseWeights(vtkXMLDataElement *XMLWeight)
{
  int active;

  FuzzyWeight &Weight = this->WFIS.Weight;

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

  if (XMLWeight->GetAttribute("name") != NULL) {
    Weight.name = XMLWeight->GetAttribute("name");
  } else {
    vtkErrorMacro( << "Attribute \"name\" is missing in Weight element");
    return false;
  }

  if (XMLWeight->GetAttribute("min") != NULL) {
    Weight.min = atof(XMLWeight->GetAttribute("min"));
  } else {
    vtkErrorMacro( << "Attribute \"min\" is missing in Weight element");
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

//  cout << "Added Weight const " << Weight.constant << " name " << Weight.name
//    << " value " << Weight.value << " min " << Weight.min
//    << " max " << Weight.max << " active " << Weight.active << endl;


  return true;
}
