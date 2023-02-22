import string,os
string.punctuation
# from assets.mymodule.my_db_cred import host, password, user
import mysql.connector as sql_db
import pandas as pd
import warnings as w
w.filterwarnings('ignore')

#DataFrame for Calling Count
query1 = '''
SELECT 
     date(a.CreatedDate) As Date,
    fa.FacilityName as Location,   
    count(distinct date(a.CreatedDate)) As Camps_Conducted,
    COUNT(DISTINCT a.VisitCode) AS 'Total Beneficiaries Registered',
    COUNT(DISTINCT case when a.VisitNo=1 then a.VisitCode end) AS 'Total Unique Registered',
    COUNT(DISTINCT case when a.VisitNo>1 then a.VisitCode end) AS 'Total Revisits',
       COUNT(DISTINCT case when (d.ProcedureID in (29,30,31,32) or ph.rbs is not null or ph.spo2 is not null 
        or ph.DiastolicBP_1stReading is not null or ph.SystolicBP_1stReading is not null) then a.VisitCode end) AS 'Total Beneficiaries taken Lab tests',
    COUNT(DISTINCT c.VisitCode) AS '#ben to Drug Prescribed',
    COUNT(distinct case when (nc.NCD_Condition='Hypertension' or p.DiagnosisProvided like 'Hypertension' or
    ((ph.DiastolicBP_1stReading>90 or ph.SystolicBP_1stReading>140) and ph.rbs<200) ) then a.VisitCode end) As 'HYpertension',
    COUNT(distinct case when nc.NCD_Condition='Diabetes Mellitus' or p.DiagnosisProvided like'Diabetes Mellitus' or ((ph.DiastolicBP_1stReading<=90 or ph.SystolicBP_1stReading<=140) and ph.rbs>200)
    or (d.ProcedureID in (29) and d.TestResultValue>200) then a.VisitCode end) As 'Diabetes',
    COUNT(DISTINCT case when (nc.NCD_Condition='Diabetes Mellitus' AND nc.NCD_Condition='Hypertension') or ((ph.DiastolicBP_1stReading>90 or ph.SystolicBP_1stReading>140) and ph.rbs>200) 
     or (p.DiagnosisProvided like'%Diabetes%' and p.DiagnosisProvided like '%Hypertension%')
      then a.VisitCode end) As 'HTN & DM',  
	count(distinct case when p.DiagnosisProvided like '%Cancer%' then a.visitcode end) As Cancer,
       COUNT(DISTINCT CASE
            WHEN d.ProcedureID=32 THEN d.VisitCode
        END) AS 'Urine Sugar',
    COUNT(DISTINCT CASE
            WHEN d.ProcedureID=31 THEN d.VisitCode
        END) AS 'Urine Albumin',
        COUNT(DISTINCT CASE
            WHEN (d.ProcedureID=29 or ph.rbs is not null) THEN a.VisitCode
        END) AS 'RBS',
    COUNT(DISTINCT CASE
            WHEN d.ProcedureID =30 THEN d.VisitCode
        END) AS 'HbA1c',
        COUNT(DISTINCT CASE
            WHEN (ph.SystolicBP_1stReading is not null or ph.DiastolicBP_1stReading is not null) THEN a.VisitCode
        END) AS 'BP'
        
FROM
    db_iemr.t_benvisitdetail a
        INNER JOIN
db_iemr.i_ben_flow_outreach e ON a.VisitCode = e.beneficiary_visit_code
        LEFT JOIN
    db_iemr.t_benclinicalobservation b ON a.VisitCode = b.VisitCode
        LEFT JOIN
    db_iemr.t_prescription p on a.VisitCode=p.VisitCode    
        left join 
    db_iemr.t_ncddiagnosis nc on a.VisitCode=nc.VisitCode    
    left join db_iemr.t_phy_vitals ph on ph.VisitCode=a.VisitCode
        LEFT JOIN
        db_iemr.t_cancerdiagnosis ca on ca.visitcode=a.visitcode
        left join
    db_iemr.t_prescribeddrug c ON a.VisitCode = c.VisitCode
        LEFT JOIN
    db_iemr.t_lab_testresult d ON a.VisitCode = d.VisitCode
        LEFT JOIN
    db_iemr.t_patientissue f ON a.VisitCode = f.VisitCode
           left join db_iemr.m_van v on a.VanID=v.VanID
    left join db_iemr.m_facility fa on v.FacilityID=fa.FacilityID
WHERE
    (a.CreatedDate between '2022-02-01 00:00:00' and now()) and a.ProviderServiceMapID=3
GROUP BY date(a.CreatedDate),fa.FacilityName;
'''

