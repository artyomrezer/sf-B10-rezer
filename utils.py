import requests
import json
from config import headers, currencies_dict

class APIError(Exception):
    pass

class CurrencyConverter:
    @staticmethod
    def convert(api_params):
        api_params_len = len(api_params)

        if api_params_len != 3:
            raise APIError(f'некорректное количество параметров в строке, должно быть 3, подано {api_params_len}.')

        from_, to_, amount = api_params
        from_, to_ = from_.upper(), to_.upper()

        if from_ not in currencies_dict.keys():
            raise APIError(f'исходная валюта {from_} отсутствует среди поддерживаемых валют')

        if to_ not in currencies_dict.keys():
            raise APIError(f'конечная валюта {to_} отсутствует среди поддерживаемых валют')

        if from_ == to_:
            raise APIError(f'исходная валюта не должна быть такой же как конечная')

        try:
            amount = float(amount.replace(',', '.'))
        except ValueError:
            raise APIError(f'введенное количество исходной валюты не число')

        url = f'https://api.apilayer.com/exchangerates_data/convert?from={from_}&to={to_}&amount={amount}'
        payload = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        response = json.loads(response.content)
        result = response['result']
        return from_, to_, amount, result
