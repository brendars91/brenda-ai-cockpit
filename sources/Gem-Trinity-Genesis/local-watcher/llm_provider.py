import os
import asyncio
from pathlib import Path
from typing import Optional

# Load .env file from project root
try:
    from dotenv import load_dotenv
    # Try multiple possible .env locations
    env_paths = [
        Path(__file__).parent.parent / ".env",  # Project root
        Path(__file__).parent / ".env",          # local-watcher folder
        Path.cwd() / ".env"                      # Current working directory
    ]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            print(f"[LLMProvider] Loaded .env from: {env_path}")
            break
except ImportError:
    print("[LLMProvider] python-dotenv not installed. Environment variables must be set manually.")

class LLMProvider:
    def __init__(self, use_cache: bool = True, use_circuit_breaker: bool = True):
        """
        Initialize LLM Provider with resilience features.

        Args:
            use_cache: Enable semantic caching
            use_circuit_breaker: Enable circuit breaker pattern
        """
        self.provider = os.getenv("LLM_PROVIDER", "mock") # mock, ollama, gemini, openai
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.api_key = os.getenv("LLM_API_KEY", "")
        self._gemini_model = None

        # FASE 3: Resilience features
        self.use_cache = use_cache
        self.use_circuit_breaker = use_circuit_breaker
        self._semantic_cache = None
        self._circuit_breaker = None

        # Initialize resilience features
        if use_cache:
            try:
                from semantic_cache import get_semantic_cache
                self._semantic_cache = get_semantic_cache()
                print("[LLMProvider] Semantic cache enabled")
            except ImportError:
                print("[LLMProvider] Semantic cache not available")

        if use_circuit_breaker:
            try:
                from circuit_breaker import get_circuit_breaker
                self._circuit_breaker = get_circuit_breaker()
                print("[LLMProvider] Circuit breaker enabled")
            except ImportError:
                print("[LLMProvider] Circuit breaker not available")

        # Initialize Gemini if selected
        if self.provider == "gemini" and self.api_key:
            try:
                # Use NEW google-genai SDK (google.genai)
                from google import genai
                self._gemini_client = genai.Client(api_key=self.api_key)
                self._gemini_model_name = 'gemini-2.5-flash'  # Latest stable model
                self._use_old_genai = False
                print(f"[LLMProvider] Gemini 2.5 Flash initialized (google.genai SDK)")
            except ImportError as e:
                print(f"[LLMProvider] google-genai not installed or failed: {e}")
                self._gemini_client = None
                self._gemini_model = None
            except Exception as e:
                print(f"[LLMProvider] Gemini init failed: {e}")
                self._gemini_client = None
                self._gemini_model = None
        else:
            self._gemini_client = None
            self._gemini_model = None
            self._use_old_genai = False

    def generate(self, prompt: str, system_prompt: str = "You are a helpful assistant.", model: Optional[str] = None, **kwargs) -> str:
        """
        Synchronous generate method with caching and circuit breaker.

        Args:
            prompt: Input prompt
            system_prompt: System prompt
            model: Model name (defaults to provider default)
            **kwargs: Additional parameters

        Returns:
            Generated response
        """
        # Use provided model or default
        if not model:
            model = self.provider

        # Check semantic cache first
        if self._semantic_cache and self.use_cache:
            cached = self._semantic_cache.get(prompt, model)
            if cached:
                print(f"[LLMProvider] Cache HIT: {prompt[:30]}...")
                return cached

        # Execute with circuit breaker if enabled
        if self._circuit_breaker and self.use_circuit_breaker:
            return self._generate_with_resilience(prompt, system_prompt, model, **kwargs)
        else:
            # Direct call (original behavior)
            return self._generate_direct(prompt, system_prompt, model, **kwargs)

    def _generate_with_resilience(self, prompt: str, system_prompt: str, model: str, **kwargs) -> str:
        """
        Generate with circuit breaker and caching.

        This runs in a synchronous context but uses async internally.
        """
        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # We're in an async context, use asyncio.create_task via ThreadPoolExecutor to bridge sync->async
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(
                        asyncio.run,
                        self._generate_async_with_resilience(prompt, system_prompt, model, **kwargs)
                    )
                    result = future.result(timeout=120)
            else:
                # No running loop, use asyncio.run() which handles loop creation/cleanup
                result = asyncio.run(
                    self._generate_async_with_resilience(prompt, system_prompt, model, **kwargs)
                )

            # Extract data from CallResult if returned
            actual_result = result.data if hasattr(result, "data") else result
            
            # Cache the result
            if self._semantic_cache and self.use_cache:
                self._semantic_cache.set(
                    prompt,
                    actual_result,
                    model,
                    tokens_used=kwargs.get("max_tokens", 1000),
                    cost=self._estimate_cost(model, kwargs.get("max_tokens", 1000))
                )

            return actual_result

        except Exception as e:
            print(f"[LLMProvider] Resilient generation failed: {e}")
            # Fallback to direct generation
            return self._generate_direct(prompt, system_prompt, model, **kwargs)

    async def _generate_async_with_resilience(self, prompt: str, system_prompt: str, model: str, **kwargs) -> str:
        """
        Async generation with circuit breaker.

        Args:
            prompt: Input prompt
            system_prompt: System prompt
            model: Model name
            **kwargs: Additional parameters

        Returns:
            Generated response
        """
        # Define fallback
        async def fallback(*args, **kwargs):
            print("[LLMProvider] Using fallback response")
            return self._get_fallback_response(prompt, model)

        # Define actual call
        async def call_llm():
            # Call the appropriate provider
            if model == "mock":
                return self._mock_generate(prompt)
            elif model == "gemini":
                return await self._gemini_generate_async(prompt, system_prompt)
            elif model == "ollama":
                return await self._ollama_generate(prompt, system_prompt)
            else:
                # Default to provider from init
                if self.provider == "mock":
                    return self._mock_generate(prompt)
                elif self.provider == "gemini":
                    return await self._gemini_generate_async(prompt, system_prompt)
                elif self.provider == "ollama":
                    return await self._ollama_generate(prompt, system_prompt)
                else:
                    return "Error: Unknown provider"

        # Execute through circuit breaker
        result = await self._circuit_breaker.call(
            call_llm,
            fallback=fallback,
            model=model
        )

        return result.data if hasattr(result, "data") else result

    def _generate_direct(self, prompt: str, system_prompt: str, model: str, **kwargs) -> str:
        """
        Direct generation without resilience features (original behavior).

        Args:
            prompt: Input prompt
            system_prompt: System prompt
            model: Model name
            **kwargs: Additional parameters

        Returns:
            Generated response
        """
        # Determine which provider to use
        if model == "mock":
            return self._mock_generate(prompt)
        elif model == "gemini":
            return self._gemini_generate_sync(prompt, system_prompt)
        elif model == "ollama":
            # For ollama, we need async, so wrap it
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        future = pool.submit(asyncio.run, self._ollama_generate(prompt, system_prompt))
                        return future.result()
                else:
                    return loop.run_until_complete(self._ollama_generate(prompt, system_prompt))
            except Exception as e:
                return f"Ollama Error: {e}"
        else:
            # Use provider from init
            if self.provider == "mock":
                return self._mock_generate(prompt)
            elif self.provider == "gemini":
                return self._gemini_generate_sync(prompt, system_prompt)
            elif self.provider == "ollama":
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as pool:
                            future = pool.submit(asyncio.run, self._ollama_generate(prompt, system_prompt))
                            return future.result()
                    else:
                        return loop.run_until_complete(self._ollama_generate(prompt, system_prompt))
                except Exception as e:
                    return f"Ollama Error: {e}"
            else:
                return "Error: Unknown provider"

    async def _gemini_generate_async(self, prompt: str, system_prompt: str) -> str:
        """Async Gemini generation using new google-genai SDK."""
        # Check if using old API
        if self._use_old_genai:
            if not self._gemini_model:
                print(f"[LLMProvider] Old API Model is None. Provider: {self.provider}")
                raise Exception("Gemini (old API) not initialized. Check API key.")

            try:
                # Old API: generate_content
                response = await asyncio.to_thread(
                    self._gemini_model.generate_content,
                    prompt
                )

                if response.text:
                    return response.text
                else:
                    raise Exception("Empty response from Gemini")

            except Exception as e:
                raise Exception(f"Gemini (old API) generation failed: {e}")

        # New google-genai SDK
        if not self._gemini_client:
            print(f"[LLMProvider] Client is None. Provider: {self.provider}, Key Present: {bool(self.api_key)}")
            raise Exception("Gemini not initialized. Check API key.")

        try:
            # New API: client.models.generate_content
            response = await asyncio.to_thread(
                self._gemini_client.models.generate_content,
                model=self._gemini_model_name,
                contents=prompt
            )

            if response.text:
                return response.text
            else:
                raise Exception("Empty response from Gemini")

        except Exception as e:
            raise Exception(f"Gemini generation failed: {e}")

    def _get_fallback_response(self, prompt: str, model: str) -> str:
        """Get fallback response when API is unavailable"""
        return (
            f"# Service Temporarily Unavailable\n\n"
            f"I apologize, but the AI service is currently experiencing issues. "
            f"Your request has been logged.\n\n"
            f"**Your request was:**\n{prompt[:200]}...\n\n"
            f"**Model:** {model}\n\n"
            f"Please try again in a few moments."
        )

    def _estimate_cost(self, model: str, tokens: int) -> float:
        """Estimate API cost in USD"""
        # Rough estimates (adjust based on actual pricing)
        costs = {
            "gemini-pro": 0.00025,  # per 1K tokens
            "gemini-2.0-flash": 0.00007,
            "gemini-2.0": 0.0005,
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.002,
            "mock": 0.0
        }

        cost_per_1k = costs.get(model, 0.001)
        return (tokens / 1000) * cost_per_1k

    def get_cache_stats(self) -> Optional[dict]:
        """Get semantic cache statistics"""
        if self._semantic_cache:
            return self._semantic_cache.get_stats()
        return None

    def get_circuit_breaker_stats(self) -> Optional[dict]:
        """Get circuit breaker statistics"""
        if self._circuit_breaker:
            return self._circuit_breaker.get_state()
        return None

    def clear_cache(self):
        """Clear semantic cache"""
        if self._semantic_cache:
            self._semantic_cache.clear()
            print("[LLMProvider] Semantic cache cleared")

    def reset_circuit_breaker(self):
        """Reset circuit breaker to closed state"""
        if self._circuit_breaker:
            self._circuit_breaker.reset()
            print("[LLMProvider] Circuit breaker reset")

    def _gemini_generate_sync(self, prompt: str, system_prompt: str) -> str:
        """Synchronous Gemini generation using new google-genai SDK."""
        # Check if using old API
        if self._use_old_genai:
            if not self._gemini_model:
                print(f"[LLMProvider DEBUG] Old API Model is None. Provider: {self.provider}")
                return "Error: Gemini (old API) not initialized. Check API key."

            try:
                # Old API: generate_content
                response = self._gemini_model.generate_content(prompt)
                if response.text:
                    return response.text
                else:
                    return "Error: Empty response from Gemini"
            except Exception as e:
                return f"Gemini (old API) Error: {e}"

        # New google-genai SDK
        if not self._gemini_client:
            print(f"[LLMProvider DEBUG] Client is None. Provider: {self.provider}, Key Present: {bool(self.api_key)}")
            return "Error: Gemini not initialized. Check API key."

        try:
            # New API: client.models.generate_content
            response = self._gemini_client.models.generate_content(
                model=self._gemini_model_name,
                contents=prompt
            )
            if response.text:
                return response.text
            else:
                return "Error: Empty response from Gemini"
        except Exception as e:
            return f"Gemini Error: {e}"

    def _mock_generate(self, prompt: str) -> str:
        return f"Mock Plan for: {prompt[:30]}... \n1. Analyze request\n2. Execute tool\n3. Verify result"

    async def _ollama_generate(self, prompt: str, system_prompt: str) -> str:
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": os.getenv("OLLAMA_MODEL", "llama3"),
                    "prompt": prompt,
                    "system": system_prompt,
                    "stream": False
                }
                async with session.post(f"{self.ollama_host}/api/generate", json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("response", "")
                    else:
                        return f"Ollama Error: {resp.status}"
        except Exception as e:
            return f"Ollama Connection Failed: {str(e)}"

