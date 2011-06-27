#ifndef TAG2EFIS_H
#define TAG2EFIS_H

#include <vector>

#define FUZZY_SET_POISITION_LEFT 0
#define FUZZY_SET_POISITION_INT 1
#define FUZZY_SET_POISITION_RIGHT 2
#define FUZZY_SET_TYPE_TRIANGULAR 0
#define FUZZY_SET_TYPE_CRISP 1
#define FUZZY_SET_TYPE_BELL_SHAPE 2

// The documentation of the following trivial classes
// is located in the FuzzyInferenceScheme.xsd
// These classes describe the internal represenation of 
// the XML weighted fuzzy inference definition
class FuzzyShapeTriangular{
public:
    double center; // calibrated
    double left;
    double right;
};

class FuzzyShapeCrisp{
public:
    double left; // calibrated
    double right; // calibrated
};

class FuzzyShapeBell{
public:
    double center; // calibrated
    double sdLeft;
    double sdRight;
};

class FuzzySet {
public:
    unsigned int type;
    unsigned int priority;
    unsigned int position;
    bool constant;
    FuzzyShapeTriangular Triangular;
    FuzzyShapeCrisp Crisp;
    FuzzyShapeBell BellShape;
};

class FuzzyFactor {
public:
    int portId;
    std::string name;
    double min;
    double max;
    std::vector<FuzzySet> Sets;
};

class FuzzyResponse{
public:
    bool constant;
    double value;  // calibrated
    double sd;
};

class FuzzyResponses{
public:
    double min;
    double max;
    std::vector<FuzzyResponse> Responses;
};

class FuzzyInferenceScheme {
public:
    std::vector<FuzzyFactor> Factors;
    FuzzyResponses Responses;
    std::string name;
};

/** 
 * This class contains the computation algorithms of the weighted fuzzy inference scheme
 * 
 * 
 * \TODO Add Rene Dechow paper reference
 * 
 */
class tag2eFIS {
public:
   
    //!\brief This method computes the rule code matrix which is used to compute the 
    //! the deegree of membership of an input factor for each rule
    //!\param RuleCodeMatrix The matrix of coded rules
    //!\param numberOfRules Number of rules
    //!\param FIS The internal representation of the weighted fuzzy inference scheme
    //!\return true in case of success
    static bool ComputeRuleCodeMatrixEntries(std::vector< std::vector<int> > &RuleCodeMatrix, 
                         int numberOfRules, FuzzyInferenceScheme &FIS);
    //!\brief Compute the deegree of fullfillment of a single point for a single rule
    //!\param The factor input vector of a single point at a single time step
    //!\param rule The index of a single rule (index of row in the RuleCodeMatrix)
    //!\param RuleCodeMatrix The matrix of coded rules
    //!\param FIS The internal representation of the weighted fuzzy inference scheme
    //!\return The deegree of fullfillment of a single rule
    static double ComputeDOF(double *Input, int rule, std::vector< std::vector<int> > &RuleCodeMatrix, FuzzyInferenceScheme &FIS);

    //!\brief Compute the fuzzy inference scheme result for a single point  
    //!\param The factor input vector of a single point at a single time step
    //!\param numberOfRules Number of rules
    //!\param RuleCodeMatrix The matrix of coded rules
    //!\param FIS The internal representation of the weighted fuzzy inference scheme
    //!\param DOFVector Vector to store the rule specific deegrees of fulfillment, used to model assessment
    //!\return The result of the fuzzy inference scheme computation
    static double ComputeFISResult(double *Input, int numberOfRules, std::vector< std::vector<int> > &RuleCodeMatrix, FuzzyInferenceScheme &FIS, std::vector<double> &DOFVector);
    
    //!\brief Check if the fuzzy factor has correct alligned fuzzy sets
    static bool CheckFuzzyFactor(FuzzyFactor &Factor);
    
    //!\brief Internal unit test of all computational functions. Returns true on success.
    static bool TestFISComputation();

};

#endif	/* TAG2EFIS_H */
