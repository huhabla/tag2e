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
#include <sstream>
#include <stdlib.h>
#include <vtk-5.9/vtkErrorCode.h>

vtkCxxRevisionMacro(vtkTAG2EFuzzyInferenceModelParameter, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2EFuzzyInferenceModelParameter);

#define MAX_CHANGE_PARAMETER_RUNS 1000

//----------------------------------------------------------------------------

static int irand(int a, int e) {
    double r = e - a + 1;
    return a + (int) (r * rand() / (RAND_MAX + 1.0));
}

//----------------------------------------------------------------------------

static double norm_dist(double mean, double sd) {
    double u1, u2, x1, x2;
    u1 = (double) rand() / (double) (RAND_MAX);
    u2 = (double) rand() / (double) (RAND_MAX);
    x1 = sqrt(-2 * log(1.0 - u1)) * cos(2.0 * M_PI * u2);
    x2 = sqrt(-2 * log(1.0 - u1)) * sin(2.0 * M_PI * u2);
    return x1 * sd - mean;
}

//----------------------------------------------------------------------------

vtkTAG2EFuzzyInferenceModelParameter::vtkTAG2EFuzzyInferenceModelParameter() {
    this->NumberOfFactors = 0;
    this->NumberOfRules = 0;
    this->ParameterId = -1;
    this->ParameterValue = 0.0;
    this->ParameterIndex.clear();

    // Initiate the random number generator with the current time
    srand(time(0));
}

//----------------------------------------------------------------------------

vtkTAG2EFuzzyInferenceModelParameter::~vtkTAG2EFuzzyInferenceModelParameter() {
    ;
}

//----------------------------------------------------------------------------

