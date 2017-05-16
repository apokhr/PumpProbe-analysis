# -*- coding: utf-8 -*-
"""
Created on Mon May 15 09:57:29 2017

@author: S.Y. Agustsson
"""

from functionlibrary import genericfunctions as gfs
import numpy as np
import scipy as sp
import scipy.signal as spsignal
import matplotlib.pyplot as plt
import os

def main():

    testmat = 'RuCl3-Pr-0.5mW-Pu-1.5mW-T-005.0k-1kAVG.mat'
    testcsv = 'RuCl3- 2017-04-19 17.33.14 Pump1.5mW Temp7.0K.txt'
    testpath = '..//test_scripts//test_data//'
    savepath = "E://DATA//RuCl3//"

    matfile = testpath + testmat
    csvfile = testpath + testcsv


    scan1 = Transient()
    scan2 = Transient()
    scan1.importFile(matfile)

    scan2.importFile(csvfile)




class Transient(object):

    def __init__(self):
        """ Initialize class by defining attributes """

        ######################################
        #                Data                #
        ######################################
        self.raw_time = []          # time data
        self.raw_trace = []      # raw trace data

        self.time = []          # cleaned time axis
        self.trace = []         # cleaned and modified data trace

        ######################################
        #              Metadata              #
        ######################################

        self.material = ''      # Material name
        self.sample = ''        # Sample code name (to identify exact sample measured)
        self.date = ''          # Scan date in format YYYY-MM-DD hh.mm.ss
        self.original_filepath = '' #path to original raw file

        # parameters

        self.pump_power = 0         # Pump Power [mW]
        self.probe_power = 0        # Probe Power [mW]
        self.destruction_power = 0        # Destruction Power [mW]

        #Spot size represents the FWHM diameter from Gaussian fit of the beam profile
        self.pump_spot = 0         # Pump beam spot size [micrometers]
        self.probe_spot = 0        # Probe beam spot size [micrometers]
        self.destruction_spot = 0        # Destruction beam spot size, FWHM [micrometers]
        # excitation densities calculated from power, spotsize and repetition rate
        self.pump_energy = 0
        self.probe_energy = 0
        self.destruction_energy = 0

        # Plarization are measured clockwise in propagation direction of the beam
        self.pump_polarization = 0        # Pump beam polarization [deg], 0 = 12o'clock
        self.probe_polarization = 0       # Probe beam polarization [degg], 0 = 12o'clock
        self.destruction_polarization = 0       # Destruction beam polarization [degg], 0 = 12o'clock
        self.sample_orientation = 0   # Sample orientation, 0 = 12o'clock
        self.temperature = 0    # Temperature [K]
        self.R0 = 0             # Static reflectivity
#        self.T0 = 0             # Static Transimittivity

        ######################################
        #              Analysis              #
        ######################################

        self.analysis_log = {} #keeps track of analysis changes performed\
        self.save_name = ''      # String used as file name for saving data
#        self.parameters = {}    # Dictionary of all parameters, see initParameters()


#        self.metadataUnits = ['pump_power' :
#                              'probe_power',
#                              'destruction_power',
#                              'pump_spot',
#                              'probe_spot',
#                              'destruction_spot',
#                              'pump_energy',
#                              'probe_energy',
#                              'destruction_energy',
#                              'pump_polarization',
#                              'probe_polarization' ,
#                              'destruction_polarization',
#                              'sample_orientation',
#                              'temperature',
#                              'R0',
#                              'T0'
#                              ]

