from time import time

from web3.contract import Contract
from web3.types import TxParams
from eth_typing import Address
from web3 import Web3

from config import SLIPPAGE


def get_amount_out(contract: Contract, amount: int, from_token_address: Address,
                   to_token_address: Address) -> int:
    amount_out = contract.functions.getAmountsOut(
        amount,
        [from_token_address, to_token_address]
    ).call()
    return amount_out[1]


def create_swap_tx(from_token: str, contract: Contract, amount_out: int, from_token_address: str,
                   to_token_address: str, account_address: Address, amount: int, web3: Web3) -> TxParams:
    if from_token.lower() == 'eth':
        tx = contract.functions.swapExactETHForTokens(
            int(amount_out * (1 - SLIPPAGE)),
            [web3.to_checksum_address(from_token_address), web3.to_checksum_address(to_token_address)],
            account_address,
            int(time() + 1200)
        ).build_transaction({
            'value': amount if from_token.lower() == 'eth' else 0,
            'nonce': web3.eth.get_transaction_count(account_address),
            'from': account_address,
            'gasPrice': web3.eth.gas_price,
        })
    else:
        tx = contract.functions.swapExactTokensForETH(
            amount,
            int(amount_out * (1 - SLIPPAGE)),
            [from_token_address, to_token_address],
            account_address,
            int(time() + 1200)
        ).build_transaction({
            'value': amount if from_token.lower() == 'eth' else 0,
            'nonce': web3.eth.get_transaction_count(account_address),
            'from': account_address,
            'gasPrice': web3.eth.gas_price,
        })
    return tx
