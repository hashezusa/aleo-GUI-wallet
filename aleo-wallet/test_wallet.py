import unittest
import os
import time
import json
import tempfile
from wallet_core import AleoWalletCore
from transaction_manager import TransactionManager
from address_book import AddressBookManager, KeyManager
from security import SecurityManager
from blockchain_integration import BlockchainIntegration, PriceTracker

class TestAleoWallet(unittest.TestCase):
    """
    Test suite for the Aleo wallet functionality.
    """
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary wallet file
        self.temp_dir = tempfile.mkdtemp()
        self.wallet_file = os.path.join(self.temp_dir, "test_wallet.dat")
        
        # Create a wallet core
        self.wallet_core = AleoWalletCore(self.wallet_file)
        
        # Create other components
        self.transaction_manager = TransactionManager(self.wallet_core)
        self.address_book = AddressBookManager(self.wallet_core)
        self.key_manager = KeyManager(self.wallet_core)
        self.security = SecurityManager(self.temp_dir)
        self.blockchain = BlockchainIntegration(self.wallet_core)
        self.price_tracker = PriceTracker()
        
    def tearDown(self):
        """Clean up after each test."""
        # Remove temporary files
        if os.path.exists(self.wallet_file):
            os.remove(self.wallet_file)
        
        # Remove temporary directory
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
    
    def test_account_creation(self):
        """Test account creation functionality."""
        # Generate a new account
        account = self.wallet_core.generate_account("Test Account")
        
        # Check that the account was created
        self.assertIsNotNone(account)
        self.assertEqual(account["name"], "Test Account")
        self.assertTrue(account["private_key"].startswith("APrivateKey1"))
        self.assertTrue(account["view_key"].startswith("AViewKey1"))
        self.assertTrue(account["address"].startswith("aleo1"))
        
        # Check that the account was added to the wallet
        self.assertEqual(len(self.wallet_core.accounts), 1)
        
        # Generate another account
        account2 = self.wallet_core.generate_account("Test Account 2")
        
        # Check that the second account was created
        self.assertIsNotNone(account2)
        self.assertEqual(account2["name"], "Test Account 2")
        
        # Check that both accounts are in the wallet
        self.assertEqual(len(self.wallet_core.accounts), 2)
    
    def test_account_import(self):
        """Test account import functionality."""
        # Generate a key pair
        key_pair = self.key_manager.generate_new_key_pair()
        
        # Import the account
        account = self.wallet_core.import_account_from_private_key(
            key_pair["private_key"], "Imported Account"
        )
        
        # Check that the account was imported
        self.assertIsNotNone(account)
        self.assertEqual(account["name"], "Imported Account")
        self.assertEqual(account["private_key"], key_pair["private_key"])
        self.assertEqual(account["address"], key_pair["address"])
        
        # Check that the account was added to the wallet
        self.assertEqual(len(self.wallet_core.accounts), 1)
    
    def test_transaction_creation(self):
        """Test transaction creation functionality."""
        # Generate an account
        account = self.wallet_core.generate_account("Test Account")
        
        # Add some balance for testing
        self.wallet_core.accounts[0]["balance"] = 100.0
        
        # Create a transaction
        transaction = self.transaction_manager.create_transaction(
            0, "aleo1recipient", 10.0, "Test transaction"
        )
        
        # Check that the transaction was created
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction["type"], "Sent")
        self.assertEqual(transaction["sender"], account["address"])
        self.assertEqual(transaction["recipient"], "aleo1recipient")
        self.assertEqual(transaction["amount"], 10.0)
        self.assertEqual(transaction["memo"], "Test transaction")
        self.assertEqual(transaction["status"], "Pending")
    
    def test_transaction_sending(self):
        """Test transaction sending functionality."""
        # Generate an account
        account = self.wallet_core.generate_account("Test Account")
        
        # Add some balance for testing
        self.wallet_core.accounts[0]["balance"] = 100.0
        
        # Send a transaction
        tx_id = self.transaction_manager.send_transaction(
            0, "aleo1recipient", 10.0, "Test transaction"
        )
        
        # Check that the transaction was sent
        self.assertIsNotNone(tx_id)
        
        # Check that the transaction was added to the account's history
        transactions = self.wallet_core.get_transactions(0)
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]["transaction_id"], tx_id)
        
        # Check that the balance was updated
        self.assertLess(self.wallet_core.get_balance(0), 100.0)
    
    def test_address_book(self):
        """Test address book functionality."""
        # Generate an account
        self.wallet_core.generate_account("Test Account")
        
        # Add a contact
        result = self.address_book.add_contact(
            0, "Alice", "aleo1alice", "Friend"
        )
        
        # Check that the contact was added
        self.assertTrue(result)
        
        # Get the contacts
        contacts = self.address_book.get_contacts(0)
        
        # Check that the contact is in the list
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0]["name"], "Alice")
        self.assertEqual(contacts[0]["address"], "aleo1alice")
        self.assertEqual(contacts[0]["description"], "Friend")
        
        # Add another contact
        self.address_book.add_contact(
            0, "Bob", "aleo1bob", "Colleague"
        )
        
        # Check that both contacts are in the list
        contacts = self.address_book.get_contacts(0)
        self.assertEqual(len(contacts), 2)
        
        # Search for contacts
        results = self.address_book.search_contacts(0, "alice")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Alice")
        
        # Remove a contact
        result = self.address_book.remove_contact(0, 0)
        
        # Check that the contact was removed
        self.assertTrue(result)
        contacts = self.address_book.get_contacts(0)
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0]["name"], "Bob")
    
    def test_security_features(self):
        """Test security features."""
        # Create a master password
        result = self.security.create_master_password("test_password")
        
        # Check that the password was set
        self.assertTrue(result)
        
        # Verify the password
        result = self.security.verify_master_password("test_password")
        self.assertTrue(result)
        
        # Verify an incorrect password
        result = self.security.verify_master_password("wrong_password")
        self.assertFalse(result)
        
        # Encrypt some data
        encrypted = self.security.encrypt_data("This is sensitive data", "test_password")
        
        # Check that the data was encrypted
        self.assertIsNotNone(encrypted)
        self.assertNotEqual(encrypted, "This is sensitive data")
        
        # Decrypt the data
        decrypted = self.security.decrypt_data(encrypted, "test_password")
        
        # Check that the data was decrypted correctly
        self.assertEqual(decrypted, "This is sensitive data")
        
        # Change the password
        result = self.security.change_master_password("test_password", "new_password")
        
        # Check that the password was changed
        self.assertTrue(result)
        
        # Verify the new password
        result = self.security.verify_master_password("new_password")
        self.assertTrue(result)
        
        # Verify the old password (should fail)
        result = self.security.verify_master_password("test_password")
        self.assertFalse(result)
    
    def test_blockchain_integration(self):
        """Test blockchain integration."""
        # Check network status
        result = self.blockchain.check_network_status()
        
        # This might be True or False depending on network connectivity
        # Just check that it doesn't raise an exception
        self.assertIsNotNone(result)
        
        # Get network status
        status = self.blockchain.get_network_status()
        
        # Check that the status contains the expected fields
        self.assertIn("connected", status)
        self.assertIn("latest_block_height", status)
        self.assertIn("latest_block_hash", status)
        self.assertIn("peers", status)
        self.assertIn("last_sync_time", status)
    
    def test_price_tracker(self):
        """Test price tracker."""
        # Update prices
        result = self.price_tracker.update_prices()
        
        # Check that the prices were updated
        self.assertTrue(result)
        
        # Get the current Aleo price
        price = self.price_tracker.get_price()
        
        # Check that the price is a positive number
        self.assertGreater(price, 0)
        
        # Get price history
        history = self.price_tracker.get_price_history()
        
        # Check that the history contains at least one entry
        self.assertGreaterEqual(len(history), 1)
        
        # Check that the history entries have the expected fields
        self.assertIn("timestamp", history[0])
        self.assertIn("price", history[0])
    
    def test_wallet_persistence(self):
        """Test wallet persistence."""
        # Generate an account
        account = self.wallet_core.generate_account("Test Account")
        
        # Save the wallet
        self.wallet_core.save_wallet()
        
        # Create a new wallet core with the same file
        new_wallet = AleoWalletCore(self.wallet_file)
        
        # Check that the account was loaded
        self.assertEqual(len(new_wallet.accounts), 1)
        self.assertEqual(new_wallet.accounts[0]["name"], "Test Account")
        self.assertEqual(new_wallet.accounts[0]["address"], account["address"])
    
    def test_wallet_encryption(self):
        """Test wallet encryption."""
        # Generate an account
        self.wallet_core.generate_account("Test Account")
        
        # Encrypt the wallet
        result = self.wallet_core.encrypt_wallet("test_password")
        
        # Check that the wallet was encrypted
        self.assertTrue(result)
        self.assertTrue(self.wallet_core.is_encrypted)
        
        # Save the wallet
        self.wallet_core.save_wallet()
        
        # Create a new wallet core with the same file
        new_wallet = AleoWalletCore(self.wallet_file)
        
        # Check that the wallet is encrypted
        self.assertTrue(new_wallet.is_encrypted)
        
        # Try to decrypt with the wrong password
        result = new_wallet.decrypt_wallet("wrong_password")
        self.assertFalse(result)
        
        # Decrypt with the correct password
        result = new_wallet.decrypt_wallet("test_password")
        self.assertTrue(result)
        
        # Check that the account was loaded
        self.assertEqual(len(new_wallet.accounts), 1)
        self.assertEqual(new_wallet.accounts[0]["name"], "Test Account")


if __name__ == "__main__":
    unittest.main()
