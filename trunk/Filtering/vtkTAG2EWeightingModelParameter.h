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

/**
 * \brief This is the fuzzy inference model parameter class
 * 
 * \TODO Instead of normalized fuzzy set positions, use real values and normailze at runtime
 */

#ifndef vtkTAG2EWeightingModelParameter_H
#define	vtkTAG2EWeightingModelParameter_H

#include <vtkObject.h>
#include <vtkXMLDataElement.h>
#include "vtkTAG2EAbstractCalibratableModelParameter.h"
#include <vector>
#include <map>

class WeightingWeight{
public:
    int id;
    bool active;
    bool constant;
    double min;
    double max;
    double value;
};

class WeightingFactor{
public:
    std::string name;
};

class Weighting{
public:
    std::string name;
    WeightingFactor Factor;
    std::vector<WeightingWeight> Weights;
};


class vtkXMLDataElement;

class vtkTAG2EWeightingModelParameter : public vtkTAG2EAbstractCalibratableModelParameter {
public:
    vtkTypeRevisionMacro(vtkTAG2EWeightingModelParameter, vtkTAG2EAbstractCalibratableModelParameter);

    void PrintSelf(ostream& os, vtkIndent indent) {
        ;
    }
    static vtkTAG2EWeightingModelParameter *New();

    virtual bool GenerateInternalSchemeFromXML();
    virtual bool GenerateXMLFromInternalScheme();
    
    //BTX
    Weighting &GetInternalScheme() {
        return this->W;
    }
    //ETX

protected:

    vtkTAG2EWeightingModelParameter();
    ~vtkTAG2EWeightingModelParameter();

    bool ParseWeight(vtkXMLDataElement *wXMLWeight, WeightingWeight &Weight);
    virtual bool CreateParameterIndex();
    virtual bool SetParameter(unsigned int index, double value);

    // BTX
    Weighting W;
    // ETX

private:
    vtkTAG2EWeightingModelParameter(const vtkTAG2EWeightingModelParameter& orig);
    void operator=(const vtkTAG2EWeightingModelParameter&); // Not implemented.
};


#endif	/* vtkTAG2EWeightingModelParameter_H */
