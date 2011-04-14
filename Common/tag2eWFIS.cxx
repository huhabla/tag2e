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

#include <iostream>
#include <math.h>
#include "tag2eWFIS.h"


/* This is a static array with smapling points and associated values
 * of the standard normal distribution. It is
 * used for faster computation.
 */
static double NormDistSamplingPoints[27][2] = {
  {-4, 0.000335463},
  {-3, 0.011108997},
  {-2.5, 0.043936934},
  {-2, 0.135335283},
  {-1.8, 0.197898699},
  {-1.6, 0.2780373},
  {-1.4, 0.375311099},
  {-1.2, 0.486752256},
  {-1, 0.60653066},
  {-0.8, 0.726149037},
  {-0.6, 0.835270211},
  {-0.4, 0.923116346},
  {-0.2, 0.980198673},
  {0, 1},
  {0.2, 0.980198673},
  {0.4, 0.923116346},
  {0.6, 0.835270211},
  {0.8, 0.726149037},
  {1, 0.60653066},
  {1.2, 0.486752256},
  {1.4, 0.375311099},
  {1.6, 0.2780373},
  {1.8, 0.197898699},
  {2, 0.135335283},
  {2.5, 0.043936934},
  {3, 0.011108997},
  {4, 0.000335463}
};


// Simple maximum computation
static double max(double x, double y);

//----------------------------------------------------------------------------

bool tag2eWFIS::ComputeRuleCodeMatrixEntries(std::vector< std::vector<int> > &RuleCodeMatrix, int numberOfRules, WeightedFuzzyInferenceScheme &WFIS)
{
  int col, row, length, length1, dum, inp, num, num1;
  int numberOfFactors = WFIS.FIS.Factors.size();

  // Compute the rule code matrix which contains the 
  // permutation of all factors. The matrix enries are
  // the ids of the fuzzy set shapes.
  // The size of the matrix is numberOfRules * numberOfFactors.
  // Example:
  //
  // 2 factors with each 2 fuzzy sets == 4 Rules  
  //
  // The resulting matrix is of form:
  // 0 0
  // 0 1
  // 1 0
  // 1 1

  for (col = numberOfFactors - 1; col >= 0; col--) {
    length = 1;
    dum = col + 1;
    while (dum <= numberOfFactors - 1) {
      FuzzyFactor &Factor = WFIS.FIS.Factors[dum];
      length = length * Factor.Sets.size();
      dum = dum + 1;
    }
    length1 = 1;
    dum = col;
    while (dum <= numberOfFactors - 1) {
      FuzzyFactor &Factor = WFIS.FIS.Factors[dum];
      length1 = length1 * Factor.Sets.size();
      dum = dum + 1;
    }
    inp = 0;
    num = 0;
    num1 = 0;
    for (row = 0; row < numberOfRules; row++) {
      RuleCodeMatrix [row][col] = inp;
      num = num + 1;
      num1 = num1 + 1;
      if (num == length) {
        num = 0;
        inp = inp + 1;
      }
      if (num1 == length1) {
        num = 0;
        inp = 0;
        num1 = 0;
      }
    }
  }

  return true;
}

//----------------------------------------------------------------------------

double tag2eWFIS::ComputeFISResult(double *Input,
  int numberOfRules, std::vector< std::vector<int> > &RuleCodeMatrix, WeightedFuzzyInferenceScheme &WFIS)
{
  int rule;
  double result;
  double dof, sum_dofs;

  sum_dofs = 0.0;
  result = 0.0;

  // Compute the deegree of fullfillment for each rule
  for (rule = 0; rule < numberOfRules; rule++) {

    dof = tag2eWFIS::ComputeDOF(Input, rule, RuleCodeMatrix, WFIS);

    sum_dofs = sum_dofs + dof;
    result = result + WFIS.FIS.Responses.Responses[rule].value * dof;
  }

  // Check for wrong results and apply the deegrees of fullfillment
  if (sum_dofs == 0) {
    (std::cerr << "Sum of deegrees of fullfillments is 0. Expect wrong model results.");
    result = 0.0;
  } else {
    result = result / sum_dofs;
  }

  // Weight the result
  if (WFIS.Weight.active) {
    result *= WFIS.Weight.value;
  }

  return result;
}

//----------------------------------------------------------------------------

