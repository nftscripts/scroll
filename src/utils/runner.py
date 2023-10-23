from asyncio import sleep
import random

from loguru import logger

from src.modules.bridges.orbiter.oribter_bridge import OrbiterBridge
from src.modules.bridges.main_bridge.main_bridge import MainBridge
from src.modules.bridges.owlto.owlto_bridge import OwlBridge
from src.modules.swaps.wrapper.eth_wrapper import Wrapper
from src.modules.nft.zerius.zerius import Zerius
from src.utils.user.account import Account
from src.modules.dmail.dmail import Dmail
from config import *

from src.modules.swaps.spacefi.spacefi_swap import (
    SpaceFiLiquidityRemove,
    SpaceFiLiquidity,
    SpaceFiSwap,
)

from src.modules.swaps.sync_swap.sync_swap import (
    SyncSwapLiquidityRemove,
    SyncSwapLiquidity,
    SyncSwapSwap,
)

from src.modules.swaps.skydrome.skydrome_swap import (
    SkyDromeLiquidityRemove,
    SkyDromeLiquidity,
    SkyDromeSwap,
)

from src.modules.swaps.punk_swap.punk_swap import (
    PunkSwapLiquidityRemove,
    PunkSwapLiquidity,
    PunkSwap,
)

from src.modules.okx_withdraw.okx_withdraw import (
    OkxWithdraw,
    OkxDeposit,
)

from okx_data.okx_data import (
    PASSPHRASE,
    SECRET_KEY,
    API_KEY,
)


async def process_okx_withdrawal(private_key: str) -> None:
    receiver_address = Account(private_key).account_address
    amount = OkxWithdrawConfig.amount
    chain = OkxWithdrawConfig.chain

    withdrawal = OkxWithdraw(API_KEY, SECRET_KEY, PASSPHRASE, amount, receiver_address, chain)
    logger.info(withdrawal)
    await withdrawal.withdraw()


async def process_dmail(private_key: str) -> None:
    num_transactions = DmailConfig.num_transactions
    send_mail = Dmail(private_key)
    for _ in range(num_transactions):
        logger.info(send_mail)
        await send_mail.send_mail()


async def process_okx_deposit(private_key: str) -> None:
    with open('okx_data/okx_wallets.txt', 'r', encoding='utf-8-sig') as file:
        okx_wallets = [line.strip() for line in file]
    with open('wallets.txt', 'r', encoding='utf-8-sig') as file:
        private_keys = [line.strip() for line in file]

    if len(private_keys) != len(okx_wallets):
        logger.error(f"Number of wallets doesn't match number of OKX wallets")
        return
    private_key_index = private_keys.index(private_key)
    receiver_address = okx_wallets[private_key_index]

    amount = WithdrawFromWalletsToOKXConfig.amount
    from_chain = WithdrawFromWalletsToOKXConfig.from_chain
    withdraw_all = WithdrawFromWalletsToOKXConfig.withdraw_all
    keep_value = WithdrawFromWalletsToOKXConfig.keep_value

    deposit = OkxDeposit(private_key, from_chain, amount, keep_value, withdraw_all, receiver_address)
    logger.info(deposit)
    await deposit.deposit()


async def process_main_bridge(private_key: str) -> None:
    action = MainBridgeConfig.action
    amount = MainBridgeConfig.amount
    use_percentage = MainBridgeConfig.use_percentage
    bridge_percentage = MainBridgeConfig.bridge_percentage
    claim_eth = MainBridgeConfig.claim_eth
    main_bridge = MainBridge(
        private_key=private_key,
        action=action,
        amount=amount,
        use_percentage=use_percentage,
        bridge_percentage=bridge_percentage,
        claim_eth=claim_eth
    )
    logger.info(main_bridge)
    await main_bridge.bridge()


