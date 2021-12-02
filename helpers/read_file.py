def read_file(fn, ext=None):
    "can be a url, will call pd read_.. for the ext type"
    import pandas as pd
    import os
    import re
    if(ext!=None):
        ft="." + ext
    else:
        st=os.path.splitext(fn)
        ft=st[-1]
    if ft=='.tsv' or re.search('.tsv',ext,re.IGNORECASE):
        df=pd.read_csv(fn, sep='\t')
    elif ft=='.csv' or re.search('csv',ext,re.IGNORECASE):
        df=pd.read_csv(fn)
    elif ft=='.txt' or re.search('text',ext,re.IGNORECASE):
        df=pd.read_csv(fn, sep='\n')
    else:
        df="no reader, can !wget $url"
    return df

#start adding more utils, can use to: fn=read_file.path_leaf(url) then: !head fn
def path_leaf(path):
    import ntpath
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
