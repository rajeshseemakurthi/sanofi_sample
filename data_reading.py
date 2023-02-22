
#Importing Necessary Modules
import pandas as pd
from datetime import date
import pandas as pd
from dash import ctx
from dash_extensions.enrich import callback_context
from pandas._libs.tslibs.timestamps import Timestamp
from updated_date import Current_things

def showing_proper_int(n:int)->str:
    if (len(str(n))==1) or (len(str(n))==2) or (len(str(n))==3):
        return str(n)
    elif (len(str(n))==4):
        mk1=[str(x) for x in str(n)]
        return (mk1[0]+","+mk1[1]+mk1[2]+mk1[3])
    elif (len(str(n))==5):
        mk1=[str(x) for x in str(n)]
        return (mk1[0]+mk1[1]+","+mk1[2]+mk1[3]+mk1[4])
    elif (len(str(n))==6):  #7,87,767
        mk1=[str(x) for x in str(n)]
        return (mk1[0]+","+mk1[1]+mk1[2]+","+mk1[3]+mk1[4]+mk1[5])
    elif (len(str(n))==7): #67,56,354
        mk1=[str(x) for x in str(n)]
        return (mk1[0]+mk1[1]+","+mk1[2]+mk1[3]+","+mk1[4]+mk1[5]+mk1[6])
    elif (len(str(n))==8): #6,75,63,549
        mk1=[str(x) for x in str(n)]
        return (mk1[0]+","+mk1[1]+mk1[2]+","+mk1[3]+mk1[4]+","+mk1[5]+mk1[6]+mk1[7])
    elif (len(str(n))==9): #67,56,35,499
        mk1=[str(x) for x in str(n)]
        return (mk1[0]+mk1[1]+","+mk1[2]+mk1[3]+","+mk1[4]+mk1[5]+","+mk1[6]+mk1[7]+mk1[8])
    elif (len(str(n))==10): #6,75,63,54,997
        mk1=[str(x) for x in str(n)]
        return (mk1[0]+","+mk1[1]+mk1[2]+","+mk1[3]+mk1[4]+","+mk1[5]+mk1[6]+","+mk1[7]+mk1[8]+mk1[9])
    elif (len(str(n))==11): #67,56,35,49,976
        mk1=[str(x) for x in str(n)]
        return (mk1[0]+mk1[1]+","+mk1[2]+mk1[3]+","+mk1[4]+mk1[5]+","+mk1[6]+mk1[7]+","+mk1[8]+mk1[9]+mk1[10])
    else:
        return int(n)

#Class For Data Reading From Parquet File
class Data_Reading:
    def __init__(self):
        updated_date_obj=Current_things()
        self.today_rep_data=updated_date_obj.current_date()
        self.today_class_data = pd.to_datetime(self.today_rep_data, format='%Y-%m-%d')
        self.yesterday_class_data = self.today_class_data-pd.Timedelta(days=1)
        self.df=pd.read_parquet('data_folder/dataframe_main.parquet', engine='pyarrow')

    #Clinics Conducted Card:1
    def Clinical_operation_cumulative(self,st:str,en:str):
        clinic_df_cumulative=self.df[(self.df['Date']>=st) & (self.df['Date']<=en)]
        return showing_proper_int(clinic_df_cumulative['Camps_Conducted'].sum())

    def Clinical_operation_yesteday(self):
        df_yesterday=self.df[(self.df['Date']==self.yesterday_class_data)]        
        return showing_proper_int(df_yesterday['Camps_Conducted'].sum())

    #Total Beneficiary Visits Card:2
    def total_beneficiary_visits_cumulative(self,st:str,en:str):
        total_ben_df_cumulative=self.df[(self.df['Date']>=st) & (self.df['Date']<=en)]
        return showing_proper_int(total_ben_df_cumulative['Total Beneficiaries Registered'].sum())

    def total_beneficiary_visits_yesteday(self):
        df_yesterday=self.df[(self.df['Date']==self.yesterday_class_data)]
        return showing_proper_int(df_yesterday['Total Beneficiaries Registered'].sum())
        
    #Total Unique Registrations Card:3
    def total_Unique_registrations_cumulative(self,st:str,en:str):
        total_unique_cumulative=self.df[(self.df['Date']>=st) & (self.df['Date']<=en)]
        return showing_proper_int(total_unique_cumulative['Total Unique Registered'].sum())

    def total_Unique_registrations_yesterday(self):
        df_yesterday=self.df[(self.df['Date']==self.yesterday_class_data)]
        return showing_proper_int(df_yesterday['Total Unique Registered'].sum())

    #Total Revisits Card:4
    def total_revisits_cumulative(self,st:str,en:str):
        total_revisits_cumulative=self.df[(self.df['Date']>=st) & (self.df['Date']<=en)]
        return showing_proper_int(total_revisits_cumulative['Total Revisits'].sum())

    def total_revisits_yesteday(self):
        df_yesterday=self.df[(self.df['Date']==self.yesterday_class_data)]
        return showing_proper_int(df_yesterday['Total Revisits'].sum())
    
    #NCD Card:5
    def ncd_cumulative(self,st:str,en:str):
        ncd_cummulative=self.df[(self.df['Date']>=st) & (self.df['Date']<=en)]
        return showing_proper_int(ncd_cummulative['HYpertension'].sum()+ncd_cummulative['Diabetes'].sum()+ncd_cummulative['HTN & DM'].sum()+ncd_cummulative['Cancer'].sum())

    # NCD Card:6
    def ncd_hypertension(self,st:str,en:str):
        ncd_cummulative_hypertension=self.df[(self.df['Date']>=st) & (self.df['Date']<=en)]
        return showing_proper_int(ncd_cummulative_hypertension['HYpertension'].sum())

    def ncd_diabetes(self,st:str,en:str):
        ncd_cummulative_diabetes=self.df[(self.df['Date']>=st) & (self.df['Date']<=en)]
        return showing_proper_int(ncd_cummulative_diabetes['Diabetes'].sum())

    def ncd_cancer(self,st:str,en:str):
        ncd_cummulative_cancer=self.df[(self.df['Date']>=st) & (self.df['Date']<=en)]
        return showing_proper_int(ncd_cummulative_cancer['Cancer'].sum())

    #Tests Conducted Card:7
    def tests_cond_cumulative(self,st:str,en:str):
        tests_conduc_cummulative=self.df[(self.df['Date']>=st) & (self.df['Date']<=en)]
        return showing_proper_int(tests_conduc_cummulative['Total Beneficiaries taken Lab tests'].sum())

    def tests_conduc_yesteday(self):
        df_yesterday=self.df[(self.df['Date']==self.yesterday_class_data)]
        return showing_proper_int(df_yesterday['Total Beneficiaries taken Lab tests'].sum())

    #Received Medication Card:8
    def received_medication_cumulative(self,st:str,en:str):
        received_med_cummulative=self.df[(self.df['Date']>=st) & (self.df['Date']<=en)]
        return showing_proper_int(received_med_cummulative['#ben to Drug Prescribed'].sum())

    def received_medication_yeesterday(self):
        df_yesterday=self.df[(self.df['Date']==self.yesterday_class_data)]
        return showing_proper_int(df_yesterday['#ben to Drug Prescribed'].sum())

obj_1=Data_Reading()
