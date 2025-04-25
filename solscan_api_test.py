import requests
import json
import time

# Replace with your actual Solscan API key
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MzA3MDI4NDk5NjUsImVtYWlsIjoibGF0azNAcHJvdG9ubWFpbC5jaCIsImFjdGlvbiI6InRva2VuLWFwaSIsImFwaVZlcnNpb24iOiJ2MiIsImlhdCI6MTczMDcwMjg0OX0.oF3B2xZFkT495ZfUJ5UYGaUJ08P6LslY5OI9hG3f4aY"
url = "https://pro-api.solscan.io/v2.0/transaction/actions"
headers = {
    "accept": "application/json",
    "token": API_KEY  # Use "token" header as per your format
}

# List of contract addresses to filter out
exclude_addresses = {
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
    "2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo",
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
}

def get_transaction_details(transaction_signature):
    params = {
        "tx": transaction_signature  # Use "tx" as the parameter for transaction hash
    }

    response = requests.get(url, headers=headers, params=params)

    # Check the status code
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Extract token addresses from transfers
        if data.get('success') and 'data' in data:
            transfers = data['data'].get('transfers', [])

            # Use a set to prevent duplicates
            contract_addresses = set(
                transfer['token_address'] for transfer in transfers 
                if 'token_address' in transfer and 
                len(transfer['token_address']) == 44 and 
                transfer['token_address'] not in exclude_addresses  # Exclude specified addresses
            )

            return contract_addresses, data  # Return contract addresses and the full response
        else:
            print("No transfer data found or request was not successful.")
            return set(), None  # Return an empty set and None if no data is found
    elif response.status_code == 403:  # Handle "Too Many Requests" error
        print("Error 403: Too Many Requests. Sleeping for 61 seconds...")
        time.sleep(61)  # Sleep for 61 seconds
        return None  # Return None in case of an error
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return set(), None  # Return an empty set and None in case of an error

def update_contract_addresses(log_filename="transaction_logs.json", response_filename="transaction_responses.json"):
    # Read the existing transaction logs
    with open(log_filename, "r") as file:
        logs = [json.loads(line) for line in file.readlines()]

    # Process logs and update contract addresses
    with open(response_filename, "w") as response_file:  # Open response file
        for index, log_entry in enumerate(logs):
            if log_entry.get("contract_address") is None:  # Check for null contract address
                signature = log_entry.get("signature")
                if signature:
                    while True:  # Loop to retry fetching details only on 403 error
                        print(f"Fetching contract address for transaction: {signature}")
                        contract_addresses, api_response = get_transaction_details(signature)

                        if api_response is not None:  # Check if we received a valid response
                            if contract_addresses:
                                # Update log entry with the first valid contract address found
                                log_entry['contract_address'] = next(iter(contract_addresses))
                                print(f"Updated contract address for transaction {signature}: {log_entry['contract_address']}")

                            # Add Solscan API update status
                            log_entry['solscan_update_status'] = 'yes' if log_entry['contract_address'] else 'no'
                            
                            # Write the original log entry and API response on the same line
                            response_line = json.dumps(log_entry) + " " + json.dumps(api_response) + "\n"
                            response_file.write(response_line)  # Write the line to the response file
                            break  # Exit the loop after a successful request
                        elif api_response is None:  # Handle 403 error case
                            print(f"Retrying transaction {signature} due to error...")

                        # Break the loop if another error occurs (non-403)
                        else:
                            break

    # Write the updated logs back to the original file
    with open(log_filename, "w") as file:
        for log in logs:
            file.write(json.dumps(log) + "\n")

if __name__ == "__main__":
    update_contract_addresses()
