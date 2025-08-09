import os
import time
import json
import requests
import threading
from typing import Dict, Any, List, Optional, Tuple
from wallet_core import AleoWalletCore
from transaction_manager import TransactionManager
from aleo_api import AleoBlockchainAPI, AleoWalletAPI

class BlockchainIntegration:
    """
    Integrates the Aleo wallet with the blockchain network.
    Handles synchronization, network status monitoring, and blockchain interactions.
    """
    
    def __init__(self, wallet_core: AleoWalletCore, blockchain_api: AleoBlockchainAPI = None):
        """
        Initialize the Blockchain Integration.
        
        Args:
            wallet_core: The wallet core instance
            blockchain_api: Optional blockchain API instance
        """
        self.wallet_core = wallet_core
        self.blockchain_api = blockchain_api or AleoBlockchainAPI()
        self.wallet_api = AleoWalletAPI(self.blockchain_api)
        self.transaction_manager = TransactionManager(wallet_core, blockchain_api)
        
        # Network status
        self.is_connected = False
        self.last_sync_time = 0
        self.sync_interval = 60  # seconds
        self.sync_in_progress = False
        
        # Blockchain info
        self.latest_block_height = 0
        self.latest_block_hash = ""
        self.network_peers = 0
        
        # Callbacks
        self.on_sync_complete_callbacks = []
        self.on_new_transaction_callbacks = []
        self.on_network_status_change_callbacks = []
        
    def start_sync_thread(self) -> None:
        """Start a background thread for periodic synchronization."""
        def sync_thread():
            while True:
                try:
                    # Check if it's time to sync
                    current_time = time.time()
                    if current_time - self.last_sync_time >= self.sync_interval:
                        self.sync_with_blockchain()
                        
                    # Check network status
                    self.check_network_status()
                    
                    # Sleep for a short time
                    time.sleep(5)
                except Exception as e:
                    print(f"Error in sync thread: {e}")
                    time.sleep(30)  # Wait longer after an error
        
        # Start the thread
        thread = threading.Thread(target=sync_thread, daemon=True)
        thread.start()
        
    def check_network_status(self) -> bool:
        """
        Check the network status.
        
        Returns:
            True if connected, False otherwise
        """
        try:
            # Get the latest block height
            height = self.blockchain_api.get_latest_height()
            
            # If we get here, we're connected
            was_connected = self.is_connected
            self.is_connected = True
            
            # If the connection status changed, notify callbacks
            if not was_connected:
                self._notify_network_status_change(True)
                
            return True
        except Exception as e:
            print(f"Network status check failed: {e}")
            
            # If we were connected before, notify callbacks
            if self.is_connected:
                self.is_connected = False
                self._notify_network_status_change(False)
                
            return False
            
    def sync_with_blockchain(self) -> bool:
        """
        Synchronize the wallet with the blockchain.
        
        Returns:
            True if successful, False otherwise
        """
        if self.sync_in_progress:
            return False
            
        self.sync_in_progress = True
        
        try:
            # Update blockchain info
            self._update_blockchain_info()
            
            # Sync each account
            for i in range(len(self.wallet_core.accounts)):
                self._sync_account(i)
                
            # Update the last sync time
            self.last_sync_time = time.time()
            
            # Notify callbacks
            self._notify_sync_complete()
            
            self.sync_in_progress = False
            return True
        except Exception as e:
            print(f"Error syncing with blockchain: {e}")
            self.sync_in_progress = False
            return False
            
    def _update_blockchain_info(self) -> None:
        """Update blockchain information."""
        try:
            # Get the latest block height
            self.latest_block_height = self.blockchain_api.get_latest_height()
            
            # Get the latest block hash
            self.latest_block_hash = self.blockchain_api.get_latest_hash()
            
            # Get chain status
            chain_status = self.blockchain_api.get_chain_status()
            if isinstance(chain_status, dict):
                self.network_peers = chain_status.get("peers", 0)
        except Exception as e:
            print(f"Error updating blockchain info: {e}")
            
    def _sync_account(self, account_index: int) -> None:
        """
        Synchronize an account with the blockchain.
        
        Args:
            account_index: Index of the account to sync
        """
        account = self.wallet_core.get_account(account_index)
        if not account:
            return
            
        # Get the account address
        address = account["address"]
        
        # Get the latest block height
        latest_height = self.latest_block_height
        
        # Determine the start height for transaction search
        # In a real implementation, we would store the last synced height for each account
        # For now, we'll just look back 1000 blocks
        start_height = max(0, latest_height - 1000)
        
        try:
            # Get public transactions for the address
            tx_ids = self.blockchain_api.get_public_transactions_for_address(
                address, start_height, latest_height
            )
            
            # Process each transaction
            for tx_id in tx_ids:
                # Check if we already have this transaction
                existing_tx = self.transaction_manager.get_transaction(account_index, tx_id)
                if existing_tx:
                    continue
                    
                # Get the transaction details
                tx_details = self.blockchain_api.get_transaction(tx_id)
                
                # Process the transaction
                self._process_transaction(account_index, tx_details)
                
            # Update the account balance
            self._update_account_balance(account_index)
            
        except Exception as e:
            print(f"Error syncing account {address}: {e}")
            
    def _process_transaction(self, account_index: int, tx_details: Dict[str, Any]) -> None:
        """
        Process a transaction and add it to the account history if relevant.
        
        Args:
            account_index: Index of the account
            tx_details: Transaction details from the blockchain
        """
        if not tx_details:
            return
            
        account = self.wallet_core.get_account(account_index)
        if not account:
            return
            
        # Extract transaction information
        tx_id = tx_details.get("id", "")
        sender = tx_details.get("sender", "")
        recipient = tx_details.get("recipient", "")
        amount = float(tx_details.get("amount", 0))
        fee = float(tx_details.get("fee", 0))
        timestamp = tx_details.get("timestamp", int(time.time()))
        block_height = tx_details.get("block_height", 0)
        
        # Determine if this is a sent or received transaction
        tx_type = None
        if sender == account["address"]:
            tx_type = "Sent"
        elif recipient == account["address"]:
            tx_type = "Received"
        else:
            # Transaction not directly related to this account
            return
            
        # Create a transaction object
        transaction = {
            "type": tx_type,
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
            "fee": fee,
            "memo": tx_details.get("memo", ""),
            "timestamp": timestamp,
            "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)),
            "status": "Confirmed",
            "transaction_id": tx_id,
            "block_height": block_height
        }
        
        # Add the transaction to the account's history
        self.wallet_core.add_transaction(account_index, transaction)
        
        # Notify callbacks
        self._notify_new_transaction(account_index, transaction)
        
    def _update_account_balance(self, account_index: int) -> None:
        """
        Update an account's balance based on its transactions.
        
        Args:
            account_index: Index of the account
        """
        account = self.wallet_core.get_account(account_index)
        if not account:
            return
            
        # In a real implementation, we would query the blockchain for the account balance
        # For now, we'll calculate it based on the transactions
        
        # Get all transactions
        transactions = self.wallet_core.get_transactions(account_index)
        
        # Calculate the balance
        balance = 0.0
        for tx in transactions:
            if tx["type"] == "Received":
                balance += tx["amount"]
            elif tx["type"] == "Sent":
                balance -= (tx["amount"] + tx["fee"])
                
        # Update the account balance
        self.wallet_core.accounts[account_index]["balance"] = balance
        self.wallet_core.save_wallet()
        
    def send_transaction(self, account_index: int, recipient_address: str, amount: float, memo: str = "") -> str:
        """
        Send a transaction to the blockchain.
        
        Args:
            account_index: Index of the sender account
            recipient_address: Recipient's address
            amount: Amount to send
            memo: Optional memo/message
            
        Returns:
            Transaction ID
        """
        # Use the transaction manager to send the transaction
        return self.transaction_manager.send_transaction(account_index, recipient_address, amount, memo)
        
    def get_transaction_status(self, tx_id: str) -> Dict[str, Any]:
        """
        Get the status of a transaction from the blockchain.
        
        Args:
            tx_id: Transaction ID
            
        Returns:
            Transaction status information
        """
        try:
            # Get the transaction details
            tx_details = self.blockchain_api.get_transaction(tx_id)
            
            if not tx_details:
                return {"status": "Unknown", "confirmations": 0}
                
            # Extract status information
            block_height = tx_details.get("block_height", 0)
            
            # Calculate confirmations
            confirmations = 0
            if block_height > 0:
                confirmations = max(0, self.latest_block_height - block_height + 1)
                
            return {
                "status": "Confirmed" if confirmations > 0 else "Pending",
                "confirmations": confirmations,
                "block_height": block_height,
                "timestamp": tx_details.get("timestamp", 0)
            }
        except Exception as e:
            print(f"Error getting transaction status: {e}")
            return {"status": "Error", "error": str(e)}
            
    def get_network_status(self) -> Dict[str, Any]:
        """
        Get the current network status.
        
        Returns:
            Network status information
        """
        return {
            "connected": self.is_connected,
            "latest_block_height": self.latest_block_height,
            "latest_block_hash": self.latest_block_hash,
            "peers": self.network_peers,
            "last_sync_time": self.last_sync_time
        }
        
    def register_on_sync_complete(self, callback) -> None:
        """
        Register a callback to be called when synchronization completes.
        
        Args:
            callback: Function to call
        """
        if callback not in self.on_sync_complete_callbacks:
            self.on_sync_complete_callbacks.append(callback)
            
    def register_on_new_transaction(self, callback) -> None:
        """
        Register a callback to be called when a new transaction is detected.
        
        Args:
            callback: Function to call with (account_index, transaction)
        """
        if callback not in self.on_new_transaction_callbacks:
            self.on_new_transaction_callbacks.append(callback)
            
    def register_on_network_status_change(self, callback) -> None:
        """
        Register a callback to be called when the network status changes.
        
        Args:
            callback: Function to call with (is_connected)
        """
        if callback not in self.on_network_status_change_callbacks:
            self.on_network_status_change_callbacks.append(callback)
            
    def _notify_sync_complete(self) -> None:
        """Notify all registered sync complete callbacks."""
        for callback in self.on_sync_complete_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Error in sync complete callback: {e}")
                
    def _notify_new_transaction(self, account_index: int, transaction: Dict[str, Any]) -> None:
        """
        Notify all registered new transaction callbacks.
        
        Args:
            account_index: Index of the account
            transaction: Transaction details
        """
        for callback in self.on_new_transaction_callbacks:
            try:
                callback(account_index, transaction)
            except Exception as e:
                print(f"Error in new transaction callback: {e}")
                
    def _notify_network_status_change(self, is_connected: bool) -> None:
        """
        Notify all registered network status change callbacks.
        
        Args:
            is_connected: Whether the network is connected
        """
        for callback in self.on_network_status_change_callbacks:
            try:
                callback(is_connected)
            except Exception as e:
                print(f"Error in network status change callback: {e}")


