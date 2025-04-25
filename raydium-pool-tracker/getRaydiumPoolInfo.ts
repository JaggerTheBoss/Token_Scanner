import { Connection, PublicKey } from '@solana/web3.js';
import { LIQUIDITY_STATE_LAYOUT_V4 } from '@raydium-io/raydium-sdk';

// Create a connection to the Solana cluster
const connection = new Connection('https://api.mainnet-beta.solana.com');

// Function to get pool information for a specified pool address
async function getPoolInfo(poolAddressString) {
    const poolAddress = new PublicKey(poolAddressString); // Convert the pool address string to a PublicKey

    const accountInfo = await connection.getAccountInfo(poolAddress);
    if (accountInfo) {
        const poolData = LIQUIDITY_STATE_LAYOUT_V4.decode(accountInfo.data);

        // Fetch balance from the base vault (SOL reserve)
        const baseVaultAddress = new PublicKey(poolData.baseVault);
        const baseVaultBalance = await connection.getTokenAccountBalance(baseVaultAddress);
        
        // Log information about the pool
        console.log('Base Mint (SOL):', poolData.baseMint.toString());
        console.log('Quote Mint:', poolData.quoteMint.toString());
        console.log('SOL Reserve in Base Vault:', baseVaultBalance.value.amount);
    } else {
        console.log('Pool not found.');
    }
}

// Example usage: Call the function with a specific pool address
const poolAddress = '4AZRPNEfCJ7iw28rJu5aUyeQhYcvdcNm8cswyL51AY9i'; // Replace with your desired pool address
getPoolInfo(poolAddress);
