from aiohttp import ClientSession
from asyncio import sleep
from src.modules.bridges.main_bridge.utils.data.proof_data.request_data import headers
from loguru import logger


async def get_proof_data(tx_hash: str) -> tuple[int, int, str, str, str]:
    async with ClientSession(headers=headers) as session:
        json_data = {
            'txs': [
                tx_hash,
            ],
        }
        while True:
            response = await session.post(url='https://mainnet-api-bridge.scroll.io/api/txsbyhashes', json=json_data)
            response_text = await response.json()
            data = response_text['data']['result']
            for information in data:
                amount = int(information['amount'])
                nonce = int(information['claimInfo']['nonce'])
                message = information['claimInfo']['message']
                batch_index = int(information['claimInfo']['batch_index'])
                proof = information['claimInfo']['proof']
            if proof == '0x':
                logger.info(f'Claim transaction is not ready yet..')
                await sleep(150)
                continue
            break

        return amount, nonce, message, batch_index, proof
