#!/usr/bin/env python3
"""Test script untuk validasi auth controller"""

import sys
sys.path.insert(0, '.')

from app.controllers.auth_controller import AuthController

def test_username_validation():
    """Test username validation rules"""
    controller = AuthController()
    
    print("=" * 60)
    print("TEST: Username Validation")
    print("=" * 60)
    
    test_cases = [
        ("", "Username harus diisi"),
        ("ab", "Username terlalu pendek (< 3 karakter)"),
        ("a" * 21, "Username terlalu panjang (> 20 karakter)"),
        ("john doe", "Username dengan spasi"),
        ("john@doe", "Username dengan karakter khusus"),
        ("john_doe", "Username valid dengan underscore"),
        ("john-doe", "Username valid dengan dash"),
        ("john.doe", "Username valid dengan titik"),
        ("john123", "Username valid alphanumeric"),
    ]
    
    for username, description in test_cases:
        errors = controller._validate_username(username)
        status = "❌ ERROR" if errors else "✓ OK"
        error_msg = errors.get("username", "")
        print(f"{status}: {description}")
        if error_msg:
            print(f"       → {error_msg}")
        print()


def test_password_validation():
    """Test password validation rules"""
    controller = AuthController()
    
    print("=" * 60)
    print("TEST: Password Validation")
    print("=" * 60)
    
    test_cases = [
        ("", "Password harus diisi"),
        ("1234567", "Password terlalu pendek (< 8 karakter)"),
        ("12345678", "Password valid (8 karakter)"),
        ("myPassword123!", "Password valid (13 karakter)"),
    ]
    
    for password, description in test_cases:
        errors = controller._validate_password(password)
        status = "❌ ERROR" if errors else "✓ OK"
        error_msg = errors.get("password", "")
        print(f"{status}: {description}")
        if error_msg:
            print(f"       → {error_msg}")
        print()


def test_email_validation():
    """Test email validation rules"""
    controller = AuthController()
    
    print("=" * 60)
    print("TEST: Email Validation")
    print("=" * 60)
    
    test_cases = [
        ("", "Email harus diisi"),
        ("invalid.email", "Email tanpa domain"),
        ("invalid@.com", "Email dengan format tidak valid"),
        ("user@domain.com", "Email valid"),
        ("john.doe123@example.co.uk", "Email valid (domain kompleks)"),
    ]
    
    for email, description in test_cases:
        errors = controller._validate_email(email)
        status = "❌ ERROR" if errors else "✓ OK"
        error_msg = errors.get("email", "")
        print(f"{status}: {description}")
        if error_msg:
            print(f"       → {error_msg}")
        print()


if __name__ == "__main__":
    test_username_validation()
    test_password_validation()
    test_email_validation()
    
    print("=" * 60)
    print("✓ Semua test selesai!")
    print("=" * 60)
