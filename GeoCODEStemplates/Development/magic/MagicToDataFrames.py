
# coding: utf-8

# # Unpack MagIC database text file into Pandas dataframes
# 
# This notebook should be saved as MagicToDataFrames.py if any changes are made. The python is then imported into the PmagPy_AnalysisFromWebCall notebook.
# Code is modified from code at https://github.com/PmagPy/PmagPy in ipmag.py and pmag.py modules (Licensed under a 3-clause BSD license. See [license.txt](https://github.com/ltauxe/PmagPy/blob/master/license.txt) for details.).
# Modifed and adapted by Stephen M. Richard 2019-06-06

# In[1]:

#imports
import pandas as pd
import requests


# In[2]:

def magicToDataframe(data_model="3.0", txt=""):
    """
    takes the name of a text file downloaded from the MagIC database and
    unpacks it into a dictionary of pandas dataframes. Each dataframe is named
    for the tab heading in the MagIC database file.
    Parameters
    ----------
    infile : str
        MagIC-format file to unpack
   
    txt : str, default ""
        if infile is not provided, you may provide a string with file contents instead
        (useful for downloading MagIC file directly from earthref)
        
    returns a dictionary 
    
    """
    infile=None
    framedict = {}
    
    if data_model == 2.5:
        method_col = "magic_method_codes"
    else:
        method_col = "method_codes"
    
    if txt:
        infile = txt.split("\n")
    else:
        print("no input text provided")
        return(framedict)
    
    
    File = []  # will contain all non-blank lines from downloaded file
    for line in infile:
        line = line.replace('\n', '')
        if line[0:4] == '>>>>' or len(line.strip()) > 0:  # skip blank lines
            File.append(line)
    #print(File)
    #return(framedict)
    
    LN = 0  # tracks our progress iterating through File
    type_list = []
    filenum = 0
    while LN < len(File) - 1:
        line = File[LN]
        if ">>>>" in line:
            LN += 1
            continue
        file_type = line.split('\t')[1]
        file_type = file_type.lower()
        if file_type[-1] == "\n":
            file_type = file_type[:-1]

        #print('working on: ', repr(file_type))
        if file_type not in type_list:
            type_list.append(file_type)
        else:
            filenum += 1
        LN += 1
        line = File[LN]
        # skip empty tables
        if line == ">>>>>>>>>>":
            LN += 1
            continue
        keys = line.replace('\n', '').split('\t')
        if keys[0][0] == '.':
            keys = line.replace('\n', '').replace('.', '').split('\t')
            keys.append('RecNo')  # cludge for new MagIC download format
        LN += 1
        Recs = []
        while LN < len(File):
            line = File[LN]
            # finish up one file type and then break
            if ">>>>" in line and len(Recs) > 0:
                
                NewRecs = []
                for rec in Recs:
                    if method_col in list(rec.keys()):
                        meths = rec[method_col].split(":")
                        if len(meths) > 0:
                            methods = ""
                            for meth in meths:
                                methods = methods + meth.strip() + ":"  # get rid of nasty spaces!!!!!!
                            rec[method_col] = methods[:-1]
                    NewRecs.append(rec)
                magic_writeDict(framedict, Recs, file_type)
                
                #print("Recs ", Recs)
                #print("data tab: ", file_type)
                Recs = []
                LN += 1
                break
            # keep adding records of the same file type
            else:
                rec = line.split('\t')
                Rec = {}
                if len(rec) == len(keys):
                    for k in range(len(rec)):
                        Rec[keys[k]] = rec[k]
                    Recs.append(Rec)
                # in case of magic_search_results.txt, which has an extra
                # column:
                elif len(rec) - len(keys) == 1:
                    for k in range(len(rec))[:-1]:
                        Rec[keys[k]] = rec[k]
                    Recs.append(Rec)
                elif len(rec) < len(keys):
                    for k in range(len(rec)):
                        Rec[keys[k]] = rec[k]
                    for k in range(len(rec), len(keys)):
                        Rec[keys[k]] = ""
                    Recs.append(Rec)
                else:
                    print('WARNING:  problem in file with line: ')
                    print(line)
                    print('skipping....')
                LN += 1
    if len(Recs) > 0:

        NewRecs = []
        for rec in Recs:
            if method_col in list(rec.keys()):
                meths = rec[method_col].split(":")
                if len(meths) > 0:
                    methods = ""
                    for meth in meths:
                        methods = methods + meth.strip() + ":"  # get rid of nasty spaces!!!!!!
                    rec[method_col] = methods[:-1]
            NewRecs.append(rec)
        magic_writeDict(framedict,Recs, file_type)
        #print("Recs /n", Recs)
        #print("data tab: ", file_type)
  
    return framedict


