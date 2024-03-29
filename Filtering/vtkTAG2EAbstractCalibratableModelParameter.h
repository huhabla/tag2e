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
#include <vector>

class vtkTAG2EAbstractCalibratableModelParameter : public vtkTAG2EAbstractModelParameter {
public:
    vtkTypeRevisionMacro(vtkTAG2EAbstractCalibratableModelParameter, vtkTAG2EAbstractModelParameter);

    //!\brief Change arbritary a model parameter using a specific standard deviation
    //! The method GenerateInternalSchemeFromXML must be called first, before you can use this method
    virtual bool ModifyParameterRandomly(double sd);
    //!\brief Change a model parameter at index using a specific standard deviation
    //! The method GenerateInternalSchemeFromXML must be called first, before you can use this method
    virtual bool ModifyParameter(int index, double sd);
    //!\brief Return a model parameter at index. No index range check is performed.
    //! The method GenerateInternalSchemeFromXML must be called first, before you can use this method
    virtual double GetParameterValue(int index){return this->ParameterValues[index];};
    //!\brief Restore the last modified model parameter 
    //! The method GenerateInternalSchemeFromXML must be called first, before you can use this method
    virtual bool RestoreLastModifiedParameter();
    
    //!\brief Return the number of calibratable parameter
    vtkGetMacro(NumberOfCalibratableParameter, int);
    //!\brief Reimplemented from abstract model parameter to call
    //! the internal representation generator
    virtual bool GetXMLRepresentation(vtkXMLDataElement *root);
    //!\brief Reimplemented from abstract model parameter to call
    //! the internal representation generator
    virtual bool SetXMLRepresentation(vtkXMLDataElement *root);
    
    //!\brief IMPLEMENT THIS METHOD IN SUBCLASS
    virtual bool GenerateInternalSchemeFromXML() = 0;
    //!\brief IMPLEMENT THIS METHOD IN SUBCLASS
    virtual bool GenerateXMLFromInternalScheme() = 0;
    
protected:
    vtkSetMacro(NumberOfCalibratableParameter, int);

    vtkTAG2EAbstractCalibratableModelParameter();
    ~vtkTAG2EAbstractCalibratableModelParameter();
    
    //!\brief IMPLEMENT THIS METHOD IN SUBCLASS
    virtual bool CreateParameterIndex() = 0;
    //!\brief IMPLEMENT THIS METHOD IN SUBCLASS
    virtual bool SetParameter(unsigned int index, double value) = 0;
    //!\brief Append a parameter state to the internal parameter arrays for calibration
    virtual void AppendParameterState(unsigned int index, double value, double min, double max);
    //!\brief Update a parameter state to the internal parameter arrays for calibration
    virtual void UpdateParameterState(unsigned int index, double old_value, double new_value);

    
    int NumberOfCalibratableParameter;
    double ParameterValue; // This variable stores the old parameter value
    unsigned int ParameterId; // This is the id of the last changed parameter, -1 nothing changed yet

    // BTX
    std::vector <unsigned int> ParameterIndex;
    std::vector <double> ParameterValues;
    std::vector < std::vector <double> > ParameterMinMax;
    // ETX

private:
    vtkTAG2EAbstractCalibratableModelParameter(const vtkTAG2EAbstractCalibratableModelParameter& orig);
    void operator=(const vtkTAG2EAbstractCalibratableModelParameter&); // Not implemented. 
};

#endif	/* vtkTAG2EAbstractCalibratableModelParameter_H */
