import json
import requests
import time

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MzA3MDI4NDk5NjUsImVtYWlsIjoibGF0azNAcHJvdG9ubWFpbC5jaCIsImFjdGlvbiI6InRva2VuLWFwaSIsImFwaVZlcnNpb24iOiJ2MiIsImlhdCI6MTczMDcwMjg0OX0.oF3B2xZFkT495ZfUJ5UYGaUJ08P6LslY5OI9hG3f4aY"  # Replace with your actual Solscan API key

def get_transaction_details(transaction_signature):
    url = "https://pro-api.solscan.io/v2.0/transaction/detail"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    print(f"Requesting details for signature: {transaction_signature}")
    print(f"Headers: {headers}")

    params = {
        "txHash": transaction_signature
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print("401 Authentication failed.")
            return None
        elif response.status_code == 400:
            print(f"400 Bad Request: {response.json().get('errors', {}).get('message')}")
            return None
        elif response.status_code == 403:
            print("403 Too Many Requests. Waiting before retrying...")
            time.sleep(60)  # Wait for a minute before retrying
            return get_transaction_details(transaction_signature)  # Retry the request
        elif response.status_code == 500:
            print("500 Internal Server Error.")
            return None
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

def update_contract_addresses(log_filename="transaction_logs.json"):
    # Read the existing transaction logs
    with open(log_filename, "r") as file:
        logs = [json.loads(line) for line in file.readlines()]

    # Process logs and update contract addresses
    for index, log_entry in enumerate(logs):
        if log_entry.get("contract_address") is None:  # Check for null contract address
            signature = log_entry.get("signature")
            if signature:
                print(f"Fetching contract address for transaction: {signature}")
                transaction_details = get_transaction_details(signature)
                if transaction_details and 'data' in transaction_details:
                    # Extract the contract address from token_1 and token_2
                    token_1 = transaction_details['data'].get('token_bal_change', [{}])[0].get('token_address', None)
                    token_2 = transaction_details['data'].get('token_bal_change', [{}])[1].get('token_address', None)

                    # Determine the valid contract address
                    if token_1 and len(token_1) == 44:
                        log_entry['contract_address'] = token_1
                    elif token_2 and len(token_2) == 44:
                        log_entry['contract_address'] = token_2

                    print(f"Updated contract address for transaction {signature}: {log_entry['contract_address']}")
                else:
                    print(f"No valid details found for transaction: {signature}")

        # Introduce a delay to prevent hitting the API rate limit
        if (index + 1) % 100 == 0:  # After every 100 requests
            print("Sleeping for 60 seconds to manage API rate limit...")
            time.sleep(60)  # Sleep for a minute

    # Write the updated logs back to the file
    with open(log_filename, "w") as file:
        for log in logs:
            file.write(json.dumps(log) + "\n")

if __name__ == "__main__":
    update_contract_addresses()
