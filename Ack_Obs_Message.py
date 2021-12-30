#!/usr/bin/env python
# coding: utf-8

# # S5000F Bicycle example
# ## Creation of Acknowledgment / Observation messages
# 
# [HTML version](./Create_Hums_message.html)
# 
# **Date** : 20/04/2020 
# 
# **Program Version ** : 1.0           
# **Python Version **  : 3.8.1
# 
# **Source repository** : https://github.com/BernardRaust/Bicycle-trek-Chemin-de-la-Simone
# 
# **Support** : <mailto:bernard.raust@gmail.com>
# 
# ---------
# 
# This python module is answering a received S5000F message by issuing either an **Acknowledgment** or an **Observation** message.
# 
# The main steps are:<ol>
# <li> read 'oldest' xml file 'S5000F message' in folder Input.
# <li> move this file from folder Input to folder Archive.
# <li> parse this file and extract header/trailer information necessary to answer
# <li> if parsing is OK, create Acknowledgment message and store it in folder Output
# <li> if parsing is NOK, create Observation message and store it in folder Output</ol>
# 
# ---------

# ## 1 - Preparation

# In[1]:


import os
#%ls
get_ipython().run_line_magic('cd', '"C:\\Users\\Bernard\\Documents\\PROJETS\\Bike\\Version 2-1\\ASD5000F\\Bicycle-trek-Chemin-de-la-Simone"')


# In[2]:


import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile

import numpy as np

from lxml import etree
from copy import deepcopy 
import copy

from datetime import datetime

import re

get_ipython().system('pip install xmlschema')
import xmlschema


# In[3]:


# Define pos_hash function which return a positive hash number
# For removing random seed which is set at each Python runtime, set-up PYTHONHASHSEED value 
# %env PYTHONHASHSEED=19531130

import sys
def pos_hash(s):
    h=hash(s)
    if h < 0:
        h += sys.maxsize
    return(str(h))


# ### 1 Get xml file to be processed
# xml file to be processed are stored in an input folder.

# In[40]:


import glob
list_of_input_files = glob.glob('../Input_folder/*.xml')       # get xml input files to be processed

latest_file = min(list_of_input_files, key=os.path.getctime)   # pick the oldest one

pathname,filename = os.path.split(latest_file)
print(f"'{filename}'")
print()

# check that input file has no element <!ENTITY>

nb_entity = 0
with open(latest_file) as f:
    for line in f:
        match = re.search('<!ENTITY', line)
        if match :
            nb_entity = nb_entity + 1 

# entity are not allowed in input xml file, therefore it is not processed and considered as trash
if nb_entity:
    print(f'File "{tail}" contains at least one <!ENTITY> and so it is considered as trash')  # Move xml file from input folder to archive folder
import shutil
archive_file = latest_file.replace('Input','Output')
shutil.move(latest_file, archive_file)
# ## Validation of message header and footer
# In a first phase, message header and footer are processsed to get information necessary to process message content: Is the message received within a valid project, sent by an authorized organization, ...

# In[41]:


# Create a parser from S5000F enveloppe schema
parser_enveloppe = xmlschema.XMLSchema11('../Schema_folder/s5000f_envelope.xsd')


# In[42]:


# select elements of message header/trailer to be parsed
path_header = './msgId/*|./msgDate/*|./msgStatus/*|./msgType/*|'
path_trailer = './msgParty/*|./msgContext/*|./relatedMsg/*|./rmks/*|./secs/*'
xpath_elts = path_header + path_trailer

# Parse xml file with previous object parser
list_of_errors = xmlschema.iter_errors(latest_file,
                                       schema=parser_enveloppe,
                                       cls=xmlschema.XMLSchema11,
                                       path=xpath_elts,
                                       schema_path=None,
                                       use_defaults=True,
                                       namespaces=None,
                                       locations=None,
                                       base_url=None,
                                       defuse='always',
                                       timeout=300,
                                       lazy=True)


# In[43]:


if not(list_of_errors):
    print ("Parsing errors in message enveloppe:\n")
    for e in list_of_errors:
        print(e)
        reason = re.search("Reason:(.*)", str(e))
        path = re.search("Path:(.*)", str(e))
        print (f"{reason[0]}\n   {path[0]}\n")
else:
    print ("Message enveloppe successfully parsed !")


# ## Get message header and footer information
# In a second phase, message header and footer information are extracted from xml message header.

# In[44]:


# metadata (uid, type, date, time, status, sender, receiver, context and classification)
# are declared as mandatory in the message XSD schema, therefore their extraction does not
# any exception 

with open(latest_file, 'r') as fd:
    tree = etree.parse(fd)
    root = tree.getroot()
    uid = root.attrib['uid']
    _type = root.xpath('./msgType/code')[0].text
    date = root.xpath('./msgDate/date')[0].text
    time = root.xpath('./msgDate/time')[0].text
    status = root.xpath('./msgStatus/state')[0].text  
    context = root.xpath('./msgContext/context/projRef/projId/id')[0].text
    classification = root.xpath('./secs/sec/secClassDefRef/secClass/name')[0].text
    
    _msgPty = root.xpath('./msgPty')
    parties = {}    
    for elt in _msgPty:
        type = (elt.xpath('./ptyType/code'))[0].text
        id = (elt.xpath('./party/persRef/persId/id'))[0].text
        parties[type]=id  
    sender = parties['S']
    receiver = parties['R']


# In[45]:


print(uid,_type,date,time,status,sender,receiver,context,classification)


# ### Appendix A: Validation with XMLschema
# 
# [xmlschema Documentation Release 1.1.2](https://readthedocs.org/projects/xmlschema/downloads/pdf/latest/)
# 
# [xmlschema github](https://github.com/sissaschool/xmlschema)

