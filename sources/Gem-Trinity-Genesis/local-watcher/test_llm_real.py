import os
import sys

# Load environment variables
try:
    from dotenv import load_dotenv
    env_paths = [
        Path(__file__).parent.parent / ".env",
        Path(__file__).parent / ".env",
        Path.cwd() / ".env"
    ]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            print(f"Loaded .env from: {env_path}")
            break
except:
    pass

# Import LLMProvider after loading env
from llm_provider import LLMProvider
from pathlib import Path

print("=" * 60)
print("TESTING LLM PROVIDER WITH GOOGLE-GENAI SDK")
print("=" * 60)

# Check environment
print(f"\n[ENV] LLM_PROVIDER: {os.getenv('LLM_PROVIDER', 'not set')}")
print(f"[ENV] LLM_API_KEY present: {bool(os.getenv('LLM_API_KEY'))}")

# Initialize provider
provider = LLMProvider(use_cache=False, use_circuit_breaker=False)

print(f"\n[PROVIDER] Provider type: {provider.provider}")
print(f"[PROVIDER] API Key present: {bool(provider.api_key)}")
print(f"[PROVIDER] Using old genai: {getattr(provider, '_use_old_genai', False)}")

# Check initialization
if hasattr(provider, '_gemini_client'):
    print(f"[PROVIDER] Gemini Client: {'SET' if provider._gemini_client else 'NOT SET'}")
if hasattr(provider, '_gemini_model'):
    print(f"[PROVIDER] Gemini Model (old): {'SET' if provider._gemini_model else 'NOT SET'}")
if hasattr(provider, '_gemini_model_name'):
    print(f"[PROVIDER] Model name: {provider._gemini_model_name}")

# Test generation
print("\n" + "=" * 60)
print("TESTING LLM GENERATION")
print("=" * 60)

try:
    print("\n[TEST] Calling generate()...")
    response = provider.generate(
        prompt="What is 2 + 2? Answer with just the number.",
        system_prompt="You are a helpful assistant.",
        model="gemini"
    )
    print(f"\n[SUCCESS] Response: {response}")
except Exception as e:
    print(f"\n[ERROR] {e}")

print("\n" + "=" * 60)