async def process_owl_bridge(private_key: str) -> None:
    from_chain = OwlBridgeConfig.from_chain
    to_chain = OwlBridgeConfig.to_chain
    amount = OwlBridgeConfig.amount
    use_percentage = OwlBridgeConfig.use_percentage
    bridge_percentage = OwlBridgeConfig.bridge_percentage

    owl_bridge = OwlBridge(
        private_key=private_key,
        amount=amount,
        use_percentage=use_percentage,
        bridge_percentage=bridge_percentage,
        from_chain=from_chain,
        to_chain=to_chain
    )
    logger.info(owl_bridge)
    await owl_bridge.bridge()


async def process_orbiter_bridge(private_key: str) -> None:
    from_chain = OrbiterBridgeConfig.from_chain
    to_chain = OrbiterBridgeConfig.to_chain
    amount = OrbiterBridgeConfig.amount
    use_percentage = OrbiterBridgeConfig.use_percentage
    bridge_percentage = OrbiterBridgeConfig.bridge_percentage

    owl_bridge = OrbiterBridge(
        private_key=private_key,
        amount=amount,
        use_percentage=use_percentage,
        bridge_percentage=bridge_percentage,
        from_chain=from_chain,
        to_chain=to_chain
    )
    logger.info(owl_bridge)
    await owl_bridge.bridge()


async def process_swap_all_to_eth(private_key: str) -> None:
    tokens_list = SwapAllTokensConfig.tokens_list
    to_token = SwapAllTokensConfig.to_token
    random.shuffle(tokens_list)
    amount = 0
    use_percentage = False
    swap_percentage = 0
    swap_all_balance = True
    swap_list = [SkyDromeSwap, PunkSwap, SyncSwapSwap, SpaceFiSwap]
    for token in tokens_list:
        swap_class = random.choice(swap_list)
        swap_all_tokens_swap = swap_class(private_key=private_key,
                                          from_token=token,
                                          to_token=to_token,
                                          amount=amount,
                                          use_percentage=use_percentage,
                                          swap_percentage=swap_percentage,
                                          swap_all_balance=swap_all_balance)
        logger.info(swap_all_tokens_swap)
        await swap_all_tokens_swap.swap()
        random_sleep = random.randint(MIN_PAUSE, MAX_PAUSE)
        logger.info(f'Sleeping {random_sleep} seconds...')
        await sleep(random_sleep)


async def process_random_dex_swap(private_key: str) -> None:
    token = RandomDexSwapConfig.from_token
    to_token = RandomDexSwapConfig.to_token
    amount = RandomDexSwapConfig.amount
    num_swaps = RandomDexSwapConfig.num_swaps
    swap_list = [SyncSwapSwap, PunkSwap, SkyDromeSwap, SpaceFiSwap]
    for _ in range(num_swaps):
        swap_class = random.choice(swap_list)
        random_dex_swap = swap_class(private_key=private_key,
                                     from_token=token,
                                     to_token=to_token,
                                     amount=amount,
                                     use_percentage=False,
                                     swap_percentage=0,
                                     swap_all_balance=False)

        logger.info(random_dex_swap)
        await random_dex_swap.swap()
        random_sleep = random.randint(MIN_PAUSE, MAX_PAUSE)
        logger.info(f'Sleeping {random_sleep} seconds...')
        await sleep(random_sleep)


async def process_skydrome_swap(private_key: str) -> None:
    from_token = SkyDromeSwapConfig.from_token
    to_token = SkyDromeSwapConfig.to_token
    amount = SkyDromeSwapConfig.amount
    use_percentage = SkyDromeSwapConfig.use_percentage
    swap_percentage = SkyDromeSwapConfig.swap_percentage
    swap_all_balance = SkyDromeSwapConfig.swap_all_balance

    swap = SkyDromeSwap(
        private_key=private_key,
        from_token=from_token,
        to_token=to_token,
        amount=amount,
        use_percentage=use_percentage,
        swap_percentage=swap_percentage,
        swap_all_balance=swap_all_balance
    )
    logger.info(swap)
    await swap.swap()


