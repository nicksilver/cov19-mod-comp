import pandas as pd
import zipfile
import requests
from io import BytesIO


class IhmeData(object):
    """
    Fetches and processes latest IHME data
    """

    def __init__(self, state='Montana'):
        self.path = 'https://ihmecovid19storage.blob.core.windows.net/latest/ihme-covid19.zip'
        self.state = state

    def make_pd(self):
        r = requests.get(self.path)
        zipf = zipfile.ZipFile(BytesIO(r.content))
        zipname = zipf.filelist[1].filename
        df = pd.read_csv(zipf.open(zipname), index_col='date')
        return df[df['location_name'] == self.state]

    def get_allbed(self):
        """
        Get all hospitalizations using beds
        """
        df = self.make_pd()
        cols = ['allbed_lower', 'allbed_mean', 'allbed_upper']
        allbed = df[cols]
        allbed.columns = ['ihme_lower', 'ihme_mean', 'ihme_upper']
        allbed.index = pd.to_datetime(allbed.index)
        return allbed


class CanData(object):
    """
    Fetches and processes latest CovidActNow data
    """

    def __init__(self, state='MT'):
        self.path ='https://raw.githubusercontent.com/covid-projections/covid-projections/develop/public/data/{}.{}.json' 
        self.state = state
        self.cols = [
            "day_index",
            "date",
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "all_hospitalized",
            "all_infected",
            "dead",
            "beds",
            "i",
            "j",
            "k",
            "l",
            "population",
            "m",
            "n",
        ]

    def make_pd(self, scenario):
        """
        scenario (int): 0-3 from CovidActNow
        """
        new_path = self.path.format(
            self.state,
            scenario
        )
        can = pd.read_json(new_path)
        can.columns = self.cols
        can.set_index('date', inplace=True)
        return can
            
    def get_allbed(self, drop_0_2=True):
        can_var = 'all_hospitalized'
        allbed = pd.DataFrame()
        for i in range(4):
            can = self.make_pd(i)
            can_allbed = can[can_var]
            allbed = allbed.merge(
                can_allbed,
                how='outer',
                left_index=True,
                right_index=True
            )
        allbed.columns = ['can_0', 'can_1', 'can_2', 'can_3']
        allbed.index = pd.to_datetime(allbed.index)
        if drop_0_2:
            allbed.drop(columns=['can_0', 'can_2'], inplace=True)
        return allbed

class ChimeData(object):
    """
    Fetches and processes latest IHME data
    """

    def __init__(self):
        self.path = 'data/CHIME_apr8/2020-04-08_{}.csv'

    def get_allbed(self):
        """
        Get all hospitalizations using beds
        """
        new_path = self.path.format('projected_admits')
        allbed = pd.read_csv(new_path)
        allbed.set_index('date', inplace=True)
        allbed.index = pd.to_datetime(allbed.index)
        allbed = allbed['hospitalized'].to_frame()
        allbed.columns = ['chime']
        allbed.index = pd.to_datetime(allbed.index)
        return allbed
