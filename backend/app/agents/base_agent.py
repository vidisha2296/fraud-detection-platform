import asyncio
import time
from typing import Any, Callable, Dict, List, Optional, TypeVar
from pydantic import BaseModel
from tenacity import (
    retry, stop_after_attempt, wait_exponential, 
    retry_if_exception_type, AsyncRetrying, RetryError
)
from app.core.circuit_breaker import CircuitBreaker
from app.core.security import sanitize_input, detect_prompt_injection
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class AgentResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}

class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=30,
            name=name
        )
    
    async def execute_with_guardrails(
        self,
        tool_func: Callable[..., Any],
        *args,
        **kwargs
    ) -> AgentResponse:
        """Execute tool with all guardrails applied"""
        
        # Circuit breaker check
        if not self.circuit_breaker.allow_request():
            logger.warning(f"Circuit breaker open for {self.name}")
            return AgentResponse(
                success=False,
                error=f"Circuit breaker open for {self.name}"
            )
        
        # Input sanitization
        sanitized_args = [sanitize_input(arg) for arg in args]
        sanitized_kwargs = {k: sanitize_input(v) for k, v in kwargs.items()}
        
        # Prompt injection detection
        for i, arg in enumerate(sanitized_args + list(sanitized_kwargs.values())):
            if isinstance(arg, str) and detect_prompt_injection(arg):
                logger.warning(f"Prompt injection detected in argument {i}")
                return AgentResponse(
                    success=False,
                    error="Prompt injection detected in input"
                )
        
        try:
            # Execute with timeout and retries
            result = await self._execute_with_retries(
                tool_func, *sanitized_args, **sanitized_kwargs
            )
            self.circuit_breaker.on_success()
            return AgentResponse(success=True, data=result)
            
        except Exception as e:
            logger.error(f"Agent {self.name} execution failed: {str(e)}")
            self.circuit_breaker.on_failure()
            return AgentResponse(success=False, error=str(e))
    
    async def _execute_with_retries(
        self,
        tool_func: Callable[..., Any],
        *args,
        **kwargs
    ) -> Any:
        """Execute tool with retries and timeout using AsyncRetrying"""
        retryer = AsyncRetrying(
            stop=stop_after_attempt(2),
            wait=wait_exponential(multiplier=1, min=0.15, max=0.4),
            retry=retry_if_exception_type((TimeoutError, ConnectionError, asyncio.TimeoutError)),
            reraise=True
        )
        
        async for attempt in retryer:
            with attempt:
                try:
                    # Execute with timeout
                    return await asyncio.wait_for(
                        tool_func(*args, **kwargs),
                        timeout=1.0  # 1 second timeout per tool
                    )
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout in attempt {attempt.retry_state.attempt_number}")
                    raise TimeoutError(f"Operation timed out after 1 second")
                except Exception as e:
                    logger.error(f"Attempt {attempt.retry_state.attempt_number} failed: {str(e)}")
                    raise
    
    # Alternative simpler retry implementation without tenacity
    async def _execute_with_retries_simple(
        self,
        tool_func: Callable[..., Any],
        *args,
        **kwargs
    ) -> Any:
        """Simple retry implementation without external dependencies"""
        max_attempts = 2
        base_delay = 0.15
        max_delay = 0.4
        
        last_exception = None
        
        for attempt in range(1, max_attempts + 1):
            try:
                return await asyncio.wait_for(
                    tool_func(*args, **kwargs),
                    timeout=1.0
                )
            except (TimeoutError, ConnectionError, asyncio.TimeoutError) as e:
                last_exception = e
                logger.warning(f"Attempt {attempt} failed: {str(e)}")
                
                if attempt == max_attempts:
                    break
                
                # Exponential backoff with jitter
                delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                jitter = delay * 0.1
                actual_delay = delay + (jitter * (time.time() % 1))
                
                await asyncio.sleep(actual_delay)
            except Exception as e:
                # Don't retry on other exceptions
                raise e
        
        raise last_exception or TimeoutError("All retry attempts failed")