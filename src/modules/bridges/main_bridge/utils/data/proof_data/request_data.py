import pyuseragents


headers = {
    'authority': 'mainnet-api-bridge.scroll.io',
    'accept': '*/*',
    'accept-language': 'ru,en;q=0.9,ru-RU;q=0.8,en-US;q=0.7',
    'content-type': 'application/json',
    'origin': 'https://scroll.io',
    'referer': 'https://scroll.io/',
    'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': pyuseragents.random(),
}
