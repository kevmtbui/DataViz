from flask import Flask, render_template, request, redirect
import pandas as pd
import plotly.graph_objs as go
import os
from utils.etl import process_csv

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

saved_charts = []
latest_charts = []
latest_filename = ""

@app.route('/', methods=['GET', 'POST'])
def index():
    global saved_charts, latest_charts, latest_filename
    summary = {}
    indicators = {'MA20': False, 'MA50': False, 'RSI': False, 'Bollinger': False, 'MACD': False}
    trim_nan = False

    if request.method == 'POST':
        # Delete request
        if 'delete_saved' in request.form:
            try:
                index_to_delete = int(request.form['delete_saved'])
                if 0 <= index_to_delete < len(saved_charts):
                    del saved_charts[index_to_delete]
            except:
                pass
            return redirect('/')

        # Save chart request
        if 'save_chart' in request.form:
            idx = int(request.form['save_chart']) - 1
            if 0 <= idx < len(latest_charts):
                saved_charts.append(latest_charts[idx])
                del latest_charts[idx]
            return redirect('/')

        # Upload + graph generation
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == "":
                return render_template("index.html", charts=[], summary={}, saved_charts=saved_charts)

            latest_filename = os.path.splitext(file.filename)[0]
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            selected = request.form.getlist("indicators")
            for ind in selected:
                indicators[ind] = True

            trim_nan = 'trim' in request.form
            df, summary = process_csv(filepath, indicators)

            if trim_nan:
                columns_to_check = []
                if indicators['MA20']: columns_to_check.append('MA20')
                if indicators['MA50']: columns_to_check.append('MA50')
                if indicators['RSI']: columns_to_check.append('RSI')
                if indicators['MACD']: columns_to_check.extend(['MACD', 'Signal'])
                if indicators['Bollinger']: columns_to_check.extend(['UpperBand', 'LowerBand'])
                if columns_to_check:
                    df = df.dropna(subset=columns_to_check, how='any')

            if df.empty:
                return render_template("index.html", charts=[], summary={"Error": "No data to display after trimming."}, saved_charts=saved_charts)

            charts = []

            fig = go.Figure()
            fig.update_layout(
                title="Stock Price & Indicators",
                yaxis_title="Price",
                plot_bgcolor="#121212",
                paper_bgcolor="#121212",
                font_color="white",
                xaxis=dict(rangeslider=dict(visible=True), type='date')
            )
            fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name='Close'))

            if indicators['MA20']: fig.add_trace(go.Scatter(x=df['Date'], y=df['MA20'], name='MA20'))
            if indicators['MA50']: fig.add_trace(go.Scatter(x=df['Date'], y=df['MA50'], name='MA50'))
            if indicators['Bollinger'] and 'UpperBand' in df and 'LowerBand' in df:
                fig.add_trace(go.Scatter(x=df['Date'], y=df['UpperBand'], name='Upper Band', line=dict(dash='dot')))
                fig.add_trace(go.Scatter(x=df['Date'], y=df['LowerBand'], name='Lower Band', line=dict(dash='dot')))
            charts.append({'html': fig.to_html(full_html=False), 'label': f"{latest_filename} – Main Chart"})

            if indicators['RSI'] and 'RSI' in df:
                fig_rsi = go.Figure()
                fig_rsi.update_layout(
                    title="RSI (Relative Strength Index)",
                    yaxis_title="RSI",
                    plot_bgcolor="#121212",
                    paper_bgcolor="#121212",
                    font_color="white",
                    xaxis=dict(rangeslider=dict(visible=True), type='date')
                )
                fig_rsi.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], name='RSI'))
                charts.append({'html': fig_rsi.to_html(full_html=False), 'label': f"{latest_filename} – RSI"})

            if indicators['MACD'] and 'MACD' in df and 'Signal' in df:
                fig_macd = go.Figure()
                fig_macd.update_layout(
                    title="MACD",
                    yaxis_title="MACD Value",
                    plot_bgcolor="#121212",
                    paper_bgcolor="#121212",
                    font_color="white",
                    xaxis=dict(rangeslider=dict(visible=True), type='date')
                )
                fig_macd.add_trace(go.Scatter(x=df['Date'], y=df['MACD'], name='MACD'))
                fig_macd.add_trace(go.Scatter(x=df['Date'], y=df['Signal'], name='Signal'))
                charts.append({'html': fig_macd.to_html(full_html=False), 'label': f"{latest_filename} – MACD"})

            latest_charts = charts.copy()

    return render_template("index.html", charts=latest_charts, summary=summary, saved_charts=saved_charts)

if __name__ == '__main__':
    app.run(debug=True)
