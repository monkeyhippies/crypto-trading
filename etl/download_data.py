"""
This script downloads crytpocurrency timeseries data
for all coins listed on poloniex.com

https://poloniex.com/support/api/
"""
import os
import requests
import json

import pandas as pd

ENDPOINT = 'https://poloniex.com/public'
DATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '../',
    'data'
)

class InvalidCurrencyPairException(Exception):
    pass

def save(data, filename):

    df = pd.DataFrame(data)
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
            data = download(
                currency=currency,
                base_currency=base_currency
            )
        except InvalidCurrencyPairException as e:
            print e
            print "SKIPPING: {}, {} Invalid currency pair".format(
                base_currency,
                currency
            )
            continue

        save(data, filename='{}.csv'.format(currency))

def download(
    currency,
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

    return data

if __name__ == '__main__':
    download_all()
