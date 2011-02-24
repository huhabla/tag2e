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

#ifndef vtkTAG2EModelMonteCarloVariationAnalyser_H
#define	vtkTAG2EModelMonteCarloVariationAnalyser_H

#include "vtkTAG2EAbstractModelVariationAnalyser.h"

class vtkDataArrayCollection;
class vtkTemporalDataSetSource;

class vtkTAG2EModelMonteCarloVariationAnalyser : public vtkTAG2EAbstractModelVariationAnalyser {
public:
    vtkTypeRevisionMacro(vtkTAG2EModelMonteCarloVariationAnalyser, vtkTAG2EAbstractModelVariationAnalyser);
    static vtkTAG2EModelMonteCarloVariationAnalyser *New(); 

    //!\brief The maximum number of Iterations used for monte carlo simulation
    vtkSetMacro(MaxNumberOfIterations, int);
    //!\brief The number of random values which should be used in each iteration, default 1000
    vtkSetMacro(NumberOfRandomValues, int);
    //!\brief In case the model needs several time steps to run, the number of time steps
    //! can be set here explicitely. Default is one time step.
    vtkGetMacro(NumberOfTimeSteps, int);
    //!\brief Return the number of time steps
    vtkSetMacro(NumberOfTimeSteps, int);
protected:
    vtkTAG2EModelMonteCarloVariationAnalyser();
    ~vtkTAG2EModelMonteCarloVariationAnalyser();

    virtual int RequestData(vtkInformation *, vtkInformationVector **, vtkInformationVector *);
    virtual vtkTemporalDataSetSource *GenerateModelInput(int timeSteps);
    virtual vtkDataArrayCollection *GenerateRandomValuesArrayCollection(int timeSteps);
    virtual vtkDataArray *GenerateRandomValueArray(int numRandomValues, const char *df, double param1, double param2);
    
    int NumberOfRandomValues;

private:
    vtkTAG2EModelMonteCarloVariationAnalyser(const vtkTAG2EModelMonteCarloVariationAnalyser& orig); // Not implemented.
    void operator=(const vtkTAG2EModelMonteCarloVariationAnalyser&); // Not implemented.
};

#endif	/* vtkTAG2EModelMonteCarloVariationAnalyser_H */