async def process_wrapper(private_key: str) -> None:
    action = WrapperConfig.action
    amount = WrapperConfig.amount
    use_all_balance = WrapperConfig.use_all_balance
    use_percentage = WrapperConfig.use_percentage
    percentage_to_wrap = WrapperConfig.percentage_to_wrap

    wrapper = Wrapper(
        private_key=private_key,
        action=action,
        amount=amount,
        use_all_balance=use_all_balance,
        use_percentage=use_percentage,
        percentage_to_wrap=percentage_to_wrap
    )
    logger.info(wrapper)
    await wrapper.wrap()


async def process_punk_swap(private_key: str) -> None:
    from_token = PunkSwapConfig.from_token
    to_token = PunkSwapConfig.to_token
    amount = PunkSwapConfig.amount
    use_percentage = PunkSwapConfig.use_percentage
    swap_percentage = PunkSwapConfig.swap_percentage
    swap_all_balance = PunkSwapConfig.swap_all_balance

    swap = PunkSwap(
        private_key=private_key,
        from_token=from_token,
        to_token=to_token,
        amount=amount,
        use_percentage=use_percentage,
        swap_percentage=swap_percentage,
        swap_all_balance=swap_all_balance
    )
    logger.info(swap)
    await swap.swap()


async def process_sync_swap_swap(private_key: str) -> None:
    from_token = SyncSwapSwapConfig.from_token
    to_token = SyncSwapSwapConfig.to_token
    amount = SyncSwapSwapConfig.amount
    use_percentage = SyncSwapSwapConfig.use_percentage
    swap_percentage = SyncSwapSwapConfig.swap_percentage
    swap_all_balance = SyncSwapSwapConfig.swap_all_balance

    swap = SyncSwapSwap(
        private_key=private_key,
        from_token=from_token,
        to_token=to_token,
        amount=amount,
        use_percentage=use_percentage,
        swap_percentage=swap_percentage,
        swap_all_balance=swap_all_balance
    )
    logger.info(swap)
    await swap.swap()


async def process_punk_swap_liquidity(private_key: str) -> None:
    token = PunkSwapLiquidityConfig.token
    token2 = PunkSwapLiquidityConfig.token2
    amount = PunkSwapLiquidityConfig.amount
    use_percentage = PunkSwapLiquidityConfig.use_percentage
    liquidity_percentage = PunkSwapLiquidityConfig.liquidity_percentage

    liquidity = PunkSwapLiquidity(
        private_key=private_key,
        token=token,
        token2=token2,
        amount=amount,
        use_percentage=use_percentage,
        liquidity_percentage=liquidity_percentage
    )
    logger.info(liquidity)
    await liquidity.add_liquidity()


async def process_punk_swap_liquidity_remove(private_key: str) -> None:
    from_token_pair = PunkSwapLiquidityRemoveConfig.token2
    removing_percentage = PunkSwapLiquidityRemoveConfig.removing_percentage
    remove_all = PunkSwapLiquidityRemoveConfig.remove_all

    liquidity_remove = PunkSwapLiquidityRemove(
        private_key=private_key,
        from_token_pair=from_token_pair,
        remove_all=remove_all,
        removing_percentage=removing_percentage,
        token=PunkSwapLiquidityRemoveConfig.token
    )
    logger.info(liquidity_remove)
    await liquidity_remove.remove_liquidity()


async def process_sync_swap_liquidity(private_key: str) -> None:
    token = SyncSwapLiquidityConfig.token
    token2 = SyncSwapLiquidityConfig.token2
    amount = SyncSwapLiquidityConfig.amount
    use_percentage = SyncSwapLiquidityConfig.use_percentage
    liquidity_percentage = SyncSwapLiquidityConfig.liquidity_percentage

    liquidity = SyncSwapLiquidity(
        private_key=private_key,
        token=token,
        token2=token2,
        amount=amount,
        use_percentage=use_percentage,
        liquidity_percentage=liquidity_percentage
    )
    logger.info(liquidity)
    await liquidity.add_liquidity()


