from dataclasses import dataclass

# from web3.middleware import geth_poa_middleware
from web3.types import TxParams
from eth_typing import Address
from hexbytes import HexBytes
from web3 import Web3

from src.utils.data.chains import SCROLL
from src.utils.user.utils import Utils


@dataclass
class Wallet:
    address: Address
    private_key: str


class Account(Utils):
    def __init__(self, private_key: str, rpc: str = SCROLL.rpc) -> None:
        self.web3 = Web3(Web3.HTTPProvider(rpc))
        self.account = self.web3.eth.account.from_key(private_key)
        self.account_address = self.account.address

        self.__wallet = Wallet(self.account_address, private_key)

        super().__init__()

    def get_wallet_balance(self, token: str, stable_address: str) -> float:
        if token.lower() != 'eth':
            contract = self.web3.eth.contract(address=Web3.to_checksum_address(stable_address),
                                              abi=self.load_abi('erc20'))
            balance = contract.functions.balanceOf(self.__wallet.address).call()
        else:
            balance = self.web3.eth.get_balance(self.__wallet.address)

        return balance

    def sign_transaction(self, tx: TxParams) -> HexBytes:
        signed_tx = self.web3.eth.account.sign_transaction(tx, self.__wallet.private_key)
        raw_tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = self.web3.to_hex(raw_tx_hash)
        return tx_hash