#Database connections
def mycon(db_name:str):
    while 1:
        try:
            mydb = sql_db.connect(host="192.168.45.221",user="Rajesh_s",password="Rajesh_s@2022$", database=db_name,auth_plugin="mysql_native_password")
            return mydb
        except Exception as e:
            print(e)
            print("In Exception Block..'Continue' Reverted.")
            continue
        break

def data_frame(query):
    db_name="db_iemr"
    mydb = mycon(db_name)

    mycursor = mydb.cursor()
    mycursor.execute(query)

    df=pd.DataFrame(mycursor, columns=[i[0] for i in mycursor.description])
    df.drop_duplicates(inplace=True)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df.dropna(inplace=True)
    # print("Sanofi Internal Excel file been Created..!")
    # self.df.to_csv("internal_sanofi_excel.csv")
    
    while 1:
        try:
            if os.listdir('data_folder')==[]:
                df.to_parquet("data_folder/dataframe_main.parquet")
            elif os.listdir('data_folder')!=[]:
                if 'dataframe_main.parquet' in os.listdir('data_folder'):
                    os.remove("data+folder/dataframe_main.parquet")
                    df.to_parquet("data_folder/dataframe_main.parquet")
                elif 'dataframe_main.parquet' not in os.listdir('data_folder'):
                    df.to_parquet("data_folder/dataframe_main.parquet")
                else:
                    print("file_have been Corrupted,I am in Else Block.")
            else:
                print("Thread safe Been Corrupted.I am in Else block.")
        except:
            continue
        break
    print("New Parquet File Been Updated..!")