#%% metadata management

    def initMetadata_filename(self):
        """Initializes all metadata variables obtainable from the file name """

        metadata = gfs.name_to_info(self.original_filepath)
        noinfo = True
        for key in metadata:
            if key == 'Scan Date':
                self.date = metadata[key]
                noinfo = False
            elif key == 'Pump Power':
                self.pump_power = metadata[key]
                noinfo = False
            elif key == 'Probe Power':
                self.probe_power = metadata[key]
                noinfo = False
            elif key == 'Temperature':
                self.temperature = metadata[key]
                noinfo = False
            elif key == 'Destruction Power':
                self.destruction_power = metadata[key]
                noinfo = False
            elif key == 'Material':
                self.material = metadata[key]
                noinfo = False
                #print(self.material)
            elif key == 'Pump Spot':
                self.pump_spot = metadata[key]
                noinfo = False
            elif key == 'Probe Spot':
                self.probe_spot = metadata[key]
                noinfo = False
            elif key == 'Other':
                self.other = metadata[key]
                noinfo = False
            else:
                print('Unidentified Key: ' + key)
        if noinfo:
            print('No information obtained from filename ' + str(self.original_filename))
        self.calcEnergyDensities()

    def calcEnergyDensities(self):
        """ recalculate metadata depending on given parameters
        calculates:
               - energy densities
        """
        rep_rate = 283000
        if self.pump_power != 0:
            self.pump_energy = gfs.getEnergyDensity(self.pump_spot,
                                                     self.pump_power,
                                                     rep_rate/2)
        else:
            self.pump_power = 0

        if self.probe_power != 0:
            self.probe_energy = gfs.getEnergyDensity(self.probe_spot,
                                                    self.probe_power,
                                                    rep_rate/2)
        else:
            self.pump_energy = 0

        if self.destruction_power != 0:
            self.destruction_energy = gfs.getEnergyDensity(self.destruction_spot,
                                                           self.destruction_power,
                                                           rep_rate)
        else:
            self.destruction_energy = 0


    def initMetadata(self):
        """Initializes all metadata variables obtainable from the file name,
        when a file has the correct naming structure:
            MaTeRiAl_pu12mW_pr5mW_de50mW_temp4K_pupol45_prpol-45_001.xxx """
        print("method initMetadata still not made...")


    def fetchMetadata(self):
        """ Returns a dictionary containing all metadata information available
            keys are attribute names and values the corresponding value.
        """

        metadata = {}
        var = self.__dict__

        ignore_list = ['time', 'trace', 'raw_time', 'raw_trace']

        for key in var:
            if not key in ignore_list:
                try:
                    # if parameter is a number != 0 append to metadata
                    if float(var[key]) != 0:
                        metadata[key] = var[key]
                # if not a number, and not an empty string
                except ValueError:
                    if len(var[key]) == 0:
                        pass
                    else:
                        metadata[key] = var[key]
                # if not a number, and not an empty list
                except TypeError:
                    if len(var[key]) == 0:
                        pass
                    else:
                        metadata[key] = var[key]

        return(metadata)

    def log_it(self, key, overwrite = False, *args, **kargs):
        """ generate log entry for analysis_log.
            creates a key with given key in analysis_log, making it:
                - boolean if no other args or kargs are given, flips previous
                values written in log
                - list if *args are passed
                - dictionary if **kargs are passed
            if overwrite is False, it appends values on previous logs,
            if True, it obviously overwrites them.
            """

        keystr = 'analysis_log[' + key + ']'
        # make the right type of entry for the log
        if kargs:
            entry = {}
            for key in kargs:
                entry[key] = kargs[key]
        elif args:
            entry = []
            for arg in args:
                entry.append(arg)
        else:
            entry = 'Boolean'
        # Check if previous logs with this key and eventually overwrite/append
        # the new entry.
        try:
            #getattr(self, keystr)
            prev = getattr(self, keystr)
            if entry == 'boolean':
                setattr(self, keystr, not prev)

            elif entry is list:
                if overwrite:
                    setattr(self, keystr, prev + entry)
                else:
                    entry = prev.append(entry)
                    setattr(self, keystr, entry)
            elif entry is dict:
                if overwrite:
                    setattr(self, keystr, prev + entry)
                else:
                    new_entry = {}
                    for key in entry:
                        if key in prev:
                            new_entry[key] = prev[key].append(entry[key])
                        else:
                            new_entry[key] = entry[key]

                    setattr(self, keystr, new_entry)
        except AttributeError:
            setattr(self, keystr, entry)



    def writeMetadata_fromDict(self,mdDict):
        """test method for importing metadata from dictionary"""

        var = self.__dict__

        trackvars = []
        for key in var:
            if mdDict[var]:
                setattr(self,var,mdDict[var])
                trackvars.append(mdDict[var])
        print('Imported the following parameters: ' + ', '.join(trackvars))

    def getUnit(self,parameter):
        ''' Returns the unit of the given parameter.'''
        splitpar = parameter.split('_')
        if splitpar[-1] == 'power':
            return('mW')
        elif splitpar[-1] == 'polarization' or splitpar[-1] == 'orientation':
            return('deg')
        elif splitpar[-1] == 'R0':
            return('V')
        elif splitpar[-1] == 'trace':
            return('')
        elif splitpar[-1] == 'time':
            return('ps')
        elif splitpar[-1] == 'energy':
            return('mJ/cm^2')



