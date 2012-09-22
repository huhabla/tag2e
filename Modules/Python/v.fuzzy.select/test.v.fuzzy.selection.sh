# @preprocess

# Create a region which works in UTM, LL and other projections
g.region n=15 s=0 e=12 w=0 res=1
# Generate the value maps
#r.mapcalc --o expr="map1 = 5 + 1*row()*sin(row()) + 1*col()*cos(col())"
#r.mapcalc --o expr="map1 = row()"
r.mapcalc --o expr="sfactor = row()"
r.mapcalc --o expr="weight = col()"
r.mapcalc --o expr="map1 = row()"
r.mapcalc --o expr="map2 = row()*col()/100.0"
r.mapcalc --o expr="map3 = sin(row() + col())"

# Compute some result
# r = x + y*y + z * x
r.mapcalc --o expr="result_mapcalc = map1 + map2*map2 + map3 * map1"

r.to.vect --o input=map1 output=map1 type=point column=map1
r.to.vect --o input=map2 output=map2 type=point column=map2
r.to.vect --o input=map3 output=map3 type=point column=map3
r.to.vect --o input=weight output=weight type=point column=weight
r.to.vect --o input=sfactor output=sfactor type=point column=sfactor

r.to.vect --o input=result_mapcalc output=result_mapcalc type=point column=result_mapcalc

v.db.join  map=result_mapcalc column=cat otable=map1 ocolumn=cat --v
v.db.join  map=result_mapcalc column=cat otable=map2 ocolumn=cat --v
v.db.join  map=result_mapcalc column=cat otable=map3 ocolumn=cat --v
v.db.join  map=result_mapcalc column=cat otable=weight ocolumn=cat --v
v.db.join  map=result_mapcalc column=cat otable=sfactor ocolumn=cat --v

# @test
v.fuzzy.select --o input=result_mapcalc factors=map1,map2,map3 \
                   target=result_mapcalc fuzzysets=2,3 rsum=RSummary.txt rpdf=RSummary.pdf \
                   iter=70000 runs=10 sdepth=3 result=Result.txt  treduce=1.02 sdreduce=1.02\
                   breakcrit=0.0001

v.fuzzy.select --o -b input=result_mapcalc factors=map1,map2,map3 \
                   target=result_mapcalc fuzzysets=2,3 rsum=RSummary_bagging.txt rpdf=RSummary_bagging.pdf \
                   iter=70000 runs=10 sdepth=3 result=Result_bagging.txt  treduce=1.02 sdreduce=1.02\
                   breakcrit=0.0001 samplingfactor=sfactor


v.fuzzy.select --o input=result_mapcalc factors=map1,map2,map3 \
                   target=result_mapcalc fuzzysets=2,3 rsum=RSummary_weitght.txt rpdf=RSummary_weight.pdf \
                   iter=70000 runs=10 sdepth=3 weightnum=12 weightfactor=weight \
                   result=Result_weight.txt  treduce=1.02 sdreduce=1.02 -w \
                   breakcrit=0.0001
