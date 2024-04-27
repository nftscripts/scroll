from typing import List, Union
from asyncio import sleep
import random

from loguru import logger
from web3 import Web3
import ccxt

from src.modules.okx_withdraw.utils.okx_sub_transfer import transfer_from_subaccs_to_main
from src.modules.okx_withdraw.utils.data import get_withdrawal_fee
from src.utils.wrappers.decorators import retry
from src.utils.user.account import Account

from okx_data.okx_data import (
    USE_PROXY,
    proxy,
)

from src.utils.data.chains import (
    okx_chain_mapping,
    chain_mapping,
)


class OkxWithdraw:
    def __init__(self, api_key: str, api_secret: str, passphrase: str, amount: Union[float, List[float]],
                 receiver_address: str, chain: str) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        if isinstance(amount, List):
            self.amount = round(random.uniform(amount[0], amount[1]), 6)
        elif isinstance(amount, float):
            self.amount = amount
        else:
            logger.error(f'amount must be List[float] or float. Got {type(amount)}')
            return

        self.receiver_address = receiver_address
        self.chain = chain
        rpc = okx_chain_mapping[chain].rpc
        self.web3 = Web3(Web3.HTTPProvider(rpc))
        self.okex = ccxt.okx({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'password': self.passphrase,
            'enableRateLimit': True,
            'proxies': {
                'http': proxy if USE_PROXY is True else None,
                'https': proxy if USE_PROXY is True else None
            },
        })

    def __repr__(self) -> str:
        return f'Withdrawing {self.amount} ETH to {self.receiver_address} | CHAIN: {self.chain}'

    async def withdraw(self) -> None:
        try:
            chain_name = 'ETH' + '-' + self.chain
            fee = await get_withdrawal_fee('ETH', chain_name, self.okex)
            eth_balance_before_withdraw = self.web3.eth.get_balance(
                self.web3.to_checksum_address(self.receiver_address))
            self.okex.withdraw('ETH', self.amount, self.receiver_address, params={
                'toAddress': self.receiver_address,
                'chainName': chain_name,
                'dest': 4,
                'fee': fee,
                'pwd': '-',
                'amt': self.amount,
                'network': self.chain
            })

            logger.success(
                f'Successfully withdrawn {self.amount} ETH to {self.chain} for wallet {self.receiver_address}')
            await self.wait_for_eth(eth_balance_before_withdraw)

        except Exception as ex:
            logger.error(f'Something went wrong {ex}')
            return

    async def wait_for_eth(self, eth_balance_before_withdraw: int) -> None:
        logger.info(f'Waiting for ETH to arrive on Metamask...')
        while True:
            try:
                balance = self.web3.eth.get_balance(
                    self.web3.to_checksum_address(self.receiver_address))
                if balance > eth_balance_before_withdraw:
                    logger.success(f'ETH has arrived | [{self.receiver_address}]')
                    break
                await sleep(20)
            except Exception as ex:
                logger.error(f'Something went wrong {ex}')
                await sleep(10)
                continue


class OkxDeposit(Account):
    def __init__(self, private_key: str, from_chain: str, amount: Union[float, List[float]],
                 keep_value: Union[float, List[float]], withdraw_all: bool, receiver_address: str) -> None:
        self.from_chain = from_chain
        rpc = chain_mapping[from_chain.lower()].rpc
        super().__init__(private_key, rpc=rpc)
        self.scan = chain_mapping[from_chain.lower()].scan
        self.receiver_address = receiver_address
        if isinstance(amount, List):
            self.amount = round(random.uniform(amount[0], amount[1]), 6)
        elif isinstance(amount, float):
            self.amount = amount
        else:
            logger.error(f'amount must be List[float] or float. Got {type(amount)}')
            return

        if isinstance(keep_value, list):
            self.keep_value = random.uniform(keep_value[0], keep_value[1])
        else:
            self.keep_value = keep_value
        self.withdraw_all = withdraw_all

    def __repr__(self) -> str:
        return f'Withdrawing {self.amount} ETH from {self.account_address} to {self.receiver_address} | CHAIN: {self.from_chain}'

    @retry()
    async def deposit(self) -> None:
        balance = self.get_wallet_balance('ETH', '...')

        if balance == 0:
            logger.error(f'Your balance is 0 | {self.account.address}')
            return
        if self.withdraw_all is True:
            amount = balance - int(self.keep_value * 10 ** 18)
        else:
            amount = int(self.amount * 10 ** 18)

        tx = {
            'chainId': self.web3.eth.chain_id,
            'from': self.account_address,
            'to': self.web3.to_checksum_address(self.receiver_address),
            'value': amount,
            'nonce': self.web3.eth.get_transaction_count(self.account_address),
            'gasPrice': self.web3.eth.gas_price
        }
        gas_limit = self.web3.eth.estimate_gas(tx)
        tx.update({'gas': gas_limit})

        tx_hash = self.sign_transaction(tx)

        self.logger.success(
            f'Successfully withdrawn {round((amount / 10 ** 18), 6)} from {self.account.address} to {self.receiver_address} TX: {self.scan}/{tx_hash}'
        )

        await sleep(300)
        logger.debug('Transferring from SubAccount to MainAccount')
        await transfer_from_subaccs_to_main()