def data_frame_main():
#DataFrame for Calling Count
    query = '''
    SELECT 
        date(a.CreatedDate) As Date,
        fa.FacilityName as Location,   
        count(distinct date(a.CreatedDate)) As Camps_Conducted,
        COUNT(DISTINCT a.VisitCode) AS 'Total Beneficiaries Registered',
        COUNT(DISTINCT case when a.VisitNo=1 then a.VisitCode end) AS 'Total Unique Registered',
        COUNT(DISTINCT case when a.VisitNo>1 then a.VisitCode end) AS 'Total Revisits',
        COUNT(DISTINCT case when (d.ProcedureID in (29,30,31,32) or ph.rbs is not null or ph.spo2 is not null 
            or ph.DiastolicBP_1stReading is not null or ph.SystolicBP_1stReading is not null) then a.VisitCode end) AS 'Total Beneficiaries taken Lab tests',
        COUNT(DISTINCT c.VisitCode) AS '#ben to Drug Prescribed',
        COUNT(distinct case when (nc.NCD_Condition='Hypertension' or p.DiagnosisProvided like 'Hypertension' or
        ((ph.DiastolicBP_1stReading>90 or ph.SystolicBP_1stReading>140) and ph.rbs<200) ) then a.VisitCode end) As 'HYpertension',
        COUNT(distinct case when nc.NCD_Condition='Diabetes Mellitus' or p.DiagnosisProvided like'Diabetes Mellitus' or ((ph.DiastolicBP_1stReading<=90 or ph.SystolicBP_1stReading<=140) and ph.rbs>200)
        or (d.ProcedureID in (29) and d.TestResultValue>200) then a.VisitCode end) As 'Diabetes',
        COUNT(DISTINCT case when (nc.NCD_Condition='Diabetes Mellitus' AND nc.NCD_Condition='Hypertension') or ((ph.DiastolicBP_1stReading>90 or ph.SystolicBP_1stReading>140) and ph.rbs>200) 
        or (p.DiagnosisProvided like'%Diabetes%' and p.DiagnosisProvided like '%Hypertension%')
        then a.VisitCode end) As 'HTN & DM',  
        count(distinct case when p.DiagnosisProvided like '%Cancer%' then a.visitcode end) As Cancer,
        COUNT(DISTINCT CASE
                WHEN d.ProcedureID=32 THEN d.VisitCode
            END) AS 'Urine Sugar',
        COUNT(DISTINCT CASE
                WHEN d.ProcedureID=31 THEN d.VisitCode
            END) AS 'Urine Albumin',
            COUNT(DISTINCT CASE
                WHEN (d.ProcedureID=29 or ph.rbs is not null) THEN a.VisitCode
            END) AS 'RBS',
        COUNT(DISTINCT CASE
                WHEN d.ProcedureID =30 THEN d.VisitCode
            END) AS 'HbA1c',
            COUNT(DISTINCT CASE
                WHEN (ph.SystolicBP_1stReading is not null or ph.DiastolicBP_1stReading is not null) THEN a.VisitCode
            END) AS 'BP'
            
    FROM
        db_iemr.t_benvisitdetail a
            INNER JOIN
    db_iemr.i_ben_flow_outreach e ON a.VisitCode = e.beneficiary_visit_code
            LEFT JOIN
        db_iemr.t_benclinicalobservation b ON a.VisitCode = b.VisitCode
            LEFT JOIN
        db_iemr.t_prescription p on a.VisitCode=p.VisitCode    
            left join 
        db_iemr.t_ncddiagnosis nc on a.VisitCode=nc.VisitCode    
        left join db_iemr.t_phy_vitals ph on ph.VisitCode=a.VisitCode
            LEFT JOIN
            db_iemr.t_cancerdiagnosis ca on ca.visitcode=a.visitcode
            left join
        db_iemr.t_prescribeddrug c ON a.VisitCode = c.VisitCode
            LEFT JOIN
        db_iemr.t_lab_testresult d ON a.VisitCode = d.VisitCode
            LEFT JOIN
        db_iemr.t_patientissue f ON a.VisitCode = f.VisitCode
            left join db_iemr.m_van v on a.VanID=v.VanID
        left join db_iemr.m_facility fa on v.FacilityID=fa.FacilityID
    WHERE
        a.CreatedDate>='2022-02-01 00:00:00' and a.ProviderServiceMapID=3
    GROUP BY date(a.CreatedDate),fa.FacilityName;
    '''
    
    db_name="db_iemr"
    mydb = mycon(db_name)

    mycursor = mydb.cursor()
    mycursor.execute(query)

    df=pd.DataFrame(mycursor, columns=[i[0] for i in mycursor.description])
    df.drop_duplicates(inplace=True)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df.dropna(inplace=True)
    
    while 1:
        try:
            if os.listdir('data_folder')==[]:
                df.to_parquet("data_folder/dataframe_main.parquet")
            elif os.listdir('data_folder')!=[]:
                if 'dataframe_main.parquet' in os.listdir('data_folder'):
                    os.remove("data_folder/dataframe_main.parquet")
                    df.to_parquet("data_folder/dataframe_main.parquet")
                elif 'dataframe_main.parquet' not in os.listdir('data_folder'):
                    df.to_parquet("data_folder/dataframe_main.parquet")
                else:
                    print("file_have been Corrupted,I am in Else Block.")
            else:
                print("Thread safe Been Corrupted.I am in Else block.")
        except:
            continue
        break