# **xmlschema.validate**<br>(xml_document, schema=None, cls=None, path=None, schema_path=None,
# use_defaults=True, namespaces=None, locations=None, base_url=None, defuse=’remote’, timeout=300, lazy=False)<br><br>
# Validates an XML document against a schema instance. This function builds an <mark>XMLSchema</mark> object for validating the XML document. Raises an <mark>XMLSchemaValidationError</mark> if the XML document is not validated against the schema.<br><br>
# **Parameters**<ul>
# <li>xml_document – can be an XMLResource instance, a file-like object a path to a file
# or an URI of a resource or an Element instance or an ElementTree instance or a string
# containing the XML data. If the passed argument is not an XMLResource instance a new
# one is built using this and defuse, timeout and lazy arguments.
# <li>schema – can be a schema instance or a file-like object or a file path or a URL of a resource
# or a string containing the schema.
# <li>cls – class to use for building the schema instance (for default XMLSchema is used).
# <li>path – is an optional XPath expression that matches the elements of the XML data that
# have to be decoded. If not provided the XML root element is used.
# <li>schema_path – an XPath expression to select the XSD element to use for decoding. If
# not provided the path argument or the source root tag are used.
# <li>use_defaults – defines when to use element and attribute defaults for filling missing
# required values.
# <li>namespaces – is an optional mapping from namespace prefix to URI.
# <li>locations – additional schema location hints, used if a schema instance has to be built.
# <li>base_url – is an optional custom base URL for remapping relative locations, for default
# uses the directory where the XSD or alternatively the XML document is located.
# <li>defuse – optional argument to pass for construct schema and XMLResource instances.
# <li>timeout – optional argument to pass for construct schema and XMLResource instances.
# <li>lazy – optional argument for construct the XMLResource instance
def iter_errors(xml_document, schema=None, cls=None, path=None, schema_path=None,
                use_defaults=True, namespaces=None, locations=None, base_url=None,
                defuse='remote', timeout=300, lazy=False):
    """
    Creates an iterator for the errors generated by the validation of an XML document.
    Takes the same arguments of the function :meth:`validate`.
    """
    source, schema = get_context(
        xml_document, schema, cls, locations, base_url, defuse, timeout, lazy
    )
    return schema.iter_errors(source, path, schema_path, use_defaults, namespaces)from pprint import pprint
from xml.etree import ElementTree

xs = xmlschema.XMLSchema11('../Schema_folder/s5000f_2-0_isfDataset.xsd')
pprint(xs.to_dict(latest_file))
# In[8]:


help(xmlschema.validate)

# Parse xml file with previous object parser
# to be developped: compile XSD into a parser object to limit processing time by reusing parser
xmlschema.validate(latest_file, 
                   schema='../Schema_folder/s5000f_2-0_isfDataset.xsd', 
                   cls=xmlschema.XMLSchema11,
                   path=None,
                   schema_path=None,
                   use_defaults=True,
                   namespaces=None,
                   locations=None,
                   base_url=None,
                   defuse='remote',
                   timeout=300,
                   lazy=True)
# In[9]:


errors = [str(e) for e in xmlschema.iter_errors('../Schema_folder/s5000f_2-0_isfDataset.xsd',
                                                cls='XMLSchema11',lazy=True)]

if len(errors) == 0:
    print("Successfully parse message enveloppe")
else:
    print("ERRORS: %s" % ('\n++++++\n'.join(errors[:len(errors)])))


# In[ ]:


parser = etree.XMLParser(dtd_validation=True)   # create a parser object

# get data from received message
message = etree.parse(input_file[0])
# message = etree.parse(input_file[0],parser)

root = message.getroot()
# print(etree.tostring(root))
print(input_file)


# In[ ]:


# get parties identifier and type (Sender, Receiver, Forwarder, etc ... )
# store result in dictionary parties 

nmsp = {'n1':'http://www.asd-europe.org/s-series/s5000f'}

elt_msgPty = message.xpath('./msgPty')
parties = {}

for elt in elt_msgPty:
    type = (elt.xpath('./ptyType/code'))[0].text
    id = (elt.xpath('./party/persRef/persId/id'))[0].text
    parties[type]=id
    
# print(parties)


# In[ ]:


# Get message data which are required to build Ack or Obs message
msg_uid = root.attrib['uid']
msg_sender_id = parties['S']
msg_receiver_id = parties['R']
msg_context = root.xpath('./msgContext/context/projRef/projId/id')[0].text
msg_classification = root.xpath('./secs/sec/secClassDefRef/secClass/name')[0].text

#print (f"uid:      {msg_uid}\nsender:   {msg_sender_id}\nreceiver: {msg_receiver_id}")
#print (f"project:  {msg_context}\nsecurity: {msg_classification}")


# In[ ]:


xsd=etree.parse(file_header)        # create an element xsd from string 'file_header'
message = etree.ElementTree(xsd)    # create a document tree 'doc' by inserting xsd as element 
root = message.getroot()            # get root element


