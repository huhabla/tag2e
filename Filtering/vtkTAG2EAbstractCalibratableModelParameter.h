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

/*
 * \brief This is the abstract base class for all model parameter which must
 * be calibrated (Fuzzy models, ...)
 * 
 * This class defines the interface which is used by the simulated annealing 
 * class to modify the model parameter. The interface must be implemented in the 
 * subclasses.
 */


#ifndef vtkTAG2EAbstractCalibratableModelParameter_H
#define	vtkTAG2EAbstractCalibratableModelParameter_H

#include <vtkTAG2EAbstractModelParameter.h>

class vtkTAG2EAbstractCalibratableModelParameter : public vtkTAG2EAbstractModelParameter {
public:
    vtkTypeRevisionMacro(vtkTAG2EAbstractCalibratableModelParameter, vtkTAG2EAbstractModelParameter);
    
    //!\brief Abstract Method to change arbritary a model parameter
    virtual void ChangeParameterRandomly() = 0;
    //!\brief Abstract Restore the last randomly modified model parameter 
    virtual void RestoreParameter() = 0;

protected:

    vtkTAG2EAbstractCalibratableModelParameter();
    ~vtkTAG2EAbstractCalibratableModelParameter();
    
private:
    vtkTAG2EAbstractCalibratableModelParameter(const vtkTAG2EAbstractCalibratableModelParameter& orig);
    void operator=(const vtkTAG2EAbstractCalibratableModelParameter&); // Not implemented. 
};

#endif	/* vtkTAG2EAbstractCalibratableModelParameter_H */
