# This file is licensed under CC0 Universal 1.0
import requests
from helpers import time_cache


# use at most 15 minute old exchange rate
@time_cache(60 * 15)
def get_fx_rates():
    """ Get fx rates for USD:CAD, USD:XMR """
    url = 'https://min-api.cryptocompare.com/data/price?fsym=USD&tsyms=CAD,XMR'
    try:
        return requests.get(url).json()
    except requests.RequestException as e:
        # send yourself a notification via Email, Telegram bot, Matrix bot, Discord webhook
        # for fiat currencies use a backup exchange rate since we can expect some consistency
        # for crypto-currencies, consider showing user an error instead
        return {'CAD': 1.3}


def cad_to_usd(cad):
    return cad / get_fx_rates()['CAD']


def usd_to_cad(usd):
    return usd * get_fx_rates()['CAD']


def usd_to_xmr(usd, as_atomic=False):
    # throws KeyEror
    return round(usd * get_fx_rates()['XMR'] * 1e12) if as_atomic else round(usd * get_fx_rates()['XMR'], 12)


def price_as(usd: float, currency='USD', as_str=False):
    # throws KeyError if currency = 'XMR'
    currency = currency.upper()
    if currency == 'CAD':
        return f'C${usd_to_cad(usd):.2f}' if as_str else usd_to_cad(usd)
    elif currency == 'XMR':
        return f'Ɱ {usd_to_xmr(usd):.5f}' if as_str else usd_to_xmr(usd)
    return f'US${usd:.2f}' if as_str else usd


def price_alt(usd, currency='USD', as_str=False):
    return price_as(usd, currency='USD' if currency == 'CAD' else 'CAD', as_str=as_str)
