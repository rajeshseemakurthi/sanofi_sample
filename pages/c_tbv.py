import dash
import datetime
from datetime import date
from dash import html, dcc
from dash import Dash, dash_table
import pandas as pd
import pandas
from updated_date import Current_things
from data_reading import Data_Reading
from collections import OrderedDict
from pandas._libs.tslibs.timestamps import Timestamp
from dash import html, dcc, callback, Input, Output
# from sql_query_fetching_second import df

dash.register_page(__name__, path='/c_tbv'
                            ,title='c_tbv'
                            ,name='c_tbv'
                   )

dr=Data_Reading()

st = Timestamp('2022-11-01 00:00:00')
# st = Timestamp('2022-11-01 00:00:00', freq='MS')
st = st.to_pydatetime()
today = pd.to_datetime(date.today(), format='%Y-%m-%d')
yesterday = today-pd.Timedelta(days=1)

start_tbv=Timestamp('2022-10-15 00:00:00')
# start_tbv=Timestamp('2022-10-15 00:00:00', freq='MS')
end_tbv=Timestamp('2022-11-05 00:00:00')
# end_tbv=Timestamp('2022-11-05 00:00:00', freq='MS')

obj_datepicker_tbv=Current_things()

df_tbv=pd.DataFrame()

df_column_tbv = pd.DataFrame({'Location':pd.Series(dtype='str'),
                        'Beneficiary Visits-Yesterday': pd.Series(dtype='int'),
                        'Beneficiary Visits-Cumulative': pd.Series(dtype='int')})

layout = html.Div([
    html.Div([html.P("Total Beneficairy Visits(Unique & Revisits)")],className='tbv_title',style={"margin-left":"26%","margin-top":"3%","border":"2px double black","border-radius":"8px","width":"46%","text-align":'center',"font-size":"x-large","color":"black","font-family":"serif","font-weight":"700","background-color":"#d9dae0","padding-top":"3px"}),
    html.Div([
    html.Div(dcc.DatePickerRange(id='my_date_picker_range_tbv',display_format='D-M-Y',min_date_allowed=date(2022, 2, 1),max_date_allowed=obj_datepicker_tbv.current_date(),initial_visible_month=obj_datepicker_tbv.current_date(),start_date=date(2022, 2, 1),end_date=obj_datepicker_tbv.current_date(),style={"position":"relative","display":"inline-block","width":"110%","border-radius":"39px","margin-left":"115%","margin-top":"5%","margin-bottom":"7%"}),style={}),
    html.A([html.P("Home",style={})],href='/',style={"border":"2px double black","margin-left":"41%","border-radius":"8px","height":"36px","padding":"6px","margin-top":"18px","background-color":"rgb(215, 215, 215)"}),
    html.A([html.I(className="fa fa-refresh",style={})],href=dash.page_registry['pages.c_tbv']['path'],style={"width":"4%","height":"2.3rem","margin-left":"0.8rem","margin-top":"1.5%","text-align":"center","font-size":"22px","background-color":"rgb(215,215,215)","border-radius":"8px","border":"2px double black"})
    ],style={'display':'flex','flex-direction':'row',"margin-bottom":'-23px'}),
    html.Div([html.Div(id="c_tbv_error",className="tbv",style={"width":"70%","height":"1.5rem","margin-left":"20%","margin-top":"3px","font-family":"ui-sans-serif","font-size":"medium"})],style={}),
    dash_table.DataTable(columns=[{'id': c, 'name': c} for c in df_column_tbv.columns],id="table_tbv",
                        style_cell={'overflow': 'hidden','textOverflow': 'ellipsis','maxWidth': '50%','textAlign': 'center'},
                        style_cell_conditional=[{'if': {'column_id': c},'textAlign': 'left'} for c in ['Date', 'Region']],
                        style_data={'color': 'black','backgroundColor': 'white'},
                        style_table={"width":"606px","margin-left":"20.5vw","margin-bottom":"4%"},
                        style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(220, 220, 220)'}],
                        style_header={'backgroundColor': 'rgb(210, 210, 210)','color': 'black','fontWeight': 'bold'}),
    dcc.Interval(
            id='interval-component',
            interval=5*60*1000, # updates in every 5 Minutes
            n_intervals=20
        )
])
@callback(Output('table_tbv','data'),Output('c_tbv_error','children'),
    inputs=dict(n_intervals=Input('interval-component', 'n_intervals'),start_date=Input('my_date_picker_range_tbv','start_date'),end_date=Input('my_date_picker_range_tbv','end_date')))
