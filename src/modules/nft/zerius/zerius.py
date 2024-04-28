from asyncio import sleep
import random

from typing import (
    Union,
    List,
)

from eth_typing import HexStr

from src.database.utils import DataBaseUtils
from src.utils.user.account import Account
from config import USE_DATABASE

from src.modules.nft.zerius.utils.data import (
    get_l0_fee,
    get_nft_id,
)


class Zerius(Account):
    def __init__(self, private_key: str, chain_to_bridge: Union[str, List[str]]) -> None:
        super().__init__(private_key=private_key)

        self.contract = self.load_contract('0xeb22c3e221080ead305cae5f37f0753970d973cd', self.web3, 'zerius')
        self.chain_ids = {
            "arb": 110,
            "op": 111,
            "polygon": 109,
            "bsc": 102,
            "avax": 106,
        }
        if isinstance(chain_to_bridge, List):
            self.chain_to_bridge = random.choice(chain_to_bridge)
        elif isinstance(chain_to_bridge, str):
            self.chain_to_bridge = chain_to_bridge
        else:
            self.logger.error(f'chain_to_bridge must be str or List[str]. Got {type(chain_to_bridge)}')
            return
        self.chain_id = self.chain_ids[self.chain_to_bridge.lower()]
        self.db_utils = DataBaseUtils('mint')

    def __repr__(self) -> None:
        return f'{self.__class__.__name__} | {self.account_address}'

    def mint(self) -> HexStr:
        mint_fee = self.contract.functions.mintFee().call()
        tx = self.contract.functions.mint().build_transaction({
            'from': self.account_address,
            'value': mint_fee,
            'nonce': self.web3.eth.get_transaction_count(self.account_address),
            "gasPrice": self.web3.eth.gas_price
        })

        tx_hash = self.sign_transaction(tx)
        confirmed = self.wait_until_tx_finished(tx_hash)

        if confirmed:
            self.logger.success(
                f'Successfully Minted NFT | TX: https://blockscout.scroll.io/tx/{tx_hash}'
            )
        return tx_hash

    async def bridge(self) -> None:
        mint_hash = self.mint()

        if not mint_hash:
            return

        await sleep(10)
        nft_id = get_nft_id(self.web3, mint_hash)
        random_sleep = random.randint(20, 30)
        self.logger.debug(f'Sleeping {random_sleep} seconds before bridge...')
        await sleep(random_sleep)

        l0_fee = get_l0_fee(self.contract, self.chain_id, nft_id, self.account_address)
        base_bridge_fee = self.contract.functions.bridgeFee().call()

        tx = self.contract.functions.sendFrom(
            self.account_address,
            self.chain_id,
            self.account_address,
            nft_id,
            '0x0000000000000000000000000000000000000000',
            '0x0000000000000000000000000000000000000000',
            '0x0001000000000000000000000000000000000000000000000000000000000003d090'
        ).build_transaction({
            'from': self.account_address,
            'value': l0_fee + base_bridge_fee,
            'nonce': self.web3.eth.get_transaction_count(self.account_address),
            "gasPrice": self.web3.eth.gas_price
        })

        tx_hash = self.sign_transaction(tx)
        confirmed = self.wait_until_tx_finished(tx_hash)

        if confirmed:
            self.logger.success(
                f'Successfully Bridged NFT into {self.chain_to_bridge} | TX: https://blockscout.scroll.io/tx/{tx_hash}'
            )

            if USE_DATABASE:
                await self.db_utils.add_to_db(self.account_address, f'https://blockscout.scroll.io/tx/{tx_hash}', 'Zerius')
