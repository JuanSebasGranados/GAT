import pysal
import csv
import numpy as np

def generateWeights(shapefilepath, csvobspath, rows, col):
    #contiguity based weights.can do distance and others.
    w = pysal.queen_from_shapefile(shapefilepath)

    csvobs = open(csvobspath, newline='')
    csvobs = csv.reader(csvobs)
    row0 = [row[0] for row in csvobs]
    keys = {row0[i] : i for i in range(0, len(row0))} #get row number for observation of interest.
    csvobs = pysal.open(csvobspath, "r")
    csvcol = csvobs.by_col(str(col))
    observations = []
    #if someone wants to only look at a subset of observations:
    if type(rows) == list:
        observations = [csvcol[keys[x]] if x in rows else None for x in row0]
    #Assume that observations=='ALL'
    else: observations = csvcol

    #set order same as observations. assumes that shapefile is ordered the right way.
    # When we get real data we will need to compare locations from shapefile and locations from observations and order that way.
    if not w.id_order_set: w.id_order = list(range(0, len(observations)))

    w.transform = 'r'
    csvobs.close()
    observations = np.array(observations)
    return observations, w

#fill in missing observations with average of values from neighbors. account for fact that neighbors may be missing too.
#easy to implement weighted average as well. Will be useful for weights in terms of distances.
def fillEmpty(observations, w):
    observationstemp = [np.nan if x is None else x for x in observations]
    full, ids = w.full()
    nans = np.where(np.isnan(observationstemp))
    nans = list(nans[0])
    cards = w.cardinalities
    for nan in nans:
        row = list(full[nan])
        numnans = 0
        curtotal = 0
        for i in range(0, len(row)):
            curw = row[i]
            if curw != 0:
                if np.isnan(observationstemp[i]):
                    numnans += 1
                else:
                    curtotal += observationstemp[i]
        avg = curtotal / (cards[nan] - numnans)
        observationstemp[nan] = avg
    return observationstemp

#can extract more info from following objects, right now returns pseudo p-value and calculated statistic and expected value of statistic
#where applicable.
def gamma(similarity, w):
    g = pysal.Gamma(similarity, w, standardize='yes')

    return g.p_sim_g, g.g

def moran(similarity, w):
    m = pysal.Moran(similarity, w, two_tailed='False')

    return m.p_sim, m.I, m.EI

def geary(similarity, w):
    g = pysal.Geary(similarity, w)

    return g.p_sim, g.C, g.EC

def moranLocal(similarity, w):
    m = pysal.Moran_Local(similarity, w)

    return m.p_sim.mean(), m.Is, m.EI_sim

