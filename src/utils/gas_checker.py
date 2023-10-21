from time import sleep

from loguru import logger
from web3 import Web3

from config import MAX_GWEI


def get_gas() -> int:
    try:
        w3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/eth'))
        gas_price = w3.eth.gas_price
        gwei = w3.from_wei(gas_price, 'gwei')

        return gwei
    except Exception as error:
        logger.error(f"Error while getting gas price: {error}")


def wait_gas() -> None:
    while True:
        gas = get_gas()

        if gas > MAX_GWEI:
            logger.info(f'Current GWEI: {gas} > {MAX_GWEI}')
            sleep(60)
        else:
            break