# In[4]:

def download_from_magic(con_id, data_model="3.0"):
    """
    Download a MagIC contribution directly from the MagIC API.
    If successful, this will write individual MagIC files to
    your chosen dir_path
    Parameters
    ----------
    data_model : string
        MagIC data model version, default '3.0'
    con_id : number
        MagIC contribution id, i.e. 12366
    dir_path : str, default "."
        directory for outputting files
    Returns
    ---------
    bool : True or False indicating whether download was successful
    """
    if not requests:
        print('-W- You must install the requests module to use this functionality')
        return
    try:
        res = requests.get('https://earthref.org/MagIC/download/{}/'.format(con_id))
    except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout):
        print("-W- Could not connect to MagIC")
        return
    if not res.ok:
        print("-W- Could not connect to MagIC -- check your requested contribution id ({})".format(con_id))
        return
    resultframedict = {}
    print("CALL magicToDataframe")
    resultframedict = magicToDataframe(txt=res.text)
    
    #print some citation information for the source
    if not(resultframedict['contribution'].empty):
        thecontribs=resultframedict['contribution']
        thekeys=(list(thecontribs))
        for index, row in thecontribs.iterrows():
            if 'contributor' in thekeys:
                contrib = 'contributor: ' + row['contributor'] + '; '
            else:
                contrib = ''
            if 'author' in thekeys:
                auth = 'author: ' + row['author'] + '; '
            else:
                auth = ''

            if 'reference' in thekeys:
                refer = ' reference: ' + row['reference']
            else:
                refer = ''
            print(contrib + auth + refer)
        
        
    return resultframedict


# In[5]:

def magic_writeDict(framedict, Recs, file_type):
    """
    Parameters
    _________
    framedict == the dictionary of frames. the key is file_type, values are pandas
        frame constructed from Recs
    Recs : list of dictionaries in MagIC format
    file_type : MagIC table type (e.g., specimens)
    Return :
    [True,False] : True if successful
    ofile : same as input
    Effects :
        writes a MagIC formatted file from Recs
    """
    if len(Recs) < 1:
        print('No records to write to file {}'.format(ofile))
        return False, ""
   # if os.path.split(ofile)[0] != "" and not os.path.isdir(os.path.split(ofile)[0]):
      #  os.mkdir(os.path.split(ofile)[0])
    #mag_out = open(ofile, 'w+', errors="backslashreplace")
    #print("file_type: ",file_type)
    framedict[file_type]=pd.DataFrame(Recs)
    #framedict[file_type]=Recs
    #print("framedict: ", framedict)

    print('data table: ' + file_type + '; ' + str(len(Recs)) + ' records')
    return True


# #change from markdown to code for testing
# 
# 
# outputdict = {}
# outputdict = download_from_magic(16619)
# print("output: ", outputdict)

# #change from markdown to code for testing
# 
# 
# if not(outputdict['contribution'].empty):
#     thecontribs=outputdict['contribution']
#     thekeys=(list(thecontribs))
#     for index, row in thecontribs.iterrows():
#         if 'contributor' in thekeys:
#             contrib = 'contributor: ' + row['contributor'] + '; '
#         else:
#             contrib = ''
#         if 'author' in thekeys:
#             auth = 'author: ' + row['author'] + '; '
#         else:
#             auth = ''
#         
#         if 'reference' in thekeys:
#             refer = ' reference: ' + row['reference']
#         else:
#             refer = ''
#         print(contrib + auth + refer)
# 
# 
# 
# 

# In[ ]:




# In[ ]:



