# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import datetime,dash,multiprocessing
from datetime import date
from flask import request
from dash import dcc, html,ctx
from updated_date import Current_things
from data_reading import Data_Reading
import pandas as pd
import dash_bootstrap_components as dbc
from sql_query_fetching import data_frame,data_frame_main
from dash import html
from dash_extensions.enrich import callback_context
from dash import html, dcc, callback, Input, Output

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
    a.CreatedDate>='2022-02-01 00:00:00' and a.ProviderServiceMapID=3
GROUP BY date(a.CreatedDate),fa.FacilityName;
'''

dash.register_page(__name__, path='/'
                            ,title='Sanofi Dashboard'
                            ,name='Sanofi Dashboard'
                   )

obj_home=Current_things()

layout=html.Div([
            #First Div For Header Class
            html.Div([
                html.Img(src='./assets/image/logo_removebg.png',alt='sanofi_logo',className="sanofi_logo_class"),
                # html.P("ver:1.0",className="version_class"),
                html.P("Sanofi Dashboard",className="sanofi_name"),
                html.Img(src='./assets/image/sehat_ok_please_removebg.png',alt='sehat_logo',className="sehat_logo_class"),
                html.Img(src='./assets/image/piramal_logo.png',alt='piramal_logo',className="piramal_logo_class"),
                ],className="class_header"),
            #Second Div For Div-Body Class
            html.Div([
                html.Div([
                    dcc.DatePickerRange(id='my_date_picker_range_home',className="calender_class",display_format='DD-MM-Y',min_date_allowed=date(2022, 2, 1),max_date_allowed=obj_home.current_date(),initial_visible_month=obj_home.current_date(),start_date=date(2022, 2, 1),end_date=obj_home.current_date(),style={}),
                    # dcc.DatePickerRange(id='my_date_picker_range_home',with_portal=True,className="calender_class",display_format='DD-MM-Y',min_date_allowed=date(2019, 7, 31),max_date_allowed=date.today(),initial_visible_month=date.today(),start_date=date(2019, 7, 31),end_date=date.today(),style={}),
                    html.Div([html.P("",id="error_box",className="error_bar_class")],className="error_bar"),                    
                    # html.Div([html.Img(src='./assets/image/refresh_new_removebg.png',alt='refresh_logo',className="refresh_logo_class")],className="refresh_class"),                    
                    html.A([html.Img(src='./assets/image/refresh_new_removebg.png',alt='refresh_logo',className="refresh_logo_class")],href="/",className="refresh_class"),
                    # html.P("ver:1.0",className="version_class")
                    ],className="middle_layer"),
                html.Div([
                    #Cards First Row
                    html.Div([
                        #First Card
                        html.Div([
                            #Upper Part
                            html.Div([html.P("Clinic's Conducted ",className="first_card_upper_part_name"),
                                    html.A([html.Img(src='./assets/image/right_new.png',alt='right_arrow_new',id="right_new_id",className="right_arrow_new_class")],href=dash.page_registry['pages.c_clinics_conducted']['path'],className="")
                                    #   html.Br(),
                                    #   html.P("Since 4th Feb-2022",className="first_card_upper_part_name")
                                      ],className="first_card_upper_part"),
                            #Lower Part
                            html.Div([
                                html.P("(Since 4th Feb-2022)",className="first_card_upper_part_name"),
                                #Total Count
                                html.Div([html.P("Cumulative :",className="first_card_lower_one_count"),html.P(id="first_card_lower_one_value")],className="first_card_lower_one"),
                                #Yesterday Count
                                html.Div([html.P("Yesterday :",className="first_card_lower_two_count"),html.P(id="first_card_lower_two_value")],className="first_card_lower_two"),
                                # html.A([html.Img(src='./assets/image/right_new.png',alt='right_arrow_new',id="right_new_id",className="right_arrow_new_class")],href=dash.page_registry['pages.c_clinics_conducted']['path'],className="")
                                ],className="first_card_lower_part"),                 
                            ],className="first_card"),
                        #Second Card
                        html.Div([
                            #Upper Part
                            html.Div([html.P("Total Beneficiary Visits",className="second_card_upper_part_name"),
                                    html.A([html.Img(src='./assets/image/right_new.png',alt='right_arrow_new',className="right_arrow_new_class")],href=dash.page_registry['pages.c_tbv']['path'],className="")
                                    ],className="second_card_upper_part"),
                            #Lower Part
                            html.Div([
                                #Total Count
                                html.Div([html.P("Cumulative :",className="second_card_lower_one_count"),html.P(id="second_card_lower_one_value")],className="second_card_lower_one"),
                                #Yesterday Count
                                html.Div([html.P("Yesterday :",className="second_card_lower_two_count"),html.P(id="second_card_lower_two_value")],className="second_card_lower_two"),
                                # html.A([html.Img(src='./assets/image/right_new.png',alt='right_arrow_new',className="right_arrow_new_class")],href=dash.page_registry['pages.c_tbv']['path'],className="")
                                ],className="second_card_lower_part"),
                            ],className="second_card"),
                        #Third Card
                        html.Div([
                            #Upper Part
                            html.Div([html.P("Unique Registration's",className="third_card_upper_part_name"),
                                    html.A([html.Img(src='./assets/image/right_new.png',alt='right_arrow_new',className="right_arrow_new_class")],href=dash.page_registry['pages.c_unique_registrations']['path'],className="")
                                    ],className="third_card_upper_part"),
                            #Lower Part
                            html.Div([
                                #Total Count
                                html.Div([html.P("Cumulative :",className="third_card_lower_one_count"),html.P(id="third_card_lower_one_value")],className="third_card_lower_one"),
                                #Yesterday Count
                                html.Div([html.P("Yesterday :",className="third_card_lower_two_count"),html.P(id="third_card_lower_two_value")],className="third_card_lower_two"),
                                # html.A([html.Img(src='./assets/image/right_new.png',alt='right_arrow_new',className="right_arrow_new_class")],href=dash.page_registry['pages.c_unique_registrations']['path'],className="")
                                ],className="third_card_lower_part"),                            
                            ],className="third_card"),
                        #Fourth Card
                        html.Div([
                            #Upper Part
                            html.Div([html.P("Revisit's",className="fourth_card_upper_part_name"),
                                    html.A([html.Img(src='./assets/image/right_new.png',alt='right_arrow_new',className="right_arrow_new_class")],href=dash.page_registry['pages.c_revisits']['path'],className="")
                                    ],className="fourth_card_upper_part"),
                            #Lower Part
                            html.Div([
                                #Total Count
                                html.Div([html.P("Cumulative :",className="fourth_card_lower_one_count"),html.P(id="fourth_card_lower_one_value")],className="fourth_card_lower_one"),
                                #Yesterday Count
                                html.Div([html.P("Yesterday :",className="fourth_card_lower_two_count"),html.P(id="fourth_card_lower_two_value")],className="fourth_card_lower_two"),
                                # html.A([html.Img(src='./assets/image/right_new.png',alt='right_arrow_new',className="right_arrow_new_class")],href=dash.page_registry['pages.c_revisits']['path'],className="")
                                ],className="fourth_card_lower_part"),
                            ],className="fourth_card"),
                        ],className="first_row"),
                    #Cards second row Starting
                    html.Div([
                        #Fifth Card
                        html.Div([
                            #Upper Part
                            html.Div([html.P("NCD",className="fifth_card_upper_part_name"),
                                    html.A([html.Img(src='./assets/image/right_new.png',alt='right_arrow_new',className="right_arrow_new_class")],href=dash.page_registry['pages.c_ncd']['path'],className="")
                                    ],className="fifth_card_upper_part"),
                            #Lower Part
                            html.Div([
                                #Total Count
                                html.Div([html.P("Cumulative :",className="fifth_card_lower_one_count"),html.P(id="fifth_card_lower_one_value")],className="fifth_card_lower_one"),
                                html.P("(HyperTension+Diabates+Cancer)",className="fifth_card_additional_text"),
                                #Yesterday Count
                                # html.Div([html.P("Yesterday :",className="fifth_card_lower_two_count"),html.P("2983974897",id="fifth_card_lower_two_value")],className="fifth_card_lower_two"),
                                # html.A([html.Img(src='./assets/image/right_new.png',alt='right_arrow_new',className="right_arrow_new_class")],href=dash.page_registry['pages.c_ncd']['path'],className="")
                                ],className="fifth_card_lower_part"),  
                            ],className="fifth_card"),
                        #Sixth Card
                        html.Div([
                            #Upper Part
                            html.Div([html.P("NCD Breakup",className="sixth_card_upper_part_name"),
                                    html.A([html.Img(src='./assets/image/right_new.png',alt='right_arrow_new',className="right_arrow_new_class")],href=dash.page_registry['pages.c_ncd_breakup']['path'],className="")
                                    ],className="sixth_card_upper_part"),
                            #Lower Part
                            html.Div([
                                #Hypertension Count
                                html.Div([html.P("Hypertension :",className="sixth_card_lower_one_count"),html.P(id="sixth_card_lower_one_value")],className="sixth_card_lower_one"),
                                #Diabetes Count
                                html.Div([html.P("Diabetes :",className="sixth_card_lower_two_count"),html.P(id="sixth_card_lower_two_value")],className="sixth_card_lower_two"),
                                #CAncer Count
                                html.Div([html.P("Cancer :",className="sixth_card_lower_three_count"),html.P(id="sixth_card_lower_three_value")],className="sixth_card_lower_three"),
                                # html.A([html.Img(src='./assets/image/right_new.png',alt='right_arrow_new',className="right_arrow_new_class")],href=dash.page_registry['pages.c_ncd_breakup']['path'],className="")
                                ],className="sixth_card_lower_part"),                            
                            ],className="sixth_card"),
                        #Seventh Card
                        html.Div([
                            #Upper Part
                            html.Div([html.P("Test's Conducted",className="seventh_card_upper_part_name"),
                                    html.A([html.Img(src='./assets/image/right_new.png',alt='right_arrow_new',className="right_arrow_new_class")],href=dash.page_registry['pages.c_tests_conducted']['path'],className="")
                                    ],className="seventh_card_upper_part"),
                            #Lower Part
                            html.Div([
                                #Total Count
                                html.Div([html.P("Cumulative :",className="seventh_card_lower_one_count"),html.P(id="seventh_card_lower_one_value")],className="seventh_card_lower_one"),
                                #Yesterday Count
                                html.Div([html.P("Yesterday :",className="seventh_card_lower_two_count"),html.P(id="seventh_card_lower_two_value")],className="seventh_card_lower_two"),
                                # html.A([html.Img(src='./assets/image/right_new.png',alt='right_arrow_new',className="right_arrow_new_class")],href=dash.page_registry['pages.c_tests_conducted']['path'],className="")
                                ],className="seventh_card_lower_part"),
                            ],className="seventh_card"),
                        #Eigth Card
                        html.Div([
                            #Upper Part
                            html.Div([html.P("Medicated patients",className="eight_card_upper_part_name"),
                                    html.A([html.Img(src='./assets/image/right_new.png',alt='right_arrow_new',className="right_arrow_new_class")],href=dash.page_registry['pages.c_mp']['path'],className="")
                                    ],className="eight_card_upper_part"),
                            #Lower Part
                            html.Div([
                                #Total Count
                                html.Div([html.P("Cumulative :",className="eight_card_lower_one_count"),html.P(id="eight_card_lower_one_value")],className="eight_card_lower_one"),
                                #Yesterday Count
                                html.Div([html.P("Yesterday :",className="eight_card_lower_two_count"),html.P(id="eight_card_lower_two_value")],className="eight_card_lower_two"),
                                # html.A([html.Img(src='./assets/image/right_new.png',alt='right_arrow_new',className="right_arrow_new_class")],href=dash.page_registry['pages.c_mp']['path'],className="")
                                ],className="eight_card_lower_part"),
                            ],className="eigth_card")
                        ],className="second_row"),
                    html.P("@Powered by Piramal Swasthya.",className="down_name")
                    ],className="complete_cards")
                ],className="class_body"),
                dcc.Interval(
                    id='interval-component',
                    interval=5*60*1000, # updates in every 5 Minutes
                    n_intervals=20
                    )
    ],className="main_class")


@callback([Output('my_date_picker_range_home',"max_date_allowed"),
        Output('my_date_picker_range_home',"initial_visible_month"),
        Output('my_date_picker_range_home',"end_date")],
        [Input('interval-component', 'n_intervals')])
def date_updation(n_intervals):
    obj_home_date_callbacks=Data_Reading()
    if n_intervals:
        return [obj_home_date_callbacks.today_rep_data,obj_home_date_callbacks.today_rep_data,obj_home_date_callbacks.today_rep_data]
    else:
        return [obj_home_date_callbacks.today_rep_data,obj_home_date_callbacks.today_rep_data,obj_home_date_callbacks.today_rep_data]


@callback(
            #first card
            Output('first_card_lower_one_value','children'),
            Output('first_card_lower_two_value','children'),
            #2nd Card
            Output('second_card_lower_one_value','children'),
            Output('second_card_lower_two_value','children'),
            #3rd Card
            Output('third_card_lower_one_value','children'),
            Output('third_card_lower_two_value','children'),
            #4th Card
            Output('fourth_card_lower_one_value','children'),
            Output('fourth_card_lower_two_value','children'),
            #5th Card
            Output('fifth_card_lower_one_value','children'),
            #6th Card
            Output('sixth_card_lower_one_value','children'),
            Output('sixth_card_lower_two_value','children'),
            Output('sixth_card_lower_three_value','children'),
            #7th Card
            Output('seventh_card_lower_one_value','children'),
            Output('seventh_card_lower_two_value','children'),
            #8th Card
            Output('eight_card_lower_one_value','children'),
            Output('eight_card_lower_two_value','children'),
            #Output Error for Date
            Output('error_box','children'),
            #Input for Taking's
            inputs=dict(n_intervals=Input('interval-component', 'n_intervals'),start_date=Input('my_date_picker_range_home','start_date'),end_date=Input('my_date_picker_range_home','end_date')),
        )
def marker_click_loc(n_intervals:int,start_date:str,end_date:str):
    obj_home_callbacks=Data_Reading()
    if n_intervals:
        # p1=multiprocessing.Process(target=data_frame,args=[query1])
        p1=multiprocessing.Process(target=data_frame_main)
        p1.start()
        marker_id=dash.callback_context.triggered[0]
        button_clicked = ctx.triggered_id
        st = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        en =  datetime.datetime.strptime(end_date, '%Y-%m-%d')
        
        if (button_clicked==None):
            return obj_home_callbacks.Clinical_operation_cumulative(st,en),obj_home_callbacks.Clinical_operation_yesteday(),obj_home_callbacks.total_beneficiary_visits_cumulative(st,en),obj_home_callbacks.total_beneficiary_visits_yesteday(),obj_home_callbacks.total_Unique_registrations_cumulative(st,en),obj_home_callbacks.total_Unique_registrations_yesterday(),obj_home_callbacks.total_revisits_cumulative(st,en),obj_home_callbacks.total_revisits_yesteday(),obj_home_callbacks.ncd_cumulative(st,en),obj_home_callbacks.ncd_hypertension(st,en),obj_home_callbacks.ncd_diabetes(st,en),obj_home_callbacks.ncd_cancer(st,en),obj_home_callbacks.tests_cond_cumulative(st,en),obj_home_callbacks.tests_conduc_yesteday(),obj_home_callbacks.received_medication_cumulative(st,en),obj_home_callbacks.received_medication_yeesterday()," "
        elif (button_clicked=='start_date'):
            if (st>en):
                return " "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","Start: {} Date Greater Than End: {} Date Value.".format(st,en)
            elif (st==en):
                return obj_home_callbacks.Clinical_operation_cumulative(st,en),obj_home_callbacks.Clinical_operation_yesteday(),obj_home_callbacks.total_beneficiary_visits_cumulative(st,en),obj_home_callbacks.total_beneficiary_visits_yesteday(),obj_home_callbacks.total_Unique_registrations_cumulative(st,en),obj_home_callbacks.total_Unique_registrations_yesterday(),obj_home_callbacks.total_revisits_cumulative(st,en),obj_home_callbacks.total_revisits_yesteday(),obj_home_callbacks.ncd_cumulative(st,en),obj_home_callbacks.ncd_hypertension(st,en),obj_home_callbacks.ncd_diabetes(st,en),obj_home_callbacks.ncd_cancer(st,en),obj_home_callbacks.tests_cond_cumulative(st,en),obj_home_callbacks.tests_conduc_yesteday(),obj_home_callbacks.received_medication_cumulative(st,en),obj_home_callbacks.received_medication_yeesterday()," "
            elif (st<en):
                return obj_home_callbacks.Clinical_operation_cumulative(st,en),obj_home_callbacks.Clinical_operation_yesteday(),obj_home_callbacks.total_beneficiary_visits_cumulative(st,en),obj_home_callbacks.total_beneficiary_visits_yesteday(),obj_home_callbacks.total_Unique_registrations_cumulative(st,en),obj_home_callbacks.total_Unique_registrations_yesterday(),obj_home_callbacks.total_revisits_cumulative(st,en),obj_home_callbacks.total_revisits_yesteday(),obj_home_callbacks.ncd_cumulative(st,en),obj_home_callbacks.ncd_hypertension(st,en),obj_home_callbacks.ncd_diabetes(st,en),obj_home_callbacks.ncd_cancer(st,en),obj_home_callbacks.tests_cond_cumulative(st,en),obj_home_callbacks.tests_conduc_yesteday(),obj_home_callbacks.received_medication_cumulative(st,en),obj_home_callbacks.received_medication_yeesterday()," "
            else:
                return obj_home_callbacks.Clinical_operation_cumulative(st,en),obj_home_callbacks.Clinical_operation_yesteday(),obj_home_callbacks.total_beneficiary_visits_cumulative(st,en),obj_home_callbacks.total_beneficiary_visits_yesteday(),obj_home_callbacks.total_Unique_registrations_cumulative(st,en),obj_home_callbacks.total_Unique_registrations_yesterday(),obj_home_callbacks.total_revisits_cumulative(st,en),obj_home_callbacks.total_revisits_yesteday(),obj_home_callbacks.ncd_cumulative(st,en),obj_home_callbacks.ncd_hypertension(st,en),obj_home_callbacks.ncd_diabetes(st,en),obj_home_callbacks.ncd_cancer(st,en),obj_home_callbacks.tests_cond_cumulative(st,en),obj_home_callbacks.tests_conduc_yesteday(),obj_home_callbacks.received_medication_cumulative(st,en),obj_home_callbacks.received_medication_yeesterday()," "
        elif (button_clicked=='end_date'):
            if (st>en):
                return " "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","Start: {} Date Greater Than End: {} Date Value.".format(st,en),obj_home_callbacks.today_rep_data,obj_home_callbacks.today_rep_data," "
            elif (st==en):
                return obj_home_callbacks.Clinical_operation_cumulative(st,en),obj_home_callbacks.Clinical_operation_yesteday(),obj_home_callbacks.total_beneficiary_visits_cumulative(st,en),obj_home_callbacks.total_beneficiary_visits_yesteday(),obj_home_callbacks.total_Unique_registrations_cumulative(st,en),obj_home_callbacks.total_Unique_registrations_yesterday(),obj_home_callbacks.total_revisits_cumulative(st,en),obj_home_callbacks.total_revisits_yesteday(),obj_home_callbacks.ncd_cumulative(st,en),obj_home_callbacks.ncd_hypertension(st,en),obj_home_callbacks.ncd_diabetes(st,en),obj_home_callbacks.ncd_cancer(st,en),obj_home_callbacks.tests_cond_cumulative(st,en),obj_home_callbacks.tests_conduc_yesteday(),obj_home_callbacks.received_medication_cumulative(st,en),obj_home_callbacks.received_medication_yeesterday()," "
            elif (st<en):
                return obj_home_callbacks.Clinical_operation_cumulative(st,en),obj_home_callbacks.Clinical_operation_yesteday(),obj_home_callbacks.total_beneficiary_visits_cumulative(st,en),obj_home_callbacks.total_beneficiary_visits_yesteday(),obj_home_callbacks.total_Unique_registrations_cumulative(st,en),obj_home_callbacks.total_Unique_registrations_yesterday(),obj_home_callbacks.total_revisits_cumulative(st,en),obj_home_callbacks.total_revisits_yesteday(),obj_home_callbacks.ncd_cumulative(st,en),obj_home_callbacks.ncd_hypertension(st,en),obj_home_callbacks.ncd_diabetes(st,en),obj_home_callbacks.ncd_cancer(st,en),obj_home_callbacks.tests_cond_cumulative(st,en),obj_home_callbacks.tests_conduc_yesteday(),obj_home_callbacks.received_medication_cumulative(st,en),obj_home_callbacks.received_medication_yeesterday()," "
            else:
                return obj_home_callbacks.Clinical_operation_cumulative(st,en),obj_home_callbacks.Clinical_operation_yesteday(),obj_home_callbacks.total_beneficiary_visits_cumulative(st,en),obj_home_callbacks.total_beneficiary_visits_yesteday(),obj_home_callbacks.total_Unique_registrations_cumulative(st,en),obj_home_callbacks.total_Unique_registrations_yesterday(),obj_home_callbacks.total_revisits_cumulative(st,en),obj_home_callbacks.total_revisits_yesteday(),obj_home_callbacks.ncd_cumulative(st,en),obj_home_callbacks.ncd_hypertension(st,en),obj_home_callbacks.ncd_diabetes(st,en),obj_home_callbacks.ncd_cancer(st,en),obj_home_callbacks.tests_cond_cumulative(st,en),obj_home_callbacks.tests_conduc_yesteday(),obj_home_callbacks.received_medication_cumulative(st,en),obj_home_callbacks.received_medication_yeesterday()," "
        else:
            return obj_home_callbacks.Clinical_operation_cumulative(st,en),obj_home_callbacks.Clinical_operation_yesteday(),obj_home_callbacks.total_beneficiary_visits_cumulative(st,en),obj_home_callbacks.total_beneficiary_visits_yesteday(),obj_home_callbacks.total_Unique_registrations_cumulative(st,en),obj_home_callbacks.total_Unique_registrations_yesterday(),obj_home_callbacks.total_revisits_cumulative(st,en),obj_home_callbacks.total_revisits_yesteday(),obj_home_callbacks.ncd_cumulative(st,en),obj_home_callbacks.ncd_hypertension(st,en),obj_home_callbacks.ncd_diabetes(st,en),obj_home_callbacks.ncd_cancer(st,en),obj_home_callbacks.tests_cond_cumulative(st,en),obj_home_callbacks.tests_conduc_yesteday(),obj_home_callbacks.received_medication_cumulative(st,en),obj_home_callbacks.received_medication_yeesterday()," "
    else:
        return dash.no_update,obj_home_callbacks.Clinical_operation_yesteday(),dash.no_update,obj_home_callbacks.total_beneficiary_visits_yesteday(),dash.no_update,obj_home_callbacks.total_Unique_registrations_yesterday(),dash.no_update,obj_home_callbacks.total_revisits_yesteday(),dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,obj_home_callbacks.tests_conduc_yesteday(),dash.no_update,obj_home_callbacks.received_medication_yeesterday()," "
    