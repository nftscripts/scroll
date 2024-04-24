import random
import time

from src.utils.wrappers.decorators import retry
from src.utils.user.account import Account

from src.utils.data.contracts import (
    contracts,
    abi_names,
)


class Omnisea(Account):
    def __init__(self, private_key: str) -> None:
        super().__init__(private_key)

    def __str__(self) -> str:
        return f'[{self.account_address}] | Creating NFT on Omnisea'

    @staticmethod
    def generate_collection_data() -> tuple[str, str]:
        title = "".join(random.sample([chr(i) for i in range(97, 123)], random.randint(5, 15)))
        symbol = "".join(random.sample([chr(i) for i in range(65, 91)], random.randint(3, 6)))
        return title, symbol

    @retry()
    async def create(self) -> None:
        contract = self.load_contract(contracts['omnisea'], self.web3, abi_names['omnisea'])
        title, symbol = self.generate_collection_data()

        tx = contract.functions.create([
            title,
            symbol,
            "",
            "",
            0,
            True,
            0,
            int(time.time()) + 1000000]
        ).build_transaction({
            'value': 0,
            'nonce': self.web3.eth.get_transaction_count(self.account_address),
            'from': self.account_address,
            "gasPrice": self.web3.eth.gas_price
        })

        tx_hash = self.sign_transaction(tx)
        self.wait_until_tx_finished(tx_hash)