class PriceTracker:
    """
    Tracks the price of Aleo and other cryptocurrencies.
    """
    
    def __init__(self):
        """Initialize the Price Tracker."""
        self.prices = {}
        self.price_history = {}
        self.last_update_time = 0
        self.update_interval = 60  # seconds
        
        # Callbacks
        self.on_price_update_callbacks = []
        
    def start_price_tracking(self) -> None:
        """Start a background thread for price tracking."""
        def track_prices():
            while True:
                try:
                    # Check if it's time to update
                    current_time = time.time()
                    if current_time - self.last_update_time >= self.update_interval:
                        self.update_prices()
                        
                    # Sleep for a short time
                    time.sleep(5)
                except Exception as e:
                    print(f"Error in price tracking thread: {e}")
                    time.sleep(30)  # Wait longer after an error
        
        # Start the thread
        thread = threading.Thread(target=track_prices, daemon=True)
        thread.start()
        
    def update_prices(self) -> bool:
        """
        Update cryptocurrency prices.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # In a real implementation, we would use a price API
            # For now, we'll simulate it with placeholder values
            
            # Simulate price changes
            import random
            
            # Get the current Aleo price or start with a default
            current_price = self.prices.get("aleo", 0.25)
            
            # Simulate a price change
            price_change = random.uniform(-0.01, 0.01)
            new_price = max(0.01, current_price + price_change)
            
            # Update the price
            self.prices["aleo"] = new_price
            
            # Update the price history
            if "aleo" not in self.price_history:
                self.price_history["aleo"] = []
                
            # Add the price to the history
            self.price_history["aleo"].append({
                "timestamp": int(time.time()),
                "price": new_price
            })
            
            # Keep only the last 24 hours of history (assuming 1 update per minute)
            if len(self.price_history["aleo"]) > 1440:  # 24 hours * 60 minutes
                self.price_history["aleo"] = self.price_history["aleo"][-1440:]
                
            # Update the last update time
            self.last_update_time = time.time()
            
            # Notify callbacks
            self._notify_price_update("aleo", new_price)
            
            return True
        except Exception as e:
            print(f"Error updating prices: {e}")
            return False
            
    def get_price(self, symbol: str = "aleo") -> float:
        """
        Get the current price of a cryptocurrency.
        
        Args:
            symbol: Symbol of the cryptocurrency
            
        Returns:
            Current price
        """
        return self.prices.get(symbol.lower(), 0.0)
        
    def get_price_history(self, symbol: str = "aleo", hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get the price history of a cryptocurrency.
        
        Args:
            symbol: Symbol of the cryptocurrency
            hours: Number of hours of history to return
            
        Returns:
            List of price history points
        """
        history = self.price_history.get(symbol.lower(), [])
        
        # Filter by time
        if hours > 0:
            cutoff_time = int(time.time()) - (hours * 3600)
            history = [point for point in history if point["timestamp"] >= cutoff_time]
            
        return history
        
    def register_on_price_update(self, callback) -> None:
        """
        Register a callback to be called when prices are updated.
        
        Args:
            callback: Function to call with (symbol, price)
        """
        if callback not in self.on_price_update_callbacks:
            self.on_price_update_callbacks.append(callback)
            
    def _notify_price_update(self, symbol: str, price: float) -> None:
        """
        Notify all registered price update callbacks.
        
        Args:
            symbol: Symbol of the cryptocurrency
            price: New price
        """
        for callback in self.on_price_update_callbacks:
            try:
                callback(symbol, price)
            except Exception as e:
                print(f"Error in price update callback: {e}")


