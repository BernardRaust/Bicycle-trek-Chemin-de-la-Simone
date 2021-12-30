#!/usr/bin/env python
# coding: utf-8

# # Read S5000F message header and trailer

# In[6]:


get_ipython().system('ipython nbconvert --to python *.ipynb')


# In[1]:


import glob
import os
list_of_input_files = glob.glob('../Input_folder/*.xml')       # get xml input files to be processed

latest_file = min(list_of_input_files, key=os.path.getctime)   # pick the oldest one

pathname,filename = os.path.split(latest_file)
print(f"'{filename}'")
print()


# In[2]:


import lxml.etree as etree
import datetime as dt
import numpy as np
import pandas as pd
import re
import os

__author__ = "Bernard Raust"
__credits__ = ["Bernard Raust"]
__version__ = "1.0.0"
__maintainer__ = "Bernard Raust"
__email__ = "bernard.raust@gmail.com"
__status__ = "Development"

class Header():
    '''
    Extract header and trailer information of a S5000F message:
    Input: Path of message xml file
    Local attributes: 
        - uid, id, type, date, time, status, sender, receiver, context and classification
        - dict: dictionary containing all previous information
    Exception if some metadata are missing. They are set has mandatory in XSD message envelope.
    '''
    def __init__(self, path):
        with open(path, 'r') as fd:
            tree = etree.parse(fd)
            self.__root = tree.getroot()
            self.__path = path
            self.uid = self.__root.attrib['uid']
            self.id = self.__root.xpath('./msgId/id')[0].text
            self.type = self.__root.xpath('./msgType/code')[0].text
            self.date = self.__root.xpath('./msgDate/date')[0].text
            self.time = self.__root.xpath('./msgDate/time')[0].text
            self.status = self.__root.xpath('./msgStatus/state')[0].text   
            self.context = self.__root.xpath('./msgContext/context/projRef/projId/id')[0].text
            self.classification = self.__root.xpath('./secs/sec/secClassDefRef/secClass/name')[0].text

            _msgPty = self.__root.xpath('./msgPty')
            parties = {}
            for elt in _msgPty:
                type = (elt.xpath('./ptyType/code'))[0].text
                id = (elt.xpath('./party/persRef/persId/id'))[0].text
                parties[type]=id  
            self.sender = parties['S']
            self.receiver = parties['R']
            
            self.dict ={'uid':self.uid,
                        'id':self.id,
                        'type':self.type,
                        'date':self.date,
                        'time':self.time,
                        'status':self.status,
                        'context':self.context,
                        'classif':self.classification,
                        'sender':self.sender,
                        'receiver':self.receiver,}
            
    def __str__(self):
        '''Display message metadata'''
        l0 = f"HEADER and TRAILER of {filename} contains:\n"
        l1 = f"  Message identification = {msg.uid}\n"
        l2 = f"  Message type           = {msg.type}\n"
        l3 = f"  Message issue date     = {msg.date}\n"
        l4 = f"  Message issue time     = {msg.time}\n"
        l5 = f"  Message status         = {msg.status}\n"
        l6 = f"  Message context        = {msg.context}\n"
        l7 = f"  Message classification = {msg.classification}\n"
        l8 = f"  Message sender         = {msg.sender}\n"
        l9 = f"  Message receiver       = {msg.receiver}\n"
        line =[l0,l1,l2,l3,l4,l5,l6,l7,l8,l9]
        return ("".join(line))
    
class CreateHeader():
    
    def __init__(self, metadata):
        '''
        Create an element tree with sub elements header, content and trailer
        input:  dictionary containing all metadata to fill header and trailer
                  uid, type, date, time, status, sender, receiver, context and classification
        Output: element tree with sub-element header, content and trailer.
                Content is an empty element used as placeholder for future message content
        '''
        
        pass
    
class MessageAnswer():
    '''
    Create a message answer to a received message.
    Message answer is either an Acknowledgment or an Observation message'''
    def __init__(self,metadata):
        now = dt.datetime.now()
        date = now.strftime('%Y-%m-%d')
        time = now.strftime('%H:%M:%S.0Z')
        status = ''
        


# In[3]:


head = Header(latest_file)
head.dict


# In[4]:


now = dt.datetime.now()
date = now.strftime('%Y-%m-%d')
time = now.strftime('%H:%M:%S.0Z')
print(date)
print(time)


# In[5]:


# Define pos_hash function which return a positive hash number
# For removing random seed which is set at each Python runtime, set-up PYTHONHASHSEED value 
# %env PYTHONHASHSEED=19531130

