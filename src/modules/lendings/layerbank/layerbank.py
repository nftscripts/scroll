from typing import Union, List
import random

from src.database.utils import DataBaseUtils
from src.utils.user.account import Account
from src.utils.data.tokens import tokens
from config import USE_DATABASE

from src.utils.data.contracts import (
    contracts,
    abi_names,
)


class LayerBankDeposit(Account):
    def __init__(self, private_key: str, amount: Union[float, List[float]], use_percentage: bool,
                 percentage: Union[float, List[float]], only_collateral: bool) -> None:

        super().__init__(private_key=private_key)

        if isinstance(amount, List):
            self.amount = random.uniform(amount[0], amount[1])
        elif isinstance(amount, float):
            self.amount = amount
        else:
            self.logger.error(f'amount must be float or list[float]. Got {type(amount)}')
            return

        self.use_percentage = use_percentage
        if isinstance(percentage, List):
            self.percentage = random.uniform(percentage[0], percentage[1])
        elif isinstance(percentage, float):
            self.percentage = percentage
        else:
            self.logger.error(f'percentage must be float or list[float]. Got {type(percentage)}')
            return

        self.contract = self.load_contract(
            address=contracts['layerbank'],
            web3=self.web3,
            abi_name=abi_names['layerbank']
        )
        self.only_collateral = only_collateral
        self.db_utils = DataBaseUtils('lending')

    def __repr__(self) -> str:
        return f'{self.__class__.__name__} | [{self.account_address}]'

    async def deposit(self) -> None:
        balance = self.get_wallet_balance('ETH', tokens['ETH'])

        if balance == 0:
            self.logger.warning(f'Your balance is 0 | [{self.account_address}]')
            return
        if not self.only_collateral:
            if self.use_percentage:
                amount = int(balance * self.percentage)
            else:
                amount = int(self.amount * 10 ** 18)
        else:
            amount = 0

        if not self.only_collateral:
            tx = self.contract.functions.supply(
                self.web3.to_checksum_address('0x274C3795dadfEbf562932992bF241ae087e0a98C'),
                amount
            ).build_transaction({
                'value': amount,
                'nonce': self.web3.eth.get_transaction_count(self.account_address),
                'from': self.account_address,
                "gasPrice": self.web3.eth.gas_price
            })
        else:
            txs = [self.contract.functions.enterMarkets(
                [self.web3.to_checksum_address('0x274C3795dadfEbf562932992bF241ae087e0a98C')]
            ), self.contract.functions.exitMarket(
                self.web3.to_checksum_address('0x274C3795dadfEbf562932992bF241ae087e0a98C')
            )]
            tx = random.choice(txs).build_transaction({
                'value': amount,
                'nonce': self.web3.eth.get_transaction_count(self.account_address),
                'from': self.account_address,
                "gasPrice": self.web3.eth.gas_price
            })

        tx_hash = self.sign_transaction(tx)

        if not self.only_collateral:
            self.logger.success(
                f'Successfully deposited {amount / 10 ** 18} ETH | TX: https://blockscout.scroll.io/tx/{tx_hash}'
            )
        else:
            self.logger.success(
                f'Successfully used collateral | TX: https://blockscout.scroll.io/tx/{tx_hash}'
            )
        if USE_DATABASE:
            await self.db_utils.add_to_db(self.account_address, f'https://blockscout.scroll.io/tx/{tx_hash}',
                                          self.__class__.__name__, amount / 10 ** 18)


class LayerBankWithdraw(Account):
    def __init__(self, private_key: str, amount: Union[float, List[float]], withdraw_all: bool, use_percentage: bool,
                 percentage: Union[float, List[float]]) -> None:

        super().__init__(private_key=private_key)

        if isinstance(amount, List):
            self.amount = random.uniform(amount[0], amount[1])
        elif isinstance(amount, float):
            self.amount = amount
        else:
            self.logger.error(f'amount must be float or list[float]. Got {type(amount)}')
            return

        self.withdraw_all = withdraw_all
        self.use_percentage = use_percentage
        if withdraw_all is True and use_percentage is True:
            self.logger.warning(f'You are using withdraw_all and use_percentage both True. Using withdraw_all = True')
        if isinstance(percentage, List):
            self.percentage = random.uniform(percentage[0], percentage[1])
        elif isinstance(percentage, float):
            self.percentage = percentage
        else:
            self.logger.error(f'percentage must be float or list[float]. Got {type(percentage)}')
            return

        self.contract = self.load_contract(
            address=contracts['layerbank'],
            web3=self.web3,
            abi_name=abi_names['layerbank']
        )
        self.db_utils = DataBaseUtils('lending')

    def __repr__(self) -> str:
        return f'{self.__class__.__name__} | [{self.account_address}]'

    async def withdraw(self) -> None:
        balance = self.get_wallet_balance('...', '0x274C3795dadfEbf562932992bF241ae087e0a98C')

        if balance == 0:
            self.logger.warning(f"You don't have any tokens to withdraw | [{self.account_address}]")
            return

        if self.use_percentage:
            amount = int(balance * self.percentage)
        else:
            amount = int(self.amount * 10 ** 18)

        if self.withdraw_all:
            amount = balance

        tx = self.contract.functions.redeemUnderlying(
            self.web3.to_checksum_address('0x274C3795dadfEbf562932992bF241ae087e0a98C'),
            amount
        ).build_transaction({
            'value': 0,
            'nonce': self.web3.eth.get_transaction_count(self.account_address),
            'from': self.account_address,
            "gasPrice": self.web3.eth.gas_price
        })

        tx_hash = self.sign_transaction(tx)

        self.logger.success(
            f'Successfully withdrawn {amount / 10 ** 18} ETH | TX: https://blockscout.scroll.io/tx/{tx_hash}'
        )
        if USE_DATABASE:
            await self.db_utils.add_to_db(self.account_address, f'https://blockscout.scroll.io/tx/{tx_hash}',
                                          self.__class__.__name__, amount / 10 ** 18)
