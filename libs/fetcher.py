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

    def get_icubed(self):
        df = self.make_pd()
        cols = ['ICUbed_lower', 'ICUbed_mean', 'ICUbed_upper']
        icubed = df[cols]
        icubed.columns = ['ihme_lower', 'ihme_mean', 'ihme_upper']
        icubed.index = pd.to_datetime(icubed.index)
        return icubed


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
            
    def get_allbed(self, drop_0_2=True, scenarios=[1, 3]):
        can_var = 'all_hospitalized'
        allbed = pd.DataFrame()
        scenarios = scenarios
        for i in scenarios:
            can = self.make_pd(i)
            can_allbed = can[can_var]
            allbed = allbed.merge(
                can_allbed,
                how='outer',
                left_index=True,
                right_index=True
            )
        allbed.columns = ['can_' + str(i) for i in scenarios]
        allbed.index = pd.to_datetime(allbed.index)
        return allbed


class ChimeData(object):
    """
    Fetches and processes downloaded CHIME data
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
    
    def get_icubed(self):
        """
        Get all ICU beds
        """
        new_path = self.path.format('projected_admits')
        allbed = pd.read_csv(new_path)
        allbed.set_index('date', inplace=True)
        allbed.index = pd.to_datetime(allbed.index)
        allbed = allbed['icu'].to_frame()
        allbed.columns = ['chime']
        allbed.index = pd.to_datetime(allbed.index)
        return allbed


class UmCphrData(object):
    """
    Fetches and processes downloaded Landguth data
    """

    def __init__(self):
        self.path = 'data/umcphr/mt_region_hosp_icu_vent.csv'

    def get_allbed(self):
        """
        Get all hospitalizations using beds
        """

        allbed = pd.read_csv(self.path)
        allbed.set_index('DateReported', inplace=True)
        allbed.index = pd.to_datetime(allbed.index)
        allbed = allbed[allbed['Location'] == 'Montana']
        allbed = allbed[['PredHosp4wk', 'PredHosp3mth', 'PredHospOPT']]
        allbed.columns = ['umcphr_4wk', 'umcphr_3mth', 'umcphr_opt']
        allbed.index = pd.to_datetime(allbed.index)
        return allbed

    def get_icubed(self):
        """
        Get all icu beds
        """
        
        allbed = pd.read_csv(self.path)
        allbed.set_index('DateReported', inplace=True)
        allbed.index = pd.to_datetime(allbed.index)
        allbed = allbed[allbed['Location'] == 'Montana']
        allbed = allbed[['PredICU4wk', 'PredICU3mth', 'PredICUOPT']]
        allbed.columns = ['umcphr_4wk', 'umcphr_3mth', 'umcphr_opt']
        allbed.index = pd.to_datetime(allbed.index)
        return allbed