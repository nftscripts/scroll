from typing import Union, List

from web3.contract import Contract
from eth_typing import Address
from loguru import logger
from web3 import Web3

from src.modules.bridges.orbiter.utils.transaction_data import create_bridge_tx
from src.utils.data.chains import chain_mapping
from src.utils.base_bridge import BaseBridge
from src.utils.data.types import Types


class OrbiterBridge(BaseBridge):
    def __init__(self, private_key: str, amount: Union[float, List[float]], use_percentage: bool,
                 bridge_percentage: Union[float, List[float]], from_chain: str, to_chain: str) -> None:
        dex_name = 'Orbiter'
        scan = chain_mapping[from_chain.lower()].scan
        rpc = chain_mapping[from_chain.lower()].rpc
        orbiter_codes = {
            "eth": 9001,
            "arb": 9002,
            "op": 9007,
            "era": 9014,
            "base": 9021,
            "scroll": 9019
        }
        code = orbiter_codes[to_chain.lower()]
        if use_percentage is False:
            if isinstance(amount, float):
                if not 0.005 < amount < 5:
                    logger.error(f'Limits error. 0.005 < amount < 5. Got {amount}')
                    return
            elif isinstance(amount, List):
                if not (amount[0] > 0.005 and amount[1] < 5):
                    logger.error(f'Limits error. 0.0035 < amount < 0.2. Got {amount}')
                    return
            else:
                logger.error(f'amount must be List or float. Got {type(amount)}')
                return

        super().__init__(private_key, amount, use_percentage, bridge_percentage, contract_address=None, abi_name=None,
                         dex_name=dex_name, rpc=rpc, scan=scan, from_chain=from_chain, to_chain=to_chain, code=code)

    def __repr__(self) -> str:
        return f'🛸 | {self.__class__.__name__}: {self.account_address} | {self.from_chain} => {self.to_chain}'

    def create_bridge_tx(self, contract: Contract, amount: int, web3: Web3, account_address: Address
                         ) -> Types.BridgeTransaction:
        return create_bridge_tx(amount, web3, account_address)

    def check_eligibility(self, amount: int) -> tuple[bool, Union[float, None], Union[int, None]]:
        min_limit = 0.005
        max_limit = 5

        if min_limit < amount / 10 ** 18 < max_limit:
            return True, None, None
        return True, min_limit, max_limit
