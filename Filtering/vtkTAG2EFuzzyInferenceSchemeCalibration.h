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

#ifndef VTKTAG2EFUZZYINFERENCESCHEMECALIBRATION_H
#define	VTKTAG2EFUZZYINFERENCESCHEMECALIBRATION_H

#include "vtkTAG2EAbstractCalibrationParameter.h"
#include "vtkTAG2EFuzzyInferenceScheme.h"

class vtkTAG2EFuzzyInferenceSchemeCalibration : public vtkTAG2EFuzzyInferenceScheme {
public:
    vtkTypeRevisionMacro(vtkTAG2EFuzzyInferenceSchemeCalibration, vtkTAG2EFuzzyInferenceScheme);

    void PrintSelf(ostream& os, vtkIndent indent) {
        ;
    }
    static vtkTAG2EFuzzyInferenceSchemeCalibration *New();

    virtual void ChangeParameter(int idx) {
        ;
    }

    virtual int GetNumberOfParameter() {
        ;
    }

    virtual double GetF() {
        ;
    }
    
protected:   
    vtkTAG2EFuzzyInferenceSchemeCalibration(){;}
    virtual ~vtkTAG2EFuzzyInferenceSchemeCalibration(){;}
private:
    vtkTAG2EFuzzyInferenceSchemeCalibration(const vtkTAG2EFuzzyInferenceSchemeCalibration& orig);
    void operator=(const vtkTAG2EFuzzyInferenceSchemeCalibration&); // Not implemented.
};

#endif	/* VTKTAG2EFUZZYINFERENCESCHEMECALIBRATION_H */
