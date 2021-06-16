import os
import datetime
import requests
import urllib

def sync(filename, repo = 'https://raw.githubusercontent.com/jankoslavic/pypinm/master', max_age_of_file = 60):
    local_filename = filename.split('/')[-1]
    if os.path.exists(local_filename) and \
       (datetime.datetime.now()-datetime.datetime.fromtimestamp(os.path.getmtime(local_filename))).seconds<\
        max_age_of_file:
        True
    else:
        print('Downloading file: {:s}'.format(local_filename))
        file = urllib.request.urlopen(repo+filename).read()
        with open(local_filename, 'wb') as f:
            f.write(file)

