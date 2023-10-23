from abc import ABC, abstractmethod
from typing import Union, List
import random

from web3.contract import Contract
from eth_typing import Address
from web3 import Web3

from src.utils.wrappers.decorators import retry
from src.database.utils import DataBaseUtils
from src.utils.user.account import Account
from src.utils.data.tokens import tokens
from src.utils.data.types import Types
from config import USE_DATABASE


class BaseSwap(ABC, Account):
    def __init__(self, private_key: str, from_token: str, to_token: Union[str, List[str]], amount: Union[float, List[float]],
                 use_percentage: bool, swap_percentage: Union[float, List[float]], swap_all_balance: bool,
                 contract_address: str, abi_name: str, dex_name: str) -> None:

        super().__init__(private_key)

        self.private_key = private_key
        self.from_token = from_token
        if isinstance(to_token, List):
            self.to_token = random.choice(to_token)
        elif isinstance(to_token, str):
            self.to_token = to_token
        else:
            self.logger.error(f'to_token must be str or list[str]. Got {type(to_token)}')
            return
        if isinstance(amount, List):
            self.amount = round(random.uniform(amount[0], amount[1]), 7)
        else:
            self.amount = amount
        self.use_percentage = use_percentage
        if isinstance(swap_percentage, List):
            self.swap_percentage = random.uniform(swap_percentage[0], swap_percentage[1])
        else:
            self.swap_percentage = swap_percentage
        self.swap_all_balance = swap_all_balance
        self.contract_address = contract_address
        self.abi_name = abi_name
        self.dex_name = dex_name
        self.db_utils = DataBaseUtils('swap')
        if self.use_percentage and self.swap_all_balance:
            self.logger.warning('You set use_percentage and swap_all_balance both True. Using swap_percentage.')

    @retry()
    async def swap(self) -> None:
        from_token_address, to_token_address = tokens[self.from_token.upper()], tokens[self.to_token.upper()]
        contract = self.load_contract(self.contract_address, self.web3, self.abi_name)
        balance = self.get_wallet_balance(self.from_token, from_token_address)
        amount = self.create_amount(self.from_token, from_token_address, self.web3, self.amount)

        if balance == 0:
            self.logger.error(f'🅾️ | Your balance is 0 | {self.account_address}')
            return

        if self.swap_all_balance is True and self.from_token.lower() == 'eth':
            self.logger.error(
                "You can't use swap_all_balance = True with ETH token. Using amount_from, amount_to")
        if self.swap_all_balance is True and self.from_token.lower() != 'eth':
            amount = balance

        if self.use_percentage is True:
            amount = int(balance * self.swap_percentage)

        if amount > balance:
            self.logger.error(f'📉 | Not enough balance for wallet {self.account_address}')
            return

        amount_out = self.get_amount_out(contract, amount, Web3.to_checksum_address(from_token_address),
                                         Web3.to_checksum_address(to_token_address))

        if self.from_token.lower() != 'eth':
            await self.approve_token(amount, self.private_key, from_token_address, self.contract_address,
                                     self.account_address, self.web3)

        tx = self.create_swap_tx(self.from_token, self.to_token, contract, amount_out, from_token_address,
                                 to_token_address, self.account_address, amount, self.web3)

        tx.update({'gasPrice': self.web3.eth.gas_price})
        gas_limit = self.web3.eth.estimate_gas(tx)
        tx.update({'gas': gas_limit})

        tx_hash = self.sign_transaction(tx)

        self.logger.success(
            f'Successfully swapped {"all" if self.swap_all_balance is True and self.from_token.lower() != "eth" and self.use_percentage is False else f"{int(self.swap_percentage * 100)}%" if self.use_percentage is True else self.amount} {self.from_token} tokens => {self.to_token} | TX: https://blockscout.scroll.io/tx/{tx_hash}'
        )

        if USE_DATABASE:
            if self.from_token.lower() == 'eth':
                value_amount = self.amount
            elif self.to_token.lower() == 'eth':
                value_amount = amount_out * 1e-18
            else:
                value_amount = self.get_amount_out(contract, amount, Web3.to_checksum_address(from_token_address),
                                                   Web3.to_checksum_address(
                                                       '0x5300000000000000000000000000000000000004')) * 1e-18

            await self.db_utils.add_to_db(self.account_address, f'https://blockscout.scroll.io/tx/{tx_hash}',
                                          self.dex_name, value_amount, self.from_token, self.to_token)

    @abstractmethod
    def get_amount_out(self, contract: Contract, amount: int, from_token_address: Address,
                       to_token_address: Address) -> Types.AmountOut:
        """Get the amount after swap."""

    @abstractmethod
    def create_swap_tx(self, from_token: str, to_token: str, contract: Contract, amount_out: int,
                       from_token_address: str, to_token_address: str, account_address: Address, amount: int,
                       web3: Web3) -> Types.SwapTransaction:
        """Create a transaction for swap."""
