import pandas as pd

def process_csv(filepath):
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    df['MA20'] = df['Close'].rolling(window=20).mean()

    summary = {
        'Min Price': round(df['Close'].min(), 2),
        'Max Price': round(df['Close'].max(), 2),
        'Mean Volume': int(df['Volume'].mean())
    }

    return df, summary