# ## 2 Acknowledgment message <a name="para21"/>
# 
# ### 2-1 Example of Acknowledgment message
# 
# **a) message root**
# 
#     <?xml version="1.0" encoding="UTF-8"?>
#         <n1:isfdataset uid="msg5264594691834755926" crud="I" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.asd-europe.org/s-series/s5000f ../00_XSD_Version_2.0/s5000f_2-0_isfdataset.xsd" xmlns:n1="http://www.asd-europe.org/s-series/s5000f">
#     <!-- previous uid uniquely associated to this message allows future reference if needed -->
# 
# **b) message header**
# 
#      <!-- ======================== MESSAGE HEADER ========================== -->
#      <msgId>
#          <id>Acknowledgment message of msgNNNNNNN</id></msgId>
#      <msgDate>
#          <date>2020-04-11</date><time>10:53:09.0Z</time></msgDate>
#      <msgStatus>
#          <state>F</state></msgStatus>
#      <msgType>
#          <code>ACK</code></msgType>  
#          
# **c) message content** 
# 
#      <!-- ======================== MESSAGE CONTENT ========================== -->
#      <msgAck/>
# 
# **d) message trailer**
# 
# 	<!-- ======================== MESSAGE TRAILER ========================== -->
# 	<msgContext>
# 		<context><projRef><projId><id>ASD/AIA S5000F Bicycle Example</id></projId>
#         </projRef></context></msgContext>
# 	<msgPty>
# 		<ptyType><code>S</code></ptyType>
#         <party><persRef><persId><id>Bernard Raust</id></persId></persRef></party></msgPty>
# 	<msgPty><ptyType><code>R</code></ptyType>
#         <party><persRef><persId><id>Guillaume Ollivier</id></persId></persRef></party></msgPty>
# 	<rmks>
# 		<rmk><text><descr>Acknowledgment of message msgNNNNNNN</descr></text></rmk></rmks>
# 	<secs>
# 		<sec><secClassDefRef><secClass><name>NUC</name></secClass></secClassDefRef></sec></secs>
#     </n1:isfDataset>

# ### 2-2 Creation of Acknowledgment message
# 
# **a) creation of ACK message root**

# In[ ]:


file_header='''
<n1:isfDataset crud="I" xsi:schemaLocation="http://www.asd-europe.org/s-series/s5000f ../00_XSD_Version_2.0/s5000f_2-0_isfdataset.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:n1="http://www.asd-europe.org/s-series/s5000f"></n1:isfDataset>
'''
xsd=etree.fromstring(file_header)   # create an element xsd from string 'file_header'
message = etree.ElementTree(xsd)    # create a document tree 'doc' by inserting xsd as element 
root = message.getroot()            # get root element


# **b) creation of ACK message header**

# In[ ]:


# msg_metadata is a dictionnary which store message metadata value
msg_metadata = {'msgId':'Acknowledgment of msg',
                'msgCode':'ACK',
                'msgDate':'',
                'msgTime':'',
                'msgStatus':'F',
                'msgContext':'ASD/AIA S5000F Bicycle Example',
                'msgSenderCode':'S',
                'msgSenderId':'',
                'msgReceiverCode':'R',
                'msgReceiver':'',
                'msgRelation':'',
                'relatedMsg':'',
                'msgRemark':'',
                'msgSecurity':'NUC',}

# msg_pathname is a dictionnary which store message pathname
msg_pathname = {'msgId':           'n1:isfdataset/msgId/id',
                'msgCode':         'n1:isfdataset/msgType/code',
                'msgDate':         'n1:isfdataset/msgDate/date',
                'msgTime':         'n1:isfdataset/msgDate/time',
                'msgStatus':       'n1:isfdataset/msgStatus/state',
                'msgContext':      'n1:isfdataset/msgContext/context/projRef/id',
                'msgSenderCode':   'n1:isfdataset/msgPty/ptyType/code',
                'msgSenderId':     'n1:isfdataset/msgPty/party/orgRef/orgId/id',
                'msgReceiverCode': 'n1:isfdataset/msgPty/ptyType/code',
                'msgReceiver':     'n1:isfdataset/msgPty/party/orgRef/orgId/id',
                'msgRelation':     'n1:isfdataset/relatedMsg/relType/code',
                'relatedMsg':      'n1:isfdataset/relatedMsg/msgRef/msgId/id',
                'msgRemark':       'n1:isfdataset/rmk/text/descr/',
                'msgSecurity':     'n1:isfdataset/secs/sec/secClassDefRef/secClass/name>',}


# In[ ]:


df = pd.DataFrame.from_dict(msg_pathname,orient='index',columns=['Pathname'])
df = df.join(pd.DataFrame.from_dict(msg_metadata,orient='index',columns=['Value']))
df


# The entries are:

# In[ ]:


# entries are
entries = [
    {'Path': 'Item/Info/Name', 'Value': 'Body HD'},
    {'Path': 'Item/Info/Synopsis', 'Value': 'A great movie'},
    {'Path': 'Item/Locales/Locale[@Country="US"][@Language="ES"]/Name', 'Value': 'El Grecco'},
    {'Path': 'Item/Genres/Genre', 'Value': 'Action'},
    {'Path': 'Item/Genres/Genre', 'Value': 'Drama'},
    {'Path': 'Item/Purchases/Purchase[@Country="US"]/HDPrice', 'Value': '10.99'},
    {'Path': 'Item/Purchases/Purchase[@Country="US"]/SDPrice', 'Value': '9.99'},
    {'Path': 'Item/Purchases/Purchase[@Country="CA"]/SDPrice', 'Value': '4.99'},
]


# To parse each xpath step, I use the following regular expressions

# In[ ]:


TAG_REGEX = r"(?P<tag>\w+)"
CONDITION_REGEX = r"(?P<condition>(?:\[.*?\])*)"
STEP_REGEX = TAG_REGEX + CONDITION_REGEX
ATTR_REGEX = r"@(?P<key>\w+)=\"(?P<value>.*?)\""

search_step = re.compile(STEP_REGEX, flags=re.DOTALL).search
findall_attr = re.compile(ATTR_REGEX, flags=re.DOTALL).findall


def parse_step(step):
    mo = search_step(step)
    if mo:
        tag = mo.group("tag")
        condition = mo.group("condition")
        return tag, dict(findall_attr(condition))
    raise ValueError(xpath)


# The **parse_step** return a tag name and a attributes dictionary. Then, I process the same way to build the XML tree:

# In[ ]:


root = None
for entry in entries:
    path = entry["Path"]
    parts = path.split("/")
    xpath_list = ["/" + parts[0]] + parts[1:]
    curr = root
    for xpath in xpath_list:
        tag_name, attrs = parse_step(xpath)
        if curr is None:
            root = curr = etree.Element(tag_name, **attrs)
        else:
            nodes = curr.xpath(xpath)
            if nodes:
                curr = nodes[0]
            else:
                curr = etree.SubElement(curr, tag_name, **attrs)
    if curr.text:
        curr = etree.SubElement(curr.getparent(), curr.tag, **curr.attrib)
    curr.text = entry["Value"]

print(etree.tostring(root, pretty_print=True).decode())


# ## 1 - Upload XML data into pandas dataframe

# <b>a) Description of XML structure of GPX Garmin file "activity_4588550232.xml"</b>
# 
# Trek point information is stored in elements called 'trkpt' located at <mark>gpx/trk/trkseg</mark>. See example below:
# 
#      <trkpt lat="43.60018135048449039459228515625" log="5.42250336147844791412353515625">
#             <ele>348.600006103515625</ele>
#             <time>2020-02-25T06:27:35.000Z</time>
#             <extensions>
#                 <ns3:TrackPointExtension>
#                     <ns3:hr>114</ns3:hr>
#                     <ns3:cad>66</ns3:cad>
#                 </ns3:TrackPointExtension>
#             </extensions>
#       </trkpt>
# 
# <b>b) list of data with their xpath address:</b><ul>
# <li>longitude   (<mark>trkpt[@lon]</mark>)
# <li>latitude    (<mark>trkpt[@lat]</mark>)
# <li>elevation   (<mark>trkpt/ele</mark>)
# <li>time        (<mark>trkpt/time</mark>)
# <li>heartRate measured in beats per minute  (<mark>trkpt/extensions/ns3:TrackPointExtension/ns3:hr</mark>)
# <li>cadence measured in revolutions per minute    (<mark>trkpt/extensions/ns3:TrackPointExtension/ns3:cad</mark>)
# </ul>

# In[ ]:


# read Garmin GPX data and store them in a pandas dataframe
trekdata = etree.parse('activity_4588550232.xml')
root = trekdata.getroot()

# create namespace dictionary
ns={'a':'http://www.topografix.com/GPX/1/1',
    'ns2':'http://www.garmin.com/xmlschemas/GpxExtensions/v3',
    'ns3':'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'}


# In[ ]:


TimeStamp, Longitude, Latitude, Elevation, Date, Time, HeartRate, Cadence = [],[],[],[],[],[],[],[]

for e in root.findall(".//a:trkpt",ns):
    TimeStamp.append(e[1].text)
    Longitude.append(e.attrib['lon'])
    Latitude.append(e.attrib['lat'])
    Elevation.append(e[0].text)
    Date.append(e[1].text[0:10])
    Time.append(e[1].text[11:19])
    for ext in e.findall('.//ns3:TrackPointExtension',ns):
        HeartRate.append(ext[0].text)
        Cadence.append(ext[1].text)
        
#'TimeStamp':pd.to_datetime(TimeStamp), # convert string to datetime
    
df=pd.DataFrame({'Longitude': Longitude,
                 'Latitude': Latitude,
                 'Elevation': Elevation,
                 'Date': Date,
                 'Time': Time,
                 'HeartRate': HeartRate,
                 'Cadence': Cadence}, index = TimeStamp) 


# In[ ]:


# cell to beactivated to create an EXCEL file 'result.xslx' containing dataframe data 
# !pip install openpyxl      # A Python library to read/write Excel 2010 xlsx/xlsm files 
df.to_excel(r'result.xlsx', index = False)

# hide information 5 minutes after departure time during 953 seconds
# measurement values set to NaN (not a number) and time values set to NaT (not a time)

trek_start = df.loc[0,'TimeStamp']                        
hide_start = trek_start + pd.to_timedelta(5, unit='m')
hide_end = hide_start + pd.to_timedelta(953, unit='s')
trek_end = df.loc[len(df)-1,'TimeStamp']

df.loc[(df.TimeStamp > hide_start) & (df.TimeStamp < hide_end),
       ['TimeStamp','Longitude','Latitude','Elevation']]= pd.NaT,np.NaN,np.NaN,np.NaN
# # 2 Creation of message ReportUsageInformation
# S5000F message have 4 parts:<ul><li>XML schema reference (see [para 2-0](#para20))</li><li>Message header (see [para 2-1](#para21))<li>Message content (see [para 2-2](#para22))<li>Message trailer (see [para 2-3](#para23)</ul>

# ## 2-0 XML schema reference <a name="para20"/>
# 
# <b>a) overview of XML Schema reference</b><br>
# 
#     <n1:isfDataset xmlns:n1="http://www.asd-europe.org/s-series/s5000f" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" crud="I" uid="msg3229307517681392546" xsi:schemaLocation="http://www.asd-europe.org/s-series/s5000f s5000f_2-0_isfDataset.xsd"><br>
# <b>b) creation of XML Schema reference</b>

# In[ ]:


file_header='''
<n1:isfDataset crud="I" xsi:schemaLocation="http://www.asd-europe.org/s-series/s5000f ../00_XSD_Version_2.0/s5000f_2-0_isfdataset.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:n1="http://www.asd-europe.org/s-series/s5000f"></n1:isfDataset>
'''
xsd=etree.fromstring(file_header)   # create an element xsd from string 'file_header'
message = etree.ElementTree(xsd)    # create a document tree 'doc' by inserting xsd as element 
root = message.getroot()            # get root element


# ## 2-1 Message header <a name="para21"/>
# <b>a) overview of message header</b>
# 
#      <!-- ======================== MESSAGE HEADER ========================== -->
#      <msgId>
#          <id>Bicycle trek chemin de la Simone Aix-en-Provence on 2020-02-25</id></msgId>
#      <msgDate>
#          <date>2020-04-11</date><time>10:53:09.0Z</time></msgDate>
#      <msgStatus>
#          <state>F</state></msgStatus>
#      <msgType>
#          <code>UC50902</code></msgType>     
# <b>b) define function to create message header</b>

