from typing import Union, List

from web3.contract import Contract
from eth_typing import Address
from loguru import logger
from web3 import Web3

from src.modules.bridges.owlto.utils.transaction_data import create_bridge_tx
from src.utils.data.chains import chain_mapping
from src.utils.base_bridge import BaseBridge
from src.utils.data.types import Types


class OwlBridge(BaseBridge):
    def __init__(self, private_key: str, amount: Union[float, List[float]], use_percentage: bool,
                 bridge_percentage: Union[float, List[float]], from_chain: str, to_chain: str) -> None:
        dex_name = 'Owlto'
        scan = chain_mapping[from_chain.lower()].scan
        rpc = chain_mapping[from_chain.lower()].rpc
        owlto_codes = {
            'scroll': '0006',
            'era': '0002',
            'base': '0012',
            'linea': '0007',
            'arb': '0004',
            'op': '0003',
            'eth': '0001'
        }
        code = owlto_codes[to_chain.lower()]
        if use_percentage is False:
            if isinstance(amount, float):
                if not 0.0035 < amount < 0.2:
                    logger.error(f'Limits error. 0.0035 < amount < 0.2. Got {amount}')
                    return
            elif isinstance(amount, List):
                if not (amount[0] > 0.0035 and amount[1] < 0.2):
                    logger.error(f'Limits error. 0.0035 < amount < 0.2. Got {amount}')
                    return
            else:
                logger.error(f'amount must be List or float. Got {type(amount)}')
                return

        super().__init__(private_key, amount, use_percentage, bridge_percentage, contract_address=None, abi_name=None,
                         dex_name=dex_name, rpc=rpc, scan=scan, from_chain=from_chain, to_chain=to_chain, code=code)

    def __repr__(self) -> str:
        return f'🦉 | {self.__class__.__name__}: {self.account_address} | {self.from_chain} => {self.to_chain}'

    def create_bridge_tx(self, contract: Contract, amount: int, web3: Web3, account_address: Address
                         ) -> Types.BridgeTransaction:
        return create_bridge_tx(amount, web3, account_address)

    def check_eligibility(self, amount: int) -> tuple[bool, Union[float, None], Union[float, None]]:
        min_limit = 0.0035
        max_limit = 0.2

        if min_limit < amount / 10 ** 18 < max_limit:
            return True, None, None
        return False, min_limit, max_limit
