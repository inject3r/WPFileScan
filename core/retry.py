# ============================================================================
# core/retry.py
# ============================================================================
"""
Custom retry logic for WPFileScan
"""

import random


class RetryManager:
    """Custom retry manager for handling failed requests"""
    
    def __init__(self, max_retries: int = 5, delay_min: float = 0.05, delay_max: float = 3.0):
        self.max_retries = max_retries
        self.delay_min = delay_min
        self.delay_max = delay_max
    
    def should_retry(self, attempt: int) -> bool:
        return attempt < self.max_retries
    
    def get_delay(self) -> float:
        return random.uniform(self.delay_min, self.delay_max)