import dash
import datetime
from datetime import date
from dash import html, dcc
from dash import Dash, dash_table
import pandas as pd
import pandas
from collections import OrderedDict
from updated_date import Current_things
from pandas._libs.tslibs.timestamps import Timestamp
from data_reading import Data_Reading
from dash import html, dcc, callback, Input, Output
# from sql_query_fetching_second import df

dr=Data_Reading()
dash.register_page(__name__, path='/c_mp'
                            ,title='c_mp'
                            ,name='c_mp'
                   )

st = Timestamp('2022-11-01 00:00:00')
# st = Timestamp('2022-11-01 00:00:00', freq='MS')
st = st.to_pydatetime()
today = pd.to_datetime(date.today(), format='%Y-%m-%d')
yesterday = today-pd.Timedelta(days=1)

start_clinic=Timestamp('2022-10-15 00:00:00')
# start_clinic=Timestamp('2022-10-15 00:00:00', freq='MS')
end_clinic=Timestamp('2022-11-05 00:00:00')
# end_clinic=Timestamp('2022-11-05 00:00:00', freq='MS')

#Empty DataFrame for df['Total Beneficiaries taken Lab tests']
df_mp_main=pd.DataFrame()

obj_datepicker_mp=Current_things()

df_column_clinic = pd.DataFrame({'Location':pd.Series(dtype='str'),
                        'Common Diseases-Yesterday Count': pd.Series(dtype='int'),
                        'Common Diseases-Cumulative Count': pd.Series(dtype='int')})

layout = html.Div([
    html.Div([html.P("Total Medicated Patients")],className='cd_title',style={"margin-left":"26%","margin-top":"3%","border":"2px double black","border-radius":"8px","width":"46%","text-align":'center',"font-size":"x-large","color":"black","font-family":"serif","font-weight":"700","background-color":"#d9dae0","padding-top":"3px"}),
    html.Div([
    html.Div(dcc.DatePickerRange(id='my_date_picker_range_mp',display_format='D-M-Y',initial_visible_month=obj_datepicker_mp.current_date(),min_date_allowed=date(2022, 2, 1),max_date_allowed=obj_datepicker_mp.current_date(),start_date=date(2022, 2, 1),end_date=obj_datepicker_mp.current_date(),style={"position":"relative","display":"inline-block","width":"110%","border-radius":"39px","margin-left":"115%","margin-top":"5%","margin-bottom":"7%"}),style={}),
    html.A([html.P("Home",style={})],href='/',style={"border":"2px double black","margin-left":"41%","border-radius":"8px","height":"36px","padding":"6px","margin-top":"18px","background-color":"rgb(215, 215, 215)"}),
    html.A([html.I(className="fa fa-refresh",style={})],href=dash.page_registry['pages.c_mp']['path'],style={"width":"4%","height":"2.3rem","margin-left":"0.8rem","margin-top":"1.5%","text-align":"center","font-size":"22px","background-color":"rgb(215,215,215)","border-radius":"8px","border":"2px double black"})
    ],style={'display':'flex','flex-direction':'row',"margin-bottom":'-23px'}),
    html.Div([html.Div(id="c_cd_error",className="cd_error",style={"width":"70%","height":"1.5rem","margin-left":"20%","margin-top":"3px","font-family":"ui-sans-serif","font-size":"medium"})],style={}),
    dash_table.DataTable(columns=[{'id': c, 'name': c} for c in df_column_clinic.columns],id="table_cd",
                        style_cell={'overflow': 'hidden','textOverflow': 'ellipsis','maxWidth': '50%','textAlign': 'center'},
                        style_cell_conditional=[{'if': {'column_id': c},'textAlign': 'left'} for c in ['Date', 'Region']],
                        style_data={'color': 'black','backgroundColor': 'white'},
                        style_table={"width":"606px","margin-left":"17%","margin-bottom":"4%"},
                        style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(220, 220, 220)'}],
                        style_header={'backgroundColor': 'rgb(210, 210, 210)','color': 'black','fontWeight': 'bold'}),
        dcc.Interval(
            id='interval-component',
            interval=5*60*1000, # updates in every 5 Minutes
            n_intervals=20
        )
])

@callback(Output('table_cd','data'),Output('c_cd_error','children'),
    inputs=dict(n_intervals=Input('interval-component', 'n_intervals'),start_date=Input('my_date_picker_range_mp','start_date'),end_date=Input('my_date_picker_range_mp','end_date')))
