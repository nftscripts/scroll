from asyncio import sleep

from web3.contract import Contract
from web3.types import TxParams
from eth_typing import Address
from loguru import logger
from web3 import Web3

from src.modules.bridges.main_bridge.utils.data.proof_data.txsbyhashes import get_proof_data
from src.utils.data.chains import ETH
from src.utils.user.utils import Utils


def create_bridge_tx(contract: Contract, amount: int, web3: Web3, account_address: Address) -> TxParams:
    if contract.address == web3.to_checksum_address('0xF8B1378579659D8F7EE5f3C929c2f3E332E41Fd6'):
        utils = Utils()
        oracle_contract = utils.load_contract('0x987e300fDfb06093859358522a79098848C33852',
                                              web3,
                                              'oracle')
        fee = oracle_contract.functions.estimateCrossDomainMessageFee(168000).call()

        tx = contract.functions.depositETH(
            amount,
            168000
        ).build_transaction({
            'value': amount + fee,
            'nonce': web3.eth.get_transaction_count(account_address),
            'from': account_address,
            'maxFeePerGas': 0,
            'maxPriorityFeePerGas': 0,
            'gas': 0
        })
    elif contract.address == web3.to_checksum_address('0x4C0926FF5252A435FD19e10ED15e5a249Ba19d79'):
        tx = contract.functions.withdrawETH(
            amount,
            0
        ).build_transaction({
            'value': amount,
            'nonce': web3.eth.get_transaction_count(account_address),
            'from': account_address,
            'gasPrice': 0,
            'gas': 0
        })
    else:
        logger.error(f'Unknown error')
        return
    return tx


async def claim_eth(tx_hash: str, private_key: str) -> None:
    web3 = Web3(Web3.HTTPProvider(ETH.rpc))
    account = web3.eth.account.from_key(private_key)
    account_address = account.address

    contract = web3.eth.contract(Web3.to_checksum_address('0x6774Bcbd5ceCeF1336b5300fb5186a12DDD8b367'),
                                 abi=Utils.load_abi('eth_claim'))

    while True:
        try:
            amount, nonce, message, batch_index, proof = await get_proof_data(tx_hash)
            break
        except Exception as ex:
            logger.error(f'Transaction is not ready yet | {ex}')
            await sleep(120)

    tx = contract.functions.relayMessageWithProof(
        Web3.to_checksum_address('0x6EA73e05AdC79974B931123675ea8F78FfdacDF0'),
        Web3.to_checksum_address('0x7F2b8C31F88B6006c382775eea88297Ec1e3E905'),
        amount,
        nonce,
        message,
        [batch_index, proof]
    ).build_transaction({
        'value': 0,
        'nonce': web3.eth.get_transaction_count(account_address),
        'from': account_address,
        'maxFeePerGas': 0,
        'maxPriorityFeePerGas': 0,
        'gas': 0
    })
    while True:
        try:
            tx.update({'maxFeePerGas': web3.eth.gas_price})
            tx.update({'maxPriorityFeePerGas': web3.eth.gas_price})
            gas_limit = web3.eth.estimate_gas(tx)
            tx.update({'gas': gas_limit})

            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            raw_tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash = web3.to_hex(raw_tx_hash)
            logger.success(f'Successfully claimed {amount / 10 ** 18} ETH | TX: https://etherscan.io/tx/{tx_hash}')
        except Exception as ex:
            if 'not ready' in str(ex):
                logger.error('Claim transaction is not ready yet...')
                await sleep(150)
                continue
            else:
                logger.error(ex)
                break