import sys
def pos_hash(s):
    h=hash(s)
    if h < 0:
        h += sys.maxsize
    return(str(h))


# In[54]:


import hashlib
def _create_uid():
    '''message uid is msg+ hashcode(message id)'''
    hash_string='BIKE TREK AIX-EN-PROVENCE ON 2020-02-25T06:27:35.000Z msg4762705562253142615'
    return 'msg'+pos_hash(hash_string)


# In[55]:


a = _create_uid()
print(a)


# In[ ]:


class Header_Trailer_Reader:
    def __init__(self, path):
        try:
            with open(path, 'rb') as fd:
                self.dic = xmltodict.parse(fd.read().decode('utf8'))
            self.__path = path
            self.__patientInfoNode = self.dic['sapphire']['dcarRecord']['patientInfo']
            self.__ecgNode = self.__patientInfoNode['visit']['order']['ecgResting']['params']['ecg']['wav']['ecgWaveformMXG']
            self.header = self.__makeHeaderDic()
            self.__makeDataArray()
            self.__makeStructuredArray()

        except Exception: 
            print(traceback.print_exc())
# 
    
    def __makeHeaderDic(self):
        patientInfo = self.__patientInfoHeader()
        deviceInfo = self.__deviceInfoHeader()
        acquisitionInfo = self.__aquisitionInfoHeader()
        return {'PatientInfo': patientInfo, 'DeviceInfo': deviceInfo, 'AcquisitionInfo': acquisitionInfo}


    def __patientInfoHeader(self):
        if('unknownID' in self.__patientInfoNode.keys() or 'name' not in self.__patientInfoNode.keys()):
            given_name = 'Unknown'
            family_name = 'Unknown'
            id = 'Unknown'
        else:
            given_name = self.__patientInfoNode['name']['given']['@V']
            family_name = self.__patientInfoNode['name']['family']['@V']
            id = self.__patientInfoNode['identifier']['id']['@V']
        gender = self.__patientInfoNode['gender']['@V']
        race = self.__patientInfoNode['raceCode']['@V']
        pacemaker = self.__patientInfoNode['visit']['order']['testInfo']['hasPacemaker']['@V']
        return {'Given_Name': given_name, 'Family_Name': family_name, 'ID': id, 'Gender': gender, 'Race': race, 'Pacemaker': pacemaker}

    
    def __deviceInfoHeader(self):
        deviceModel = self.__patientInfoNode['visit']['order']['device']['modelID']['@V']
        deviceName = self.__patientInfoNode['visit']['order']['device']['deviceName']['@V']
        deviceSerial = self.__patientInfoNode['visit']['order']['device']['serialID']['@V']
        return {'DeviceModel': deviceModel, 'DeviceName': deviceName, 'DeviceSerial': deviceSerial}

    
    def __aquisitionInfoHeader(self):
        acquisitionDate = self.__patientInfoNode['visit']['order']['testInfo']['acquisitionDateTime']['@V']
        LeadAmplitudeUnitsPerBit = self.__ecgNode['@S']
        LeadAmplitudeUnits = self.__ecgNode['@U']
        Res = self.__ecgNode['@INV']
        filters = self.__getFilterInfo()
        sampleRate = {'SampleRate': self.__ecgNode['sampleRate']['@V'], 'Units': self.__ecgNode['sampleRate']['@U']}
        leadsInformation = self.__getLeadInfo()
        return {'Resolution': Res, 'AcquisitionDate': acquisitionDate, 'LeadAmplitudeUnitsPerBit': LeadAmplitudeUnitsPerBit, 'LeadAmplitudeUnits': LeadAmplitudeUnits, 'Filters': filters, 'SampleRate': sampleRate, 'LeadsInformation': leadsInformation}

    
    def __getFilterInfo(self):
        highPassNode = self.__ecgNode['filters']['highPass']
        highPass = {'Frequency': highPassNode['frequency']['@V'], 'Units': highPassNode['frequency']['@U'], 'Order': highPassNode['order']['@V']}
        LowPassNode = self.__ecgNode['filters']['lowPass']
        lowPass = {'Frequency': LowPassNode['frequency']['@V'], 'Units': LowPassNode['frequency']['@U'], 'Order': LowPassNode['order']['@V']}
        algorithms = []
        algorithmsNodes = self.__ecgNode['filters']['algorithm']
        for i in algorithmsNodes:
            if(i == 'name'):
                algorithms.append({'Name': algorithmsNodes['name']['@V'], 'Purpose': algorithmsNodes['purpose']['@V']})
                break
            else:
                algorithms.append({'Name': i['name']['@V'], 'Purpose': i['purpose']['@V']})

        return {'HighPass': highPass, 'LowPass': lowPass, 'Algorithms': algorithms}


    def __getLeadInfo(self):
        leadsNames = []
        leadsLabels = []
        for i in self.__ecgNode['ecgWaveform']:
            leadsNames.append(i['@lead'])
            leadsLabels.append(i['@label'])
            self.__numberOfSamples = i['@asizeVT']
        self.__leadsNames = leadsNames
        return {'LeadsNames': leadsNames, 'LeadsLabels': leadsLabels, 'NumberOfSamples': self.__numberOfSamples}


    def __makeDataArray(self):
        self.dataArray = np.zeros((int(self.__numberOfSamples), len(self.__leadsNames)), dtype=int)
        for i in range(0, len(self.__ecgNode['ecgWaveform'])):
            self.dataArray[:, i] = list(map(int, self.__ecgNode['ecgWaveform'][i]['@V'].split(' ')))


    def __makeStructuredArray(self):
        self.dataObject = {}
        for i in range(0, len(self.__ecgNode['ecgWaveform'])):
            self.dataObject[self.__leadsNames[i]] = self.dataArray[:, i]
        
        self.dataFrame = pd.DataFrame(self.dataObject)
        
        self.__data_string = self.dataFrame.to_string(header=False)
        self.__data_string = re.sub(' +',',', self.__data_string)
        self.__header_string = 'nSeq '
        self.__header_string += reduce((lambda x, y: x + ' ' + y), self.__leadsNames)
        self.header['AcquisitionInfo']['HeaderString'] = self.__header_string
    def getLead(self, lead):
        return self.dataFrame[[lead]]


    def __makeOSHeader(self):
        self.__OSHeader = {'00:00:00:00:00:00': {}}
        self.__OSHeader['00:00:00:00:00:00']['sensor'] = ['RAW'] * len(self.__ecgNode['ecgWaveform'])
        self.__OSHeader['00:00:00:00:00:00']['device name'] = self.header['DeviceInfo']['DeviceName']
        self.__OSHeader['00:00:00:00:00:00']['column'] = self.__header_string.split(' ')
        self.__OSHeader['00:00:00:00:00:00']['sync interval'] = 0
        self.__OSHeader['00:00:00:00:00:00']['time'] = (self.header['AcquisitionInfo']['AcquisitionDate'].split('T')[1]+'0').strip()
        self.__OSHeader['00:00:00:00:00:00']['date'] = (self.header['AcquisitionInfo']['AcquisitionDate'].split('T')[0]).strip()
        self.__OSHeader['00:00:00:00:00:00']['comments'] = ''
        self.__OSHeader['00:00:00:00:00:00']['device connection'] = 'BTH00:00:00:00:00:00'
        self.__OSHeader['00:00:00:00:00:00']['channels'] = list(range(1, 1+len(self.__ecgNode['ecgWaveform'])))
        self.__OSHeader['00:00:00:00:00:00']['mode'] = 0
        self.__OSHeader['00:00:00:00:00:00']['digital IO'] = []
        self.__OSHeader['00:00:00:00:00:00']['firmware version'] = 770
        self.__OSHeader['00:00:00:00:00:00']['device'] = 'virtual_plux'
        self.__OSHeader['00:00:00:00:00:00']['position'] = 0
        self.__OSHeader['00:00:00:00:00:00']['sampling rate'] = int(self.header['AcquisitionInfo']['SampleRate']['SampleRate'])
        self.__OSHeader['00:00:00:00:00:00']['label'] = self.__leadsNames
        self.__OSHeader['00:00:00:00:00:00']['resolution'] = [int(self.header['AcquisitionInfo']['Resolution']).bit_length()] * len(self.__ecgNode['ecgWaveform'])
        self.__OSHeader['00:00:00:00:00:00']['special'] = [{}, {}, {}, {}, {}]
        return json.dumps(self.__OSHeader)

    def saveHeader(self, filename):
        temp = open('.{}{}_header.json'.format(os.sep, filename), 'w')
        temp.write(json.dumps(self.header))
        temp.close()


    def saveToCSV(self, filename=None):
        if(filename==None):
            filename = 'GEMuseXML' + strftime("%Y-%m-%d_%H-%M-%S", gmtime())
        temp = open('.{}{}.csv'.format(os.sep, filename), 'w')
        temp.write('# ' + self.__header_string + '\n')
        temp.write(self.__data_string)
        temp.close()
    

    def saveToPandasCSV(self, filename=None, header=True):
        if(filename==None):
            filename = 'GEMuseXML' + strftime("%Y-%m-%d_%H-%M-%S", gmtime())
        self.dataFrame.to_csv('.{}{}_pandas.csv'.format(os.sep, filename))
        if(header):
            self.saveHeader(filename)


    def saveToJson(self, filename=None, header=True):
        if(filename==None):
            filename = 'GEMuseXML' + strftime("%Y-%m-%d_%H-%M-%S", gmtime())
        tempDic = {'Header': self.header, 'Data': {}}
        for i in range(0, len(self.__ecgNode['ecgWaveform'])):
            tempDic['Data'][self.__ecgNode['ecgWaveform'][i]['@lead']] = list(map(int, self.__ecgNode['ecgWaveform'][i]['@V'].split(' ')))
        temp = open('.{}{}.json'.format(os.sep, filename), 'w')
        temp.write(json.dumps(tempDic))
        temp.close()

    
    def saveToExcel(self, filename=None, header=True):
        if(filename==None):
            filename = 'GEMuseXML' + strftime("%Y-%m-%d_%H-%M-%S", gmtime())
        self.dataFrame.to_excel('.{}{}.xls'.format(os.sep, filename))
        if(header):
            self.saveHeader(filename)
    

    def saveNumpyArray(self, filename=None, header=True):
        if(filename==None):
            filename = 'GEMuseXML' + strftime("%Y-%m-%d_%H-%M-%S", gmtime())
        np.save('.{}{}.npy'.format(os.sep, filename), self.dataArray)
        if(header):
            self.saveHeader(filename)


    def saveToOPS(self, filename=None):
        if(filename==None):
            filename = 'GEMuseXML' + strftime("%Y-%m-%d_%H-%M-%S", gmtime())
        temp = open('.{}{}.txt'.format(os.sep, filename), 'w')
        temp.write('# OpenSignals Text File Format\n')
        temp.write('# ' + self.__makeOSHeader() + '\n')
        temp.write('# EndOfHeaders\n')
        temp.write(self.dataFrame.to_string(header=False))
        temp.close()


if __name__ == "__main__":

    def parseArgParser(file, arg, type):
        if(arg == ' '):
            filename = None
        else:
            filename = arg

        if(type == 'csv'):
            file.saveToCSV(filename)
        if(type == 'pcsv'):
            file.saveToPandasCSV(filename)
        elif(type == 'ops'):
            file.saveToOPS(filename)
        elif(type == 'json'):
            file.saveToJson(filename)
        elif(type == 'excel'):
            file.saveToExcel(filename)
        elif(type == 'numpy'):
            file.saveNumpyArray(filename)
        elif(type == 'all'):
            file.saveToCSV(filename)
            file.saveToPandasCSV(filename, False)
            file.saveToOPS(filename)
            file.saveToJson(filename, False)
            file.saveToExcel(filename, False)
            file.saveNumpyArray(filename)


    parser = argparse.ArgumentParser()
    parser.add_argument('file', help="file path")
    parser.add_argument("-csv", help="convert to csv", nargs='?', const=' ')
    parser.add_argument("-pcsv", help="convert to pandas csv", nargs='?', const=' ')
    parser.add_argument("-ops", help="convert to opensignals formated txt", nargs='?', const=' ')
    parser.add_argument("-x", '--excel', help="convert to excel", nargs='?', const=' ')
    parser.add_argument("-np", '--numpy', help="convert to numpy", nargs='?', const=' ')
    parser.add_argument("-json", help="convert to json", nargs='?', const=' ')
    parser.add_argument("-all", help="convert to csv, excel, numpy and json", nargs='?', const=' ')
    args = parser.parse_args()

    file = GEMuseXMLReader(args.file)

    if args.csv:
        parseArgParser(file, args.csv, 'csv')
    
    if args.pcsv:
        parseArgParser(file, args.pcsv, 'pcsv')

    if args.ops:
        parseArgParser(file, args.ops, 'ops')
    
    if args.excel:
        parseArgParser(file, args.excel, 'excel')

    if args.numpy:
        parseArgParser(file, args.numpy, 'numpy')

    if args.json:
        parseArgParser(file, args.json, 'json')

    if args.all:
        parseArgParser(file, args.all, 'all')

