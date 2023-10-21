from typing import Optional

from loguru import logger
import ccxt


async def get_withdrawal_fee(symbol_withdraw: str, chain_name: str, exchange: ccxt.okx) -> Optional[float]:
    currencies = exchange.fetch_currencies()
    for currency in currencies:
        if currency == symbol_withdraw:
            currency_info = currencies[currency]
            network_info = currency_info.get('networks', None)
            if network_info:
                for network in network_info:
                    network_data = network_info[network]
                    network_id = network_data['id']
                    if network_id == chain_name:
                        withdrawal_fee = currency_info['networks'][network]['fee']
                        if withdrawal_fee == 0:
                            return 0
                        else:
                            return withdrawal_fee

    logger.error(f"Can't get commission value, check symbolWithdraw and network values")
    return
