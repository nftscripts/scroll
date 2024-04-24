from web3.middleware import geth_poa_middleware
from web3.contract import Contract
from web3.types import TxParams
from eth_typing import Address
from eth_abi import encode
from loguru import logger
from web3 import Web3

from src.utils.data.tokens import tokens
from src.utils.user.utils import Utils
from config import SLIPPAGE


def get_amount_out(amount: int, from_token_address: Address, to_token_address: Address, web3: Web3,
                   account_address: Address) -> int:

    pool_address = get_pool(web3, from_token_address, to_token_address)
    utils = Utils()
    pool_contract = utils.load_contract(pool_address, web3, 'classic_pool_syncswap_data')
    amount_out = pool_contract.functions.getAmountOut(
        Web3.to_checksum_address(from_token_address),
        amount,
        account_address
    ).call()

    return amount_out


def get_pool(web3: Web3, from_token_address: str, to_token_address: str) -> str:
    if from_token_address == '0x06eFdBFf2a14a7c8E15944D1F4A48F9F95F663A4' and \
            to_token_address == '0xf55BEC9cafDbE8730f096Aa55dad6D22d44099Df' \
            or from_token_address == '0xf55BEC9cafDbE8730f096Aa55dad6D22d44099Df' and \
            to_token_address == '0x06eFdBFf2a14a7c8E15944D1F4A48F9F95F663A4':
        factory_address = '0x5b9f21d407F35b10CbfDDca17D5D84b129356ea3'
    else:
        factory_address = '0x37BAc764494c8db4e54BDE72f6965beA9fa0AC2d'
    classic_pool_factory = web3.eth.contract(
        address=Web3.to_checksum_address(factory_address),
        abi=Utils.load_abi('classic_pool_factory_address'))
    pool_address = classic_pool_factory.functions.getPool(Web3.to_checksum_address(from_token_address),
                                                          Web3.to_checksum_address(to_token_address)).call()

    return pool_address


def create_swap_tx(from_token: str, contract: Contract, amount_out: int, from_token_address: str,
                   to_token_address: str, account_address: Address, amount: int, web3: Web3) -> TxParams:
    pool_address = get_pool(web3, from_token_address, to_token_address)
    if pool_address == "0x0000000000000000000000000000000000000000":
        logger.error('Pool does not exist')
        return

    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    swap_data = encode(
        ["address", "address", "uint8"],
        [Web3.to_checksum_address(from_token_address), account_address, 1]
    )
    native_eth_address = "0x0000000000000000000000000000000000000000"
    steps = [{
        "pool": pool_address,
        "data": swap_data,
        "callback": native_eth_address,
        "callbackData": '0x'
    }]
    paths = [{
        "steps": steps,
        "tokenIn": Web3.to_checksum_address(
            from_token_address) if from_token.lower() != 'eth' else Web3.to_checksum_address(
            native_eth_address),
        "amountIn": amount,
    }]

    tx = contract.functions.swap(
        paths,
        int(amount_out * (1 - SLIPPAGE)),
        int(web3.eth.get_block('latest').timestamp) + 1200
    ).build_transaction({
        'from': account_address,
        'value': amount if from_token.lower() == 'eth' else 0,
        'nonce': web3.eth.get_transaction_count(account_address),
        'gasPrice': web3.eth.gas_price,
    })
    return tx


def create_liquidity_tx(from_token: str, contract: Contract, to_token_address: str,
                        account_address: Address, amount: int, web3: Web3, from_token_address) -> TxParams:
    pool_address = get_pool(web3, from_token_address, to_token_address)
    if pool_address == "0x0000000000000000000000000000000000000000":
        logger.error('Pool does not exist')
        return

    native_eth_address = "0x0000000000000000000000000000000000000000"

    callback = native_eth_address
    data = encode(
        ["address"],
        [account_address]
    )

    tx = contract.functions.addLiquidity2(
        Web3.to_checksum_address(pool_address),
        [(Web3.to_checksum_address(to_token_address), 0),
         (Web3.to_checksum_address(callback), amount)] if from_token.lower() == 'eth' else [
            (Web3.to_checksum_address(from_token_address), amount)],
        data,
        0,
        callback,
        '0x'
    ).build_transaction({
        'from': account_address,
        'value': amount if from_token.lower() == 'eth' else 0,
        'nonce': web3.eth.get_transaction_count(account_address),
        'gasPrice': web3.eth.gas_price,
    })
    return tx


def create_liquidity_remove_tx(web3: Web3, contract: Contract, from_token_pair_address: str, amount: int,
                               account_address: Address, token: str) -> TxParams:
    from_token_address = tokens[token]
    pool_address = get_pool(web3, '0x37BAc764494c8db4e54BDE72f6965beA9fa0AC2d', from_token_address,
                            from_token_pair_address)

    data = encode(
        ["address", "uint8"],
        [account_address, 1]
    )

    tx = contract.functions.burnLiquidity(
        Web3.to_checksum_address(pool_address),
        amount,
        data,
        [0, 0],
        "0x0000000000000000000000000000000000000000",
        '0x'

    ).build_transaction({
        'from': account_address,
        'nonce': web3.eth.get_transaction_count(account_address),
        'gasPrice': web3.eth.gas_price,
    })
    return tx
