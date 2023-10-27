import json


class Binance:

    @staticmethod
    def credenciales():
        credentials = {
            "url": "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search",
            "apiKey": "X3mF4XZj3aZEbeQHrXxA0a5Ll10BVK763RiOksF1L1xEjRa9Jfjvu1HjA0jwcElW",
            "secretKey": "TcTjrTinyFoWyDa5IaOViWsmu4gHQMBhUzuhkbzji2gp0OAU3YRmpWNlV88F65cd",
            "comment": "gestionTasa"
        }

        return credentials

    @staticmethod
    def consulta_bs(bs=None):
        if bs is None:
            bs = 4000
        import http.client

        conn = http.client.HTTPSConnection("p2p.binance.com")

        payload = {
            "proMerchantAds": False,
            "page": 1,
            "rows": 1,
            "payTypes": ["PagoMovil"
                         ],
            "countries": [],
            "publisherType": "merchant",
            "transAmount": str(bs),
            "asset": "USDT",
            "fiat": "VES",
            "tradeType": "SELL"
        }

        headers = {
            'cookie': "cid=1mnKK17m",
            'authority': "p2p.binance.com",
            'accept': "*/*",
            'accept-language': "es-CL,es-419;q=0.9,es;q=0.8",
            'bnc-uuid': "9d0e0910-7aac-49fd-aab1-437d4f1097f8",
            'c2ctype': "c2c_merchant",
            'clienttype': "web",
            'content-type': "application/json",
            'lang': "es",
            'origin': "https://p2p.binance.com",
            'referer': "https://p2p.binance.com/es/trade/sell/USDT?fiat=VES&payment=PagoMovil",
        }

        conn.request("POST", "/bapi/c2c/v2/friendly/c2c/adv/search", json.dumps(payload), headers)

        res = conn.getresponse()
        data = res.read()

        return json.loads(data)

    @staticmethod
    def consulta_clp(clp=None):
        if clp is None:
            clp = 20000

        print(clp)
        import http.client

        conn = http.client.HTTPSConnection("p2p.binance.com")

        payload = {
            "proMerchantAds": False,
            "page": 1,
            "rows": 1,
            "payTypes": [],
            "countries": [],
            "publisherType": None,
            "transAmou": str(int(clp)),
            "asset": "USDT",
            "fiat": "CLP",
            "tradeType": "BUY"
        }
        print(payload)
        headers = {
            'cookie': "cid=1mnKK17m",
            'authority': "p2p.binance.com",
            'accept': "*/*",
            'accept-language': "es-CL,es-419;q=0.9,es;q=0.8",
            'bnc-uuid': "9d0e0910-7aac-49fd-aab1-437d4f1097f8",
            'c2ctype': "c2c_merchant",
            'clienttype': "web",
            'content-type': "application/json",
            'lang': "es",
            'origin': "https://p2p.binance.com",
            'referer': "https://p2p.binance.com/es/trade/all-payments/USDT?fiat=CLP"
        }

        conn.request("POST", "/bapi/c2c/v2/friendly/c2c/adv/search", json.dumps(payload), headers)

        res = conn.getresponse()
        data = res.read()

        return json.loads(data)
