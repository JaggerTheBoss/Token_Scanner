import websockets
import asyncio
import json
import re

# Function to save logs to a file
def save_logs_to_file(log_data, filename="transaction_logs.json"):
    print("Saving log to file...")
    with open(filename, "a") as file:
        file.write(json.dumps(log_data) + "\n")

# Function to load contract addresses from a text file
def load_contract_addresses(filename="contract_addresses.txt"):
    with open(filename, "r") as file:
        addresses = [line.strip() for line in file if line.strip()]
    return addresses

# Function to extract potential contract addresses from logs
def extract_contract_addresses(logs):
    addresses = []
    for log in logs:
        address_match = re.findall(r'\b[A-Za-z0-9]{44}pump\b', log)
        addresses.extend(address_match)
    return addresses

async def listen_to_contract_logs(contract_addresses):
    uri = "wss://api.mainnet-beta.solana.com"

    try:
        async with websockets.connect(uri, timeout=30) as websocket:
            for address in contract_addresses:
                subscription_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "logsSubscribe",
                    "params": [
                        {"mentions": [address]},
                        {"commitment": "processed"}
                    ]
                }
                await websocket.send(json.dumps(subscription_request))
                print(f"Listening to transaction logs for contract address: {address}")

            while True:
                try:
                    response = await websocket.recv()
                    parsed_response = json.loads(response)

                    if "params" in parsed_response and "result" in parsed_response["params"]:
                        logs = parsed_response["params"]["result"]["value"]["logs"]
                        signature = parsed_response["params"]["result"]["value"]["signature"]
                        errors = []
                        instructions = []

                        found_addresses = extract_contract_addresses(logs)
                        print(f"Found addresses in logs: {found_addresses}")  # Debugging line

                        contract_address = None
                        for address in found_addresses:
                            if address in contract_addresses:
                                contract_address = address
                                break

                        for log in logs:
                            if "Instruction: Swap" in log or "Instruction: Transfer" in log or "Instruction: TransferChecked" in log:
                                instructions.append(log)
                            if "Error" in log or "failed" in log:
                                errors.append(log)

                        # Create a log entry
                        log_entry = {
                            "signature": signature,
                            "instructions": instructions,
                            "errors": errors,
                            "contract_address": contract_address,
                            "solscan_update_status": 'no',  # Initial status set to 'no'
                            "timestamp": parsed_response["params"]["result"]["context"]["slot"]
                        }

                        # Save the initial log entry
                        save_logs_to_file(log_entry)

                        if instructions:
                            print(f"\nTransaction Signature: {signature}")
                            print(f"Contract Address: {contract_address}")
                            print("Instructions:")
                            for inst in instructions:
                                print(f"  - {inst}")

                        if errors:
                            print("\nError Details:")
                            for err in errors:
                                print(f"  - {err}")

                except websockets.ConnectionClosed:
                    print("WebSocket connection closed, reconnecting...")
                    await asyncio.sleep(1)
                    await listen_to_contract_logs(contract_addresses)

    except asyncio.TimeoutError:
        print("Connection attempt timed out. Retrying...")
        await asyncio.sleep(5)
        await listen_to_contract_logs(contract_addresses)

if __name__ == "__main__":
    contract_addresses = load_contract_addresses("contract_addresses.txt")
    asyncio.run(listen_to_contract_logs(contract_addresses))
