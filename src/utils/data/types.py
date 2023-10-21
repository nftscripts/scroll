from typing import Callable

from web3.contract import Contract
from web3.types import TxParams
from eth_typing import Address
from web3 import Web3


class Types:
    AmountOut = Callable[[str, Contract, int, str, Address, int, Web3], TxParams]
    SwapTransaction = Callable[[str, str, Contract, int, str, str, Address, int, Web3], TxParams]
    LiquidityTransaction = Callable[[str, Contract, int, str, Address, int, Web3], TxParams]
    LiquidityRemoveTransaction = Callable[[Web3, Contract, str, int, Address], TxParams]
    MintTransaction = Callable[[Web3, Contract, Address], TxParams]
    BridgeTransaction = Callable[[Contract, int, Web3], TxParams]
