import pandas as pd

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def process_csv(filepath, indicators):
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')

    summary = {
        'Min Price': round(df['Close'].min(), 2),
        'Max Price': round(df['Close'].max(), 2),
        'Mean Volume': int(df['Volume'].mean())
    }

    if indicators.get('MA20'):
        df['MA20'] = df['Close'].rolling(window=20).mean()

    if indicators.get('MA50'):
        df['MA50'] = df['Close'].rolling(window=50).mean()

    if indicators.get('RSI'):
        df['RSI'] = compute_rsi(df['Close'])

    if indicators.get('Bollinger'):
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['STD20'] = df['Close'].rolling(window=20).std()
        df['UpperBand'] = df['MA20'] + 2 * df['STD20']
        df['LowerBand'] = df['MA20'] - 2 * df['STD20']

    if indicators.get('MACD'):
        df['EMA12'] = df['Close'].ewm(span=12).mean()
        df['EMA26'] = df['Close'].ewm(span=26).mean()
        df['MACD'] = df['EMA12'] - df['EMA26']
        df['Signal'] = df['MACD'].ewm(span=9).mean()

    return df, summary
