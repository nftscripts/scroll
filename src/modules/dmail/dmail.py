import random
from hashlib import sha256

from web3 import Web3

from src.utils.data.contracts import (
    contracts,
    abi_names,
)
from src.utils.wrappers.decorators import retry
from src.utils.user.account import Account
from src.database.utils import DataBaseUtils
from config import USE_DATABASE


class Dmail(Account):
    def __init__(self, private_key: str) -> None:
        self.contract_address = contracts['dmail']
        self.abi_name = abi_names['dmail']
        super().__init__(private_key=private_key)
        self.db_utils = DataBaseUtils('dmail')

    def __repr__(self) -> str:
        return f'{self.account_address} | Sending mail...'

    @retry()
    async def send_mail(self):
        contract = self.load_contract(self.contract_address, self.web3, self.abi_name)
        email = sha256(str(1e11 * random.random()).encode()).hexdigest()
        theme = sha256(str(1e11 * random.random()).encode()).hexdigest()

        data = contract.encodeABI("send_mail", args=(email, theme))

        tx = {
            'chainId': self.web3.eth.chain_id,
            'from': self.account_address,
            'to': Web3.to_checksum_address(self.contract_address),
            'data': data,
            'nonce': self.web3.eth.get_transaction_count(self.account_address),
            'gasPrice': self.web3.eth.gas_price,
            'gas': 0
        }

        gas_limit = self.web3.eth.estimate_gas(tx)
        tx.update({'gas': gas_limit})

        tx_hash = self.sign_transaction(tx)
        self.wait_until_tx_finished(tx_hash)
        if USE_DATABASE:
            await self.db_utils.add_to_db(self.account_address, tx_hash, 'Dmail')
