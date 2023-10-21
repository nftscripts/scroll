from web3.contract import Contract
from eth_typing import Address
from web3 import Web3


def get_l0_fee(contract: Contract, chain_id: str, nft_id: int, account_address: Address) -> int:
    fee = contract.functions.estimateSendFee(
        chain_id,
        account_address,
        nft_id,
        False,
        "0x"
    ).call()

    return int(fee[0] * 1.2)


def get_nft_id(web3: Web3, tx_hash: str) -> int:
    receipts = web3.eth.get_transaction_receipt(tx_hash)

    nft_id = int(receipts["logs"][0]["topics"][-1].hex(), 0)

    return nft_id