# Example usage
if __name__ == "__main__":
    # Create a wallet core
    wallet_core = AleoWalletCore()
    
    # Generate a test account
    account = wallet_core.generate_account("Test Account")
    
    # Create a blockchain integration
    blockchain = BlockchainIntegration(wallet_core)
    
    # Check network status
    is_connected = blockchain.check_network_status()
    print(f"Connected to network: {is_connected}")
    
    # Start synchronization
    if is_connected:
        blockchain.sync_with_blockchain()
        
    # Get network status
    status = blockchain.get_network_status()
    print(f"Network status: {json.dumps(status, indent=2)}")
    
    # Create a price tracker
    price_tracker = PriceTracker()
    
    # Update prices
    price_tracker.update_prices()
    
    # Get the current Aleo price
    aleo_price = price_tracker.get_price()
    print(f"Current Aleo price: ${aleo_price:.2f}")
    
    # Start background threads
    blockchain.start_sync_thread()
    price_tracker.start_price_tracking()
    
    # Wait for a while to see updates
    print("Waiting for updates...")
    time.sleep(10)
    
    # Check the updated price
    aleo_price = price_tracker.get_price()
    print(f"Updated Aleo price: ${aleo_price:.2f}")
    
    # Get the updated network status
    status = blockchain.get_network_status()
    print(f"Updated network status: {json.dumps(status, indent=2)}")
