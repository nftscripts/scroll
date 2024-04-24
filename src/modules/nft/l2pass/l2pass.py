from web3.contract import Contract

from src.utils.wrappers.decorators import retry
from src.utils.user.account import Account

from src.utils.data.contracts import (
    contracts,
    abi_names,
)


class L2Pass(Account):
    def __init__(self, private_key: str) -> None:
        super().__init__(private_key)

    def __str__(self) -> str:
        return f'[{self.account_address}] | Minting L2Pass NFT'

    @staticmethod
    def get_mint_price(contract: Contract) -> int:
        price = contract.functions.mintPrice().call()

        return price

    @retry()
    async def mint(self) -> None:
        contract = self.load_contract(contracts['l2pass'], self.web3, abi_names['l2pass'])
        price = self.get_mint_price(contract)
        tx = contract.functions.mint(1).build_transaction({
            'value': price,
            'nonce': self.web3.eth.get_transaction_count(self.account_address),
            'from': self.account_address,
            "gasPrice": self.web3.eth.gas_price
        })
        tx_hash = self.sign_transaction(tx)
        self.wait_until_tx_finished(tx_hash)
