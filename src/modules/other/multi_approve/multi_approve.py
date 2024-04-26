from asyncio import sleep
import random

from src.utils.wrappers.decorators import retry
from src.utils.data.contracts import contracts
from src.utils.user.account import Account
from src.utils.data.tokens import tokens

from config import (
    MIN_PAUSE,
    MAX_PAUSE,
)


class MultiApprove(Account):
    def __init__(self, private_key: str) -> None:
        self.private_key = private_key
        super().__init__(private_key=private_key)

    def __str__(self) -> str:
        return f'MultiApprove | [{self.account_address}]'

    @retry()
    async def approve(self) -> None:
        contract_list = [
            contracts['skydrome'],
            contracts['punkswap'],
            contracts['spacefi'],
            contracts['zebra'],
            contracts['syncswap']
        ]
        token_list = list(tokens)
        random.shuffle(token_list)

        for token in token_list:
            contract_address = random.choice(contract_list)
            if token in ["ETH", "WETH"]:
                continue
            self.logger.info(f'Approving {token}...')
            tx_hash = await self.approve_token(0, self.private_key, tokens[token],
                                               contract_address, self.account_address, self.web3)
            self.logger.info(f'Approve TX: https://scrollscan.com/tx/{tx_hash}')
            random_sleep = random.randint(MIN_PAUSE, MAX_PAUSE)
            self.logger.info(f'Sleeping {random_sleep} seconds...')
            await sleep(random_sleep)
