from typing import Union, List
import random

from loguru import logger

from src.modules.swaps.wrapper.transaction_data import create_wrap_tx
from src.utils.wrappers.decorators import retry
from src.database.utils import DataBaseUtils
from src.utils.user.account import Account
from src.utils.data.tokens import tokens
from config import USE_DATABASE


class Wrapper(Account):
    def __init__(self, private_key: str, action: str, amount: Union[float, List[float]], use_all_balance: bool,
                 use_percentage: bool, percentage_to_wrap: Union[float, List[float]]) -> None:

        super().__init__(private_key)

        self.action = action
        if isinstance(amount, List):
            self.amount = round(random.uniform(amount[0], amount[1]), 7)
        elif isinstance(amount, float):
            self.amount = amount
        else:
            logger.error(f'amount must be List[float] of float. Got {type(amount)}')
            return

        self.use_all_balance = use_all_balance
        self.use_percentage = use_percentage

        if isinstance(percentage_to_wrap, List):
            self.percentage_to_wrap = random.uniform(percentage_to_wrap[0], percentage_to_wrap[1])
        elif isinstance(percentage_to_wrap, float):
            self.percentage_to_wrap = percentage_to_wrap
        else:
            logger.error(f'percentage_to_wrap must be List[float] or float. Got {type(percentage_to_wrap)}')
            return

        if self.action.lower() == 'wrap':
            self.token = 'ETH'
            self.to_token = 'WETH'
        else:
            self.token = 'WETH'
            self.to_token = 'ETH'

        self.db_utils = DataBaseUtils('swap')

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}: {self.account_address} | {"ETH => WETH" if self.action.lower() == "wrap" else "WETH => ETH"}'

    @retry()
    async def wrap(self) -> None:
        balance = self.get_wallet_balance('ETH' if self.action.lower() == 'wrap' else 'WETH', tokens['ETH'])

        if balance == 0:
            self.logger.error(f"🅾️ | Your balance is 0 | {self.account_address}")
            return

        amount = int(self.amount * 10 ** 18)

        if self.use_all_balance is True:
            if self.action.lower() == 'unwrap':
                amount = balance
            elif self.action.lower() == 'wrap':
                self.logger.error(f'You can not use use_all_balance = True to wrap ETH. Using amount_from, amount_to.')
        if self.use_percentage:
            amount = int(balance * self.percentage_to_wrap)

        tx = create_wrap_tx(self.account_address, self.token, self.web3, amount)

        tx_hash = self.sign_transaction(tx)

        self.logger.success(
            f'Successfully {"unwrapped" if self.action.lower() == "unwrap" else "wrapped"} {amount / 10 ** 18} {"WETH => ETH" if self.action.lower() == "unwrap" else "ETH => WETH"} | TX: https://blockscout.scroll.io/tx/{tx_hash}'
        )
        if USE_DATABASE:
            await self.db_utils.add_to_db(self.account_address, tx_hash, 'Wrapping', amount * 1e-18, self.token,
                                          self.to_token)
