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
 * \brief This abstract class is the base class for all spatio-temporal numerical
 * and statistical models in TAG2E which can be specified using parameters.
 * 
 * The model parameter describe specific formulars which are used to process 
 * the input spatio-temporal data. This might be a linear regression model to
 * describe the connection between precipitation and temperature over time and space
 * or a fuzzy logic model which describes the reltation between several input values 
 * like pH, precipitation, temperatur and the resulting N2O emission.
 * 
 * Therefor the subclasses should implement general abstractions from statistical or numerical
 * models like linear regression, non-linear regression, fuzzy models, decision trees,
 * partial differential equations and so on. The parameter which describe specific 
 * models, i.e.: a linear regression with one input value like "temp = 0.5 + 3prec" , are specified
 * in the class vtkTAG2EAbstractModelParameter as XML representation. Here "prec" is the name of 
 * the vtkPointData or vtkCellData array which is the input of the linear regression model and
 * "temp" is the name of the resulting data array in the vtkTemporalDataSet ouput.
 * 
 * vtkTAG2EAbstractModel expects a vtkTemporalDataSet as input and generates
 * a vtkTemporalDataSet as output. Two methods are provided to specify the model parameter:
 * <ul>
 *   <li>A single model parameter of type vtkTAG2EAbstractModelParameter</li>
 *   <li>A collection of model parameter of type vtkTAG2EModelParameterCollection</li>
 * </ul>
 * 
 * The subclasses of this abstract class must decide which one should be used. 
 * In case the model parameter collection is used a single output must be computed.
 * 
 * 
 * 
 */

#ifndef vtkTAG2EAbstractModel_H
#define	vtkTAG2EAbstractModel_H

#include <vtkTemporalDataSetAlgorithm.h>
#include <assert.h>
#include "vtkTAG2EAbstractModelParameter.h"
#include "vtkTAG2EModelParameterCollection.h"

class vtkTAG2EAbstractModel : public vtkTemporalDataSetAlgorithm {
public:
    vtkTypeRevisionMacro(vtkTAG2EAbstractModel, vtkTemporalDataSetAlgorithm);
    static vtkTAG2EAbstractModel *New(); 

    //!\brief Set a single model parameter which should be used to process the input data
    vtkSetObjectMacro(ModelParameter, vtkTAG2EAbstractModelParameter);
    //!\brief Get the single model parameter
    vtkGetObjectMacro(ModelParameter, vtkTAG2EAbstractModelParameter);
    
    //!\Brief Set the name of the result array
    vtkSetStringMacro(ResultArrayName);
    //!\brief Get the name of the result array
    vtkGetStringMacro(ResultArrayName);
    
    vtkGetMacro(UseCellData, int);
    //!\brief Switch the procession of the data attached to the cells of 
    //! spatio-temporal input data set on/off. Default is off.
    vtkBooleanMacro(UseCellData, int);
    
protected:
    vtkTAG2EAbstractModel();
    ~vtkTAG2EAbstractModel();
    
    vtkSetMacro(UseCellData, int);

    virtual int RequestData(vtkInformation *, vtkInformationVector **, vtkInformationVector *) {
        assert("RequestData must be implemented in a subclass");
        return -1;
    }

    vtkTAG2EAbstractModelParameter *ModelParameter;
    
    int UseCellData;
    char *ResultArrayName;

private:
    vtkTAG2EAbstractModel(const vtkTAG2EAbstractModel& orig); // Not implemented.
    void operator=(const vtkTAG2EAbstractModel&); // Not implemented.
};

#endif	/* vtkTAG2EAbstractModel_H */