double tag2eWFIS::ComputeDOF(double *Input,
  int rule, std::vector< std::vector<int> > &RuleCodeMatrix, WeightedFuzzyInferenceScheme &WFIS)
{
  int numberOfFactors = WFIS.FIS.Factors.size();
  int d, pos, shape;
  double *dom = new double[numberOfFactors]; // Deegree of membership of a fuzzy set
  double *normedInput = new double[numberOfFactors]; // Normalized input values
  double dof; // The resulting deegree of fullfillment for the rule

  //cout << "Normed values" << endl;
  // Norm the Input values and write the result in normedInput
  for (d = 0; d < numberOfFactors; d++) {
    normedInput[d] = (Input[d] - WFIS.FIS.Factors[d].min) / (WFIS.FIS.Factors[d].max - WFIS.FIS.Factors[d].min);
    //cout << normedInput[d] << endl;
  }

  d = 0; // counter
  dof = 1; // We need o initialize the resulting DOF with 1
  do {
    pos = (RuleCodeMatrix[rule][d]);
    shape = WFIS.FIS.Factors[d].Sets[pos].type;

    // The value of normedInput at position d is normed [0:1] using its defiend max and min values. 
    // Larger values of 1 are possible in case of the maximum was to low estimated.
    // In case larger values than 10 we assume 
    // the membership is 100%. Values larger than 10 may occure in case values are missing and 
    // replaced by a large default number.
    if ((normedInput[d] > 10) || (normedInput[d] < 0)) {
      dom[d] = 1;
    } else {
      FuzzySet &Set = WFIS.FIS.Factors[d].Sets[pos];
      switch (shape) {

      case FUZZY_SET_TYPE_BELL_SHAPE: // gauss bell shape fuzzy numbers
        if (normedInput[d] - Set.BellShape.center <= 0) //left_side of the mean of the fuzzy number
        {
          if ((normedInput[d] - Set.BellShape.center) / Set.BellShape.sdLeft<-4) {
            dom[d] = 0.0;
          } else {
            dom[d] = InterpolatePointInNormDist((normedInput[d] - Set.BellShape.center) / Set.BellShape.sdLeft);
          }
        } else { //right side of the mean of the fuzzy number
          if ((normedInput[d] - Set.BellShape.center) / Set.BellShape.sdRight > 4) {
            dom[d] = 0.0;
          } else {
            dom[d] = InterpolatePointInNormDist((normedInput[d] - Set.BellShape.center) / Set.BellShape.sdRight);
          }
        }
        break;

      case FUZZY_SET_TYPE_TRIANGULAR: // triangular fuzzy numbers
        double m;

        if (normedInput[d] - Set.Triangular.center <= 0) //left side of the fuzzy number
        {
          if ((Set.Triangular.left) > 1111) {
            dom[d] = 1.0;
          } else {
            m = 1.0 / Set.Triangular.left;
            dom[d] = max(0.0, m * (normedInput[d] - Set.Triangular.center) + 1);
          }
        } else//right side of fuzzy number
        {
          if (Set.Triangular.right > 1111) {
            dom[d] = 1.0;
          } else {
            m = -1.0 / Set.Triangular.right;
            dom[d] = max(0.0, m * (normedInput[d] - Set.Triangular.center) + 1);
          }
        }
        break;

      case FUZZY_SET_TYPE_CRISP: // all or nothing the split is just in the middle between two alphas
        if (normedInput[d] >= Set.Crisp.left && normedInput[d] <= Set.Crisp.right) {
          dom[d] = 1.0;
        } else {
          dom[d] = 0.0;
        }
        break;
      }
    }

    dof *= dom[d]; // Accumulate the deegree of fullfillment
    d++;
  } while (d < (numberOfFactors));

  delete [] dom;
  delete [] normedInput;
  
  //  cout << "Deegree of fullfillment " << dof << endl;
  return dof;
}

//----------------------------------------------------------------------------

double tag2eWFIS::InterpolatePointInNormDist(double value)
{
  int w1 = 0, w2 = 26, w3 = 0;
  double dummy;
  do {
    dummy = (w1 + w2) / 2;
    w3 = floor(dummy);
    if (value > NormDistSamplingPoints[w3 ][0]) {
      w1 = w3;
    } else {
      w2 = w3;
    }
  } while (w1 + 1 < w2);

  return NormDistSamplingPoints[w1][1] +
    (NormDistSamplingPoints[w2][1] -
    NormDistSamplingPoints[w1][1]) /
    (NormDistSamplingPoints[w2][0] -
    NormDistSamplingPoints[w1][0]) *
    (value - NormDistSamplingPoints[w1][0]);
}

//----------------------------------------------------------------------------

double max(double x, double y)
{
  double w;
  if (x < y) {
    w = y;
  } else {
    w = x;
  }
  return w;
}
