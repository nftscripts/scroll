from web3.types import TxParams
from eth_typing import Address
from web3 import Web3


def create_bridge_tx(amount: int, web3: Web3, account_address: Address) -> TxParams:
    return {
        'chainId': web3.eth.chain_id,
        'from': account_address,
        'to': web3.to_checksum_address('0x5e809a85aa182a9921edd10a4163745bb3e36284'),
        'value': amount,
        'nonce': web3.eth.get_transaction_count(account_address),
        'gas': 0
    }
