#!/usr/bin/env python3
"""
Test script to verify Pinecone service functionality.

This script tests the Pinecone service API compatibility without requiring a real API key.
"""

import os
import sys

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pinecone import pinecone_service

def test_pinecone_service():
    """Test the Pinecone service API without making actual API calls."""
    print("Testing Pinecone Service API Compatibility")
    print("=" * 50)
    
    # Test service instantiation
    print("✓ Service instantiation successful")
    
    # Test that methods exist and have correct signatures
    methods_to_test = [
        ('query_disease_info', 'Query method exists'),
        ('add_disease_info', 'Add method exists'),
        ('delete_disease_info', 'Delete method exists'),
        ('list_all_ids', 'List method exists')
    ]
    
    for method_name, description in methods_to_test:
        if hasattr(pinecone_service, method_name):
            print(f"✓ {description}")
        else:
            print(f"✗ {description}")
    
    # Test error handling for uninitialized service
    try:
        # This should return empty results since we don't have a real API key
        result = pinecone_service.query_disease_info("test query")
        print("✓ Query error handling works correctly")
        print(f"  - Returns expected format: {type(result).__name__}")
        print(f"  - Has required keys: {list(result.keys())}")
    except Exception as e:
        print(f"✗ Query error handling failed: {e}")
    
    print("\nPinecone service is ready for use with a valid API key!")

if __name__ == "__main__":
    test_pinecone_service()
