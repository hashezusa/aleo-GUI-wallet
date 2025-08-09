import os
import time
import json
import base64
import hashlib
import secrets
from typing import Dict, Any, List, Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class SecurityManager:
    """
    Manages security features for the Aleo wallet, including encryption,
    authentication, and secure storage of sensitive data.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the Security Manager.
        
        Args:
            data_dir: Optional directory for storing security-related files
        """
        self.data_dir = data_dir or os.path.expanduser("~/.aleo_wallet")
        self.security_config_file = os.path.join(self.data_dir, "security_config.json")
        
        # Ensure the data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Default security settings
        self.default_settings = {
            "password_required": True,
            "auto_lock_timeout": 300,  # 5 minutes
            "failed_attempts_limit": 5,
            "encryption_strength": "high",
            "pbkdf2_iterations": 100000,
            "last_access": 0,
            "failed_attempts": 0,
            "locked": False
        }
        
        # Load or create security settings
        self.settings = self.load_security_settings()
        
    def load_security_settings(self) -> Dict[str, Any]:
        """
        Load security settings from file or create default settings.
        
        Returns:
            Dictionary of security settings
        """
        if os.path.exists(self.security_config_file):
            try:
                with open(self.security_config_file, "r") as f:
                    settings = json.load(f)
                return {**self.default_settings, **settings}
            except Exception as e:
                print(f"Error loading security settings: {e}")
                
        return self.default_settings.copy()
    
    def save_security_settings(self) -> bool:
        """
        Save security settings to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.security_config_file, "w") as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving security settings: {e}")
            return False
    
    def update_security_settings(self, updates: Dict[str, Any]) -> bool:
        """
        Update security settings.
        
        Args:
            updates: Dictionary of settings to update
            
        Returns:
            True if successful, False otherwise
        """
        self.settings.update(updates)
        return self.save_security_settings()
    
    def create_master_password(self, password: str) -> bool:
        """
        Create a master password for the wallet.
        
        Args:
            password: The master password
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate a salt
            salt = os.urandom(16)
            
            # Derive a key from the password
            key = self.derive_key_from_password(password, salt)
            
            # Store the salt and password hash
            self.settings["password_salt"] = base64.b64encode(salt).decode('utf-8')
            self.settings["password_hash"] = base64.b64encode(hashlib.sha256(key).digest()).decode('utf-8')
            
            # Update settings
            self.settings["password_required"] = True
            self.settings["last_access"] = int(time.time())
            self.settings["failed_attempts"] = 0
            self.settings["locked"] = False
            
            return self.save_security_settings()
        except Exception as e:
            print(f"Error creating master password: {e}")
            return False
    
    def verify_master_password(self, password: str) -> bool:
        """
        Verify the master password.
        
        Args:
            password: The password to verify
            
        Returns:
            True if the password is correct, False otherwise
        """
        try:
            # Check if password is required
            if not self.settings.get("password_required", True):
                return True
                
            # Check if the wallet is locked due to too many failed attempts
            if self.settings.get("locked", False):
                # Check if the lockout period has expired (1 hour)
                lockout_time = self.settings.get("lockout_time", 0)
                if int(time.time()) - lockout_time < 3600:
                    return False
                else:
                    # Reset the lockout
                    self.settings["locked"] = False
                    self.settings["failed_attempts"] = 0
                    self.save_security_settings()
            
            # Get the stored salt and hash
            salt_b64 = self.settings.get("password_salt")
            hash_b64 = self.settings.get("password_hash")
            
            if not salt_b64 or not hash_b64:
                return False
                
            salt = base64.b64decode(salt_b64)
            stored_hash = base64.b64decode(hash_b64)
            
            # Derive a key from the provided password
            key = self.derive_key_from_password(password, salt)
            
            # Compare the hashes
            computed_hash = hashlib.sha256(key).digest()
            
            if computed_hash == stored_hash:
                # Password is correct, reset failed attempts and update last access
                self.settings["failed_attempts"] = 0
                self.settings["last_access"] = int(time.time())
                self.save_security_settings()
                return True
            else:
                # Password is incorrect, increment failed attempts
                failed_attempts = self.settings.get("failed_attempts", 0) + 1
                self.settings["failed_attempts"] = failed_attempts
                
                # Check if we've reached the limit
                if failed_attempts >= self.settings.get("failed_attempts_limit", 5):
                    self.settings["locked"] = True
                    self.settings["lockout_time"] = int(time.time())
                
                self.save_security_settings()
                return False
                
        except Exception as e:
            print(f"Error verifying master password: {e}")
            return False
    
    def change_master_password(self, old_password: str, new_password: str) -> bool:
        """
        Change the master password.
        
        Args:
            old_password: The current password
            new_password: The new password
            
        Returns:
            True if successful, False otherwise
        """
        # Verify the old password
        if not self.verify_master_password(old_password):
            return False
            
        # Create the new password
        return self.create_master_password(new_password)
    
    def disable_password_protection(self, password: str) -> bool:
        """
        Disable password protection.
        
        Args:
            password: The current password
            
        Returns:
            True if successful, False otherwise
        """
        # Verify the password
        if not self.verify_master_password(password):
            return False
            
        # Disable password protection
        self.settings["password_required"] = False
        return self.save_security_settings()
    
    def enable_password_protection(self, password: str) -> bool:
        """
        Enable password protection.
        
        Args:
            password: The password to set
            
        Returns:
            True if successful, False otherwise
        """
        return self.create_master_password(password)
    
    def is_password_protected(self) -> bool:
        """
        Check if the wallet is password protected.
        
        Returns:
            True if password protected, False otherwise
        """
        return self.settings.get("password_required", True)
    
    def is_locked(self) -> bool:
        """
        Check if the wallet is locked due to too many failed attempts.
        
        Returns:
            True if locked, False otherwise
        """
        if not self.settings.get("locked", False):
            return False
            
        # Check if the lockout period has expired (1 hour)
        lockout_time = self.settings.get("lockout_time", 0)
        if int(time.time()) - lockout_time < 3600:
            return True
        else:
            # Reset the lockout
            self.settings["locked"] = False
            self.settings["failed_attempts"] = 0
            self.save_security_settings()
            return False
    
    def should_auto_lock(self) -> bool:
        """
        Check if the wallet should auto-lock based on inactivity.
        
        Returns:
            True if should auto-lock, False otherwise
        """
        if not self.settings.get("password_required", True):
            return False
            
        auto_lock_timeout = self.settings.get("auto_lock_timeout", 300)
        last_access = self.settings.get("last_access", 0)
        
        return int(time.time()) - last_access > auto_lock_timeout
    
    def update_last_access(self) -> bool:
        """
        Update the last access timestamp.
        
        Returns:
            True if successful, False otherwise
        """
        self.settings["last_access"] = int(time.time())
        return self.save_security_settings()
    
    def derive_key_from_password(self, password: str, salt: bytes) -> bytes:
        """
        Derive a cryptographic key from a password.
        
        Args:
            password: The password
            salt: The salt
            
        Returns:
            The derived key
        """
        iterations = self.settings.get("pbkdf2_iterations", 100000)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        
        return kdf.derive(password.encode())
    
    def encrypt_data(self, data: str, password: str = None) -> str:
        """
        Encrypt data with a password.
        
        Args:
            data: The data to encrypt
            password: Optional password (uses master password if not provided)
            
        Returns:
            Encrypted data as a base64 string
        """
        try:
            # Generate a salt
            salt = os.urandom(16)
            
            # Derive a key from the password
            if password:
                key = self.derive_key_from_password(password, salt)
            else:
                # Use the stored salt for the master password
                stored_salt = base64.b64decode(self.settings.get("password_salt", ""))
                if not stored_salt:
                    raise ValueError("No master password set")
                key = self.derive_key_from_password(password, stored_salt)
                salt = stored_salt
            
            # Generate an initialization vector
            iv = os.urandom(16)
            
            # Create a cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Pad the data to a multiple of 16 bytes (AES block size)
            padded_data = self.pad_data(data.encode())
            
            # Encrypt the data
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            # Combine salt, IV, and encrypted data
            result = salt + iv + encrypted_data
            
            # Return as base64
            return base64.b64encode(result).decode('utf-8')
        except Exception as e:
            print(f"Error encrypting data: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str, password: str = None) -> str:
        """
        Decrypt data with a password.
        
        Args:
            encrypted_data: The encrypted data as a base64 string
            password: Optional password (uses master password if not provided)
            
        Returns:
            Decrypted data
        """
        try:
            # Decode from base64
            data = base64.b64decode(encrypted_data)
            
            # Extract salt, IV, and encrypted data
            salt = data[:16]
            iv = data[16:32]
            ciphertext = data[32:]
            
            # Derive a key from the password
            if password:
                key = self.derive_key_from_password(password, salt)
            else:
                # Use the stored salt for the master password
                stored_salt = base64.b64decode(self.settings.get("password_salt", ""))
                if not stored_salt:
                    raise ValueError("No master password set")
                key = self.derive_key_from_password(password, stored_salt)
            
            # Create a cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Decrypt the data
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Unpad the data
            data = self.unpad_data(padded_data)
            
            return data.decode('utf-8')
        except Exception as e:
            print(f"Error decrypting data: {e}")
            raise
    
    def pad_data(self, data: bytes) -> bytes:
        """
        Pad data to a multiple of 16 bytes (AES block size).
        
        Args:
            data: The data to pad
            
        Returns:
            Padded data
        """
        block_size = 16
        padding_size = block_size - (len(data) % block_size)
        padding = bytes([padding_size]) * padding_size
        return data + padding
    
    def unpad_data(self, data: bytes) -> bytes:
        """
        Remove padding from data.
        
        Args:
            data: The padded data
            
        Returns:
            Unpadded data
        """
        padding_size = data[-1]
        return data[:-padding_size]
    
    def generate_secure_random_bytes(self, length: int) -> bytes:
        """
        Generate cryptographically secure random bytes.
        
        Args:
            length: Number of bytes to generate
            
        Returns:
            Random bytes
        """
        return secrets.token_bytes(length)
    
    def generate_secure_random_string(self, length: int) -> str:
        """
        Generate a cryptographically secure random string.
        
        Args:
            length: Length of the string
            
        Returns:
            Random string
        """
        return secrets.token_urlsafe(length)
    
    def hash_data(self, data: str) -> str:
        """
        Create a secure hash of data.
        
        Args:
            data: The data to hash
            
        Returns:
            Hash as a hex string
        """
        return hashlib.sha256(data.encode()).hexdigest()
    
    def secure_erase(self, file_path: str) -> bool:
        """
        Securely erase a file by overwriting it with random data before deletion.
        
        Args:
            file_path: Path to the file to erase
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                return True
                
            # Get the file size
            file_size = os.path.getsize(file_path)
            
            # Overwrite the file with random data
            with open(file_path, "wb") as f:
                # Write in chunks to avoid memory issues with large files
                chunk_size = 1024 * 1024  # 1 MB
                remaining = file_size
                
                while remaining > 0:
                    write_size = min(chunk_size, remaining)
                    f.write(os.urandom(write_size))
                    remaining -= write_size
                    
            # Delete the file
            os.remove(file_path)
            
            return True
        except Exception as e:
            print(f"Error securely erasing file: {e}")
            return False


class BiometricAuthManager:
    """
    Manages biometric authentication for the Aleo wallet.
    This is a placeholder implementation as actual biometric authentication
    would require platform-specific implementations.
    """
    
    def __init__(self):
        """Initialize the Biometric Authentication Manager."""
        self.is_available = False
        self.is_enabled = False
        
        # Check if biometric authentication is available on this platform
        self.check_availability()
        
    def check_availability(self) -> bool:
        """
        Check if biometric authentication is available on this platform.
        
        Returns:
            True if available, False otherwise
        """
        # This is a placeholder implementation
        # In a real implementation, we would check the platform and available hardware
        self.is_available = False
        return self.is_available
    
    def enable(self) -> bool:
        """
        Enable biometric authentication.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available:
            return False
            
        # This is a placeholder implementation
        # In a real implementation, we would register with the platform's biometric API
        self.is_enabled = True
        return True
    
    def disable(self) -> bool:
        """
        Disable biometric authentication.
        
        Returns:
            True if successful, False otherwise
        """
        self.is_enabled = False
        return True
    
    def authenticate(self) -> bool:
        """
        Authenticate using biometrics.
        
        Returns:
            True if authentication successful, False otherwise
        """
        if not self.is_available or not self.is_enabled:
            return False
            
        # This is a placeholder implementation
        # In a real implementation, we would use the platform's biometric API
        return True


# Example usage
if __name__ == "__main__":
    # Create a security manager
    security = SecurityManager()
    
    # Create a master password
    security.create_master_password("my_secure_password")
    
    # Verify the password
    is_valid = security.verify_master_password("my_secure_password")
    print(f"Password valid: {is_valid}")
    
    # Encrypt some data
    encrypted = security.encrypt_data("This is sensitive data", "my_secure_password")
    print(f"Encrypted: {encrypted}")
    
    # Decrypt the data
    decrypted = security.decrypt_data(encrypted, "my_secure_password")
    print(f"Decrypted: {decrypted}")
    
    # Check auto-lock
    should_lock = security.should_auto_lock()
    print(f"Should auto-lock: {should_lock}")
    
    # Update security settings
    security.update_security_settings({"auto_lock_timeout": 600})
    print(f"Updated auto-lock timeout: {security.settings['auto_lock_timeout']}")
    
    # Create a biometric auth manager
    biometric = BiometricAuthManager()
    print(f"Biometric authentication available: {biometric.is_available}")
