"""Loads and validates config.json file against a config json schema"""
import locale
import json
import os
from typing import Literal
import jsonschema

class ConfigManager:
    """Manages configuration settings from a JSON file"""
    
    def __init__(self, config_file):
        """Initialize with the config file path"""
        self.config_file = config_file
        self.load_config()
        
    def load_config(self):
        """Load the configuration from the JSON file"""
        # Make sure the config file exists
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
        
        # Load the JSON config file
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)
        
        # Check if it's a multi-account config
        if 'accounts' in self.config:
            self.multi_account = True
        else:
            # For backwards compatibility, treat as a single account
            self.multi_account = False
            self.accounts = [{
                'name': 'Default',
                'awsAccessKeyId': self.config.get('awsAccessKeyId'),
                'awsSecretAccessKey': self.config.get('awsSecretAccessKey'),
                'bucket': self.config.get('bucket'),
                'storageMode': self.config.get('storageMode', 'remote')
            }]
    
    def get_accounts(self):
        """Get list of available accounts"""
        if self.multi_account:
            return self.config['accounts']
        else:
            return self.accounts
    
    def get_account(self, index):
        """Get a specific account by index"""
        accounts = self.get_accounts()
        if 0 <= index < len(accounts):
            return accounts[index]
        raise IndexError("Account index out of range")
    
    # Legacy properties for backward compatibility
    @property
    def aws_access_key_id(self):
        if self.multi_account:
            return self.get_account(0).get('awsAccessKeyId')
        return self.config.get('awsAccessKeyId')
    
    @property
    def aws_secret_access_key(self):
        if self.multi_account:
            return self.get_account(0).get('awsSecretAccessKey')
        return self.config.get('awsSecretAccessKey')
    
    @property
    def bucket(self):
        if self.multi_account:
            return self.get_account(0).get('bucket')
        return self.config.get('bucket')
    
    @property
    def storage_mode(self):
        if self.multi_account:
            return self.get_account(0).get('storageMode', 'remote')
        return self.config.get('storageMode', 'remote')
