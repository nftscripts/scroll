from aiohttp import ClientSession
from datetime import datetime
from asyncio import sleep
import base64
import json
import hmac

from typing import (
    Callable,
    Awaitable,
    Optional,
    Union,
    Dict,
)

from loguru import logger

from okx_data.okx_data import (
    SECRET_KEY,
    PASSPHRASE,
    API_KEY,
)


async def signature(timestamp: str, method: str, url: str, body: Optional[str]
                    ) -> Union[str, Callable[[str, str, str, Optional[str]], Awaitable[str]]]:
    try:
        if not body:
            body = ""
        message = timestamp + method.upper() + url + body
        mac = hmac.new(
            bytes(SECRET_KEY, encoding="utf-8"),
            bytes(message, encoding="utf-8"),
            digestmod="sha256",
        )
        d = mac.digest()
        return base64.b64encode(d).decode("utf-8")
    except Exception as ex:
        logger.error(ex)
        return await signature(timestamp, method, url, body)


async def generate_request_headers(url: str, method: str, body=''
                                   ) -> Dict[str, Union[str, Callable[[str, str, str, Optional[str]], Awaitable[str]]]]:
    dt_now = datetime.utcnow()
    ms = str(dt_now.microsecond).zfill(6)[:3]
    timestamp = f"{dt_now:%Y-%m-%dT%H:%M:%S}.{ms}Z"
    headers = {
        "Content-Type": "application/json",
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": await signature(timestamp, method, url, body),
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
        'x-simulated-trading': '0'
    }
    return headers


async def send_request(url: str, timeout: int, headers: dict, method: str, data='') -> Optional[str]:
    try:
        async with ClientSession() as session:
            async with session.get(url, timeout=timeout, headers=headers,
                                   data=data) if method == 'GET' else session.post(url,
                                                                                   timeout=timeout,
                                                                                   headers=headers,
                                                                                   data=data) as response:
                if response.status == 200:
                    await sleep(2)
                    return json.loads(await response.text())
                logger.error(f"Couldn't send request {url} : {await response.text()}")
                return False
    except Exception as ex:
        logger.error(ex)
        return False


async def transfer_from_subaccs_to_main(token='ETH') -> None:
    try:
        method = 'GET'
        headers = await generate_request_headers(url="/api/v5/users/subaccount/list",
                                                 method=method)
        list_sub = await send_request(f"https://www.okx.com/api/v5/users/subaccount/list", 10, headers, method)
        if not list_sub:
            return
        for sub_data in list_sub['data']:
            __name = sub_data['subAcct']
            method_ = "GET"
            headers = await generate_request_headers(
                url=f"/api/v5/asset/subaccount/balances?subAcct={__name}&ccy={token}",
                method=method)
            sub_balance = await send_request(
                f"https://www.okx.com/api/v5/asset/subaccount/balances?subAcct={__name}&ccy={token}", 10, headers,
                method_)
            if not sub_balance:
                return
            sub_balance = float(sub_balance['data'][0]['bal'])
            if sub_balance == 0:
                continue

            body = {"ccy": f"{token}", "amt": str(sub_balance), "from": 6, "to": 6, "type": "2",
                    "subAcct": __name}
            method = "POST"
            headers = await generate_request_headers(url=f"/api/v5/asset/transfer",
                                                     body=str(body), method=method)
            res = await send_request("https://www.okx.com/api/v5/asset/transfer", 10, headers, method, str(body))
            if len(res['data']) != 0:
                logger.success(f'Successfully transferred {sub_balance} {token}')
            else:
                if 'Insufficient balance' in str(res):
                    await sleep(2)
                    continue
                logger.warning(f'Error - {res}')
            await sleep(1)

    except Exception as ex:
        logger.error(ex)
        await sleep(2)
        return