#%% Data manipulation

    def cleanData(self,
                  cropTimeScale = True,
                  shiftTime = 0,
                  flipTime = True,
                  removeDC = True,
                  filterLowPass = True,
                  flipTrace = False
                  ):
        '''Perform a standard set of data cleaning'''
        if cropTimeScale:
            self.cropTimeScale()
        if shiftTime:
            self.shiftTime(shiftTime)
        if flipTime:
            self.flipTime()
        if removeDC:
            self.removeDC()
        if filterLowPass:
            self.filterLowPass()
        if flipTrace:
            self.flipTrace()

    def cropTimeScale(self):
        '''chops time scale to the monotonous central behaviour,
        deleting the wierd ends.
        ATTENTION: overwrites self.time and self.trace, deleting any previous changes'''

        # clear previous time and trace, and the analysis log since it goes lost

        self.analysis_log = {}
        self.time = [] #reset
        self.trace = []
        print('crop time scale, len: ' + str(len(self.raw_time)))
        maxT = max(self.raw_time)
        minT = min(self.raw_time)

        if self.raw_time[0]<self.raw_time[1]:
            start=0
            while self.raw_time[start] < maxT:
                start += 1
            end = start
            while self.raw_time[end] > minT:
                end += 1
            print('From' + str(start) + 'to'+ str(end) + 'pos')
            i=0
            while i in range(end-start):
                self.time.append(self.raw_time[i+start])
                self.trace.append(self.raw_trace[i+start])
                i += 1
        elif self.raw_time[0]>self.raw_time[1]:
            start=0
            while self.raw_time[start] > minT:
                start += 1
            end = start
            while self.raw_time[end] < maxT:
                end += 1
            print('Time scale cropped from' + str(start) + 'to'+ str(end) + ', neg')
            i=0
            while i in range(end-start):
                self.time.append(self.raw_time[i+start])
                self.trace.append(self.raw_trace[i+start])
                i += 1
        self.log_it('Crop Time Scale', maxtime = maxT, mintime = minT)

    def shiftTime(self, tshift):
        """ Shift time scale by tshift. Changes time zero
        writes to analysis_log the shifted value, or increases it if already present"""
        self.time = np.array(self.time) - tshift
        self.log_it('Shift Time', tshift)


    def flipTime(self):
        """ Flip time scale: t = -t
        also reverts order in the array"""
        self.time = self.time[::-1]
        self.time = -np.array(self.time)
        self.trace = self.trace[::-1]
        self.log_it('Flip Time')

    def flipTrace(self):
        """ Flip the Y trace, usually not needed from matlab redred software"""
        self.trace = -self.trace
        self.log_it('Flip Trace')

    def removeDC(self, window = 40): # change range in case of flipped scan!!!
        """Remove DC offset.
        offset is caluclated with 40 points (~700fs) taken at negative time delays.
        such delay is at the end of the scan in raw data, or at the beginning
        if scan was reverted by flipTime """

        try:
            if self.analysis_log['Flip Time']: pass
            shift = np.average(self.trace[0:window:1])
        except KeyError:
            tpoints = len(self.time)
            shift = np.average(self.trace[tpoints-window:tpoints:1])
        self.trace = self.trace - shift
        self.log_it('Remove DC', window = window, shift = shift)


    def filterLowPass(self, cutHigh = 0.1, order = 2, return_frequency = False):
        """ apply simple low pass filter to data
        if return_frequency is True, returns the filter frequency value
        in THz ( if time data is in ps)"""

        b, a = spsignal.butter(order, cutHigh, 'low', analog= False)
        self.trace = spsignal.lfilter(b,a,self.trace)
        frequency = gfs.nyqistFreq(self.time) * cutHigh
        self.log_it('Low Pass Filter', frequency = frequency, nyq_factor = cutHigh, order = order)
        if return_frequency:
            return frequency


    def normalizeToParameter(self, parameter):
        """ Normalize scan by dividing by its pump power value"""
        if getattr(self,parameter):
            if getattr(self,parameter) != 0:
                self.trace = self.trace / getattr(self,parameter)
        else: print('Normalization failed: invalid parameter name')
        logkey = 'Normalized by ' + parameter.replace('_',' ')
        self.log_it(logkey)

    def quickplot(self, xlabel='Time [ps]',
                  ylabel='Trace', fntsize=15,
                  title='Transient',
                  clear=False):
        """Generates a quick simple plot with matplotlib """
        if clear: plt.clf()
        quickplotfig=plt.figure(num=1)
        ax=quickplotfig.add_subplot(111)
        ax.plot(self.time, self.trace,)
        ax.set_xlabel(xlabel, fontsize=fntsize)
        ax.set_ylabel(ylabel, fontsize=fntsize)
        ax.set_title(title,fontsize=fntsize)
        ax.tick_params(axis='x', labelsize=fntsize)
        ax.tick_params(axis='y', labelsize=fntsize)
        plt.show()


