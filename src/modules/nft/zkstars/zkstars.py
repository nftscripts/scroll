from web3.contract import Contract
from web3.types import TxParams

from src.utils.data.contracts import abi_names
from src.utils.base_mint import BaseMint


class ZKStars(BaseMint):
    def __init__(self, private_key: str, contract_address: str) -> None:
        abi_name = abi_names['zkstars']
        nft_name = 'ZKStars'
        super().__init__(private_key, contract_address, abi_name, nft_name)

    def __repr__(self) -> str:
        return f'[{self.account_address}] | {self.__class__.__name__} Mint'

    def create_mint_tx(self, contract: Contract) -> TxParams:
        mint_price = contract.functions.getPrice().call()

        tx = contract.functions.safeMint(
            self.web3.to_checksum_address("0x739815d56A5FFc21950271199D2cf9E23B944F1c")
        ).build_transaction({
            'value': mint_price,
            'nonce': self.web3.eth.get_transaction_count(self.account_address),
            'from': self.account_address,
            "gasPrice": self.web3.eth.gas_price
        })
        return tx
