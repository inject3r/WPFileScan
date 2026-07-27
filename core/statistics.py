# ============================================================================
# core/statistics.py
# ============================================================================
"""
Statistics and state management for WPFileScan
"""

import time
import threading
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class ScanStatistics:
    """Container for scan statistics with thread-safe updates"""
    total_requests: int = 0
    success_count: int = 0
    not_found_count: int = 0
    error_count: int = 0
    other_status_count: int = 0
    found_urls: List[str] = field(default_factory=list)
    failed_urls: List[str] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    lock: threading.Lock = field(default_factory=threading.Lock)
    
    def to_dict(self) -> Dict[str, Any]:
        with self.lock:
            return {
                'total_requests': self.total_requests,
                'success_count': self.success_count,
                'not_found_count': self.not_found_count,
                'error_count': self.error_count,
                'other_status_count': self.other_status_count,
                'found_urls': self.found_urls,
                'failed_urls': self.failed_urls
            }
    
    def increment_total(self):
        with self.lock:
            self.total_requests += 1
    
    def increment_success(self, url: str):
        with self.lock:
            self.success_count += 1
            self.found_urls.append(url)
    
    def increment_not_found(self, url: str):
        with self.lock:
            self.not_found_count += 1
            self.failed_urls.append(url)
    
    def increment_error(self, url: str):
        with self.lock:
            self.error_count += 1
            self.failed_urls.append(url)
    
    def increment_other(self, url: str):
        with self.lock:
            self.other_status_count += 1
            self.failed_urls.append(url)


@dataclass
class ScanState:
    """Container for complete scan state for resume functionality"""
    name: str = ""
    name_variations: List[str] = field(default_factory=list)
    use_all_variations: bool = False
    statistics: ScanStatistics = field(default_factory=ScanStatistics)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'name_variations': self.name_variations,
            'use_all_variations': self.use_all_variations,
            'statistics': self.statistics.to_dict(),
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScanState':
        stats = ScanStatistics()
        stats_data = data.get('statistics', {})
        stats.total_requests = stats_data.get('total_requests', 0)
        stats.success_count = stats_data.get('success_count', 0)
        stats.not_found_count = stats_data.get('not_found_count', 0)
        stats.error_count = stats_data.get('error_count', 0)
        stats.other_status_count = stats_data.get('other_status_count', 0)
        stats.found_urls = stats_data.get('found_urls', [])
        stats.failed_urls = stats_data.get('failed_urls', [])
        
        return cls(
            name=data.get('name', ''),
            name_variations=data.get('name_variations', []),
            use_all_variations=data.get('use_all_variations', False),
            statistics=stats,
            timestamp=data.get('timestamp', datetime.now().isoformat())
        )