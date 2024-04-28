import random

from typing import (
    Union,
    List,
)

from src.database.utils import DataBaseUtils
from src.utils.user.account import Account
from src.utils.wrappers.decorators import retry
from src.utils.data.contracts import contracts, abi_names


class Aave(Account):
    def __init__(self, private_key: str, amount: Union[float, List[float]], use_percentage: bool,
                 deposit_percentage: Union[float, List[float]], remove_percentage: Union[float, List[float]],
                 remove_all: bool) -> None:
        self.private_key = private_key

        super().__init__(private_key)

        if isinstance(amount, List):
            self.amount = random.uniform(amount[0], amount[1])
        elif isinstance(amount, float):
            self.amount = amount
        else:
            self.logger.error(f'amount must be list[float] or float. Got {type(amount)}')
            return
        self.use_percentage = use_percentage

        if isinstance(deposit_percentage, List):
            self.deposit_percentage = random.uniform(deposit_percentage[0], deposit_percentage[1])
        elif isinstance(deposit_percentage, float):
            self.deposit_percentage = deposit_percentage
        else:
            self.logger.error(f'amount must be list[float] or float. Got {type(deposit_percentage)}')
            return

        if isinstance(remove_percentage, List):
            self.remove_percentage = random.uniform(remove_percentage[0], remove_percentage[1])
        elif isinstance(remove_percentage, float):
            self.remove_percentage = remove_percentage
        else:
            self.logger.error(f'amount must be list[float] or float. Got {type(remove_percentage)}')
            return

        self.remove_all = remove_all
        self.db_utils = DataBaseUtils('lending')

    async def get_deposit_amount(self):
        aave_weth_contract = self.load_contract(contracts['aave']['aave_weth'], self.web3, 'erc20')

        amount = aave_weth_contract.functions.balanceOf(self.account_address).call()

        return amount

    @retry()
    async def deposit(self) -> None:
        contract = self.load_contract(contracts['aave']['aave_contract'], self.web3, abi_names['aave'])
        amount = int(self.amount * 10 ** 18)
        balance = self.get_wallet_balance('ETH', '...')
        if self.use_percentage:
            amount = int(balance * self.deposit_percentage)

        if amount > balance:
            self.logger.error(f'Not enough balance for wallet | [{self.account_address}]')
            return

        tx = contract.functions.depositETH(
            self.web3.to_checksum_address("0x11fCfe756c05AD438e312a7fd934381537D3cFfe"),
            self.account_address,
            0
        ).build_transaction({
            'value': amount,
            'nonce': self.web3.eth.get_transaction_count(self.account_address),
            'from': self.account_address,
            "gasPrice": self.web3.eth.gas_price
        })
        self.logger.info(f"[{self.account_address}] deposit on Aave | {amount / 10 ** 18} ETH")

        tx_hash = self.sign_transaction(tx)
        confirmed = self.wait_until_tx_finished(tx_hash)

        if confirmed:
            self.logger.success(
                f'Successfully deposited {amount / 10 ** 18} ETH | TX: https://scrollscan.com/tx/{tx_hash}')

    @retry()
    async def withdraw(self) -> None:
        contract = self.load_contract(contracts['aave']['aave_contract'], self.web3, abi_names['aave'])
        deposited_amount = await self.get_deposit_amount()
        amount = int(self.amount * 10 ** 18)
        if deposited_amount == 0:
            self.logger.error(f'Your deposited amount is 0 | [{self.account_address}]')
            return
        if self.remove_all is True:
            amount = deposited_amount
        if self.use_percentage:
            amount = int(deposited_amount * self.remove_percentage)

        self.logger.info(
            f"[{self.account_address}] withdrawing from Aave | {amount / 10 ** 18} ETH"
        )

        await self.approve_token(
            amount,
            self.private_key,
            "0xf301805be1df81102c957f6d4ce29d2b8c056b2a",
            contracts['aave']['aave_contract'],
            self.account_address,
            self.web3
        )

        tx = contract.functions.withdrawETH(
            self.web3.to_checksum_address("0x11fCfe756c05AD438e312a7fd934381537D3cFfe"),
            amount,
            self.account_address
        ).build_transaction({
            'value': 0,
            'nonce': self.web3.eth.get_transaction_count(self.account_address),
            'from': self.account_address,
            "gasPrice": self.web3.eth.gas_price
        })

        tx_hash = self.sign_transaction(tx)
        confirmed = self.wait_until_tx_finished(tx_hash)

        if confirmed:
            self.logger.success(
                f'Successfully withdrawn {amount / 10 ** 18} ETH | TX: https://scrollscan.com/tx/{tx_hash}')
