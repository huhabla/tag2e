# @preprocess

# Create a region which works in UTM, LL and other projections
g.region n=80 s=0 e=120 w=0 res=10
# Generate the value maps
#r.mapcalc --o expr="map1 = 5 + 1*row()*sin(row()) + 1*col()*cos(col())"
#r.mapcalc --o expr="map1 = row()"
r.mapcalc --o expr="sfactor = row()"
r.mapcalc --o expr="map1 = exp((row()+col())/40.0)"
r.mapcalc --o expr="map2 = 1 + 3*row()*sin(row()) + 5*col()*cos(col())"
r.mapcalc --o expr="map3 = 8 + 2*row()*sin(row()) + 2*col()*cos(col())"
# Compute some results
# r = 1 * x
r.mapcalc --o expr="result1 = 1*map1"
# r = 1 * x + 5 * y*y
r.mapcalc --o expr="result2 = 1*map1 + 5 * map2*map2"
# r = 1 * x + 5 * y*y + 0.5 * z * x
r.mapcalc --o expr="result3 = 1*map1 + 5 * map2*map2 + 0.5 * map3 * map1"

r.to.vect --o input=map1 output=map1 type=point column=map1
r.to.vect --o input=map2 output=map2 type=point column=map2
r.to.vect --o input=map3 output=map3 type=point column=map3
r.to.vect --o input=sfactor output=sfactor type=point column=sfactor

r.to.vect --o input=result1 output=result1 type=point column=result1
r.to.vect --o input=result2 output=result2 type=point column=result2
r.to.vect --o input=result3 output=result3 type=point column=result3

v.db.join  map=result1 column=cat otable=map1 ocolumn=cat --v
v.db.join  map=result1 column=cat otable=sfactor ocolumn=cat --v
v.db.join  map=result2 column=cat otable=map1 ocolumn=cat --v
v.db.join  map=result2 column=cat otable=map2 ocolumn=cat --v
v.db.join  map=result3 column=cat otable=map1 ocolumn=cat --v
v.db.join  map=result3 column=cat otable=map2 ocolumn=cat --v
v.db.join  map=result3 column=cat otable=map3 ocolumn=cat --v

#v.fuzzy.calibrator --o input=result1 output=result1_cal factors=map1 target=result1 fuzzysets=2 parameter=result1_param.xml log=result1.log vtkoutput=result1 iter=5000 breakcrit=0.001
#v.db.select map=result1_cal columns=result,result1 > result1.txt
#v.fuzzy.model --o input=result1 param=result1_param.xml output=model1 vtkout=model1_vect
#r.fuzzy.model --o input=map1,result1 param=result1_param.xml output=model1 vtkout=model1_rast
#r.mapcalc --o expr="diff1 = result1 - model1"
#r.univar diff1

# Bootstrap aggregation 
#v.fuzzy.calibrator --o -b input=result1 output=result1a_cal factors=map1 \
#    target=result1 fuzzysets=2 parameter=result1a_param.xml log=result1a.log \
#    vtkoutput=result1a iter=5000 breakcrit=0.001
#v.db.select map=result1a_cal columns=result,result1 > result1a.txt
#v.fuzzy.model --o input=result1 param=result1a_param.xml output=model1a vtkout=model1a_vect
#r.fuzzy.model --o input=map1,result1 param=result1a_param.xml output=model1a vtkout=model1a_rast
#r.mapcalc --o expr="diff1a = result1 - model1a"
#r.univar diff1a

# Bootstrap aggregation and sampling factor
v.fuzzy.calibrator --o -b input=result1 samplingfactor=sfactor output=result1b_cal factors=map1 \
    target=result1 fuzzysets=2 parameter=result1b_param.xml log=result1b.log \
    vtkoutput=result1b iter=5000 breakcrit=0.001
v.db.select map=result1b_cal columns=result,result1 > result1b.txt
v.fuzzy.model --o input=result1 param=result1b_param.xml output=model1b vtkout=model1b_vect
r.fuzzy.model --o input=map1,result1 param=result1b_param.xml output=model1b vtkout=model1b_rast
r.mapcalc --o expr="diff1b = result1 - model1b"
r.univar diff1b



#v.fuzzy.calibrator --o input=result2 output=result2_cal factors=map1,map2 target=result2 fuzzysets=2,3 parameter=result2_param.xml log=result2.log vtkoutput=result2  fuzzyvtk=result2 treduce=1.001 sd=5 sdreduce=1.005 iter=15000 breakcrit=0.01
#v.db.select map=result2_cal columns=result,result2 > result2.txt
#v.fuzzy.model --o input=result2 param=result2_param.xml output=model2 vtkout=model2_vect
#r.fuzzy.model --o input=map1,map2,result2 param=result2_param.xml output=model2 vtkout=model2_rast
#r.mapcalc --o expr="diff2 = result2 - model2"
#r.univar diff2

#v.fuzzy.calibrator --o input=result3 output=result3_cal factors=map1,map2,map3 target=result3 fuzzysets=3,3,3 parameter=result3_param.xml log=result3.log vtkoutput=result3 fuzzyvtk=result3 treduce=1.0002 sd=25 sdreduce=1.001 iter=5000 breakcrit=0.1
#v.db.select map=result3_cal columns=result,result3 > result3.txt
#v.fuzzy.model --o input=result3 param=result3_param.xml output=model3 vtkout=model3_vect
#r.fuzzy.model --o input=map1,map2,map3,result3 param=result3_param.xml output=model3 vtkout=model3_rast
#r.mapcalc --o expr="diff3 = result3 - model3"
#r.univar diff3