def update_tbv_selected(n_intervals,start_date,end_date):
    if n_intervals:
        df=dr.df
        start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end =  datetime.datetime.strptime(end_date, '%Y-%m-%d')
        df_yesterday=df[df['Date']==yesterday]
        
        #If start Date > end Date Values ,Then taking Default Values from 01/11/2022 to till date   
        if start>end:
            df_tbv=pd.DataFrame()
            df_tbv_sa=df[(df['Date']>=st) & (df['Date']<=today)]
            df_tbv_initial=pd.DataFrame(df_tbv_sa.groupby(['Location'])['Total Beneficiaries Registered'].sum()).reset_index()
            df_tbv['Location']=df_tbv_initial['Location']
            tbv_n1=[]
            if (df_yesterday.empty)==True:
                for i in range(len(df_tbv_initial)):
                    tbv_n1.append(0)
                df_tbv['Beneficiary Visits-Yesterday']=tbv_n1
            elif (df_yesterday.empty)!=True:
                df_ye=df[df['Date']==yesterday]
                df_yest=pd.DataFrame(df_ye.groupby(['Location'])['Total Beneficiaries Registered'].sum()).reset_index()
                                                    
                mk1=list(df_tbv_initial['Location'])
                #for df_tbv_initial Cumulative Yesterday Count Column
                df_yeste_fe=df_yest.groupby('Location')['Total Beneficiaries Registered'].sum()
                df_yester_ma=df_yeste_fe.to_dict()            
                
                df_tbv_dict={}  #Creating empty Dataframe
                for i in range(len(mk1)):
                    if mk1[i] in df_yester_ma.keys():
                        df_tbv_dict[mk1[i]]=df_yester_ma[mk1[i]]
                    elif mk1[i] not in df_yester_ma.keys():
                        df_tbv_dict[mk1[i]]=0
                df_tbv_dict
                df_tbv_main_impo=pd.DataFrame.from_dict(df_tbv_dict,orient ='index').reset_index()
                #Joining above processed Dataframe to df_tur['Total Unique Registered Yesterday']
                df_tbv['Beneficiary Visits-Yesterday']=df_tbv_main_impo[0]
            else:
                print("I am in else loop-DOWNSTEP.MMU Opeartional Days..!") 
            df_tbv['Beneficiary Visits-Cumulative']=list(df_tbv_initial['Total Beneficiaries Registered'])
            return df_tbv.to_dict('records'),"Start: {} date is Greater Than End: {} Date Values..!".format(start,end)
        elif start==end:
            df_tbv=pd.DataFrame()
            df_tbv_sa=df[df['Date']==start]
            df_tbv_initial=pd.DataFrame(df_tbv_sa.groupby(['Location'])['Total Beneficiaries Registered'].sum()).reset_index()
            df_tbv['Location']=df_tbv_initial['Location']
            tbv_n1=[]
            if (df_yesterday.empty)==True:
                for i in range(len(df_tbv_initial)):
                    tbv_n1.append(0)
                df_tbv['Beneficiary Visits-Yesterday']=tbv_n1
            elif (df_yesterday.empty)!=True:
                df_ye=df[df['Date']==yesterday]
                df_yest=pd.DataFrame(df_ye.groupby(['Location'])['Total Beneficiaries Registered'].sum()).reset_index()
                                                    
                mk1=list(df_tbv_initial['Location'])
                #for df_tbv_initial Cumulative Yesterday Count Column
                df_yeste_fe=df_yest.groupby('Location')['Total Beneficiaries Registered'].sum()
                df_yester_ma=df_yeste_fe.to_dict()            
                
                df_tbv_dict={}  #Creating empty Dataframe
                for i in range(len(mk1)):
                    if mk1[i] in df_yester_ma.keys():
                        df_tbv_dict[mk1[i]]=df_yester_ma[mk1[i]]
                    elif mk1[i] not in df_yester_ma.keys():
                        df_tbv_dict[mk1[i]]=0
                df_tbv_dict
                df_tbv_main_impo=pd.DataFrame.from_dict(df_tbv_dict,orient ='index').reset_index()
                #Joining above processed Dataframe to df_tur['Total Unique Registered Yesterday']
                df_tbv['Beneficiary Visits-Yesterday']=df_tbv_main_impo[0]
            else:
                print("I am in else loop-DOWNSTEP.MMU Opeartional Days..!") 
            df_tbv['Beneficiary Visits-Cumulative']=list(df_tbv_initial['Total Beneficiaries Registered'])
            return df_tbv.to_dict('records')," "
        elif start<end:
            df_tbv=pd.DataFrame()
            df_tbv_sa=df[(df['Date']>=start) & (df['Date']<=end)]
            df_tbv_initial=pd.DataFrame(df_tbv_sa.groupby(['Location'])['Total Beneficiaries Registered'].sum()).reset_index()
            df_tbv['Location']=df_tbv_initial['Location']
            tbv_n1=[]
            if (df_yesterday.empty)==True:
                for i in range(len(df_tbv_initial)):
                    tbv_n1.append(0)
                df_tbv['Beneficiary Visits-Yesterday']=tbv_n1
            elif (df_yesterday.empty)!=True:
                df_ye=df[df['Date']==yesterday]
                df_yest=pd.DataFrame(df_ye.groupby(['Location'])['Total Beneficiaries Registered'].sum()).reset_index()
                                                    
                mk1=list(df_tbv_initial['Location'])
                #for df_tbv_initial Cumulative Yesterday Count Column
                df_yeste_fe=df_yest.groupby('Location')['Total Beneficiaries Registered'].sum()
                df_yester_ma=df_yeste_fe.to_dict()            
                
                df_tbv_dict={}  #Creating empty Dataframe
                for i in range(len(mk1)):
                    if mk1[i] in df_yester_ma.keys():
                        df_tbv_dict[mk1[i]]=df_yester_ma[mk1[i]]
                    elif mk1[i] not in df_yester_ma.keys():
                        df_tbv_dict[mk1[i]]=0
                df_tbv_dict
                df_tbv_main_impo=pd.DataFrame.from_dict(df_tbv_dict,orient ='index').reset_index()
                #Joining above processed Dataframe to df_tur['Total Unique Registered Yesterday']
                df_tbv['Beneficiary Visits-Yesterday']=df_tbv_main_impo[0]
            else:
                print("I am in else loop-DOWNSTEP.MMU Opeartional Days..!") 
            df_tbv['Beneficiary Visits-Cumulative']=list(df_tbv_initial['Total Beneficiaries Registered'])
            return df_tbv.to_dict('records')," "
    else:
        dash.no_update,dash.no_update