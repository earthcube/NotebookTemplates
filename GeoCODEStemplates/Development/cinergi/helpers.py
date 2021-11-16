import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import urllib.request, json
from datetime import datetime, date, time
from ipywidgets import widgets  
from IPython import get_ipython
from matplotlib import pylab
from pylab import *
from IPython.display import clear_output


def plotTimeSeriesData(data,col_name_to_plot,graphKeyVals):
    #Sets the size of the figure in the notebook

    for i in range(len(data)):
        plt.plot(data[i]['date_time'],pd.to_numeric(data[i][col_name_to_plot], errors='coerce'), label = str(graphKeyVals[i]))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())

        #fontsize of the tick labels
        plt.rc('xtick', labelsize=15) 
        plt.rc('ytick', labelsize = 15)

        #Size of ticks
        plt.tick_params(direction='out', length=10, width=2,)

        #X and Y labels
        plt.xlabel('Time',fontsize=18)
        plt.ylabel(col_name_to_plot,fontsize=18)


    plt.legend(loc = "best",prop={'size': 20})
    plt.show()
    
        
def simplify_column_names(df):
    new_header = []
    header_len = 0
    test = 0
    
    try:
        test = int(list(df.columns.values)[0][1])
        temp_header = [j[1] for j in df.columns.values]
        df.loc[-1] = temp_header
        df.index = df.index + 1  # shifting index
        df = df.sort_index()  # sorting by index
        df.columns = [j[0] for j in df.columns.values]
    except ValueError:
         pass

    for i in list(df.columns.values):
        header_len = len(i)
        if isinstance(i, str):
            new_header.append(i)
        elif isinstance(i, tuple):
            new_header.append('%s (%s)'%(i[0],i[1]))
    df.columns = new_header
    return df

#Creates a datetime object based on the dates and times and appends to the existing dataframe

#function to streamline the operation
def createDateTime(df):
    
    matchers = ['YY','MM','DD','hh',"mm"]
    datetimeref = ['year', 'month', 'day', 'hour', 'minute']
    temp = []
    for i in [j[0:3] for j in df.columns.values]:
        for j in matchers:
            if j in i and i not in temp:
                temp.append(i)

    df.columns.values[0:len(temp)] = datetimeref[0:len(temp)]
    
    df_temp = df.iloc[:,0:len(temp)]
    if len(str(df_temp['year'][0])) < 4:
        df_temp['year'] = ("%s%s")%("19",df_temp['year'][0])
    df_temp = pd.to_datetime(df_temp)
    df_temp = pd.DataFrame({'date_time': df_temp})
    df = pd.concat([df,df_temp], axis = 1)
    df = df.replace(['99.0','999.0','99.00','999','9999.0' ], np.nan)
    return df

def create_dropdown_data(cinergi_url):
    data_url = {}

    with urllib.request.urlopen(cinergi_url) as url:
        data = json.loads(url.read().decode())
        data = data["_source"]["links_s"]
        if isinstance(data,str):  
                data_url['{0}. {1}'.format(0,data)]= data             
        else:
            n = 0
            for i in data:
                if "filename" in str(i):
                    data_url['{0}. {1}'.format(n,i)]=i 
                    n += 1
    
    #widgetData = []

    #data_dropdown_options = widgetData[0].columns.values
    #data_dropdown_options = dropdown_options.tolist()

    #Generate Dropdown Options (Get all column names where sum of useable values is not 0)
    #for i in data_url:
        #dropdown_options = list(set(dropdown_options)&set((i.T[i.any()].T).columns.values))
    #dropdown_options = [x for x in dropdown_options if x not in ["hh (hr)", "mm (mn)", "#YY (#yr)","DD (dy)","date_time","MM (mo)"]]
    #return dropdown_options
    return data_url

def create_data_from_urls(data_urls):
    url_data = []
    for i in data_urls:
        try:
            url_data.append(pd.read_csv(i, delim_whitespace=True, header=[0,1], na_values=['99.0','999.0','99.00','999','9999.0' ]))
            print (' read file: '+ i)
        except:
            print('Link not a csv datafile: ' + i)

      # Preview Data from Cinergi URL
    return url_data

def create_data(cinergi_url):
    url_data = []

    with urllib.request.urlopen(cinergi_url) as url:
        data = json.loads(url.read().decode())
        data = data["_source"]["links_s"]
        if isinstance(data,str):  
            try:
                url_data.append(pd.read_csv(data, delim_whitespace=True, header=[0,1], na_values=['99.0','999.0','99.00','999','9999.0' ]))
            except:
                print('Link not a csv datafile: ' + i)
        else:
            for i in data:
                if "filename" in i:
                    try:
                        print(i)
                        url_data.append(pd.read_csv(i, delim_whitespace=True, header=[0,1], na_values=['99.0','999.0','99.00','999','9999.0' ]))
                        print (' read file: '+ i)
                    except:
                        print('Link not a csv datafile: ' + i)

            # Preview Data from Cinergi URL
    return url_data

# future. Some files are one line headers, others a multiple.
def skip_to(fle, line,**kwargs):
    if os.stat(fle).st_size == 0:
        raise ValueError("File is empty")
    with open(fle) as f:
        pos = 0
        cur_line = f.readline()
        while not cur_line.startswith(line):
            pos = f.tell()
            cur_line = f.readline()
        f.seek(pos)
        return pd.read_csv(f, **kwargs)
    
#Generates table of number of variables in each column name
def create_dropdowns(data):
    widgetData = []
    for i in data:
        display(("%s 's data (number of variables in each column)"%(i["year"][0])),pd.DataFrame(i.count()).transpose().style)
        widgetData.append(pd.DataFrame(i.count()).transpose())

    dropdown_options = widgetData[0].columns.values
    dropdown_options = dropdown_options.tolist()

    #Generate Dropdown Options (Get all column names where sum of useable values is not 0)
    for i in widgetData:
        dropdown_options = list(set(dropdown_options)&set((i.T[i.any()].T).columns.values))
    dropdown_options = [x for x in dropdown_options if x not in ["hour", "minute", "year","day","date_time","month"]]
    return dropdown_options