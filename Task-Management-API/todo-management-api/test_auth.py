"""
Quick authentication test script
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import async_session_maker
from models import User
from auth.security import hash_password, verify_password, create_access_token, verify_token

async def test_auth_flow():
    """Test the complete authentication flow"""
    print("Testing Authentication Flow\n")

    # Test 1: Password Hashing
    print("1. Testing password hashing...")
    password = "testpassword123"
    hashed = hash_password(password)
    print(f"   OK Password hashed: {hashed[:50]}...")

    # Test 2: Password Verification
    print("\n2. Testing password verification...")
    is_valid = verify_password(password, hashed)
    print(f"   OK Password verification: {is_valid}")

    if not is_valid:
        print("   ERROR ERROR: Password verification failed!")
        return False

    # Test 3: Token Creation
    print("\n3. Testing token creation...")
    token_data = {"sub": "testuser", "user_id": 1}
    access_token = create_access_token(token_data)
    print(f"   OK Token created: {access_token[:50]}...")

    # Test 4: Token Verification
    print("\n4. Testing token verification...")
    payload = verify_token(access_token)
    print(f"   OK Token payload: {payload}")

    if not payload:
        print("   ERROR ERROR: Token verification failed!")
        return False

    # Test 5: Database Connection
    print("\n5. Testing database connection...")
    try:
        async with async_session_maker() as session:
            result = await session.execute(select(User).limit(1))
            users = result.scalars().all()
            print(f"   OK Database connected. Found {len(users)} users")
    except Exception as e:
        print(f"   ERROR Database error: {e}")
        return False

    print("\nAll authentication tests passed!")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_auth_flow())
    sys.exit(0 if result else 1)
