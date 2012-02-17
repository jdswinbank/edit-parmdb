===========
edit-parmdb
===========

This software was created in support of `LOFAR's <http://www.lofar.org/>`_
`Multifrequency Snapshot Sky Survey
<http://www.astron.nl/about-astron/press-public/news/international-lofar-radio-telescope-kicks-all-sky-survey/internationa>`_
(MSSS) during the week of 13 to 17 February 2012.

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


