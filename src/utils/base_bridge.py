from typing import Union, List, Optional
from abc import ABC, abstractmethod
from fractions import Fraction
from asyncio import sleep
import random

from web3.contract import Contract
from eth_typing import Address
from web3 import Web3

from src.modules.bridges.main_bridge.utils.transaction_data import claim_eth
from src.utils.data.chains import chain_mapping
from src.utils.wrappers.decorators import retry
from src.database.utils import DataBaseUtils
from src.utils.user.account import Account
from src.utils.data.types import Types
from config import USE_DATABASE


class BaseBridge(ABC, Account):
    def __init__(self, private_key: str, amount: Union[float, List[float]], use_percentage: bool,
                 bridge_percentage: Union[float, List[float]], contract_address: Optional[str], abi_name: Optional[str],
                 dex_name: str, rpc: Optional[str], scan: str = 'https://etherscan.io/tx',
                 from_chain: Optional[str] = None, to_chain: Optional[str] = None, code: Optional[int] = None,
                 claim_eth: Optional[bool] = None) -> None:

        super().__init__(private_key, rpc)

        self.private_key = private_key

        if isinstance(amount, List):
            self.amount = round(random.uniform(amount[0], amount[1]), 7)
        else:
            self.amount = amount
        if isinstance(bridge_percentage, List):
            self.bridge_percentage = random.uniform(bridge_percentage[0], bridge_percentage[1])
        else:
            self.bridge_percentage = bridge_percentage
        self.use_percentage = use_percentage
        self.contract_address = contract_address
        self.abi_name = abi_name
        self.dex_name = dex_name
        self.scan = scan
        self.from_chain = from_chain
        self.to_chain = to_chain
        self.code = code
        self.claim_eth = claim_eth
        self.db_utils = DataBaseUtils('bridge')

    @retry()
    async def bridge(self) -> None:
        contract = None
        if not self.dex_name == 'Owlto' or not self.dex_name == 'Orbiter':
            contract = self.load_contract(self.contract_address, self.web3, self.abi_name)
        balance = self.get_wallet_balance('ETH', '...')

        if balance == 0:
            self.logger.error(f'🅾️ | Your balance is 0 | {self.account_address}')
            return

        to_chain_account = Account(self.private_key, chain_mapping[self.to_chain.lower()].rpc)
        balance_before_bridge = to_chain_account.get_wallet_balance('ETH', '...')

        if self.use_percentage:
            amount = int(balance * self.bridge_percentage)
            amount = round(amount, 7)
        else:
            amount = self.create_amount('ETH', '...', self.web3, self.amount)

        amount = int(str(amount)[:-7] + '0000000')

        if self.dex_name == 'Owlto' or self.dex_name == 'Orbiter':
            amount = int(str(Fraction(amount))[:-4] + str(self.code))

        if amount > balance:
            self.logger.error(f'📉 | Not enough balance for wallet {self.account_address}')
            return

        eligibility, min_limit, max_limit = self.check_eligibility(amount)
        if eligibility is False:
            self.logger.error(f'Limits error. {min_limit} < amount < {max_limit}. Got {amount / 10 ** 18} ETH')
            return

        tx = self.create_bridge_tx(contract, amount, self.web3, self.account_address)
        if self.dex_name == 'Orbiter' or self.dex_name == 'Owlto':
            gas_limit = self.web3.eth.estimate_gas(tx)
            tx.update({'gas': gas_limit})

        tx_hash = self.sign_transaction(tx)
        self.logger.success(
            f'Successfully bridged {amount / 10 ** 18} ETH tokens | TX: {self.scan}/{tx_hash}'
        )
        if USE_DATABASE:
            await self.db_utils.add_to_db(self.account_address, tx_hash, self.dex_name, amount / 10 ** 18)

        if self.dex_name == 'MainBridge' and self.from_chain == 'SCROLL' and self.claim_eth:
            self.logger.debug('Claiming ETH...')
            await claim_eth(tx_hash, self.private_key)

        await self.wait_for_bridge(to_chain_account, balance_before_bridge)

    async def wait_for_bridge(self, account: Account, balance_before_bridge: int) -> None:
        self.logger.info(f'Waiting for ETH to arrive in {self.to_chain.upper()}...')
        while True:
            try:
                balance = account.get_wallet_balance('ETH', '...')
                if balance > balance_before_bridge:
                    self.logger.success(f'ETH has arrived | [{self.account_address}]')
                    break
                await sleep(20)
            except Exception as ex:
                self.logger.error(f'Something went wrong {ex}')
                await sleep(10)
                continue

    @abstractmethod
    def create_bridge_tx(self, contract: Contract, amount: int, web3: Web3, account_address: Address
                         ) -> Types.BridgeTransaction:
        """Create a transaction for bridge"""

    @abstractmethod
    def check_eligibility(self, amount: int) -> Union[bool, tuple[bool, float, int]]:
        """Check if eligible for bridge"""
