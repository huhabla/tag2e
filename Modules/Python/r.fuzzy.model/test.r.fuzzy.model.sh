# @preprocess

export GRASS_OVERWRITE=1

# Create a region which works in UTM, LL and other projections
g.region n=80 s=0 e=120 w=0 res=10
# Generate the value maps
r.mapcalc  expr="map1 = exp((row()+col())/40.0)"
r.mapcalc  expr="map2 = 1 + 3*row()*sin(row()) + 5*col()*cos(col())"
# r = 1 * x + 5 * y*y
r.mapcalc  expr="model = 1*map1 + 5 * map2*map2"

r.to.vect  input=map1 output=map1 type=point column=map1
r.to.vect  input=map2 output=map2 type=point column=map2

r.to.vect  input=model output=model type=point column=model

v.db.join  map=model column=cat otable=map1 ocolumn=cat --v
v.db.join  map=model column=cat otable=map2 ocolumn=cat --v

# Create the XML parameter file with standard deviation
v.fuzzy.model  input=model param=param.xml mcol=model sigparam=param_sigma.xml output=model_result
# Compute the model result and the cell specific standard deviation
r.fuzzy.model  input=map1,map2 param=param_sigma.xml output=model_result sd=model_sd
