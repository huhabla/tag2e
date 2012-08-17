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
 * \brief This class uses the SimulatedAnnealing algorithm and derived formes to calibrate
 * models. 
 * 
 * Two inputs must be provided. First the model which should be calibrated. The model
 * must be of type vtkTAG2ESimulatedAnnealingCalibratableModel and must be initialized correctly,
 * except for the model parameter. The second input is the model parameter which must be of
 * type vtkTAG2ESimulatedAnnealingCalibratableModelParameter. The model parameter will be successively 
 * modified to fit the searched taregt functions. To compute the best fit the target
 * values must be present in the output of the model. Only the first output of a model
 * is used.
 * 
 * The best fittet result of the model will be available as output of this class.
 */

#ifndef vtkTAG2ESimulatedAnnealingModelCalibrator_H
#define	vtkTAG2ESimulatedAnnealingModelCalibrator_H

#include "vtkTAG2EAbstractModelCalibrator.h"

class vtkDataSet;
class vtkTemporalDataSet;
class vtkDataArray;

class vtkTAG2ESimulatedAnnealingModelCalibrator : public vtkTAG2EAbstractModelCalibrator {
public:
    vtkTypeRevisionMacro(vtkTAG2ESimulatedAnnealingModelCalibrator,
        vtkTAG2EAbstractModelCalibrator);
    static vtkTAG2ESimulatedAnnealingModelCalibrator *New(); 
    
    //!\brief The maximum number of iteration used for calibration, default 5000
    vtkSetMacro(MaxNumberOfIterations, int);
    vtkGetMacro(MaxNumberOfIterations, int);
    //!\brief The standard deviation of a normal distribution which is used to
    //! modify the parameter of the model, default 1
    vtkSetMacro(StandardDeviation, double);
    vtkGetMacro(StandardDeviation, double);
    //!\brief The break criteria which describes the maximum difference between
    //! the model result and the target variable, default 0.01
    vtkSetMacro(BreakCriteria, double);
    vtkGetMacro(BreakCriteria, double);
    //!\brief The initial temperature, default 1
    vtkSetMacro(InitialT, double);
    vtkGetMacro(InitialT, double);
    //!\brief The term to minimize the initial temperature each
    //! step a poor result is accepted, default 1.001
    vtkSetMacro(TMinimizer, double);
    vtkGetMacro(TMinimizer, double);
    //!\brief The seed used for random number generation
    //! initialization, default current time
    vtkSetMacro(Seed, unsigned int);
    vtkGetMacro(Seed, unsigned int);
    
    //!\brief Return the best fit error of the calibration run
    vtkGetMacro(BestFitError, double);
    //!\brief Return the best fit modell assessment factor of the calibration run
    vtkGetMacro(BestFitModelAssessmentFactor, double);
    
    //!\brief Get the calibrated model parameter
    vtkGetObjectMacro(BestFitModelParameter, vtkTAG2EAbstractCalibratableModelParameter);
    
protected:
    vtkTAG2ESimulatedAnnealingModelCalibrator();
    ~vtkTAG2ESimulatedAnnealingModelCalibrator();

    virtual int RequestData(vtkInformation *, vtkInformationVector **, vtkInformationVector *);

    int MaxNumberOfIterations;
    unsigned int Seed;
    double StandardDeviation;
    double BreakCriteria;
    double InitialT;
    double TMinimizer;
    double BestFitError;
    double BestFitModelAssessmentFactor;
    
    vtkTAG2EAbstractCalibratableModelParameter *BestFitModelParameter;
    
private:
    vtkTAG2ESimulatedAnnealingModelCalibrator(const vtkTAG2ESimulatedAnnealingModelCalibrator& orig); // Not implemented.
    void operator=(const vtkTAG2ESimulatedAnnealingModelCalibrator&); // Not implemented.
};

#endif	/* vtkTAG2ESimulatedAnnealingModelCalibrator_H */
