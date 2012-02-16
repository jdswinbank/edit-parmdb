from lofar.parmdb import parmdb
import subprocess
import sys
import textwrap

class WriteableParmDB(parmdb):
    def __init__(self, name):
        super(parmdb, self).__init__(name)
        self.pdbname = name

    def setValues(self, name, values, start_freq, freqstep, start_time, timestep):
        """
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
        """
        # This is the sequence of commands passed to parmdbm.
        template = '''
            open table="%(pdbname)s"
            remove %(name)s
            add %(name)s type="scalar", nx=%(freq_steps)s, ny=%(time_steps)s, values=%(values)s, domain=[%(start_freq)s, %(end_freq)s, %(start_time)s, %(end_time)s]
            quit
        '''
        template = textwrap.dedent(template).strip()
        time_steps, freq_steps = values.shape

        # For simplicity of user interface, we take the start values of the
        # axes at the centre of the bin, but we actually need to pass the
        # edges of the bin to parmdbm.
        start_time = start_time - timestep/2
        start_freq = start_freq - freqstep/2

        # Substitute appropriate values into the parmdbm command.
        command = template % {
            "pdbname": self.pdbname,
            "name": name,
            "time_steps": time_steps,
            "freq_steps": freq_steps,
            "values": str(list(values.ravel())),
            "start_freq": start_freq,
            "end_freq": start_freq+freqstep*freq_steps,
            "start_time": start_time,
            "end_time": start_time+timestep*time_steps
        }

        # Execute parmdbm and return the result.
        p = subprocess.Popen(['parmdbm'], stdin=subprocess.PIPE)
        p.communicate(command)
        p.wait()
        if p.returncode:
            raise subprocess.CalledProcessError(p.returncode, cmd)
        else:
            return p.returncode

if __name__ == "__main__":
    p = WriteableParmDB(sys.argv[1])
    initial = p.getValues("Gain:0:0:Imag:CS103LBA")["Gain:0:0:Imag:CS103LBA"]
    print initial['values'].shape
    print initial['times'][0]
    print initial['times'][-1]
    print initial['freqs'][0]
    print initial['freqwidths']
    print initial['values'][60]
    p.setValues("Gain:0:0:Imag:CS103LBA", initial['values'], initial['freqs'][0], initial['freqwidths'][0], initial['times'][0], initial['timewidths'][0])
    final = p.getValues("Gain:0:0:Imag:CS103LBA")["Gain:0:0:Imag:CS103LBA"]
    print final['values'].shape
    print final['times'][0]
    print final['times'][-1]
    print final['freqs'][0]
    print final['freqs'][-1]
    print final['freqwidths']
    print final['values'][60]
