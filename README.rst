===========
edit-parmdb
===========

These tools are designed to provide an easy-to-use interface for manipulating
the BBS `parameter database
<http://www.lofar.org/operations/doku.php?id=engineering:software:tools:parmdbm>`_.
It provides a wrapper which extends the existing ``lofar.parmdb``
interface, making it possible to write values into the parameter database from
Python code. This is then used to provide a (reasonably!) user-friendly way to
filter bad gain solutions from ``instrument`` databases produced during MSSS
processing.

Filtering an instrument database
--------------------------------

During MSSS LBA observing, data was simultaneously recorded on calibrator
sources and target fields.  Following the proceedure outlined by (for example)
George Heald's "Further tests of MSSS field calibration" document (v2,
2012-02-12), calibration is first applied to the calibrator. Gain solutions
were then applied to the corresponding subbands in the target field.

It was observed in some calibrator observations, there were a number of
outlying amplitudes in these gain solutions, which caused corresponding
amplitude fluctuations when they were applied to the target field. For
example, see the figure below.

.. figure:: https://github.com/jdswinbank/edit-parmdb/raw/master/images/outliers.png
   :alt: Example of outliers
   :width: 50%

   Observe the two low amplitude outliers marked with crosses in this gain
   solution. When these gains are used to calibrate the target field, peaks in
   amplitude will result.

``edit_parmdb.py`` makes it easy to strip such outliers from the gain
solutions by clipping at some multiple of the RMS around the median.

An end user on the LOFAR CEP2 can run the code as
``~swinbank/edit_parmdb/edit_parmdb.py``. A (brief) help message is provided
by the ``--help`` option::

  $ ~swinbank/edit_parmdb/edit_parmdb.py --help
  Usage: edit_parmdb.py [options]
  Options:
        --auto         Automatic mode
        --last         Include last value
        --sigma=       Clip at sigma * median [default: 3]
        --station=     Process this station
        --version
        --help         Display this help and exit.

Run this command by providing an instrument database on the command line. For
example::

  $ ~swinbank/edit_parmdb/edit_parmdb.py L41977_SAP002_SB215.MS.dppp/instrument

The code will loop over all stations in instrument database. For each
polarization on each station, a pair of plots are displayed: in the upper
panel, the blue dots so the measured amplitudes. The median is a red line,
while the RMS is indicated by dashed green lines. Points which diverge from
the median by more than the threshold (by default 3; set this with the
``--sigma`` option) are marked with a cross. In the lower, those points have
been set equal to the median.  In order to write the corrected amplitudes to
the instrument database, hit 'w'. In order to quit, 'q'. In order to move to
the next plot, close the plot window.

It is possible to limit the stations which will be processed using the
``--station`` argument. This argument may be applied more than once:
``--station CS001LBA --station CS002LBA``, etc.

If you want to apply the same threshold to many stations without checking by
eye, specify the ``--auto`` option. In this mode, the threshold will be
applied to all stations (or to those specified by ``--station``)
automatically, without plotting.

The last value recorded in the instrument database usually seems to be garbage
(?). By default, we exclude it from all process. To include it, specify the
``--last`` option.

Python interface to station gains
---------------------------------

``parmdb.StationGain`` provides a convenient Python interface for manipulating
station gains. It is used by the ``edit_parmdb.py`` script.

Instantiate an instance of StationGain by providing the filename of an
instrument database and the name of the station requested. A dictionary like
interface is available for working with the gains in the various
polarizations. Data is available both as (amplitude, phase) and (real,
imaginary)::

  >>> from parmdb.stationgain import StationGain
  >>> sg = StationGain('instrument', 'CS002LBA')
  >>> sg.keys()
  ['1:1', '0:0']
  >>> sg['0:0'].amp[:2]
  array([[ 0.02724993],
       [ 0.02954095]])
  >>> sg['0:0'].phase[:2]
  array([[ 0.27146159],
       [ 0.49976455]])
  >>> sg['0:0'].real[:2]
  array([[ 0.02625204],
       [ 0.02592796]])
  >>> sg['0:0'].imag[:2]
  array([[ 0.00730679],
       [ 0.01415658]])

Note that assigning to one of ``amp``/``phase``/``real``/``imag`` will ensure
the others are updated appropriately::

  >>> sg['0:0'].amp = 100 * sg['0:0'].amp
  >>> sg['0:0'].real[:2]
  array([[ 2.62520381],
       [ 2.59279551]])

(Note that updating individual elements of these numpy arrays might have
unintended consequences -- best to assign to the whole thing at once!)

Writeable ParmDBs in Python
---------------------------

The ``lofar.parmdb`` module provides a convenient way of reading data from
parameter databases, but does not make it possible to write to the database.
This is, however, possible using the `parmdbm
<http://www.lofar.org/operations/doku.php?id=engineering:software:tools:parmdbm>`_
command line tool.

``parmdb.WriteableParmDB`` subclasses ``lofar.parmdb.parmdb`` to add a
``setValues()`` method which can be used to write to the ParmDB. It does this
by spawning an instance of ``parmdbm``: this is potentially risky (locking
issues!), but seems to work in practice.

The documentation for ``setValues()`` is::

   Write values to the ParmDB.

   Note that values should be a two dimenstional array with the first
   index corresponding to time and the second to time (this is the same
   as returned by ParmDB.getValues()).

   Arguments:

   name       -- Parameter name to write.
   values     -- NumPy array of values to write.
   start_freq -- Frequency at centre of first bin (Hz).
   freqstep   -- Bin-to-bin frequency increment (Hz).
   start_time -- Time at centre of first bin (MJD in seconds).
   timestep   -- Bin-to-bin time increment (s).

Testimonials
------------

"This is really good!" -- Alexander van der Horst.

Author
------

`John Swinbank <mailto:swinbank@transientskp.org>`_. Comments and suggestions
welcome, as are bug reports: the code definitely needs more work.

This software was created in support of `LOFAR's <http://www.lofar.org/>`_
`Multifrequency Snapshot Sky Survey
<http://www.astron.nl/about-astron/press-public/news/international-lofar-radio-telescope-kicks-all-sky-survey/internationa>`_
(MSSS) during the week of 13 to 17 February 2012.
