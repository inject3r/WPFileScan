# ============================================================================
# utils/network.py
# ============================================================================
"""
Network utilities for WPFileScan
"""

from typing import Optional, Dict

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def create_session(args) -> requests.Session:
    """Create a requests session with connection pooling"""
    session = requests.Session()
    
    if not args.disable_retry and args.retry_count > 0:
        retry_strategy = Retry(
            total=args.retry_count,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_redirect=False,
            raise_on_status=False
        )
        
        adapter = HTTPAdapter(
            pool_connections=args.concurrent_requests or 20,
            pool_maxsize=args.concurrent_requests or 20,
            max_retries=retry_strategy,
            pool_block=False
        )
    else:
        adapter = HTTPAdapter(
            pool_connections=args.concurrent_requests or 20,
            pool_maxsize=args.concurrent_requests or 20,
            pool_block=False
        )
    
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    session.headers.update({
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache'
    })
    
    return session


def get_proxy(args) -> Optional[Dict[str, str]]:
    """Get proxy configuration based on arguments"""
    if args.proxy:
        return {'http': args.proxy, 'https': args.proxy}
    if args.tor:
        port = args.tor_port or 9050
        return {'http': f'socks5://127.0.0.1:{port}', 'https': f'socks5://127.0.0.1:{port}'}
    return None