"""
This script downloads crytpocurrency timeseries data
for all coins listed on poloniex.com

https://poloniex.com/support/api/
"""
import os
import requests
import json
from datetime import datetime

import pandas as pd

ENDPOINT = 'https://poloniex.com/public'
DATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '../',
    'data'
)

class InvalidCurrencyPairException(Exception):
    pass

def transform(df):

    date_objs = df['date'].apply(lambda x: datetime.fromtimestamp(x))
    df['day_of_week'] = date_objs.apply(lambda x: x.strftime("%A"))
    df['time_of_day'] = date_objs.apply(lambda x: (x - x.replace(hour=0, minute=0, second=0)).seconds)

    return df

def save(df, filename):

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    df.to_csv(
        os.path.join(DATA_DIR, filename),
        index=False
    )

def GET(**params):
    """
    returns json-loaded data
    """

    response = requests.get(ENDPOINT, params=params)
    data = json.loads(response.text)

    if 'error' in data:
        if 'Invalid currency' in data['error']:
            raise InvalidCurrencyPairException(str(data))
        else:
            raise Exception(str(data))

    return data

def currencies():

    response = GET(
        command="returnCurrencies"
    )

    return response.keys()

def download_all():
    """
    downloads all currencies ts data
    BTC is always the first currency in currency_pair
    """

    base_currency = 'BTC'

    for currency in currencies():

        if currency == 'BTC':
            continue

        print 'Getting data for {}'.format(currency)

        try:
            download(
                currency=currency,
                filename='{}.csv'.format(currency),
                base_currency=base_currency
            )
        except InvalidCurrencyPairException as e:
            print e
            print "SKIPPING: {}, {} Invalid currency pair".format(
                base_currency,
                currency
            )
            continue

def download(
    currency,
    filename,
    base_currency='BTC',
    start=1405699200,
    end=9999999999,
    period=300
):

    currency_pair = '{}_{}'.format(base_currency, currency)
    data = GET(
        command='returnChartData', 
        currencyPair=currency_pair,
        start=start,
        end=end,
        period=period
    )

    df = pd.DataFrame(data)
    df = transform(df)

    save(df, filename)

if __name__ == '__main__':
    download_all()
