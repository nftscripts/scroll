from abc import ABC, abstractmethod
from asyncio import sleep
import random

from typing import (
    Union,
    List,
    Any,
)

from web3.contract import Contract
from eth_typing import Address
from web3 import Web3

from src.database.utils import DataBaseUtils
from src.utils.wrappers.decorators import retry
from src.utils.user.account import Account
from src.utils.data.tokens import tokens
from src.utils.data.types import Types

from config import USE_DATABASE


class BaseLiquidity(ABC, Account):
    def __init__(self, private_key: str, token: str, token2: str, amount: Union[float, List[float]],
                 use_percentage: bool, liquidity_percentage: Union[float, List[float]],
                 contract_address: str, abi_name: str, dex_name: str) -> None:

        super().__init__(private_key)

        self.private_key = private_key
        self.token = token

        self.token2 = token2
        if isinstance(token2, list):
            self.token2 = random.choice(token2)

        if isinstance(amount, List):
            self.amount = round(random.uniform(amount[0], amount[1]), 7)
        elif isinstance(amount, float):
            self.amount = amount
        else:
            self.logger.error(f'amount must be float or List[float]. Got {type(amount)}')
            return
        self.use_percentage = use_percentage
        if isinstance(liquidity_percentage, List):
            self.liquidity_percentage = random.uniform(liquidity_percentage[0], liquidity_percentage[1])
        elif isinstance(liquidity_percentage, float):
            self.liquidity_percentage = liquidity_percentage
        else:
            self.logger.error(f'liquidity_percentage must be float or List[float]. Got {type(liquidity_percentage)}')
            return
        self.contract_address = contract_address
        self.abi_name = abi_name
        self.dex_name = dex_name
        self.db_utils = DataBaseUtils('liquidity')

    @retry()
    async def add_liquidity(self) -> None:
        from_token_address, to_token_address = tokens[self.token.upper()], tokens[self.token2.upper()]
        contract = self.load_contract(self.contract_address, self.web3, self.abi_name)
        amount = self.create_amount(self.token, from_token_address, self.web3, self.amount)
        balance = self.get_wallet_balance(self.token, from_token_address)

        if self.use_percentage:
            amount = int(balance * self.liquidity_percentage)

        if amount > balance:
            self.logger.error(f'Not enough balance for wallet | {self.account_address}')
            return

        await self.approve_token(amount, self.private_key, from_token_address, self.contract_address,
                                 self.account_address, self.web3)

        await self.approve_token(amount, self.private_key, to_token_address, self.contract_address,
                                 self.account_address, self.web3)

        amount_out = 0
        if self.dex_name != 'SyncSwapLiquidity':
            while True:
                stable_balance = self.get_wallet_balance(self.token2, to_token_address)
                amount_out = self.get_amount_out(contract, amount, Web3.to_checksum_address(from_token_address),
                                                 Web3.to_checksum_address(to_token_address))
                if amount_out > stable_balance:
                    self.logger.error(f'Not enough {self.token2.upper()} balance for wallet | {self.account_address}')
                    self.logger.info(f'Swapping {amount / 10 ** 18} ETH => {self.token2.upper()}')
                    swap = await self.get_swap_instance(self.private_key, self.token, self.token2, amount / 10 ** 18)
                    await swap.swap()
                    sleep_time = random.randint(45, 75)
                    self.logger.info(f'Sleeping {sleep_time} seconds...')
                    await sleep(sleep_time)
                    continue
                break

        tx = self.create_liquidity_tx(self.token, contract, amount_out, from_token_address, to_token_address,
                                      self.account_address, amount, self.web3)

        tx_hash = self.sign_transaction(tx)

        self.logger.success(
            f'Successfully added liquidity with {amount / 10 ** 18} {self.token}, {amount_out / 10 ** 18} {self.token2.upper()} | TX: https://blockscout.scroll.io/tx/{tx_hash}'
        )
        if USE_DATABASE:
            if self.token.lower() == 'eth':
                value_amount = self.amount
            elif self.token2.lower() == 'eth':
                value_amount = amount_out * 1e-18
            else:
                value_amount = self.get_amount_out(contract, amount, Web3.to_checksum_address(from_token_address),
                                                   Web3.to_checksum_address(
                                                       '0x5300000000000000000000000000000000000004')) * 1e-18

            await self.db_utils.add_to_db(self.account_address, f'https://blockscout.scroll.io/tx/{tx_hash}',
                                          self.dex_name,
                                          value_amount * 2 if self.dex_name != 'SyncSwap' else value_amount,
                                          self.token, self.token2)

    @abstractmethod
    def get_amount_out(self, contract: Contract, amount: int, from_token_address: Address,
                       to_token_address: Address) -> Types.AmountOut:
        """Get the stable amount for liquidity."""

    @abstractmethod
    def create_liquidity_tx(self, from_token: str, contract: Contract, amount_out: int, from_token_address: str,
                            to_token_address: str, account_address: Address, amount: int,
                            web3: Web3) -> Types.LiquidityTransaction:
        """Create a transaction for liquidity."""

    @abstractmethod
    async def get_swap_instance(self, private_key: str, token: str, token2: str, amount: float) -> Any:
        """Get an instance for swap if not enough stable balance for liquidity."""