def update_tc_selected(n_intervals,start_date,end_date):
    if n_intervals:
        df=dr.df
        start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end =  datetime.datetime.strptime(end_date, '%Y-%m-%d')
        df_yesterday=df[df['Date']==yesterday]
        
        #If start Date > end Date Values ,Then taking Default Values from 01/11/2022 to till date   
        if start>end:
            df_mp_main=pd.DataFrame()
            return dash.no_update,"Start: {} date is Greater Than End: {} Date Values..!".format(start,end)
        elif start==end:
            df_mp_main=pd.DataFrame()
            df_mp=df[(df['Date']==start)]
            df_mp_initial=pd.DataFrame(df_mp.groupby(['Location'])['#ben to Drug Prescribed'].sum()).reset_index()
            df_mp_main['Location']=df_mp_initial['Location']
            mp_n1=[]
            if (df_yesterday.empty)==True:
                for i in range(len(df_mp_initial)):
                    mp_n1.append(0)
                df_mp_main['Common Diseases-Yesterday Count']=mp_n1
            else:
                df_yes=df[df['Date']==yesterday]
                df_yest=pd.DataFrame(df_yes.groupby(['Location'])['#ben to Drug Prescribed'].sum()).reset_index()
                
                mk1=list(df_mp_initial['Location'])
                #for Clinic Cumulative Yesterday Count Column
                df_yeste_fe=df_yest.groupby('Location')['#ben to Drug Prescribed'].sum()
                df_yester_ma=df_yeste_fe.to_dict()     #Getting an complete Data DF       
                
                df_yester_clin={}  #Creating empty Dataframe
                for i in range(len(mk1)):
                    if mk1[i] in df_yester_ma.keys():
                        df_yester_clin[mk1[i]]=df_yester_ma[mk1[i]]
                    elif mk1[i] not in df_yester_ma.keys():
                        df_yester_clin[mk1[i]]=0
                df_yester_clin
                df_clinic_main=pd.DataFrame.from_dict(df_yester_clin,orient ='index').reset_index()
                #Joining above processed Dataframe to df_clinic_operations['Clinic Operations Done Yesterday']
                df_mp_main['Common Diseases-Yesterday Count']=df_clinic_main[0]
            df_mp_main['Common Diseases-Cumulative Count']=list(df_mp_initial['#ben to Drug Prescribed'])
            return df_mp_main.to_dict('records'),""
        elif start<end:
            df_mp_main=pd.DataFrame()
            df_mp_initial=df[(df['Date']>=start) & (df['Date']<=end)]
            df_mp_initial=pd.DataFrame(df_mp_initial.groupby(['Location'])['#ben to Drug Prescribed'].sum()).reset_index()
            df_mp_main['Location']=df_mp_initial['Location']
            mp_n1=[]
            if (df_yesterday.empty)==True:
                for i in range(len(df_mp_initial)):
                    mp_n1.append(0)
                df_mp_main['Common Diseases-Yesterday Count']=mp_n1
            else:
                df_yes=df[df['Date']==yesterday]
                df_yest=pd.DataFrame(df_yes.groupby(['Location'])['#ben to Drug Prescribed'].sum()).reset_index()
                
                mk1=list(df_mp_initial['Location'])
                #for Clinic Cumulative Yesterday Count Column
                df_yeste_fe=df_yest.groupby('Location')['#ben to Drug Prescribed'].sum()
                df_yester_ma=df_yeste_fe.to_dict()     #Getting an complete Data DF       
                
                df_yester_clin={}  #Creating empty Dataframe
                for i in range(len(mk1)):
                    if mk1[i] in df_yester_ma.keys():
                        df_yester_clin[mk1[i]]=df_yester_ma[mk1[i]]
                    elif mk1[i] not in df_yester_ma.keys():
                        df_yester_clin[mk1[i]]=0
                df_yester_clin
                df_clinic_main=pd.DataFrame.from_dict(df_yester_clin,orient ='index').reset_index()
                #Joining above processed Dataframe to df_clinic_operations['Clinic Operations Done Yesterday']
                df_mp_main['Common Diseases-Yesterday Count']=df_clinic_main[0]
            df_mp_main['Common Diseases-Cumulative Count']=list(df_mp_initial['#ben to Drug Prescribed'])
            return df_mp_main.to_dict('records'),""
    else:
        dash.no_update,dash.no_update