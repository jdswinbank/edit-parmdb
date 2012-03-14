import numpy
import cmath
from parmdb import WriteableParmDB

class ComplexArray(object):
    def __init__(self, real, imag):
        self.data = real + 1j * imag

    def get_amp(self):
        return numpy.absolute(numpy.nan_to_num(self.data))
    def set_amp(self, new_amps):
        self.data = new_amps * self.data / numpy.absolute(self.data)
    amp = property(get_amp, set_amp)

    def get_phase(self):
        return numpy.angle(numpy.nan_to_num(self.data))
    def set_phase(self, new_phase):
        self.data = numpy.vectorize(cmath.rect)(numpy.absolute(self.data), new_phase)
    phase = property(get_phase, set_phase)

    def get_real(self):
        return numpy.real(numpy.nan_to_num(self.data))
    def set_real(self, new_real):
        self.data = new_real + 1j * numpy.imag(self.data)
    real = property(get_real, set_real)

    def get_imag(self):
        return numpy.imag(numpy.nan_to_num(self.data))
    def set_imag(self, new_imag):
        self.data = numpy.real(self.data) + 1j * new_imag
    imag = property(get_imag, set_imag)

class StationGain(dict):
    def __init__(self, parmdbfile, station):
        self.station = station
        self.parmdbfile = parmdbfile

        pdb = WriteableParmDB(self.parmdbfile)
        pols = [
            "%s:%s" % (x[1], x[2]) for x in
            (x.split(":") for x in pdb.getNames("Gain:*:Real:%s" % (station,)))
        ]
        if not pols:
            print "WARNING: No data for %s in %s" % (station, self.parmdbfile)

        for polarization in pols:
            query_real = "Gain:%s:Real:%s" % (polarization, station)
            query_imag = "Gain:%s:Imag:%s" % (polarization, station)
            real = pdb.getValuesGrid(query_real)[query_real]
            imag = pdb.getValuesGrid(query_imag)[query_imag]

            self.timescale = real['times']
            self.timestep = real['timewidths'][0]

            self.freqscale = real['freqs']
            self.freqstep = real['freqwidths'][0]

            self[polarization] = ComplexArray(real["values"], imag["values"])

        pdb = None

    def writeout(self):
        pdb = WriteableParmDB(self.parmdbfile)
        for pol, data in self.iteritems():
            pdb.setValues(
                "Gain:%s:Real:%s" % (pol, self.station),
                data.real,
                self.freqscale[0],
                self.freqstep,
                self.timescale[0],
                self.timestep
            )
            pdb.setValues(
                "Gain:%s:Imag:%s" % (pol, self.station),
                data.imag,
                self.freqscale[0],
                self.freqstep,
                self.timescale[0],
                self.timestep
            )
        pdb = None
