import random

from typing import (
    Awaitable,
    Coroutine,
)

from asyncio import (
    create_task,
    gather,
    sleep,
    run
)

from loguru import logger
from config import *

from src.utils.data.mappings import module_handlers
from src.utils.wrappers.decorators import check_gas

from src.utils.data.helper import (
    private_keys,
    active_module,
)


@check_gas
async def process_task(private_key: str, pattern: str) -> None:
    await module_handlers[pattern](private_key)


async def main() -> None:
    bridge_mappings = {
        'main_bridge': MainBridgeConfig,
        'orbiter_bridge': OrbiterBridgeConfig,
        'owl_bridge': OwlBridgeConfig
    }
    tasks = []

    for private_key in private_keys:
        patterns = active_module.copy()

        if RANDOMIZE:
            random.shuffle(patterns)
        bridge_patterns = ['main_bridge', 'orbiter_bridge', 'owl_bridge']
        deposit_bridges = []
        withdraw_bridges = []
        for bridge_pattern in bridge_patterns:
            if bridge_pattern in patterns and bridge_mappings[bridge_pattern].action.lower() == 'deposit':
                deposit_bridges.append(bridge_pattern)
            elif bridge_pattern in patterns and bridge_mappings[bridge_pattern].action.lower() == 'withdraw':
                withdraw_bridges.append(bridge_pattern)

        if deposit_bridges:
            random_deposit_bridge = random.choice(deposit_bridges)
            patterns.remove(random_deposit_bridge)
            patterns.insert(0, random_deposit_bridge)
            deposit_bridges.remove(random_deposit_bridge)

        for deposit_bridge in deposit_bridges:
            patterns.remove(deposit_bridge)

        if 'okx_withdraw' in patterns:
            patterns.remove('okx_withdraw')
            patterns.insert(0, 'okx_withdraw')
        # if 'swap_all_to_eth' in patterns:
        #     patterns.remove('swap_all_to_eth')
        #     patterns.append('swap_all_to_eth')
        if withdraw_bridges:
            random_withdraw_bridge = random.choice(withdraw_bridges)
            patterns.remove(random_withdraw_bridge)
            patterns.append(random_withdraw_bridge)
            withdraw_bridges.remove(random_withdraw_bridge)

        for withdraw_bridge in withdraw_bridges:
            patterns.remove(withdraw_bridge)

        if 'okx_deposit' in patterns:
            patterns.remove('okx_deposit')
            patterns.append('okx_deposit')

        for pattern in patterns:
            task = create_task(process_task(private_key, pattern))
            tasks.append(task)

            time_to_sleep = random.randint(MIN_PAUSE, MAX_PAUSE)
            logger.info(f'Sleeping {time_to_sleep} seconds...')
            await task
            await sleep(time_to_sleep)

    await gather(*tasks)


def start_event_loop(awaitable: Awaitable[None]) -> None:
    run(awaitable)


if __name__ == '__main__':
    start_event_loop(main())
