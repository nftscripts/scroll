from typing import Optional

from web3.contract import Contract
from web3.types import TxParams
from eth_typing import Address
from web3 import Web3


def create_bridge_tx(amount: int, web3: Web3, account_address: Address) -> TxParams:
    return {
        'chainId': web3.eth.chain_id,
        'from': account_address,
        'to': web3.to_checksum_address('0x45A318273749d6eb00f5F6cA3bC7cD3De26D642A'),
        'value': amount,
        'nonce': web3.eth.get_transaction_count(account_address),
        'gas': 0
    }
