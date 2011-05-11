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
 * \brief This is the abstract base class for algorithms which are used to calibrate 
 * statistical models. 
 * 
 * A subclass might be the simulated annealing algorithm, which is used to 
 * calibrate fuzzy inference models. This class expects calibartable models and 
 * model parameter as well as an spatio-temporal input with measured data 
 * to validate the model quality. The output should contain the best fit of the model
 * result and the measured data as well as the differences.
 * 
 * 
 */

#ifndef vtkTAG2EAbstractModelCalibrator_H
#define	vtkTAG2EAbstractModelCalibrator_H

#include <vtkTemporalDataSetAlgorithm.h>
#include "vtkTAG2EAbstractCalibratableModel.h"
#include "vtkTAG2EAbstractCalibratableModelParameter.h"

class vtkDataSet;
class vtkTemporalDataSet;
class vtkDataArray;

class vtkTAG2EAbstractModelCalibrator : public vtkTemporalDataSetAlgorithm {
public:
    vtkTypeRevisionMacro(vtkTAG2EAbstractModelCalibrator, vtkTemporalDataSetAlgorithm);
    static vtkTAG2EAbstractModelCalibrator *New(); 
    
    //!\brief Set the model which should be calibrated
    vtkSetObjectMacro(Model, vtkTAG2EAbstractCalibratableModel);
    //!\brief Get the calibrated model
    vtkGetObjectMacro(Model, vtkTAG2EAbstractCalibratableModel);
    
    //!\brief Set the model parameter which should be used as calibration base
    vtkSetObjectMacro(ModelParameter, vtkTAG2EAbstractCalibratableModelParameter);
    //!\brief Get the calibrated model parameter
    vtkGetObjectMacro(ModelParameter, vtkTAG2EAbstractCalibratableModelParameter);
    
    //!\brief Compare two data arrays of a temporal dataset 
    //! using the normative least squares algorithm
    //!\return the assessment value [0:1] in which 1 is worse and 0 is perfect match
    static double CompareTemporalDataSets(vtkTemporalDataSet *tds, 
                                           const char *ModelResultArrayName, 
                                           const char *TargetArrayName, 
                                           bool useCellData, bool verbose);
    
    //!\brief Compare the active scalar data arrays of two temporal dataset 
    //! using the normative least squares algorithm
    //!\return the assessment value [0:1] in which 1 is worse and 0 is perfect match
    static double CompareTemporalDataSets(vtkTemporalDataSet *tds1, vtkTemporalDataSet *tds2,
                                           bool useCellData, bool verbose);
    
    static double ArithmeticMean(vtkDataArray *data);
    static double StandardDeviation(vtkDataArray *data);
    static double Variance(vtkDataArray *data);

protected:
    vtkTAG2EAbstractModelCalibrator();
    ~vtkTAG2EAbstractModelCalibrator();

    virtual int RequestData(vtkInformation *, vtkInformationVector **, vtkInformationVector *) {
        vtkErrorMacro("RequestData must be implemented in a subclass");
        return -1;
    }
    
    vtkTAG2EAbstractCalibratableModel *Model;
    vtkTAG2EAbstractCalibratableModelParameter *ModelParameter;
    
private:
    vtkTAG2EAbstractModelCalibrator(const vtkTAG2EAbstractModelCalibrator& orig); // Not implemented.
    void operator=(const vtkTAG2EAbstractModelCalibrator&); // Not implemented.
};

#endif	/* vtkTAG2EAbstractModelCalibrator_H */
