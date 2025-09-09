import time
from typing import Optional

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 30, name: str = ""):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        self.failures = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half-open
    
    def allow_request(self) -> bool:
        if self.state == "open":
            if self.last_failure_time is None:
                return False
            # Check if recovery timeout has passed
            if (time.time() - self.last_failure_time) > self.recovery_timeout:
                self.state = "half-open"
                return True
            return False
        return True
    
    def on_success(self):
        # Reset on any successful request
        self.state = "closed"
        self.failures = 0
        self.last_failure_time = None
    
    def on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.failures >= self.failure_threshold:
            self.state = "open"
    
    def get_status(self) -> dict:
        return {
            "name": self.name,
            "state": self.state,
            "failures": self.failures,
            "last_failure": self.last_failure_time,
        }