# In[ ]:


# Function Message_Header(msg_date,msg_time,msg_type,msg_id,msg_status):
# inputs:
#    (string)     msg_date      : message creation date
#    (string)     msg_time      : message creation time
#    (string)     msg_type      : message type
#    (string)     msg_id        : message identifier
#    (string)     msg_status    : message status
# output:
#    (string)     xml           : xml snippet containing header data

def Message_Header(msg_date, msg_time,msg_type,msg_id,msg_status):
    xml  = "<HEADER>"
    xml += "<!-- ======================== MESSAGE HEADER ========================== -->"
    xml += "<msgId><id>" + msg_id + "</id></msgId>"
    xml += "<msgDate><date>" + msg_date + "</date>"
    xml += "<time>" + msg_time + "</time></msgDate>"
    xml += "<msgStatus><state>" + msg_status + "</state></msgStatus>"
    xml += "<msgType><code>" + msg_type + "</code></msgType></HEADER>"
    return xml  


# <b>c) create message header</b>

# In[ ]:


now = datetime.now()                                # get message timestamp
trek_date = df.iloc[0,df.columns.get_loc('Date')]   # get bicycle trek date

# create message header
msg_date   = now.strftime("%Y-%m-%d")
msg_time   = now.strftime("%H:%M:%S.0Z")
msg_type   = 'UC50902'
msg_id     = 'Bicycle trek chemin de la Simone Aix-en-Provence on '+ str(trek_date)
msg_status = 'F'
xml_header = Message_Header(msg_date,msg_time,msg_type,msg_id,msg_status)

header = etree.fromstring(xml_header)     # convert xml string to xml tree HEADER
for child in header:                      # insert children of HEADER as child of root
    root.append(child)

# Insert uid attribute in xml schema reference <n1:isfdataset>
msg_uid = 'msg'+pos_hash(msg_id)
root.set('uid',msg_uid)

# print(etree.tostring(root))


# ## 2-2 Creation of message content<a name="para22"/>
# In message content we have:<br> 1. bicycle information contained in serialPV element<br>2. usage information (longitude, latitude, elevation, heart rate, cadence) contained in measurementPoints.

# ### 2-2-1 Create bicycle as a serialProductVariant (serialPV)
# 
# First child of uc50902 contains information about the bicycle:
# 
# 	<uc50902>
# 		<serialPV uid="serialPV7521661216678648323">
# 			<!-- uid = spv & hash(ASD/AIA Bike:Mountain Bike:46) -->
# 			<prodId><id>ASD/AIA Bike</id></prodId>
# 			<prodVarId><id>Mountain Bike</id></prodVarId>
# 			<serPVId><id>46</id></serPVId>
#             
#          <!-- measurementPoints -->
#             <mpoints> °°° </mpoints>
#         </serialPV>
#     </uc50902

# In[ ]:


uc50902 = etree.SubElement(root,'uc50902')
serialPV = etree.SubElement(uc50902,'serialPV')
serialPV_uid = 'serialPV'+pos_hash('ASD/AIA Bike:Mountain Bike:46') 
serialPV.set('uid',serialPV_uid)                                # uc50902/serialPV/@uid

prodId = etree.SubElement(serialPV,'prodId') 
prodId_id = etree.SubElement(prodId,'id')
prodId_id.text='ASD/AIA Bike'                                   # uc50902/serialPV/prodId/id

prodVarId = etree.SubElement(serialPV,'prodVarId')
prodVarId_id = etree.SubElement(prodVarId,'id')
prodVarId_id.text='Mountain Bike'                               # uc50902/prodVarId/id

serPVId = etree.SubElement(serialPV,'serPVId')
serPVId_id = etree.SubElement(serPVId,'id')
serPVId_id.text='46'                                            # uc50902/serPVId/id

mpoints = etree.SubElement(serialPV,'mpoints')


# ### 2-2-2 Create measurementPoint (mPoints)

# <b>a) overview of measurementPointValue element</b><br>
# 
# 	<!-- measurementPoints -->
#     <mpoints>
#     <!-- measurementPoint for GPS longitude -->
#     <mPoint uid="mpoint7568698881537852097">
#         <!-- measurementPointIdentifier -->
#         <mPointId><id>BIKE GPS LONGITUDE</id></mPointId>
#         <!-- measurementPointValue -->
#         <mPointVal>
#             <recDate><date>2020-02-25</date><time>06:27:35.000Z</time></recDate>
#             <vdtm>MEAS</vdtm>
#             <unit>DGR</unit>
#             <value>5.42250336147844791412353515625</value>
#         </mPointVal>

# <b>b) define function <mark>mPointVal</mark> to create measurementPointValue</b><br>
# This function create an element measurementPointValue.<br> 
# It will be used to create a column for each measurementPoint (Latitude, Longitude, Elevation, Heart Rate, Cadence) in dataframe df. Cells of these columns contains xml snippet element measurementPointValue.

# In[ ]:


# Function mPointVal create xml-snippet element mPointVal representing one measurementPointValue
# input: 
#        date  - date of measurement
#        time  - time of measurement
#        vdtm  - value determination mean - 'MEAS' means measured - format string
#        unit  - unit of measurement format string
#        value - measured value
# output:
#        s     - string containing mPointVal xml element

def mPointVal(date,time,vdtm,unit,value):
    s = "<mPointVal><recDate><date>"+date.map(str)+"</date><time>"+time.map(str)+"</time>"
    s = s +"</recDate><vdtm>"+vdtm+"</vdtm><unit>"+unit+"</unit><value>"+value.map(str)
    s = s +"</value></mPointVal>"
    return s


# <b>c) create dataframe columns to store <mark>mPointVal</mark> elements</b><br>