async def process_sync_swap_liquidity_remove(private_key: str) -> None:
    from_token_pair = SyncSwapLiquidityRemoveConfig.token2
    removing_percentage = SyncSwapLiquidityRemoveConfig.removing_percentage
    remove_all = SyncSwapLiquidityRemoveConfig.remove_all

    liquidity_remove = SyncSwapLiquidityRemove(
        private_key=private_key,
        from_token_pair=from_token_pair,
        remove_all=remove_all,
        removing_percentage=removing_percentage,
        token=SyncSwapLiquidityRemoveConfig.token
    )
    logger.info(liquidity_remove)
    await liquidity_remove.remove_liquidity()


async def process_skydrome_liquidity(private_key: str) -> None:
    token = SkyDromeLiquidityConfig.token
    token2 = SkyDromeLiquidityConfig.token2
    amount = SkyDromeLiquidityConfig.amount
    use_percentage = SkyDromeLiquidityConfig.use_percentage
    liquidity_percentage = SkyDromeLiquidityConfig.liquidity_percentage

    liquidity = SkyDromeLiquidity(
        private_key=private_key,
        token=token,
        token2=token2,
        amount=amount,
        use_percentage=use_percentage,
        liquidity_percentage=liquidity_percentage
    )
    logger.info(liquidity)
    await liquidity.add_liquidity()


async def process_skydrome_liquidity_remove(private_key: str) -> None:
    from_token_pair = SkyDromeLiquidityRemoveConfig.token2
    removing_percentage = SkyDromeLiquidityRemoveConfig.removing_percentage
    remove_all = SkyDromeLiquidityRemoveConfig.remove_all

    liquidity_remove = SkyDromeLiquidityRemove(
        private_key=private_key,
        from_token_pair=from_token_pair,
        remove_all=remove_all,
        removing_percentage=removing_percentage,
        token=SkyDromeLiquidityRemoveConfig.token
    )
    logger.info(liquidity_remove)
    await liquidity_remove.remove_liquidity()


async def process_zerius_mint_bridge(private_key: str) -> None:
    chain_to_bridge = ZeruisConfig.chain_to_bridge

    zerius = Zerius(
        private_key=private_key,
        chain_to_bridge=chain_to_bridge
    )
    logger.info(zerius)
    await zerius.bridge()


async def process_spacefi_swap(private_key: str) -> None:
    from_token = SpaceFiSwapConfig.from_token
    to_token = SpaceFiSwapConfig.to_token
    amount = SpaceFiSwapConfig.amount
    use_percentage = SpaceFiSwapConfig.use_percentage
    swap_percentage = SpaceFiSwapConfig.swap_percentage
    swap_all_balance = SpaceFiSwapConfig.swap_all_balance

    swap = SpaceFiSwap(
        private_key=private_key,
        from_token=from_token,
        to_token=to_token,
        amount=amount,
        use_percentage=use_percentage,
        swap_percentage=swap_percentage,
        swap_all_balance=swap_all_balance
    )
    logger.info(swap)
    await swap.swap()


async def process_spacefi_liquidity(private_key: str) -> None:
    token = SpaceFiLiquidityConfig.token
    token2 = SpaceFiLiquidityConfig.token2
    amount = SpaceFiLiquidityConfig.amount
    use_percentage = SpaceFiLiquidityConfig.use_percentage
    liquidity_percentage = SpaceFiLiquidityConfig.liquidity_percentage

    liquidity = SpaceFiLiquidity(
        private_key=private_key,
        token=token,
        token2=token2,
        amount=amount,
        use_percentage=use_percentage,
        liquidity_percentage=liquidity_percentage
    )
    logger.info(liquidity)
    await liquidity.add_liquidity()


async def process_spacefi_liquidity_remove(private_key: str) -> None:
    from_token_pair = SpaceFiLiquidityRemoveConfig.token2
    removing_percentage = SpaceFiLiquidityRemoveConfig.removing_percentage
    remove_all = SpaceFiLiquidityRemoveConfig.remove_all

    liquidity_remove = SpaceFiLiquidityRemove(
        private_key=private_key,
        from_token_pair=from_token_pair,
        remove_all=remove_all,
        removing_percentage=removing_percentage,
        token=SpaceFiLiquidityRemoveConfig.token
    )
    logger.info(liquidity_remove)
    await liquidity_remove.remove_liquidity()
