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
 * calibrate fuzzy inference models. This class expects calibratable models and
 * model parameter as well as an input with measured data
 * to validate the model quality. The output should contain the best fit of the model
 * result and the measured data as well as the differences.
 * 
 * 
 */

#ifndef vtkTAG2EAbstractModelCalibrator_H
#define	vtkTAG2EAbstractModelCalibrator_H

#include <vtkDataSetAlgorithm.h>
#include "vtkTAG2EAbstractCalibratableModel.h"
#include "vtkTAG2EAbstractCalibratableModelParameter.h"

#define TDS_COMPARE_METHOD_NO_SCALED 1
#define TDS_COMPARE_METHOD_SQRT_SCALED 2
#define TDS_COMPARE_METHOD_LOG_SCALED 3

class vtkDataSet;
class vtkDataSet;
class vtkDataArray;

class vtkTAG2EAbstractModelCalibrator : public vtkDataSetAlgorithm {
public:
    vtkTypeRevisionMacro(vtkTAG2EAbstractModelCalibrator, vtkDataSetAlgorithm);
    static vtkTAG2EAbstractModelCalibrator *New(); 
    
    //!\brief Set the model which should be calibrated
    /**
     * @desc Set the model which should be calibrated
     * 
     * @param Model is of type vtkTAG2EAbstractCalibratableModel 
     */
    vtkSetObjectMacro(Model, vtkTAG2EAbstractCalibratableModel);
    //!\brief Get the calibrated model
    vtkGetObjectMacro(Model, vtkTAG2EAbstractCalibratableModel);
    
    //!\brief Set the model parameter which should be used as calibration base
    vtkSetObjectMacro(ModelParameter, vtkTAG2EAbstractCalibratableModelParameter);
    //!\brief Get the calibrated model parameter
    vtkGetObjectMacro(ModelParameter, vtkTAG2EAbstractCalibratableModelParameter);
    
    //!\brief Compare two data arrays of a dataset
    //! using the normative least squares algorithm
    //! \param ds1: The dataset from which two arrays are compared
    //! \param ModelResultArrayName: The first array with model results
    //! \param TargetArrayName: The second array with measured values
    //! \param useCellData Set: true if the cell data should be used,
    //!     default is point data
    //! \param verbose: Set true to get more info while computation
    //! \param useCorrectedVariance: Set true to use the corrected variance
    //!\return the assessment value [0:1] in which 1 is worse and 0 is perfect match
    static double CompareDataSets(vtkDataSet *ds,
                                           const char *ModelResultArrayName, 
                                           const char *TargetArrayName, 
                                           bool useCellData, bool verbose,
                                           bool useCorrectedVariance);
    
    //!\brief Compare the active scalar data arrays of two dataset
    //! using the normative least squares algorithm
    //! \param ds1: The first dataset from which the active scalars are used
    //! \param ds2: The second dataset from which the active scalars are used
    //! \param useCellData Set: true if the cell data should be used,
    //!     default is point data
    //! \param verbose: Set true to get more info while computation
    //! \param useCorrectedVariance: Set true to use the corrected variance
    //!\return the assessment value [0:1] in which 1 is worse and 0 is perfect match
    static double CompareDataSets(vtkDataSet *ds1, vtkDataSet *ds2,
                                           bool useCellData, bool verbose,
                                           bool useCorrectedVariance);
    
    //!\brief Compute the residuals of the active data arrays in the datasets
    //! \param ds1: The first dataset from which the active scalars are used
    //! \param ds2: The second dataset from which the active scalars are used
    //! \param useCellData Set: true if the cell data should be used,
    //!     default is point data
    //! \param residuals: The array to store the residuals
    //! \param useSquaredResiduals: Set true to compute squared residuals
    static bool ComputeDataSetsResiduals(vtkDataSet *ds1, vtkDataSet *ds2,
                bool useCellData, vtkDataArray *residuals, bool useSquaredResiduals);
    
    static double ArithmeticMean(vtkDataArray *data);
    static double StandardDeviation(vtkDataArray *data, bool useCorrectedVariance);
    static double StandardDeviation(vtkDataSet *ds, const char *ArrayName,
                                    bool useCellData, bool useCorrectedVariance);
    static double Variance(vtkDataArray *data, bool computeCorrectedVariance,
                           bool assumeMeanZero);
    static double Variance(vtkDataSet *ds, const char *ArrayName,
                           bool useCellData, bool computeCorrectedVariance,
                           bool assumeMeanZero);

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
