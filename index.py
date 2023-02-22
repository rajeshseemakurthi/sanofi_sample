
#Importing Necessary Modules
from dash import Dash,html
import dash_bootstrap_components as dbc
import dash

external_scripts = [
    {
        'src': 'https://code.jquery.com/jquery-3.6.1.js',
        'integrity': 'sha256-3zlB5s2uwoUzrXK3BT7AX3FyvojsraNFxCc2vC/7pNI=',
        'crossorigin': 'anonymous'
    },
    {
        'src': 'https://cdnjs.cloudflare.com/ajax/libs/popper.js/2.9.2/umd/popper.min.js',
    },
    {
        'src': 'https://cdn.jsdelivr.net/npm/bootstrap@4.1.3/dist/js/bootstrap.min.js',
        'integrity': 'sha384-ChfqqxuZUCnJSK3+MXmPNIyE6ZbWh2IMqE241rYiqJxyMiZ6OW/JmZQ5stwEULTy',
        'crossorigin': 'anonymous'
    },
    {
        'src':'https://kit.fontawesome.com/a076d05399.js',
        'crossorigin': 'anonymous'
    }
]

# external CSS stylesheets
external_stylesheets = [
    {
        "href":"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
        "rel":"stylesheet"
    },{
        'href': 'https://fonts.googleapis.com/css?family=Bree Serif',
        'rel': 'stylesheet',
    },{
        'href':'https://fonts.googleapis.com/css?family=Lobster',
        'rel':'stylesheet',
    },{
        'href': 'https://fonts.googleapis.com/css?family=Audiowide|Sofia|Trirong',
        'rel': 'stylesheet',
    },
    {
        'href': 'jquery.datetimepicker.min.css',
        'rel': 'stylesheet',
    },
    {
        'href': 'https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-Zenh87qX5JnK2Jl0vWa8Ck2rdkQ2Bzep5IDxbcnCeuOxjzrPF/et3URy9Bv1WTRi',
        'crossorigin': 'anonymous'
    }
]

app = Dash(__name__,external_scripts=external_scripts,external_stylesheets=external_stylesheets,use_pages=True,meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,use-scalable=no'}])
style = {'width': '50%', 'height': '500px', 'float': 'left'}

app.head = [html.Link(rel='stylesheet', href='./assets/uidai_style.css')]

app.layout = html.Div([
	dash.page_container
])

if __name__ == '__main__':
    app.run_server(debug=True, port=8092, host='127.0.0.1')
