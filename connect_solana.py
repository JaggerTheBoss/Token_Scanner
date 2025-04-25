from solana.rpc.async_api import AsyncClient
import asyncio

async def connect_solana():
    client = AsyncClient("https://api.mainnet-beta.solana.com")
    response = await client.get_version()

    # Directly access attributes from the RpcVersionInfo object
    if response.value:
        solana_version = response.value.solana_core  # Correct attribute access
        print("Connected to the Solana blockchain successfully!")
        print("Solana version:", solana_version)
    else:
        print("Connection issue:", response)

    await client.close()

if __name__ == "__main__":
    asyncio.run(connect_solana())
