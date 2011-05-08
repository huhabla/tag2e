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


    //!\brief This abstract method should be used to generate the internal
    //! representation for fast calibration computation from the XML decription
    virtual bool GenerateInternalSchemeFromXML() = 0;
    //!\brief This abstract method should be used to convert the internal reprsentation
    //! of the model parameter into the XML representation for file storage or copying
    virtual bool GenerateXMLFromInternalScheme() = 0;

    //!\brief Abstract Method to change arbritary a model parameter
    virtual bool ModifyParameterRandomly(double sd) = 0;
    //!\brief Abstract Restore the last modified model parameter 
    virtual bool RestoreLastModifiedParameter() = 0;
    //!\brief Abstract Method to change arbritary a model parameter
    virtual bool ModifyParameter(int index, double sd) = 0;
    //!\brief Abstract Method to get a model parameter at index
    virtual double GetParameterValue(int index) = 0;
    //!\brief Return the number of calibratable parameter
    vtkGetMacro(NumberOfCalibratableParameter, int);
    
protected:
    vtkSetMacro(NumberOfCalibratableParameter, int);

    vtkTAG2EAbstractCalibratableModelParameter();
    ~vtkTAG2EAbstractCalibratableModelParameter();
    
    int NumberOfCalibratableParameter;
    
private:
    vtkTAG2EAbstractCalibratableModelParameter(const vtkTAG2EAbstractCalibratableModelParameter& orig);
    void operator=(const vtkTAG2EAbstractCalibratableModelParameter&); // Not implemented. 
};

#endif	/* vtkTAG2EAbstractCalibratableModelParameter_H */