# In[ ]:


# Create DataFrame column to store measurement point xml-snippet 
df['xml_longitude'] = mPointVal(df['Date'],df['Time'],'MEAS','DGR',df['Longitude'])
df['xml_latitude'] = mPointVal(df['Date'],df['Time'],'MEAS','DGR',df['Latitude'])
df['xml_elevation'] = mPointVal(df['Date'],df['Time'],'MEAS','MR',df['Elevation'])
df['xml_cadence'] = mPointVal(df['Date'],df['Time'],'MEAS','MR',df['Cadence'])
df['xml_heartrate'] = mPointVal(df['Date'],df['Time'],'MEAS','MR',df['HeartRate'])


# #### to check xml snippet representing measurement point in DatFrame print first row using :<ul>
# <li>print('LONGITUDE:\n' + df.iloc[0,df.columns.get_loc('xml_longitude')])
# <li>print('\nLATITUDE:\n' + df.iloc[0,df.columns.get_loc('xml_latitude')])
# <li>print('\nELEVATION:\n' + df.iloc[0,df.columns.get_loc('xml_elevation')])
# <li>print('\nCADENCE:\n' + df.iloc[0,df.columns.get_loc('xml_cadence')])
# <li>print('\nHEARTRATE:\n' + df.iloc[0,df.columns.get_loc('xml_heartrate')])
<!-- measurementPoint for GPS longitude -->
<mPoint uid="mpoint7568698881537852097">
    <!-- measurementPointIdentifier -->
    <mPointId><id>BIKE GPS LONGITUDE</id></mPointId>
    <!-- measurementPointValue -->
    <mPointVal>
        <recDate><date>2020-02-25</date><time>06:27:35.000Z</time></recDate>
        <vdtm>MEAS</vdtm>
        <unit>DGR</unit>
        <value>5.42250336147844791412353515625</value>
    </mPointVal>
# In[ ]:


# Function mPoint create xml-snippet element mPoint holding measurementPointValue of a counter
# input: 
#        ID            - (string) measurement point id
#        measurements  - (string) column of pandasframe containing xml Measurement Point Value
# output:
#        s             - string containing mPoint xml element

def mPoint(ID,measurements):   
    s = '<!-- measurementPoint for ' + ID + ' --><mPoint uid="'
    s = s + 'mpoint' + pos_hash(ID) + '"><!-- measurementPointIdentifier -->'
    s = s + "<mPointId><id>" + ID + "</id></mPointId><!-- measurementPointValue -->"
    s = s + df[measurements].str.cat() + '</mPoint>'
    return(s)

xml_lon = mPoint('GPS longitude','xml_longitude')
xml_lat = mPoint('GPS latitude','xml_latitude')
xml_ele = mPoint('GPS elevation','xml_elevation')
xml_cad = mPoint('GPS cadence','xml_cadence')
xml_hea = mPoint('GPS heart rate','xml_heartrate')

xml = "".join([xml_lon, xml_lat, xml_ele, xml_cad, xml_hea])


# In[ ]:


# mPoint create element <mpoint> as child of element <mpoints>
def mPoint(mPoint_id_val,df_col_name,unit_name):
    # mPoint_id is identifier of mPoint to be stored in mPointId/id
    # df_col is dataframe column containing usage information
    
    mPoint = etree.SubElement(mpoints,'mPoint')
    mPoint_uid = 'mpoint' + pos_hash(mPoint_id_val)
    mPoint.set('uid',mPoint_uid)
    mPointId = etree.SubElement(mPoint,'mPointId')
    mPointId_id = etree.SubElement(mPointId,'id')
    mPointId_id.text = mPoint_id_val
      
    for e in df.iterrows():
        mPointVal = etree.SubElement(mPoint,'mPointVal')
        recDate = etree.SubElement(mPointVal,'recDate')
        date = etree.SubElement(recDate,'date')
        date.text = e[1]['Date']
        time = etree.SubElement(recDate,'time')
        time.text = e[1]['Time']
        vdtm = etree.SubElement(mPointVal,'vdtm')
        vdtm.text = 'MEAS'
        unit = etree.SubElement(mPointVal,'unit')
        unit.text = unit_name
        value = etree.SubElement(mPointVal,'value')
        value.text = e[1][df_col_name]    


# In[ ]:


mPoint('BIKE GPS LATITUDE','Latitude','DGR')
mPoint('BIKE GPS LONGITUDE','Longitude','DGR')
mPoint('BIKE GPS ELEVATION','Elevation','MR')
mPoint('CYCLIST HEART RATE','HeartRate','/MIN')
mPoint('BIKE CADENCE','Cadence','/MIN')

	<uc50902>
		<serialPV uid="serialPV7521661216678648323">
			<!-- uid = spv & hash(ASD/AIA Bike:Mountain Bike:46) -->
			<prodId><id>ASD/AIA Bike</id></prodId>
			<prodVarId><id>Mountain Bike</id></prodVarId>
			<serPVId><id>46</id></serPVId>
		<!-- measurementPoints -->
		<mpoints>
		<!-- measurementPoint for GPS longitude -->
		<mPoint uid="mpoint7568698881537852097">
			<!-- measurementPointIdentifier -->
			<mPointId><id>BIKE GPS LONGITUDE</id></mPointId>
			<!-- measurementPointValue -->
			<mPointVal>
				<recDate>
					<date>2020-02-25</date>
					<time>06:27:35.000Z</time>
				</recDate>
				<vdtm>MEAS</vdtm>
				<unit>DGR</unit>
				<value>5.42250336147844791412353515625</value>
			</mPointVal>
			<mPointVal>
				<recDate>
					<date>2020-02-25</date>
					<time>06:27:36.000Z</time>
				</recDate>
				<vdtm>MEAS</vdtm>
				<unit>DGR</unit>
				<value>5.4225021041929721832275390625</value>
			</mPointVal>
			</mPoint>
			
		<mPoint uid="mpoint6172891642263870591">
			<!-- measurementPointIdentifier -->
			<mPointId><id>BIKE GPS LATITUDE</id></mPointId>
			<!-- measurementPointValue -->
			<mPointVal>
				<recDate>
					<date>2020-02-25</date>
					<time>06:27:35.000Z</time>
				</recDate>
				<vdtm>MEAS</vdtm>
				<unit>DGR</unit>
				<value>43.60018135048449039459228515625</value>
			</mPointVal>
			<mPointVal>
				<recDate>
					<date>2020-02-25</date>
					<time>06:27:36.000Z</time>
				</recDate>
				<vdtm>MEAS</vdtm>
				<unit>DGR</unit>
				<value>43.6001673527061939239501953125</value>
			</mPointVal>
			</mPoint>
			
		<mPoint uid="mpoint6345860573655649344">
			<!-- measurementPointIdentifier -->
			<mPointId><id>BIKE GPS ELEVATION</id></mPointId>
			<!-- measurementPointValue -->
			<mPointVal>
				<recDate>
					<date>2020-02-25</date>
					<time>06:27:35.000Z</time>
				</recDate>
				<vdtm>MEAS</vdtm>
				<unit>MR</unit>
				<value>348.600006103515625</value>
			</mPointVal>
			<mPointVal>
				<recDate>
					<date>2020-02-25</date>
					<time>06:27:36.000Z</time>
				</recDate>
				<vdtm>MEAS</vdtm>
				<unit>MR</unit>
				<value>348.600006103515625</value>
			</mPointVal>
			</mPoint>
							
		<mPoint uid="mpoint491392568479456041">
			<!-- measurementPointIdentifier -->
			<mPointId><id>CYCLIST HEART RATE</id></mPointId>
			<!-- measurementPointValue -->
			<mPointVal>
				<recDate>
					<date>2020-02-25</date>
					<time>06:27:35.000Z</time>
				</recDate>
				<vdtm>MEAS</vdtm>
				<unit>/MIN</unit>
				<value>114</value>
			</mPointVal>
			<mPointVal>
				<recDate>
					<date>2020-02-25</date>
					<time>06:27:36.000Z</time>
				</recDate>
				<vdtm>MEAS</vdtm>
				<unit>/MIN</unit>
				<value>114</value>
			</mPointVal>
			</mPoint>
			
		<mPoint uid="mpoint3026329868358448984">
			<!-- measurementPointIdentifier -->
			<mPointId><id>BIKE CADENCE</id></mPointId>
			<!-- measurementPointValue -->
			<mPointVal>
				<recDate>
					<date>2020-02-25</date>
					<time>06:27:35.000Z</time>
				</recDate>
				<vdtm>MEAS</vdtm>
				<unit>/MIN</unit>
				<value>66</value>
			</mPointVal>
			<mPointVal>
				<recDate>
					<date>2020-02-25</date>
					<time>06:27:36.000Z</time>
				</recDate>
				<vdtm>MEAS</vdtm>
				<unit>/MIN</unit>
				<value>0</value>
			</mPointVal>
			</mPoint>		
			
	</mpoints>
	</serialPV>
	</uc50902>
# ## 2-3 Creation of message trailer<a name="para23"/>
# 
# <b>a) overview of message trailer</b><br>
# 
# 	<!-- ======================== MESSAGE TRAILER ========================== -->
# 	<msgContext>
# 		<context><projRef><projId><id>ASD/AIA S5000F Bicycle Example</id></projId>
#         </projRef></context></msgContext>
# 	<msgPty>
# 		<ptyType><code>S</code></ptyType>
#         <party><persRef><persId><id>Guillaume Ollivier</id></persId></persRef></party></msgPty>
# 	<msgPty><ptyType><code>R</code></ptyType>
#         <party><persRef><persId><id>Bernard Raust</id></persId></persRef></party></msgPty>
# 	<rmks>
# 		<rmk><text><descr>Feedback about bike trek done on 2020-02-25</descr></text></rmk></rmks>
# 	<secs>
# 		<sec><secClassDefRef><secClass><name>NUC</name></secClass></secClassDefRef></sec></secs>
#     </n1:isfDataset>

# <b>b) define function to create message trailer</b><br>

# In[ ]:


# Function Message_Trailer(msg_timestamp,msg_type,msg_id,msg_status):
# inputs:
#    (string)     msg_project     : message issued within project / context
#    (string)     msg_sender      : sender of message
#    (string)     msg_receiver    : receiver of message
#    (string)     msg_remarks     : remarks about message
#    (string)     msg_classif     : message classification
# output:
#    (string)     xml             : xml snippet containing trailer data

def Message_Trailer(msg_project,msg_sender,msg_receiver,msg_remarks,msg_classif):
    xml  = "<TRAILER><!-- ======================== MESSAGE TRAILER ========================== -->"
    xml += "<msgContext><context><projRef><projId><id>" + msg_project + "</id></projId>"
    xml += "</projRef></context></msgContext>"
    xml += "<msgPty><ptyType><code>S</code></ptyType><party><persRef><persId><id>" + msg_sender
    xml += "</id></persId></persRef></party></msgPty>"
    xml += "<msgPty><ptyType><code>R</code></ptyType><party><persRef><persId><id>" + msg_receiver
    xml += "</id></persId></persRef></party></msgPty>"
    xml += "<rmks><rmk><text><descr>" + msg_remarks + "</descr></text></rmk></rmks>"
    xml += "<secs><sec><secClassDefRef><secClass><name>" + msg_classif
    xml += "</name></secClass></secClassDefRef></sec></secs></TRAILER>"
    return xml 


# <b>c) create message trailer</b><br>

# In[ ]:


msg_project  = 'ASD/AIA S5000F Bicycle Example'
msg_sender   = 'Guillaume OLLIVIER (g.ollivier@a2l.net)'
msg_receiver = 'Bernard RAUST (bernard.raust@edxea.com)'
msg_remarks  = 'Feedback about bicycle trek done on '+ trek_date +' reported on ' + msg_date
msg_classif  = 'NUC'

xml_trailer = Message_Trailer(msg_date,msg_time,msg_type,msg_id,msg_status)

trailer = etree.fromstring(xml_trailer)     # convert xml string to xml tree TRAILER
for child in trailer:                        # insert children of TRAILER as child of root
    root.append(child)


# In[ ]:


# store message in output xmfile
message_file = open(msg_uid+'.xml', "wb")
message_file.write(etree.tostring(message,pretty_print=False,xml_declaration=True, encoding='UTF-8'))
message_file.close()


# #### to display full content of xml message
# go to [last notebook cell](#fin)

# # 3 Display bicycle trek
# 
# During bicycle trek, usage information is monitored and stored in bicycle computer. Then this data is uploaded in personal computer using message UC500902 'Report Usage Information'. This paragraph demonstrates how this usage information could be processed and displayed on personal computer.<br>
# 
# This paragraph implement module <mark>gmaps</mark> 
# ([see jupyter-gmaps documentation](https://jupyter-gmaps.readthedocs.io/en/latest/index.html)) which is a python API to google map. 
# 
# ### 3-1 Installation of gmaps¶
# Installation is done from an Anaconda prompt window <mark>(Anaconda3 / Anaconda Prompt)</mark>.
# 
# $ > <mark>conda install -c conda-forge gmaps</mark>
# 
# $ > <mark>Jupyter notebook</mark>
# 
# <b>Reminder:</b><br>
# information about package is given by         : <mark>help(gmaps)</mark><br>
# information about method 'figure' is given by : <mark>gmaps.figure?</mark>

# In[ ]:


import gmaps
import gmaps.datasets

gmaps.configure(api_key="AI...")  # eDXEA - API google map key 


# ### 3-2 drawing of 'route of the bike'

# In[ ]:


geo_points = df[['Latitude','Longitude']].apply(tuple, axis=1)
trek_route = [(float(a),float(b)) for a,b in geo_points]


# In[ ]:


mean_long = df['Longitude'].map(float).mean()
mean_lat = df['Latitude'].map(float).mean()

fig = gmaps.figure(center=(mean_lat, mean_long),
                   zoom_level=15,
                   map_type='SATELLITE',
                   display_toolbar=False
                  )

trek = gmaps.Polygon(trek_route,
                     stroke_color='red',
                     stroke_weight=2,
                     fill_color='white',
                     fill_opacity=0.0)

drawing = gmaps.drawing_layer(features=[trek], show_controls=False)

fig.add_layer(drawing)
fig


# ![image.png](attachment:image.png)

# ### 3-3 Distance of the trek

# In[ ]:


import math

def getDistance(lat1,lon1,lat2,lon2):
    # This uses the haversine formula, which remains a good numerical computation,
    # even at small distances, unlike the Shperical Law of Cosines.
    # This method has ~0.3% error built in.
    R = 6371 # Radius of Earth in km

    dLat = math.radians(float(lat2) - float(lat1))
    dLon = math.radians(float(lon2) - float(lon1))
    lat1 = math.radians(float(lat1))
    lat2 = math.radians(float(lat2))


    a = math.sin(dLat/2) * math.sin(dLat/2) +         math.cos(lat1) * math.cos(lat2) * math.sin(dLon/2) * math.sin(dLon/2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    d = R * c 

    return d


# In[ ]:


# create column to store Latitude and Longitude shifted by one second (one row)
df['Latitude1']=df.Latitude.shift(1)
df['Longitude1']=df.Longitude.shift(1)

df['Distance']=df.apply(lambda df: getDistance(pd.Series(df['Latitude1']),
                                               pd.Series(df['Longitude1']),
                                               pd.Series(df['Latitude']),
                                               pd.Series(df['Longitude'])),
                        axis=1)

distance = int(df['Distance'].sum()*1000)
print(f"Lenght of bicycle trek was {distance} m")


# ### 3-4 Display measurement Elevation, Cadence and Heart Rate

# In[ ]:


import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')


# In[ ]:


# Compute timestamp value to have 10 intervals on x axis
df.index = pd.to_datetime(df.index)                             # convert index value to datetime
ts_loc = pd.to_datetime(np.linspace(df.index[0].value, 
                                    df.index[-1].value, 10))    # compute 10 intervals
ts_loc = ts_loc.round(freq='S')                                 # round tick timestamp to second
ts_names = ([df.loc[ts_loc[i],'Time'] for i in range(0,10)])    # get time associated to tick place

fig, ax = plt.subplots(figsize=(20, 5))

sample=180

ax1 = plt.subplot(1,3,1)
ax1.plot(df['Elevation'].rolling(sample).mean()[::sample])
ax1.set_title('Elevation (meter)')
ax1.set_xticks(ts_loc, minor=False)
ax1.set_xticklabels(ts_names, rotation="vertical") 

ax2 = plt.subplot(1,3,2)
ax2.plot(df['Cadence'].rolling(sample).mean()[::sample])
ax2.set_title('Cadence (revolutions per minute)')
ax2.set_xticks(ts_loc, minor=False)
ax2.set_xticklabels(ts_names, rotation="vertical") 

ax3 = plt.subplot(1,3,3)
ax3.plot(df['HeartRate'].rolling(sample).mean()[::sample])
ax3.set_title('Heart Rate (beats per minute)')
ax3.set_xticks(ts_loc, minor=False)
ax3.set_xticklabels(ts_names, rotation="vertical") 

fig.tight_layout()


# # FIN DU MODULE<a id='fin'/>
