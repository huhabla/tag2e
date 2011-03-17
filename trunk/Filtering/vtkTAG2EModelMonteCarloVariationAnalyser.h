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
 * \brief This is a simple implementation of the monte carlo algorithm to be used in
 * uncertainty and sensitivity analysis
 * 
 * This class generates model input data using the monte carlo method and random values based on different 
 * distribution functions. It expects the model input variable distribution description as XML tree
 * and the model which which is used to compute the response values. The model must be 
 * provided full configured, so that all model parameter are set and valid. The input 
 * variable distribution description must fit the model parameter description (equal names
 * and the use of port 0 only). 
 * 
 * The created output includes the vtkTemporalDataSet of the model of the last monte carlo iteration
 * and the result array for all iterations as field data. The name of the result field data array
 * is the same as the result array name of the model.
 * 
 * A simple break criteria is used to check the convergence of the monte carlo iteration,
 * which is the computation of the difference of the max and min value of the normalized cumulative
 * result array. You can set the error break criteria to your needs.
 * 
 * Be aware that the result field data array can become very large for many random variables and iterations.
 * Use this array to compute the distribution and range of your result data.
 * 
 */

#ifndef vtkTAG2EModelMonteCarloVariationAnalyser_H
#define	vtkTAG2EModelMonteCarloVariationAnalyser_H

#include "vtkTAG2EAbstractModelVariationAnalyser.h"

class vtkDataArrayCollection;
class vtkTemporalDataSetSource;
class vtkRInterface;

class vtkTAG2EModelMonteCarloVariationAnalyser : public vtkTAG2EAbstractModelVariationAnalyser {
public:
    vtkTypeRevisionMacro(vtkTAG2EModelMonteCarloVariationAnalyser, vtkTAG2EAbstractModelVariationAnalyser);
    static vtkTAG2EModelMonteCarloVariationAnalyser *New(); 

    //!\brief The maximum number of Iterations used for monte carlo simulation
    vtkSetMacro(MaxNumberOfIterations, int);
    //!\brief The number of random values which should be used in each iteration, default 1000.
    //! The number of random values must be reasonable large, because the break criteria is computed 
    //! within each time steps based on the current number of random values and the cumulative sum over
    //! all generated result values.
    vtkSetMacro(NumberOfRandomValues, int);
    //!\brief In case the model needs several time steps to run, the number of time steps
    //! can be set here explicitely. Default is one time step. For each time step 
    //! all random variables are generated so the number of random variables in each iteration
    //! is NumberOfRandomValues * NumberOfTimeSteps.
    vtkGetMacro(NumberOfTimeSteps, int);
    //!\brief Return the number of time steps
    vtkSetMacro(NumberOfTimeSteps, int);
    //!\brief The change in the cumulative sum of the result in each iteration which is used as break criteria
    vtkGetMacro(BreakCriterion, double);
    //!\brief The change in the cumulative sum of the result in each iteration which is used as break criteria
    vtkSetMacro(BreakCriterion, double);
    
protected:
    vtkTAG2EModelMonteCarloVariationAnalyser();
    ~vtkTAG2EModelMonteCarloVariationAnalyser();

    virtual int RequestData(vtkInformation *, vtkInformationVector **, vtkInformationVector *);
    virtual vtkTemporalDataSetSource *GenerateModelInput(int timeSteps);
    virtual vtkDataArrayCollection *GenerateRandomValuesArrayCollection(int timeSteps);
    virtual vtkDataArray *GenerateRandomValueArray(int numRandomValues, const char *df, double param1, double param2);
    virtual double ComputeNormalizedCumulativeSum(vtkDoubleArray *sum, vtkDoubleArray *dist, vtkTemporalDataSet *modeloutput, double startsum, int startcount);
    virtual bool CheckBreakCriterion(vtkDoubleArray *sum);
    
    int NumberOfRandomValues;
    vtkRInterface *RInterface;
    double BreakCriterion;
    vtkDoubleArray *NormalizedCumulativeSum;

private:
    vtkTAG2EModelMonteCarloVariationAnalyser(const vtkTAG2EModelMonteCarloVariationAnalyser& orig); // Not implemented.
    void operator=(const vtkTAG2EModelMonteCarloVariationAnalyser&); // Not implemented.
};

#endif	/* vtkTAG2EModelMonteCarloVariationAnalyser_H */
