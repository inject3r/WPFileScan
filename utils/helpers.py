# ============================================================================
# utils/helpers.py
# ============================================================================
"""
Helper functions for WPFileScan
"""

import random
from typing import List, Dict, Optional


def get_user_agent(args) -> str:
    """Get user agent based on arguments"""
    if args.mobile:
        return "Mozilla/5.0 (Linux; Android 10; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    if args.random_agent:
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        return random.choice(user_agents)
    if args.user_agent:
        return args.user_agent
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def generate_name_variations(base_name: str, versions: List[str]) -> List[str]:
    """Generate all possible variations of a name"""
    try:
        name = base_name.strip().lower()
        
        capitalizations = [
            name,
            name.capitalize(),
            name.upper(),
            name.title(),
            name[0].lower() + name[1:].upper(),
            name[0].upper() + name[1:-1].lower() + name[-1].upper(),
            ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(name)),
            ''.join(c.lower() if i % 2 == 0 else c.upper() for i, c in enumerate(name)),
        ]
        
        seen = set()
        unique_capitalizations = []
        for cap in capitalizations:
            if cap not in seen:
                seen.add(cap)
                unique_capitalizations.append(cap)
        
        variations = []
        seen_final = set()
        
        # Priority 1: Simple names
        for cap in unique_capitalizations:
            if cap not in seen_final:
                seen_final.add(cap)
                variations.append(cap)
        
        # Priority 2: Names with numbers (only if no versions provided)
        if not versions:
            number_formats = [lambda c, i: f"{c}-{i}", lambda c, i: f"{c}{i}", lambda c, i: f"{c} ({i})"]
            for cap in unique_capitalizations:
                for i in range(1, 11):
                    for fmt in number_formats:
                        var = fmt(cap, i)
                        if var not in seen_final:
                            seen_final.add(var)
                            variations.append(var)
        
        # Priority 3: Names with versions (if provided)
        if versions:
            version_formats = [lambda c, v: f"{c}-{v}", lambda c, v: f"{c}{v}"]
            for cap in unique_capitalizations:
                for version in versions:
                    for fmt in version_formats:
                        var = fmt(cap, version)
                        if var not in seen_final:
                            seen_final.add(var)
                            variations.append(var)
            
            # Priority 4: Combined (version + number)
            for cap in unique_capitalizations:
                for version in versions:
                    for i in range(1, 6):
                        for fmt in [f"{cap}-{version}-{i}", f"{cap}{version}-{i}"]:
                            if fmt not in seen_final:
                                seen_final.add(fmt)
                                variations.append(fmt)
        
        return variations
        
    except Exception as e:
        return [base_name]


def build_headers(args) -> Dict[str, str]:
    """Build HTTP headers for request"""
    headers = {
        'User-Agent': get_user_agent(args),
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache'
    }
    
    if args.cookie:
        headers['Cookie'] = args.cookie
    
    if args.header:
        for header in args.header:
            try:
                key, value = header.split(':', 1)
                headers[key.strip()] = value.strip()
            except ValueError:
                pass
    
    return headers