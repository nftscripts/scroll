from abc import (
    abstractmethod,
    ABC,
)

from web3.contract import Contract

from src.utils.wrappers.decorators import retry
from src.database.utils import DataBaseUtils
from src.utils.user.account import Account
from src.utils.data.types import Types
from config import USE_DATABASE


class BaseMint(ABC, Account):
    def __init__(self, private_key: str, contract_address: str, abi_name: str, nft_name: str,
                 amount: float = None) -> None:
        super().__init__(private_key)
        self.db_utils = DataBaseUtils('mint')
        self.contract_address = contract_address
        self.abi_name = abi_name
        self.nft_name = nft_name
        self.amount = amount

    @retry()
    async def mint(self) -> None:
        contract = self.load_contract(self.contract_address, self.web3, self.abi_name)
        balance = self.get_wallet_balance('ETH', '...')

        if balance == 0:
            self.logger.error(f'🅾️ | Your balance is 0 | {self.account_address}')
            return

        tx = self.create_mint_tx(contract)
        if tx is None:
            return

        tx_hash = self.sign_transaction(tx)
        confirmed = self.wait_until_tx_finished(tx_hash)

        if confirmed:
            self.logger.success(
                f'Successfully minted NFT | TX: https://scrollscan.com/tx/{tx_hash}'
            )
            if USE_DATABASE:
                await self.db_utils.add_to_db(self.account_address, f'https://scrollscan.com/tx/{tx_hash}',
                                              self.nft_name, self.amount)

    @abstractmethod
    def create_mint_tx(self, contract: Contract) -> Types.MintTransaction:
        """Create a transaction for mint."""
