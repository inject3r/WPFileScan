# ============================================================================
# main.py
# ============================================================================
#!/usr/bin/env python3
"""
WPFileScan - WordPress Brute Force File Finder
A professional tool for discovering WordPress uploaded files through intelligent
brute force techniques with name variations and date-based scanning.

Author: Professional Developer
Version: 1.0.0
License: MIT
"""

import sys
import os
import logging
import signal

from config import Colors
from cli.parser import parse_arguments
from ui.banner import print_banner
from core.scanner import WPFileScanner


def main() -> None:
    try:
        if len(sys.argv) == 1:
            print_banner()
            print(Colors.colorize("[!] No arguments provided.", Colors.WARNING))
            print(Colors.colorize("[i] Use -h or --help for usage information.", Colors.INFO))
            sys.exit(0)
        
        args = parse_arguments()
        print_banner()
        
        if args.tor and args.check_tor:
            try:
                import socks
                import socket
                sock = socks.socksocket()
                sock.set_proxy(socks.SOCKS5, "127.0.0.1", args.tor_port)
                sock.settimeout(5)
                sock.connect(("check.torproject.org", 80))
                sock.send(b"GET / HTTP/1.0\r\nHost: check.torproject.org\r\n\r\n")
                response = sock.recv(1024)
                if b"Congratulations" in response:
                    print(Colors.colorize("[+] Tor is working properly", Colors.SUCCESS))
                else:
                    print(Colors.colorize("[!] Tor might not be working properly", Colors.WARNING))
                sock.close()
            except Exception as e:
                print(Colors.colorize(f"[!] Tor check failed: {e}", Colors.ERROR))
                sys.exit(1)
        
        scanner = WPFileScanner(args)
        
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        scanner.scan(
            name=args.name,
            use_all_variations=args.all_variations,
            resume=args.resume
        )
        
    except KeyboardInterrupt:
        print(Colors.colorize("\n[!] Interrupted by user", Colors.WARNING))
        sys.exit(0)
    except Exception as e:
        print(Colors.colorize(f"\n[!] Critical error: {e}", Colors.ERROR))
        sys.exit(1)


if __name__ == "__main__":
    main()