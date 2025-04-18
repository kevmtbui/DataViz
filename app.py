from flask import Flask, render_template, request
import pandas as pd
import plotly.graph_objs as go
import os
from utils.etl import process_csv

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    charts = []
    summary = {}
    if request.method == 'POST':
        file = request.files['file']
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        df, summary = process_csv(filepath)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name='Close'))
        fig.add_trace(go.Scatter(x=df['Date'], y=df['MA20'], name='MA20'))
        chart = fig.to_html(full_html=False)
        charts.append(chart)

    return render_template("index.html", charts=charts, summary=summary)

if __name__ == '__main__':
    app.run(debug=True)