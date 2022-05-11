import numpy as np
import requests as requests
import re
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO

def get_file_list(region_id):
    dwd_monthly_data_url = 'https://opendata.dwd.de/climate_environment/CDC/observations_global/CLIMAT/monthly/qc/air_temperature_mean/historical/'
    response = requests.get(dwd_monthly_data_url)
    file_list = []
    if response.status_code != 200:
        raise ConnectionRefusedError
    else:
        parsed_html = BeautifulSoup(response.text, "html.parser")
        for a in parsed_html.body.find_all('a', href=True):
            if re.search(region_id+r"_[0-9]{6}_[0-9]{6}.txt", a['href']):
                file_list.append(a['href'])
    return file_list

def get_station_info():
    station_info_url = 'https://opendata.dwd.de/climate_environment/CDC/help/stations_list_CLIMAT_data.txt'
    response = requests.get(station_info_url)
    if response.status_code != 200:
        raise ConnectionRefusedError
    else:
        parsed_html = StringIO(response.text.replace(' ', ''))
        df = pd.read_csv(parsed_html, sep=';')
    return df

def get_station_data(file_id):
    dwd_monthly_data_url = 'https://opendata.dwd.de/climate_environment/CDC/observations_global/CLIMAT/monthly/qc/air_temperature_mean/historical/'
    response = requests.get(dwd_monthly_data_url+file_id)
    if response.status_code != 200:
        raise ConnectionRefusedError
    else:
        parsed_html = StringIO(response.text.replace(' ', ''))
        tempreture_df = pd.read_csv(parsed_html, sep=';')
    return tempreture_df

if __name__ == '__main__':
    # region_id = '01152'
    country_name = 'Mozambique'
    #Jan   Feb   Mrz   Apr   Mai  Jun   Jul   Aug   Sep   Okt   Nov   Dez
    year = 2018
    month = 'Dez'
    station_info = get_station_info()
    station_info_country = station_info[station_info['Country']==country_name]
    station_ids = station_info_country['WMO-StationID'].to_numpy()
    station_names = station_info_country['StationName'].to_numpy()
    for idx, station_id in enumerate(station_ids):
        print('Station name '+station_names[idx])
        file_list = get_file_list(station_id)
        if len(file_list) == 0:
            print('NO file available')
            continue
        print('Parsing file '+file_list[-1])
        station_data = get_station_data(file_list[-1])
        print("Station_data:\n", station_data)
        tempreture = station_data[station_data['Jahr']==int(year)][month].values
        if np.size(tempreture):
            station_info_country.loc[station_info_country['WMO-StationID']==station_id, 'tempreture']=tempreture[0]
        else:
            station_info_country.loc[station_info_country['WMO-StationID']==station_id, 'tempreture']=np.nan
    print(station_info_country)
    station_info_country.to_csv('csv/'+str(year)+' '+month+' '+country_name+'.csv')
