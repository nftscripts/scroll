from src.utils.wrappers.decorators import retry
from src.utils.user.account import Account

from src.utils.data.contracts import (
    contracts,
    abi_names,
)


class RubyScore(Account):
    def __init__(self, private_key: str) -> None:
        super().__init__(private_key)

    def __str__(self) -> str:
        return f'[{self.account_address}] Voting on RubyScore'

    @retry()
    async def vote(self) -> None:
        contract = self.load_contract(contracts['rubyscore'], self.web3, abi_names['rubyscore'])
        tx = contract.functions.vote().build_transaction({
            'value': 0,
            'nonce': self.web3.eth.get_transaction_count(self.account_address),
            'from': self.account_address,
            "gasPrice": self.web3.eth.gas_price
        })

        tx_hash = self.sign_transaction(tx)
        self.wait_until_tx_finished(tx_hash)
