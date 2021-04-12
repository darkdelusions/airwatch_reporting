import pandas as pd
import requests
import json
import os
from os import path
from datetime import datetime

#Open the config file found in the config folder
with open('config/config.json') as json_config:
    config = json.load(json_config)

#Creates a Global varible called headers 
global headers
headers = {
        'AW-TENANT-CODE': config['authentication']['api_key'],
        'Content-Type': 'application/json',
        'Authorization': "Basic " + config['authentication']['authorization']
}

#Gets the device data need and creates a pandas dataframe
def get_device_data():
    endpoint_url = config['authentication']['airwatch_url'] + "/API/mdm/devices/search"
    query_string = {"orderby":"user" , "pagesize":"15000"}
    device_response = requests.get(endpoint_url, headers=headers, params=query_string).json()
    device_list = []
    for device in device_response['Devices']:
        try:    
            device_list.append([device['UserName'], device['UserId']['Name'], device['UserEmailAddress'], device['Platform'], device['Model'], device['SerialNumber'], device['LastSeen'], device['Imei'], device['DeviceCellularNetworkInfo'][0]['CarrierName'], device['PhoneNumber'], device['EnrollmentStatus'], device['LastEnrolledOn'], device['AssetNumber']])
        except:
             device_list.append([device['UserName'], device['UserId']['Name'], device['UserEmailAddress'], device['Platform'], device['Model'], device['SerialNumber'], device['LastSeen'], device['Imei'],"", device['PhoneNumber'], device['EnrollmentStatus'], device['LastEnrolledOn'], device['AssetNumber']])
    device_dataset = pd.DataFrame(device_list)
    device_dataset.columns = ['_user_name','user_full_name','_user_email','_device_platform','device_model','_device_serial_number','_event_created_time_utc','device_imei','device_current_carrier','device_phone_number','device_enrollment_status',' device_enrollment_date_utc','device_asset_number']	
    return(device_dataset)

def get_user_data():
    endpoint_url = config['authentication']["airwatch_url"] + "/API/system/users/search"
    query_string = {"orderby":"user" , "pagesize":"15000"}
    users_response= requests.get(endpoint_url, headers=headers, params=query_string).json()
    users_list = []
    for users in users_response['Users']: 
        users_list.append([users['Email'],users['CustomAttribute1'], users['CustomAttribute2'], users['CustomAttribute5']])
    users_dataset = pd.DataFrame(users_list)
    users_dataset.columns = ['_user_email','user_department','user_custom_attribute_1','user_custom_attribute_5']
    return(users_dataset)

def merge_data(df1,df2):
    date = datetime.now().strftime("%Y-%m-%d")
    merged_dataset = pd.merge(df1, df2, how='outer', on='_user_email')
    clean_merged_dataset = merged_dataset.replace({r'\s+$': '', r'^\s+': ''}, regex=True).replace(r'\n',  ' ', regex=True)
    clean_merged_dataset.to_csv(f'ITAM Report-' + date + '.csv',  index=False)


def date_test():
    date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
    print(f'ITAM Report-' + str(date) + '.csv')


def main():
    df1 = get_device_data()
    df2 = get_user_data()
    merge_data(df1,df2)



main()