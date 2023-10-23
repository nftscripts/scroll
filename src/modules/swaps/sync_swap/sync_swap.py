from typing import Union, List

from web3.contract import Contract
from eth_typing import Address
from web3 import Web3

from src.utils.base_liquidity_remove import BaseLiquidityRemove
from src.utils.base_liquidity import BaseLiquidity
from src.utils.base_swap import BaseSwap
from src.utils.data.types import Types

from src.utils.data.contracts import (
    contracts,
    abi_names,
)

from src.modules.swaps.sync_swap.utils.transaction_data import (
    create_liquidity_remove_tx,
    create_liquidity_tx,
    get_amount_out,
    create_swap_tx,
)


class SyncSwapSwap(BaseSwap):
    def __init__(self, private_key: str, from_token: str, to_token: Union[str, List[str]],
                 amount: Union[float, List[float]], use_percentage: bool, swap_percentage: Union[float, List[float]],
                 swap_all_balance: bool) -> None:
        contract_address = contracts['syncswap']
        abi_name = abi_names['syncswap']
        dex_name = self.__class__.__name__

        super().__init__(private_key, from_token, to_token, amount, use_percentage, swap_percentage, swap_all_balance,
                         contract_address, abi_name, dex_name)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}: {self.account_address} | {self.from_token} => {self.to_token}'

    def get_amount_out(self, contract: Contract, amount: int, from_token_address: Address,
                       to_token_address: Address) -> Types.AmountOut:
        return get_amount_out(amount, from_token_address, to_token_address, self.web3, self.account_address)

    def create_swap_tx(self, from_token: str, to_token: str, contract: Contract, amount_out: int,
                       from_token_address: str, to_token_address: str, account_address: Address, amount: int,
                       web3: Web3) -> Types.SwapTransaction:
        return create_swap_tx(from_token, contract, amount_out, from_token_address, to_token_address,
                              account_address, amount, web3)


class SyncSwapLiquidity(BaseLiquidity):
    def __init__(self, private_key: str, token: str, token2: str, amount: Union[float, List[float]],
                 use_percentage: bool, liquidity_percentage: Union[float, List[float]]) -> None:
        contract_address = contracts['syncswap']
        abi_name = abi_names['syncswap']
        dex_name = self.__class__.__name__
        super().__init__(private_key, token, token2, amount, use_percentage, liquidity_percentage,
                         contract_address, abi_name, dex_name)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}: {self.account_address}'

    def get_amount_out(self, contract: Contract, amount: int, from_token_address: Address,
                       to_token_address: Address) -> Types.AmountOut:
        return get_amount_out(contract, amount, from_token_address, to_token_address, self.account_address)

    def create_liquidity_tx(self, from_token: str, contract: Contract, amount_out: int, from_token_address: str,
                            to_token_address: str, account_address: Address, amount: int, web3: Web3
                            ) -> Types.LiquidityTransaction:
        return create_liquidity_tx(from_token, contract, to_token_address, account_address, amount,
                                   web3, from_token_address)

    async def get_swap_instance(self, private_key: str, token: str, token2: str, amount: int) -> SyncSwapSwap:
        return SyncSwapSwap(private_key, token, token2, amount, False, 0, False)


class SyncSwapLiquidityRemove(BaseLiquidityRemove):
    def __init__(self, private_key: str, from_token_pair: Union[str, List[str]], remove_all: bool,
                 removing_percentage: float, token: str = None) -> None:
        contract_address = contracts['syncswap']
        abi_name = abi_names['syncswap']
        pool_name = 'SyncSwap'

        super().__init__(private_key, from_token_pair, remove_all, removing_percentage, contract_address, abi_name,
                         pool_name, token=token)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}: {self.account_address}'

    def create_liquidity_remove_tx(self, web3: Web3, contract: Contract, from_token_pair_address: str,
                                   amount: int, account_address: Address, token: str = None
                                   ) -> Types.LiquidityRemoveTransaction:
        return create_liquidity_remove_tx(web3, contract, from_token_pair_address, amount, account_address, token)
