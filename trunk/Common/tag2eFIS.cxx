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
#include <iomanip>
#include <math.h>
#include "tag2eFIS.h"

using namespace std;

#define TOLERANCE 0.002

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
//!\brief Interpolate the y value of a standard normal distribution at position x
//!\param x the position in the standard normal distribution
//!\return The interpolated value
static double InterpolatePointInNormDist (double x);

//----------------------------------------------------------------------------

bool tag2eFIS::ComputeRuleCodeMatrixEntries(std::vector< std::vector<int> > &RuleCodeMatrix, int numberOfRules, FuzzyInferenceScheme &FIS)
{
  int col, row, length, length1, dum, inp, num, num1;
  int numberOfFactors = FIS.Factors.size();

  // Compute the rule code matrix which contains the 
  // permutation of all factors. The matrix entries are
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
      FuzzyFactor &Factor = FIS.Factors[dum];
      length = length * Factor.Sets.size();
      dum = dum + 1;
    }
    length1 = 1;
    dum = col;
    while (dum <= numberOfFactors - 1) {
      FuzzyFactor &Factor = FIS.Factors[dum];
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

double tag2eFIS::ComputeFISResult(double *Input,
  int numberOfRules, std::vector< std::vector<int> > &RuleCodeMatrix, FuzzyInferenceScheme &FIS, std::vector<double> &DOFVector)
{
  int rule;
  double result;
  double dof, sum_dofs;

  sum_dofs = 0.0;
  result = 0.0;

  // Compute the deegree of fullfillment for each rule
  for (rule = 0; rule < numberOfRules; rule++) {

    dof = tag2eFIS::ComputeDOF(Input, rule, RuleCodeMatrix, FIS);
    
    DOFVector[rule] = dof;

    sum_dofs = sum_dofs + dof;
    result = result + FIS.Responses.Responses[rule].value * dof;
    //std::cout << "Fuzzy Parameter rule dof value and result " << std::endl;
    //std::cout << rule << " " << dof << " " << FIS.Responses.Responses[rule].value << " " << result << std::endl;
  }

  // Check for wrong results and apply the deegrees of fullfillment
  if (sum_dofs == 0) {
    std::cerr << "Warning in line: " << __LINE__ << ": Sum of deegrees of fullfillments is 0. Expect wrong model results: " << std::endl;
    for(unsigned int i = 0; i < FIS.Factors.size(); i++)
      std::cerr << "  Factor: " << i + 1 << " Value: " << Input[i] << std::endl;
    std::cerr << std::endl;
    result = 0.0;
  } else {
    result = result / sum_dofs;
  }

  return result;
}

//----------------------------------------------------------------------------

double tag2eFIS::ComputeDOF(double *Input,
  int rule, std::vector< std::vector<int> > &RuleCodeMatrix, FuzzyInferenceScheme &FIS)
{
  int numberOfFactors = FIS.Factors.size();
  int d, pos, shape;
  double *dom = new double[numberOfFactors]; // Deegree of membership of a fuzzy set
  double dof; // The resulting deegree of fullfillment for the rule

  d = 0; // counter
  dof = 1; // We need o initialize the resulting DOF with 1
  do {
    pos = (RuleCodeMatrix[rule][d]);
    shape = FIS.Factors[d].Sets[pos].type;
    FuzzyFactor &Factor = FIS.Factors[d];

    //std::cout << "Factor " << d << " Input " << Input[d] << " Rule " << rule << std::endl;
        
    if ((Input[d] > Factor.max) || (Input[d] < Factor.min)) {
      dom[d] = 1;
    } else {
      FuzzySet &Set = FIS.Factors[d].Sets[pos];
      switch (shape) {

      // ATTENTION: The bellshape implementation must be updated to 
      // compute mormalized input values for bellshape interpolation
      case FUZZY_SET_TYPE_BELL_SHAPE: // gauss bell shape fuzzy numbers
        if (Input[d] - Set.BellShape.center <= Factor.min) //left_side of the mean of the fuzzy number
        {
          if ((Input[d] - Set.BellShape.center) / Set.BellShape.sdLeft<-4) {
            dom[d] = 0.0;
          } else {
            dom[d] = InterpolatePointInNormDist((Input[d] - Set.BellShape.center) / Set.BellShape.sdLeft);
          }
        } else { //right side of the mean of the fuzzy number
          if ((Input[d] - Set.BellShape.center) / Set.BellShape.sdRight > 4) {
            dom[d] = 0.0;
          } else {
            dom[d] = InterpolatePointInNormDist((Input[d] - Set.BellShape.center) / Set.BellShape.sdRight);
          }
        }
        break;

      case FUZZY_SET_TYPE_TRIANGULAR: // triangular fuzzy numbers
        double m;
        
        if (Input[d] - Set.Triangular.center <= 0) //left side of the fuzzy number
        {
          if ((Set.Triangular.left) > fabs(Factor.max - Factor.min)) {
            dom[d] = 1.0;
          } else {
            m = 1.0 / Set.Triangular.left;
            dom[d] = max(0.0, m * (Input[d] - Set.Triangular.center) + 1);
          }
          //std::cout << "Left side dom " << dom[d] << std::endl;
        } else//right side of fuzzy number
        {
          if (Set.Triangular.right > fabs(Factor.max - Factor.min)) {
            dom[d] = 1.0;
          } else {
            m = -1.0 / Set.Triangular.right;
            dom[d] = max(0.0, m * (Input[d] - Set.Triangular.center) + 1);
          }
          //std::cout << "Right side dom " << dom[d] << std::endl;
        }
        break;

      case FUZZY_SET_TYPE_CRISP: // all or nothing the split is just in the middle between two alphas
        if (Input[d] >= Set.Crisp.left && Input[d] <= Set.Crisp.right) {
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

  //std::cout << "Deegree of fullfillment " << dof << std::endl;
  return dof;
}

//----------------------------------------------------------------------------

bool tag2eFIS::CheckFuzzyFactor(FuzzyFactor& Factor, bool verbose)
{
  unsigned int j;

  for (j = 0; j < Factor.Sets.size(); j++) {
    FuzzySet &Set = Factor.Sets[j];
    
    //TODO: Implement crisp and bellshape
    if (Set.type == FUZZY_SET_TYPE_TRIANGULAR) {
      
      if(Set.Triangular.center > Factor.max){
	  if(verbose)
              std::cerr << "WARNING: in line " << __LINE__ << "  Center is larger then max:" 
		    << setprecision(15) << Factor.max << " < " 
                    << setprecision(15) << Set.Triangular.center << std::endl;
          return false;
        }        
      
      if(Set.Triangular.center < Factor.min){
	  if(verbose)
              std::cerr << "WARNING: in line " << __LINE__ << "  Center is lower then min:" 
		    << setprecision(15) << Factor.min << " > " 
                    << setprecision(15) << Set.Triangular.center << std::endl;
          return false;
        }        
      
      // Check the center position
      if (Set.position == FUZZY_SET_POISITION_LEFT || Set.position == FUZZY_SET_POISITION_INT) {
        if (Factor.Sets[j + 1].Triangular.center <= Set.Triangular.center) {
	  if(verbose)
              std::cerr << "WARNING:  in line " << __LINE__ << "  Wrong center in fuzzy Sets " << j << " > " << j + 1 
                    << " : " << setprecision(15) << Set.Triangular.center << " and " 
                    << setprecision(15) << Factor.Sets[j + 1].Triangular.center << std::endl;
          return false;
        }  
        if (fabs(Factor.Sets[j + 1].Triangular.left - Set.Triangular.right) > TOLERANCE) {
	  if(verbose)
              std::cerr << "WARNING:  in line " << __LINE__ << "  Triangle shapes are different between fuzzy sets " << j << " and " 
                    << j + 1 << " : " << setprecision(15) << Set.Triangular.right << " and " 
                    << setprecision(15) << Factor.Sets[j + 1].Triangular.left << std::endl;
          return false;
        } 
        double value = Set.Triangular.right + Set.Triangular.center;
        double diff = fabs(Factor.Sets[j + 1].Triangular.center - value);
        if( diff > TOLERANCE){
	  if(verbose)
              std::cerr << "WARNING:  in line " << __LINE__ << "  Triangle shapes of fuzzy sets " << j << " and " 
                    << j + 1 << " are incorrect positioned, difference: " 
                    << setprecision(15) << diff << " center[j]+right " << setprecision(15) << value
                    << " center[j + 1] "  << setprecision(15) << Factor.Sets[j + 1].Triangular.center
                    << std::endl;
          return false;
        }
      }
      
      if (Set.position == FUZZY_SET_POISITION_RIGHT || Set.position == FUZZY_SET_POISITION_INT) {
        if (Factor.Sets[j - 1].Triangular.center >= Set.Triangular.center) {
	  if(verbose)
              std::cerr << "WARNING:  in line " << __LINE__ << "  Wrong center in fuzzy Sets " << j << " < " << j - 1 
                    << " : " << setprecision(15) << Set.Triangular.center << " and " 
                    << setprecision(15) << Factor.Sets[j - 1].Triangular.center << std::endl;
          return false;
        }        
        if (fabs(Factor.Sets[j - 1].Triangular.right - Set.Triangular.left) > TOLERANCE) {
	  if(verbose)
              std::cerr << "WARNING:  in line " << __LINE__ << "  Triangle shapes are different between fuzzy sets " 
                    << j << " and " << j - 1 << " : " << setprecision(15) << Set.Triangular.left << " and " 
                    << setprecision(15) << Factor.Sets[j - 1].Triangular.right << std::endl;
          return false;
        } 
        double value = Set.Triangular.center - Set.Triangular.left;
        double diff = fabs(Factor.Sets[j - 1].Triangular.center - value);
        if( diff > TOLERANCE){
	  if(verbose)
              std::cerr << "WARNING:  in line " << __LINE__ << "  Triangle shapes of fuzzy sets " << j << " and " 
                    << j - 1 << " are incorrect positioned, difference: " 
                    << setprecision(15) << diff << " center[j]+left " << setprecision(15) << value
                    << " center[j - 1] " << setprecision(15) << Factor.Sets[j - 1].Triangular.center
                    << std::endl;
          return false;
        }
      }
    }
  }

  return true;
}
//----------------------------------------------------------------------------

double max(double x, double y)
{
  if (x < y) {
    return y;
  } 
  
  return x;
}

//----------------------------------------------------------------------------

double InterpolatePointInNormDist(double value)
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

bool tag2eFIS::TestFISComputation()
{
  // Create a simple weighted fuzzy inference scheme
  FuzzyInferenceScheme FIS;

  FIS.name = "Test";

  // We have 2 factors with each 2 fuzzy sets
  FuzzyFactor F1; // nrate
  FuzzyFactor F2; // temprature

  FuzzySet F1S1;
  FuzzySet F1S2;

  FuzzySet F2S1;
  FuzzySet F2S2;

  // 4 rules -> 2 * 2 fuzzy sets
  FuzzyResponse R1;
  FuzzyResponse R2;
  FuzzyResponse R3;
  FuzzyResponse R4;

  // Create a factor with two triangle shape fuzzy sets

  // The triangle shape of nrate has the following form
  // nrate min = 0.0 max = 150.0
  //   ___  ___
  //  |   \/   |
  //  |   /\   |
  //  0 60 90  150

  // Create a factor with two triangle shape fuzzy sets

  // The triangle shape of temp has the following form
  // temp min = -15 max = 35
  //   ___  ___
  //  |   \/   |
  //  |   /\   |
  // -15 5  15 35
  
  F1S1.type = FUZZY_SET_TYPE_TRIANGULAR;
  F1S2.type = FUZZY_SET_TYPE_TRIANGULAR;

  F1S1.constant = true;
  F1S2.constant = true;

  F1S1.position = FUZZY_SET_POISITION_LEFT;
  F1S2.position = FUZZY_SET_POISITION_RIGHT;

  F1S1.priority = 0;
  F1S2.priority = 0;

  F2S1.type = FUZZY_SET_TYPE_TRIANGULAR;
  F2S2.type = FUZZY_SET_TYPE_TRIANGULAR;

  F2S1.constant = true;
  F2S2.constant = true;

  F2S1.position = FUZZY_SET_POISITION_LEFT;
  F2S2.position = FUZZY_SET_POISITION_RIGHT;

  F2S1.priority = 0;
  F2S2.priority = 0;
  
  F1S1.Triangular.left = 151;
  F1S1.Triangular.center = 60;
  F1S1.Triangular.right = 30;

  F1S2.Triangular.left = 30;
  F1S2.Triangular.center = 90;
  F1S2.Triangular.right = 151;

  F2S1.Triangular.left = 51;
  F2S1.Triangular.center = 5;
  F2S1.Triangular.right = 10;

  F2S2.Triangular.left = 10;
  F2S2.Triangular.center = 15;
  F2S2.Triangular.right = 51;

  F1.min = 0;
  F1.max = 150;
  F1.name = "nrate";
  F1.portId = 0;
  F1.Sets.push_back(F1S1);
  F1.Sets.push_back(F1S2);

  if(!tag2eFIS::CheckFuzzyFactor(F1))
  {
    return false; 
  }
  
  F2.min = -15;
  F2.max = 35;
  F2.name = "temp";
  F2.portId = 0;
  F2.Sets.push_back(F2S1);
  F2.Sets.push_back(F2S2);
  
  if(!tag2eFIS::CheckFuzzyFactor(F2))
  {
    return false; 
  }

  R1.value = 1;
  R2.value = 2;
  R3.value = 3;
  R4.value = 4;

  FIS.Responses.Responses.push_back(R1);
  FIS.Responses.Responses.push_back(R2);
  FIS.Responses.Responses.push_back(R3);
  FIS.Responses.Responses.push_back(R4);

  FIS.Responses.min = 1;
  FIS.Responses.max = 4;

  FIS.Factors.push_back(F1);
  FIS.Factors.push_back(F2);

  int i, j;
  int numberOfRules = 4;
  int numberOfFactors = 2;

  std::cout << "ComputeRuleCodeMatrixEntries Test" << std::endl;

  // Create the rule code matrix
  std::vector< std::vector<int> > RuleCodeMatrix(numberOfRules, std::vector<int>(numberOfFactors));
  std::vector<double> DOFVector(numberOfRules);

  tag2eFIS::ComputeRuleCodeMatrixEntries(RuleCodeMatrix, numberOfRules, FIS);

  for (i = 0; i < numberOfRules; i++) {
    for (j = 0; j < numberOfFactors; j++) {
      std::cout << RuleCodeMatrix[i][j] << " ";
    }
    std::cout << std::endl;
  }

  if (RuleCodeMatrix[0][0] != 0 ||
    RuleCodeMatrix[0][1] != 0 ||
    RuleCodeMatrix[1][0] != 0 ||
    RuleCodeMatrix[1][1] != 1 ||
    RuleCodeMatrix[2][0] != 1 ||
    RuleCodeMatrix[2][1] != 0 ||
    RuleCodeMatrix[3][0] != 1 ||
    RuleCodeMatrix[3][1] != 1) {
    (std::cerr << "ComputeRuleCodeMatrixEntries failed");
    return false;
  }

  std::cout << "ComputeDOF Test 1 Mean" << std::endl;
  // First test the mean
  double Input[2] = {75.0, 10.0};
  double result;

  result = tag2eFIS::ComputeDOF(Input, 0, RuleCodeMatrix, FIS);
  if (fabs(result - 0.25) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 1 1");
    return false;
  }
  result = tag2eFIS::ComputeDOF(Input, 1, RuleCodeMatrix, FIS);
  if (fabs(result - 0.25) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 1 2");
    return false;
  }
  result = tag2eFIS::ComputeDOF(Input, 2, RuleCodeMatrix, FIS);
  if (fabs(result - 0.25) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 1 3");
    return false;
  }
  result = tag2eFIS::ComputeDOF(Input, 3, RuleCodeMatrix, FIS);
  if (fabs(result - 0.25) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 1 4");
    return false;
  }

  std::cout << "ComputeFISResult Test 1" << std::endl;
  result = tag2eFIS::ComputeFISResult(Input, numberOfRules, RuleCodeMatrix, FIS, DOFVector);
  std::cout << "Result = " << result << std::endl;
  if (fabs(result - 2.5) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeFISResult Test 1");
    return false;
  }

  std::cout << "ComputeDOF Test 2 Left border" << std::endl;

  Input[0] = 0.0;
  Input[1] = -15.0;

  result = tag2eFIS::ComputeDOF(Input, 0, RuleCodeMatrix, FIS);
  if (fabs(result - 1.0) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 2 1");
    return false;
  }
  result = tag2eFIS::ComputeDOF(Input, 1, RuleCodeMatrix, FIS);
  if (fabs(result - 0.0) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 2 2");
    return false;
  }
  result = tag2eFIS::ComputeDOF(Input, 2, RuleCodeMatrix, FIS);
  if (fabs(result - 0.0) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 2 3");
    return false;
  }
  result = tag2eFIS::ComputeDOF(Input, 3, RuleCodeMatrix, FIS);
  if (fabs(result - 0.0) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 2 4");
    return false;
  }

  std::cout << "ComputeFISResult Test 2" << std::endl;
  result = tag2eFIS::ComputeFISResult(Input, numberOfRules, RuleCodeMatrix, FIS, DOFVector);
  std::cout << "Result = " << result << std::endl;
  if (fabs(result - 1.0) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeFISResult Test 2");
    return false;
  }

  std::cout << "ComputeDOF Test 3 right border" << std::endl;

  Input[0] = 150;
  Input[1] = 35;

  result = tag2eFIS::ComputeDOF(Input, 0, RuleCodeMatrix, FIS);
  if (fabs(result - 0.0) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 3 1");
    return false;
  }
  result = tag2eFIS::ComputeDOF(Input, 1, RuleCodeMatrix, FIS);
  if (fabs(result - 0.0) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 3 2");
    return false;
  }
  result = tag2eFIS::ComputeDOF(Input, 2, RuleCodeMatrix, FIS);
  if (fabs(result - 0.0) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 3 3");
    return false;
  }
  result = tag2eFIS::ComputeDOF(Input, 3, RuleCodeMatrix, FIS);
  if (fabs(result - 1.0) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 3 4");
    return false;
  }

  std::cout << "ComputeFISResult Test 3" << std::endl;
  result = tag2eFIS::ComputeFISResult(Input, numberOfRules, RuleCodeMatrix, FIS, DOFVector);
  std::cout << "Result = " << result << std::endl;
  if (fabs(result - 4.0) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeFISResult Test 3");
    return false;
  }

  return true;
}
