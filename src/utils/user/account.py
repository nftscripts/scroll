from dataclasses import dataclass
from time import sleep, time

from web3.exceptions import TransactionNotFound
from web3.types import TxParams
from web3 import Web3
from eth_typing import (
    Address,
    HexStr,
)

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

    def sign_transaction(self, tx: TxParams) -> HexStr:
        signed_tx = self.web3.eth.account.sign_transaction(tx, self.__wallet.private_key)
        raw_tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = self.web3.to_hex(raw_tx_hash)
        return tx_hash

    def wait_until_tx_finished(self, tx_hash: HexStr, max_wait_time=180) -> bool:
        start_time = time()
        while True:
            try:
                receipts = self.web3.eth.get_transaction_receipt(tx_hash)
                status = receipts.get("status")
                if status == 1:
                    self.logger.success(f"Transaction confirmed! {tx_hash}")
                    return True
                elif status is None:
                    sleep(0.3)
                else:
                    self.logger.error(f"Transaction failed! {tx_hash}")
                    return False
            except TransactionNotFound:
                if time() - start_time > max_wait_time:
                    print(f'FAILED TX: {hash}')
                    return False
                sleep(1)
