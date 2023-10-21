from web3.types import TxParams
from eth_typing import Address
from web3 import Web3

from src.utils.data.tokens import tokens
from src.utils.user.utils import Utils


def create_wrap_tx(account_address: Address, from_token: str, web3: Web3, amount: int) -> TxParams:
    contract = web3.eth.contract(address=tokens['ETH'], abi=Utils.load_abi('eth'))

    if from_token.lower() == 'eth':
        tx = contract.functions.deposit().build_transaction({
            'value': amount,
            'nonce': web3.eth.get_transaction_count(account_address),
            'from': account_address,
            'gasPrice': 0,
            'gas': 0
        })
    else:
        tx = contract.functions.withdraw(amount).build_transaction({
            'value': 0,
            'nonce': web3.eth.get_transaction_count(account_address),
            'from': account_address,
            'gasPrice': 0,
            'gas': 0
        })

    return tx
