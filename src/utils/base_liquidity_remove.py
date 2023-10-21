import random
from abc import ABC, abstractmethod
from typing import Union, List

from web3.contract import Contract
from eth_typing import Address
from loguru import logger
from web3 import Web3

from src.utils.data.types import Types
from src.utils.user.account import Account
from src.utils.wrappers.decorators import retry

from src.utils.data.tokens import (
    liquidity_tokens,
    tokens,
)


class BaseLiquidityRemove(ABC, Account):
    def __init__(self, private_key: str, from_token_pair: Union[str, List[str]], remove_all: bool,
                 removing_percentage: float, contract_address: str, abi_name: str, pool_name: str,
                 token: str = None) -> None:

        super().__init__(private_key)

        self.private_key = private_key

        if isinstance(from_token_pair, List):
            self.from_token_pair = random.choice(from_token_pair)
        elif isinstance(from_token_pair, str):
            self.from_token_pair = from_token_pair
        else:
            self.logger.error(f'from_token_pair must be str or list[str]. Got {type(from_token_pair)}')

        self.remove_all = remove_all
        self.removing_percentage = removing_percentage
        self.contract_address = contract_address
        self.abi_name = abi_name
        self.pool_name = pool_name
        self.token = token

    @retry()
    async def remove_liquidity(self) -> None:
        contract = self.load_contract(self.contract_address, self.web3, self.abi_name)
        liquidity_token_address = liquidity_tokens[self.pool_name]['ETH' if self.token is None else self.token.upper()][
            self.from_token_pair.upper()]
        balance = self.get_wallet_balance('...', liquidity_token_address)

        if balance == 0:
            logger.debug("You don't have any tokens to withdraw")
            return

        amount = self.create_liquidity_remove_amount(balance, self.remove_all, self.removing_percentage)

        await self.approve_token(amount, self.private_key, liquidity_token_address, self.contract_address,
                                 self.account_address, self.web3)

        tx = self.create_liquidity_remove_tx(self.web3, contract, tokens[self.from_token_pair.upper()],
                                             amount, self.account_address, token=self.token)

        tx.update({'gasPrice': self.web3.eth.gas_price})
        gas_limit = self.web3.eth.estimate_gas(tx)
        tx.update({'gas': gas_limit})

        tx_hash = self.sign_transaction(tx)

        logger.success(
            f'Removed {"all" if self.remove_all else f"{int(self.removing_percentage * 100)}%"} {self.from_token_pair} tokens from {self.pool_name} pool | TX: https://blockscout.scroll.io/tx/{tx_hash}'
        )

    @abstractmethod
    def create_liquidity_remove_tx(self, web3: Web3, contract: Contract, from_token_pair_address: str,
                                   amount: int, account_address: Address, token: str = None
                                   ) -> Types.LiquidityRemoveTransaction:
        """Create a transaction for liquidity removal."""
