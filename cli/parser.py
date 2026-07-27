# ============================================================================
# cli/parser.py
# ============================================================================
"""
Command line argument parser for WPFileScan
"""

import argparse


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='WPFileScan - WordPress Brute Force File Finder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic scan with required parameters
  python main.py -u https://example.com -path /wp-content/uploads -n backup -ext .zip,.rar -sy 2022 -ey 2026
  
  # Scan with verbose output
  python main.py -u https://example.com -path /wp-content/uploads -n backup -ext .zip -sy 2022 -ey 2026 -v
  
  # Scan with specific month and versions
  python main.py -u https://example.com -path /wp-content/uploads -n backup -ext .zip -sy 2022 -ey 2026 --month 7 --versions "1.0.1,1.3.3"
  
  # Download found files
  python main.py -u https://example.com -path /wp-content/uploads -n backup -ext .zip -sy 2022 -ey 2026 --enable-download
  
  # Disable retry
  python main.py -u https://example.com -path /wp-content/uploads -n backup -ext .zip -sy 2022 -ey 2026 --disable-retry
        """
    )
    
    parser.add_argument(
        '-u', '--url',
        type=str,
        required=True,
        help='Target URL (e.g., https://example.com)'
    )
    
    parser.add_argument(
        '-path', '--path',
        type=str,
        required=True,
        help='Upload path (e.g., /wp-content/uploads)'
    )
    
    parser.add_argument(
        '-n', '--name',
        type=str,
        required=True,
        help='Base name to scan (e.g., "backup")'
    )
    
    parser.add_argument(
        '-ext', '--extensions',
        type=str,
        required=True,
        help='File extensions to search (comma separated, e.g., .zip,.rar,.7z)'
    )
    
    parser.add_argument(
        '-sy', '--start-year',
        type=int,
        required=True,
        help='Start year for scanning'
    )
    
    parser.add_argument(
        '-ey', '--end-year',
        type=int,
        required=True,
        help='End year for scanning'
    )
    
    parser.add_argument(
        '-a', '--all-variations',
        action='store_true',
        help='Use all name variations (priority order)'
    )
    
    parser.add_argument(
        '-r', '--resume',
        action='store_true',
        help='Resume from last saved progress'
    )
    
    parser.add_argument(
        '--month',
        type=int,
        action='append',
        help='Specific month to scan (can be used multiple times, default: all months)'
    )
    
    parser.add_argument(
        '--versions',
        type=str,
        help='Version numbers to check (comma separated, e.g., "1.0.1,1.3.3,1.0.0")'
    )
    
    parser.add_argument(
        '--enable-download',
        action='store_true',
        help='Download found files'
    )
    
    parser.add_argument(
        '--download-path',
        type=str,
        default='downloads',
        help='Download directory path (default: downloads)'
    )
    
    parser.add_argument(
        '--concurrent-requests',
        type=int,
        default=20,
        help='Number of concurrent requests (default: 20)'
    )
    
    parser.add_argument(
        '--delay-min',
        type=float,
        default=0.01,
        help='Minimum delay between requests in seconds (default: 0.01)'
    )
    
    parser.add_argument(
        '--delay-max',
        type=float,
        default=0.1,
        help='Maximum delay between requests in seconds (default: 0.1)'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=15,
        help='Request timeout in seconds (default: 15)'
    )
    
    parser.add_argument(
        '--download-timeout',
        type=int,
        default=30,
        help='Download timeout in seconds (default: 30)'
    )
    
    parser.add_argument(
        '--code',
        type=int,
        default=200,
        help='HTTP status code indicating file found (default: 200)'
    )
    
    parser.add_argument(
        '--disable-retry',
        action='store_true',
        help='Disable retry on timeout/connection errors'
    )
    
    parser.add_argument(
        '--retry-count',
        type=int,
        default=5,
        help='Number of retry attempts (default: 5)'
    )
    
    parser.add_argument(
        '--http1.0',
        action='store_true',
        help='Use HTTP version 1.0 (old)'
    )
    
    parser.add_argument(
        '--http2',
        action='store_true',
        help='Use HTTP version 2 (experimental)'
    )
    
    parser.add_argument(
        '--mobile',
        action='store_true',
        help='Imitate smartphone through HTTP User-Agent header'
    )
    
    parser.add_argument(
        '--random-agent',
        action='store_true',
        help='Use randomly selected HTTP User-Agent header value'
    )
    
    parser.add_argument(
        '-A', '--user-agent',
        type=str,
        help='HTTP User-Agent header value'
    )
    
    parser.add_argument(
        '-H', '--header',
        type=str,
        action='append',
        help='Extra header (e.g., "X-Forwarded-For: 127.0.0.1")'
    )
    
    parser.add_argument(
        '--cookie',
        type=str,
        help='HTTP Cookie header value (e.g. "PHPSESSID=a8d127e..")'
    )
    
    parser.add_argument(
        '--drop-set-cookie',
        action='store_true',
        help='Ignore Set-Cookie header from response'
    )
    
    parser.add_argument(
        '--force-ssl',
        action='store_true',
        help='Force usage of SSL/HTTPS'
    )
    
    parser.add_argument(
        '--proxy',
        type=str,
        help='Use a proxy to connect to the target URL (e.g., socks5://127.0.0.1:1080)'
    )
    
    parser.add_argument(
        '--proxy-cred',
        type=str,
        help='Proxy authentication credentials (name:password)'
    )
    
    parser.add_argument(
        '--tor',
        action='store_true',
        help='Use Tor anonymity network'
    )
    
    parser.add_argument(
        '--tor-port',
        type=int,
        default=9050,
        help='Set Tor proxy port other than default (default: 9050)'
    )
    
    parser.add_argument(
        '--check-tor',
        action='store_true',
        help='Check to see if Tor is used properly'
    )
    
    parser.add_argument(
        '--no-logging',
        action='store_true',
        help='Disable logging to a file'
    )
    
    parser.add_argument(
        '--no-truncate',
        action='store_true',
        help='Disable console output truncation'
    )
    
    parser.add_argument(
        '--alert',
        type=str,
        help='Run host OS command(s) when file is found (use {url} and {file} as placeholders)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()