#%% import export

    def importFile(self,filepath, cleanData = True):
        '''imports a file, csv or .mat'''
        try:
            ext = os.path.splitext(filepath)[-1].lower()
            if ext == '.mat':
                if os.path.basename(filepath).lower() != 't-cal.mat':
                    self.importMatFile(filepath)
                else:
                    print('Ignored t-cal.mat')
            elif ext == '.txt':
                self.importCSV(filepath)
            else:
                print('Invalid format. Couldnt import file: ' + filepath)
            if cleanData:
                self.cleanData()
        except FileNotFoundError:
            print('File ' + filepath + ' not found')



    def importMatFile(self, filepath):
        """Import data from a raw .mat file generated by redred software.
        data contains usually raw_time raw_trace and R0 information.

        """
        self.original_filepath = filepath
        data = sp.io.loadmat(filepath)
        try:
            self.raw_time = data['Daten'][2]
            self.raw_trace = data['Daten'][0]

            self.R0 = data['DC'][0][0]

        except KeyError:
            print(filepath  + ' is not a valid redred scan datafile')


    def importCSV(self, filepath):
        """
        Import data from a .txt file containing metadata in the header.

        Metadata should be coded as variable names from this class:
            material, date, pump_power, temperature, probe_polarization etc...
        Data expected is 4 couloms: raw_time, raw_trace, time, trace.

        filepath should full path to file as string.
        """
        try:
            f = open(filepath, 'r')
            #get metadata from header
            parameters = self.__dict__

            for l in f:
                line = l.split('\t')
                varname = line[0].replace(' ','_').lower()
                if varname in parameters:
                    setattr(self,varname,line[1])
            f.close()
            #get data:
            skipline = True
            n=0
            data = []

            while skipline: # skip metadata section then import array of data
                try:
                    data = np.loadtxt(filepath, delimiter=',', skiprows=n)
                    print(len(data[0]))
                    n+=1
                    skipline = False
                except ValueError:
                    n+=1

#                print(len(data[0]) + 'second')

#           Write in variable taken from column title! its more universal...

                for i in range(len(data)):
                    self.raw_time.append(data[i][0])
                    self.raw_trace.append(data[i][1])
                    self.time.append(data[i][2]) # ???? wtf error???
                    self.trace.append(data[i][3])

        except FileNotFoundError:
                    print('Couldnt find file at location : \n filepath')

    def exportCSV(self, directory):
        """
        save Transient() to a .txt file.
        in csv format (data)
        Metadata header is in tab separated values, generated as
            name/tvalue unit
        data is comma separated values, as
            raw_time, raw_trace, time, trace.

        Metadata is obtained from fetchMetadata(), resulting in all non0
        parameters available.
        """

        file = open(directory + '//' + self.save_name + '.txt', 'w+')


        metadata = self.fetchMetadata()
        parameter = ['','','']

        for key in metadata:
            parameter[0] =  str(key)
            parameter[1] = str(metadata[key])
            parameter[2] = self.getUnit(key)

            file.write('\t'.join(parameter) + '\n')

        #data
        file.write('\n############### Data ###############\n\n')
        file.write('raw_time\t\traw_trace\t\ttime\t\ttrace\n')
        for i in range(len(self.raw_time)):
            string = str(self.raw_time[i])   + ',' + str(self.raw_trace[i])
            if i <= len(self.time):
                string.append(',' + str(self.time[i]) + ','
                              + str(self.trace[i]) + '\n')
            else:
                string.append('\n')

            file.write(string)
        file.close()



if __name__ == "__main__":
    main()