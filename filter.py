import numpy
import sys
from gainsol import StationGain
from parmdb import WriteableParmDB

SIGMA = 3

if __name__ == "__main__":
    pdbfile = sys.argv[1]
    pdb = WriteableParmDB(pdbfile)
    stations = [name.split(":")[-1] for name in pdb.getNames()]
    pdb = None

    for station in stations:
        station = StationGain(pdbfile, station)
        for pol in station.values():
            median = numpy.median(pol.amp)
            stddev = numpy.std(pol.amp)
            pol.amp = numpy.where(numpy.abs(pol.amp-median) > SIGMA * stddev, median,pol.amp)
        station.writeout()
