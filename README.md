# S5000FXMLReader
&nbsp;&nbsp;&nbsp;&nbsp; Python class for reading S5000F message XML files. Returns header and trailer data of a S5000F message. This data is available as a Numpy array or a Pandas data frame.

## Dependencies
&nbsp;&nbsp;&nbsp;&nbsp; This reader needs the following libraries to parse the XML files:

- lxml (To read and write XML file)
- numpy (To save the data into an array)
- pandas (To save the data into a structured data frame)
- (To save the data into an EXCEL file)

## Usage
&nbsp;&nbsp;&nbsp;&nbsp; The S5000FXMLReader can be used in two different approaches:

- as a converter
- as a python class for accessing the data
----
### &nbsp;&nbsp;&nbsp;&nbsp; Converting XML file


&nbsp;&nbsp;&nbsp;&nbsp; The S5000FXMLReader can be called in the command line to convert the XML into a CSV, JSON, Excel, Numpy object, or all. Paired with the converted file is a JSON with the header information.

```
python3 S5000FXMLReader.py 'filename.XML' [arguments]
``` 
#### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Arguments

- [-csv [CSV]] - Convert the XML to a CSV. Output filename is optional.
- [-pcsv [PCSV]] - Convert the XML to a CSV (Pandas formated). Output filename is optional.
- [-x [EXCEL]] - Convert the XML to a Excel. Output filename is optional.
- [-np [NUMPY]] - Convert the XML to a Numpy. Output filename is optional.
- [-json [JSON]] - Convert the XML to a JSON. Output filename is optional.
- [-all [ALL]] - Convert the XML to a CSV, Excel, Numpy and JSON. Output filename is optional.
----
### &nbsp;&nbsp;&nbsp;&nbsp; Python class

&nbsp;&nbsp;&nbsp;&nbsp; The S5000FXMLReader can be also be imported by another python script and used to converted the XML files, providing the data in either a Numpy array or a Panda data frame.

```python
import GEMuseXMLReader

MessageData = S5000FXMLReader('filename.XML')

MessageData.header ## Header containing the patient, device and acquisition session parameters

MessageData.dataObject ## Dictionary containing the data separated by lead

MessageData.dataFrame ## Panda's data frame containg the acquisition data

MessageDatadataArray ## Numpy matrix containing the acquisition data
``` 

## Header

&nbsp;&nbsp;&nbsp;&nbsp; The header is structured as follows:

* Header
    * PatientInfo
        * Given_Name
        * Family_Name
        * ID
        * Gender
        * Race
        * Pacemaker

    * DeviceInfo
        * DeviceModel
        * DeviceName
        * DeviceSerial

    * AcquisitionInfo
        * AcquisitionDate
        * LeadAmplitudeUnitsPerBit
        * LeadAmplitudeUnits
        * Resolution
        * Filters
            * HighPass
            * LowPass
            * Algorithms*
                * Name
                * Purpose
        * SampleRate
        * LeadsInformation
            * LeadsNames
            * LeadsLabels
            * NumberOfSamples
        * HeaderString

* Could be more than one.