bool vtkTAG2EFuzzyInferenceModelParameter::GenerateXMLFromInternalScheme() {
    unsigned int i, j;

    vtkXMLDataElement *root = vtkXMLDataElement::New();
    root->SetName("WeightedFuzzyInferenceScheme");
    root->SetAttribute("name", this->WFIS.name.c_str());
    root->SetAttribute("xmlns", "http://tag2e.googlecode.com/files/WightedFuzzyInferenceScheme");
    root->SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance");
    root->SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme.xsd");

    vtkXMLDataElement *fis = vtkXMLDataElement::New();
    fis->SetName("FuzzyInferenceScheme");

    for (i = 0; i < this->WFIS.FIS.Factors.size(); i++) {
        FuzzyFactor &Factor = this->WFIS.FIS.Factors[i];
        vtkXMLDataElement *factor = vtkXMLDataElement::New();

        factor->SetName("Factor");
        factor->SetAttribute("name", Factor.name.c_str());
        factor->SetDoubleAttribute("min", Factor.min);
        factor->SetDoubleAttribute("max", Factor.max);
        factor->SetIntAttribute("portId", Factor.portId);

        for (j = 0; j < Factor.Sets.size(); j++) {
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

            if (Set.type == FUZZY_SET_TYPE_TRIANGULAR) {
                vtkXMLDataElement *triangular = vtkXMLDataElement::New();

                triangular->SetName("Triangular");
                triangular->SetDoubleAttribute("center", Set.Triangular.center);
                triangular->SetDoubleAttribute("left", Set.Triangular.left);
                triangular->SetDoubleAttribute("right", Set.Triangular.right);

                set->AddNestedElement(triangular);
                triangular->Delete();
            }
            if (Set.type == FUZZY_SET_TYPE_CRISP) {
                vtkXMLDataElement *crisp = vtkXMLDataElement::New();

                crisp->SetName("Crisp");
                crisp->SetDoubleAttribute("right", Set.Crisp.right);
                crisp->SetDoubleAttribute("left", Set.Crisp.left);

                set->AddNestedElement(crisp);
                crisp->Delete();
            }
            if (Set.type == FUZZY_SET_TYPE_BELL_SHAPE) {
                vtkXMLDataElement *bellshape = vtkXMLDataElement::New();

                bellshape->SetName("BellShape");
                bellshape->SetDoubleAttribute("center", Set.BellShape.center);
                bellshape->SetDoubleAttribute("sdLeft", Set.BellShape.sdLeft);
                bellshape->SetDoubleAttribute("sdRight", Set.BellShape.sdRight);

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

    responses->SetName("Responses");
    responses->SetIntAttribute("min", this->WFIS.FIS.Responses.min);
    responses->SetIntAttribute("max", this->WFIS.FIS.Responses.max);

    for (i = 0; i < this->WFIS.FIS.Responses.Responses.size(); i++) {
        FuzzyResponse &Response = this->WFIS.FIS.Responses.Responses[i];
        vtkXMLDataElement *response = vtkXMLDataElement::New();

        response->SetName("Response");
        response->SetIntAttribute("const", (int) Response.constant);
        response->SetDoubleAttribute("sd", Response.sd);
        std::ostringstream value;
        value << Response.value;
        response->SetCharacterData(value.str().c_str(), value.str().size());

        responses->AddNestedElement(response);
        response->Delete();
    }

    fis->AddNestedElement(responses);
    root->AddNestedElement(fis);
    responses->Delete();
    fis->Delete();

    vtkXMLDataElement *weight = vtkXMLDataElement::New();
    weight->SetName("Weight");
    weight->SetIntAttribute("active", (int) WFIS.Weight.active);
    weight->SetIntAttribute("const", (int) WFIS.Weight.constant);
    weight->SetDoubleAttribute("min", WFIS.Weight.min);
    weight->SetDoubleAttribute("max", WFIS.Weight.max);
    std::ostringstream value;
    value << WFIS.Weight.value;
    weight->SetCharacterData(value.str().c_str(), value.str().size());
    weight->SetAttribute("name", WFIS.Weight.name.c_str());

    root->AddNestedElement(weight);
    weight->Delete();

    this->XMLRoot->DeepCopy(root);
    root->Delete();

    return true;
}

//----------------------------------------------------------------------------

bool vtkTAG2EFuzzyInferenceModelParameter::ChangeParameterRandomly(double sd) {
    bool check = false;
    int count = 0;

    // Change a randomly selected parameter till a valid configuration is found
    while (!check) {
        
        // Avoid endless loops
        count++;
        if (count > MAX_CHANGE_PARAMETER_RUNS) {
            vtkErrorMacro( << "Maximum number of parameter runs reached");
            return false;
        }
        
        // Select randomly a uniform distributed index
        int index = irand(0, this->ParameterIndex.size() - 1);
        
        // Get min and max values for parameter range check
        double min = this->ParameterMinMax[index][0];
        double max = this->ParameterMinMax[index][1];
        // We need the current value of the selected parameter 
        // which is the base of the change
        double value = this->ParameterValues[index];
        // The range of the selected parameter
        double range = max - min;
        // A normal-distributed random number [0.0;1.0]
        double rvalue = norm_dist(0.0, sd);
        // The new parameter value 
        value = value + rvalue*range;

        // The generated value must be in range, otherwise a new value is selected
        if (value < min || value > max) {
            continue;
        }

        // Set the Parameter
        check = this->SetParameter(index, value);
        // Revert the change in case the modified parametrer result in wrong fuzzy sets
        if (check == false)
            this->RestoreParameter();
    }

    this->GenerateXMLFromInternalScheme();

    return check;
}

//----------------------------------------------------------------------------

bool vtkTAG2EFuzzyInferenceModelParameter::RestoreParameter() {
    return this->SetParameter(this->ParameterId, this->ParameterValue);
}

//----------------------------------------------------------------------------

bool vtkTAG2EFuzzyInferenceModelParameter::SetParameter(unsigned int index, double value) {
    unsigned int i, j;
    unsigned int count = 0;

    for (i = 0; i < this->WFIS.FIS.Factors.size(); i++) {
        FuzzyFactor &Factor = this->WFIS.FIS.Factors[i];

        // Important:
        // The fuzzy set position values are stored internally as normalized values,
        // but scaled to real values for random number generation. This might be a bit confusing
        // and can be a source of errors

        for (j = 0; j < Factor.Sets.size(); j++) {
            FuzzySet &Set = Factor.Sets[j];

            // Const values are not counted
            if (Set.constant == false) {
                // Fuzzy set geometry is handled normalized internally
                // We need to scale and normailze
                double scale = fabs(Factor.max - Factor.min);
                
                if (Set.type == FUZZY_SET_TYPE_TRIANGULAR) {
                    if (index == count) {
                        this->UpdateParameterState(index, Set.Triangular.center * scale, value);
                        // Assign the value
                        Set.Triangular.center = value / scale;

                        // This is the distance between the old and new center
                        double dx = (value - this->ParameterValue) / scale;

                        // We need to change the size of the left slope of the right nighbouring triangle
                        // and the right slope of the current triangle 
                        // The size of booth triangle must be identical
                        if (Set.position == FUZZY_SET_POISITION_LEFT || Set.position == FUZZY_SET_POISITION_INT) {
                            Factor.Sets[j + 1].Triangular.left -= dx;
                            Set.Triangular.right -= dx;
                        }
                        // We need to change the size of the right slope of the left nighbouring triangle
                        // and the left slope of the current triangle 
                        // The size of booth triangle must be identical
                        if (Set.position == FUZZY_SET_POISITION_RIGHT || Set.position == FUZZY_SET_POISITION_INT) {
                            Factor.Sets[j - 1].Triangular.right += dx;
                            Set.Triangular.left += dx;
                        }
                        // Check for correct fuzzy factor and fuzzy sets
                        return tag2eWFIS::CheckFuzzyFactor(Factor);
                    }
                    count++;
                }
                if (Set.type == FUZZY_SET_TYPE_CRISP) {
                    if (index == count) {
                        this->UpdateParameterState(index, Set.Crisp.left * scale, value);
                        Set.Crisp.left = value / scale;
                        return tag2eWFIS::CheckFuzzyFactor(Factor);
                    }
                    count++;
                    if (index == count) {
                        this->UpdateParameterState(index, Set.Crisp.right * scale, value);
                        Set.Crisp.right = value / scale;
                        return tag2eWFIS::CheckFuzzyFactor(Factor);
                    }
                    count++;
                }
                if (Set.type == FUZZY_SET_TYPE_BELL_SHAPE) {
                    if (index == count) {
                        this->UpdateParameterState(index, Set.BellShape.center * scale, value);
                        Set.BellShape.center = value / scale;
                        return tag2eWFIS::CheckFuzzyFactor(Factor);
                    }
                    count++;
                }
            }
        }
    }

    for (i = 0; i < this->WFIS.FIS.Responses.Responses.size(); i++) {
        FuzzyResponse &Response = this->WFIS.FIS.Responses.Responses[i];
        if (index == count) {
            this->UpdateParameterState(index, Response.value, value);
            Response.value = value;
            return true;
        }
        count++;
    }

    if (index == count) {
        this->UpdateParameterState(index, WFIS.Weight.value, value);
        WFIS.Weight.value = value;
        return true;
    }

    return false;
}

//----------------------------------------------------------------------------

void vtkTAG2EFuzzyInferenceModelParameter::UpdateParameterState(unsigned int index, double old_value, double new_value) {

    // cout << "Index " << index << " old value " << old_value << " new value " << new_value << endl;
    
    // Safe the last parameter for restauration
    this->ParameterValue = old_value;
    // Safe the last index for restauration
    this->ParameterId = index;
    // Modify the value array too 
    this->ParameterValues[index] = new_value;
}

//----------------------------------------------------------------------------

bool vtkTAG2EFuzzyInferenceModelParameter::CreateParameterIndex() {
    unsigned int i, j;
    unsigned int count = 0;

    // ATTENTION:
    // The count mechanism of CreateParameterIndex and SetParemter must be identical

    this->ParameterIndex.clear();

    // We start to count the fuzzy sets, then the responses and at last the weight

    for (i = 0; i < this->WFIS.FIS.Factors.size(); i++) {
        FuzzyFactor &Factor = this->WFIS.FIS.Factors[i];

        for (j = 0; j < Factor.Sets.size(); j++) {
            FuzzySet &Set = Factor.Sets[j];
            // Count only non-constant fuzzy sets
            if (Set.constant == false) {
                
                // Fuzzy set geometry is handled normalized internally
                // We need to scale and normailze
                double scale = fabs(Factor.max - Factor.min);
                
                if (Set.type == FUZZY_SET_TYPE_TRIANGULAR) {
                    this->AppendParameterState(count, Set.Triangular.center * scale, Factor.min, Factor.max);
                    count++;
                }
                if (Set.type == FUZZY_SET_TYPE_CRISP) {
                    this->AppendParameterState(count, Set.Crisp.left * scale, Factor.min, Factor.max);
                    count++;
                    this->AppendParameterState(count, Set.Crisp.right * scale, Factor.min, Factor.max);
                    count++;
                }
                if (Set.type == FUZZY_SET_TYPE_BELL_SHAPE) {
                    this->AppendParameterState(count, Set.BellShape.center * scale, Factor.min, Factor.max);
                    count++;
                }
            }
        }
    }

    for (i = 0; i < this->WFIS.FIS.Responses.Responses.size(); i++) {
        FuzzyResponse &Response = this->WFIS.FIS.Responses.Responses[i];
        if (Response.constant == false) {
            this->AppendParameterState(count, Response.value, this->WFIS.FIS.Responses.min,
                    this->WFIS.FIS.Responses.max);
        }
        count++;
    }

    if (WFIS.Weight.constant == false) {
        this->AppendParameterState(count, WFIS.Weight.value,
                this->WFIS.Weight.min, this->WFIS.Weight.max);
    }

    return true;
}

//----------------------------------------------------------------------------

void vtkTAG2EFuzzyInferenceModelParameter::AppendParameterState(unsigned int index, double value, double min, double max) {

    //cout << "Index " << index << " Value " << value << endl;
    
    // Save the parameter index
    this->ParameterIndex.push_back(index);
    // Save the current value of the parameter for random number generation
    this->ParameterValues.push_back(value);
    // We store the min and max values for each parameter, redundancy is intention 
    std::vector<double> mm;
    mm.push_back(min);
    mm.push_back(max);
    this->ParameterMinMax.push_back(mm);
}

//----------------------------------------------------------------------------

bool vtkTAG2EFuzzyInferenceModelParameter::GenerateInternalSchemeFromXML() {
    vtkXMLDataElement *root = this->GetXMLRoot();
    unsigned int i;

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

        if (!this->ParseFactors(XMLFIS))
            return false;

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

    // cout << this->WFIS.name << endl;

    this->CreateParameterIndex();

    return true;
}

//----------------------------------------------------------------------------

bool vtkTAG2EFuzzyInferenceModelParameter::ParseFactors(vtkXMLDataElement *XMLFIS) {
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

        if (tag2eWFIS::CheckFuzzyFactor(Factor) != true) {
            vtkErrorMacro( << "Factor " << i << " has incorrect fuzzy sets");
            return false;
        }
    }

    return true;
}

//----------------------------------------------------------------------------

bool vtkTAG2EFuzzyInferenceModelParameter::ParseFuzzySets(FuzzyFactor &Factor, vtkXMLDataElement *XMLFactor) {

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
            int val = atoi(XMLFuzzySet->GetAttribute("const"));
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

//----------------------------------------------------------------------------

bool vtkTAG2EFuzzyInferenceModelParameter::ParseResponses(vtkXMLDataElement *XMLResponses) {
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

//----------------------------------------------------------------------------

bool vtkTAG2EFuzzyInferenceModelParameter::ParseWeights(vtkXMLDataElement *XMLWeight) {
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
