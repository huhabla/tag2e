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

#ifndef VTKTAG2EFUZZYINFERENCESCHEME_H
#define	VTKTAG2EFUZZYINFERENCESCHEME_H

#include <vtkObject.h>
#include <vtkXMLDataElement.h>
#include <assert.h>
#include "vtkTAG2EAbstractCalibrationParameter.h"

class vtkKeyValueMap;

class vtkTAG2EFuzzyInferenceScheme : public vtkTAG2EAbstractCalibrationParameter {
public:
    vtkTypeRevisionMacro(vtkTAG2EFuzzyInferenceScheme, vtkTAG2EAbstractCalibrationParameter);

    void PrintSelf(ostream& os, vtkIndent indent) {
        ;
    }
    static vtkTAG2EFuzzyInferenceScheme *New();
    
    //!\brief Read the fuzzy inference scheme file specified by FileName
    bool Read(){;}
    
    //\brief filename of the XML fuzzy inference schemen which should be read or written
    vtkSetStringMacro(FileName);
    //\brief filename of the XML fuzzy inference schemen which should be read or written
    vtkGetStringMacro(FileName);
    //!\brief Compute the response for a specific faktor combination
    double ComputeResponse(vtkKeyValueMap *map/*Key - Value map of factor names and factor values (char*, double)*/){;}
    
    //!\brief Get the XML representation of the fuzzy dataset
    vtkGetObjectMacro(Root, vtkXMLDataElement);
    //!\brief Set the XML representation of the fuzzy dataset
    vtkSetObjectMacro(Root, vtkXMLDataElement);
    
protected:
    
    char *FileName;
    double **DecisionMatrix;
    vtkXMLDataElement *Root;
    
    void ComputeDecisionMatrix();
    
    // Hide the calibration paranter methods from user

    virtual void ChangeParameter(int idx) {
        assert("ChangeParameter must be implemented in a subclass");
    }

    virtual int GetNumberOfParameter() {
        assert("GetNumberOfParameter must be implemented in a subclass");
    }

    virtual double GetF() {
        assert("GetF must be implemented in a subclass");
    }

    vtkTAG2EFuzzyInferenceScheme();
    virtual ~vtkTAG2EFuzzyInferenceScheme();
private:
    vtkTAG2EFuzzyInferenceScheme(const vtkTAG2EFuzzyInferenceScheme& orig);
    void operator=(const vtkTAG2EFuzzyInferenceScheme&); // Not implemented.
};

#endif	/* VTKTAG2EFUZZYINFERENCESCHEME_H */
