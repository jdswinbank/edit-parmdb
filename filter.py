import sys
import numpy
from gainsol import StationGain
from parmdb import WriteableParmDB
from matplotlib import pyplot as plt
from scipy.interpolate import UnivariateSpline
from twisted.python import usage

class Options(usage.Options):
    optFlags = [
        ["last", None, "Include last value"]
    ]
    optParameters = [
        ["sigma", None, 3, "Clip at sigma * median", float]
    ]

    def parseArgs(self, *files):
        self['files' ] = files

def onclick(event):
    print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(event.button, event.x, event.y, event.xdata, event.ydata)

if __name__ == "__main__":
    config = Options()
    try:
        config.parseOptions()
    except usage.UsageError, errortext:
        print '%s: %s' % (sys.argv[0], errortext)
        print '%s: Try --help for usage details.' % (sys.argv[0])
        sys.exit(1)

    for pdbfile in config['files']:
        pdb = WriteableParmDB(pdbfile)
        stations = sorted(set(name.split(":")[-1] for name in pdb.getNames()))
        pdb = None

        for station in stations:
            station = StationGain(pdbfile, station)
            fig = plt.figure()
            fig.suptitle(station.station)
    #        cid = fig.canvas.mpl_connect('button_press_event', onclick)
            for ctr, value in enumerate(station.iteritems()):
                pol, data = value
                if not config['last']:
                    amplitudes = data.amp[:-1]
                    timescale = station.timescale[:-1] - station.timescale[0]
                else:
                    amplitudes = data.amp
                    timescale = station.timescale - station.timescale[0]

                smoothed = UnivariateSpline(timescale, amplitudes)
                median = numpy.median(amplitudes)
                stddev = numpy.std(amplitudes)
                ax = fig.add_subplot(len(station), 1, len(station)-ctr)
                ax.set_ylabel("%s amplitude" % pol)
                if ctr == 0: ax.set_xlabel("Time [s]")
                ax.plot(timescale, amplitudes, color='b', marker='.', ls='')
                ax.plot(timescale, smoothed(timescale), color='r', marker='', ls='-')
                ax.plot(timescale, smoothed(timescale)-stddev, color='g', marker='', ls='--')
                ax.plot(timescale, smoothed(timescale)+stddev, color='g', marker='', ls='--')
                #ax.plot(station.timescale-station.timescale[0], smoothed(station.timescale-station.timescale[0])-stddev, color='g', marker='', ls='--')
                #ax.plot(station.timescale-station.timescale[0], smoothed(station.timescale-station.timescale[0])+stddev, color='g', marker='', ls='--')
                ax.axhline(median, color='r')#, 'r-')
    #            ax.axhline(median+stddev, color='g', ls='--')
    #            ax.axhline(median-stddev, color='g', ls='--')
            print "about to show..."
            plt.show()
    #            median = numpy.median(pol.amp)
    #            stddev = numpy.std(pol.amp)
    #            pol.amp = numpy.where(numpy.abs(pol.amp-median) > config['sigma'] * stddev, median,pol.amp)
    #        station.writeout()
