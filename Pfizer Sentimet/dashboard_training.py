import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output

class ForecastDashboard:
    def __init__(self, mongodb_uri, database, collection):
        self.mongodb_uri = mongodb_uri
        self.database = database
        self.collection = collection
        self.data = None
        self.sentiment_scores = None
        self.models = [LinearRegression(), GradientBoostingRegressor()]
        self.window_sizes = [21]
        self.forecasts = []
        self.load_data()
        self.train_models()
        self.generate_forecasts()

        # Create the Dash app
        self.app = dash.Dash(__name__)

        # Define the layout of the dashboard
        self.app.layout = html.Div(
            children=[
                html.H1("Forecast Results"),
                dcc.Dropdown(
                    id="window-size-dropdown",
                    options=[{"label": str(window_size) + " Days", "value": window_size} for window_size in self.window_sizes],
                    value=self.window_sizes[0]  # Set the default window size
                ),
                dcc.Graph(id='forecast-chart-7days'),
                dcc.Graph(id='forecast-chart-30days'),
                dcc.Graph(id='forecast-chart-90days')
            ]
        )

        # Define the callback function to update the charts based on the selected window size
        @self.app.callback(
            [Output('forecast-chart-7days', 'figure'),
             Output('forecast-chart-30days', 'figure'),
             Output('forecast-chart-90days', 'figure')],
            [Input('window-size-dropdown', 'value')]
        )
        def update_charts(window_size):
            forecast_data = self.get_forecast_data(window_size)
            figure_7days = self.create_figure(forecast_data, 'forecast_7_days', window_size)
            figure_30days = self.create_figure(forecast_data, 'forecast_30_days', window_size)
            figure_90days = self.create_figure(forecast_data, 'forecast_90_days', window_size)
            return figure_7days, figure_30days, figure_90days

    def load_data(self):
        # Load data from MongoDB
        import pymongo
        client = pymongo.MongoClient(self.mongodb_uri)
        db = client[self.database]
        collection = db[self.collection]
        cursor = collection.find()
        df = pd.DataFrame(list(cursor))
        self.data = df.sort_values('date')
        self.sentiment_scores = self.data['avg(label)'].values

    def train_models(self):
        # Train models with different window sizes
        X = []
        y = []
        for window_size in self.window_sizes:
            for i in range(len(self.sentiment_scores) - window_size):
                X.append(list(self.sentiment_scores[i:i + window_size]))
                y.append(self.sentiment_scores[i + window_size])
            X = np.array(X)
            y = np.array(y)
            print('Training for window size', str(window_size))
            for model in self.models:
                model.fit(X, y)

    def generate_forecasts(self):
        # Generate forecasts for different time periods
        for window_size in self.window_sizes:
            forecast_data = {}
            for model in self.models:
                forecast_7_days = self.generate_forecast(model, window_size, 7)
                forecast_30_days = self.generate_forecast(model, window_size, 30)
                forecast_90_days = self.generate_forecast(model, window_size, 90)
                model_name = model.__class__.__name__
                forecast_data[model_name] = {
                    'forecast_7_days': forecast_7_days,
                    'forecast_30_days': forecast_30_days,
                    'forecast_90_days': forecast_90_days
                }
            self.forecasts.append({'window_size': window_size, 'forecast_data': forecast_data})

    def generate_forecast(self, model, window_size, forecast_days):
        # Generate forecast for the next n days
        forecast = []
        last_window = self.sentiment_scores[-window_size:]
        for _ in range(forecast_days):
            prediction = model.predict([last_window])[0]
            forecast.append(prediction)
            last_window = np.append(last_window[1:], prediction)
        return forecast

    def get_forecast_data(self, window_size):
        # Get the forecast data for a specific window size
        for forecast in self.forecasts:
            if forecast['window_size'] == window_size:
                return forecast['forecast_data']

    def create_figure(self, forecast_data, forecast_duration, window_size):
        # Create the forecast chart
        fig = go.Figure()
        for model_name, model_forecasts in forecast_data.items():
            forecast = model_forecasts[forecast_duration]
            fig.add_trace(go.Scatter(
                x=list(range(len(forecast))),
                y=forecast,
                mode='lines',
                name=model_name
            ))
        fig.update_layout(
            title='Forecast for {} Days (Window Size: {})'.format(forecast_duration, window_size),
            xaxis=dict(title='Day'),
            yaxis=dict(title='Forecast Value')
        )
        return fig

    def run(self):
        self.app.run_server(debug=True)





if __name__ == '__main__':
    mongodb_uri = 'mongodb://localhost:27017/'
    database = 'PFV'
    collection = 'Sentiment_Date_wise'

    dashboard = ForecastDashboard(mongodb_uri, database, collection)
    dashboard.run()
