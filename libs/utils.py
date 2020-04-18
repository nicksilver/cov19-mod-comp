import pandas as pd
from datetime import datetime
import paramiko 
import json


def calc_stats(df):
    df_dop = df.idxmax().to_frame()
    df_max = df.max().to_frame()
    df_stats = df_dop.merge(df_max, right_index=True, left_index=True)
    df_stats.columns = ['Day of Peak', 'Peak Value']
    df_stats = df_stats.astype({'Peak Value': 'int'})
    df_stats['Day of Peak'] = df_stats['Day of Peak'].dt.strftime("%m/%d/%Y")
    return df_stats

def ftp_push(localpath, remotepath):

    with open("envvars.json") as f:
        envars = json.load(f)

    host = envars['host']
    username = envars['username']
    password = envars['password']
    remotepath = "/celFtpFiles/covid19/modcomp/incoming/"
    port = 22

    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    remotepath = remotepath + localpath.split("/")[-1]
    sftp.put(localpath, remotepath)
    sftp.close()
    transport.close()

def ftp_get(remotepath, localpath):
    with open("envvars.json") as f:
        envars = json.load(f)

    host = envars['host']
    username = envars['username']
    password = envars['password']
    port = 22 

    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.get(remotepath, localpath)
    sftp.close()
    transport.close()