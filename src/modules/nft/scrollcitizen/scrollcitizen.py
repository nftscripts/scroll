from web3.contract import Contract
from web3.types import TxParams

from src.utils.data.contracts import abi_names
from src.utils.base_mint import BaseMint


class ScrollCitizen(BaseMint):
    def __init__(self, private_key: str, contract_address: str) -> None:
        abi_name = abi_names['scroll_citizen']
        nft_name = 'ScrollCitizen'
        super().__init__(private_key, contract_address, abi_name, nft_name)

    def __repr__(self) -> str:
        return f'[{self.account_address}] | {self.__class__.__name__} Mint'

    def create_mint_tx(self, contract: Contract) -> TxParams:
        tx = contract.functions.mint(
            self.web3.to_checksum_address("0x08770dA8fE1541D771B77C9C997A0E4a085A6E59")
        ).build_transaction({
            'value': int(0.0001 * 10 ** 18),
            'nonce': self.web3.eth.get_transaction_count(self.account_address),
            'from': self.account_address,
            "gasPrice": self.web3.eth.gas_price
        })
        return tx
