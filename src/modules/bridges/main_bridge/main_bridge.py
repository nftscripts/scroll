from typing import Union, List

from web3.contract import Contract
from eth_typing import Address
from web3 import Web3

from src.modules.bridges.main_bridge.utils.transaction_data import create_bridge_tx
from src.utils.data.chains import chain_mapping
from src.utils.data.chains import ETH, SCROLL
from src.utils.base_bridge import BaseBridge
from src.utils.data.types import Types


class MainBridge(BaseBridge):
    def __init__(self, private_key: str, action: str, amount: Union[float, List[float]], use_percentage: bool,
                 bridge_percentage: Union[float, List[float]], claim_eth: bool) -> None:

        dex_name = 'MainBridge'
        if action.lower() == 'deposit':
            rpc = ETH.rpc
            contract_address = '0x6774bcbd5cecef1336b5300fb5186a12ddd8b367'
            abi_name = 'main_bridge'
            scan = chain_mapping['eth'].scan
            from_chain = 'ETH'
            to_chain = 'SCROLL'
        elif action.lower() == 'withdraw':
            rpc = SCROLL.rpc
            contract_address = '0x4C0926FF5252A435FD19e10ED15e5a249Ba19d79'
            abi_name = 'main_bridge_scroll'
            scan = chain_mapping['scroll'].scan
            from_chain = 'SCROLL'
            to_chain = 'ETH'
        else:
            raise ValueError(f'Action must be deposit/withdraw only. Got {action}.')
        super().__init__(private_key, amount, use_percentage, bridge_percentage, contract_address, abi_name, dex_name,
                         rpc, scan, from_chain, to_chain, claim_eth=claim_eth)

    def __repr__(self) -> str:
        return f'Ⓜ️ | {self.__class__.__name__}: {self.account_address}'

    def create_bridge_tx(self, contract: Contract, amount: int, web3: Web3, account_address: Address
                         ) -> Types.BridgeTransaction:
        return create_bridge_tx(contract, amount, web3, account_address)

    def check_eligibility(self, amount: int) -> tuple[bool, None, None]:
        return True, None, None
