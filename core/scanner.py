# ============================================================================
# core/scanner.py
# ============================================================================
"""
Main scanner class for WPFileScan
"""

import json
import os
import sys
import time
import random
import signal
import argparse
import logging
import subprocess
import re
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import Colors, VERSION
from core.statistics import ScanStatistics, ScanState
from core.retry import RetryManager
from utils.logger import setup_logging, log_message
from utils.helpers import get_user_agent, generate_name_variations, build_headers
from utils.network import create_session, get_proxy


class WPFileScanner:
    """Main scanner class for WordPress file discovery using requests"""
    
    PROGRESS_FILE = "progress.json"
    _shutdown_flag = False
    
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.state = ScanState()
        self._running = True
        self._log_dir = self._get_log_dir()
        self._setup_logging()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Parse versions
        self.versions = []
        if args.versions:
            self.versions = [v.strip() for v in args.versions.split(',') if v.strip()]
        
        # Retry manager
        retry_count = args.retry_count if not args.disable_retry else 0
        self.retry_manager = RetryManager(
            max_retries=retry_count,
            delay_min=0.05,
            delay_max=3.0
        )
        
        # Session with connection pooling
        self.session = create_session(args)
        
        # Thread pool for concurrent requests
        self._executor = ThreadPoolExecutor(max_workers=args.concurrent_requests or 20)
        self._executor_futures = []
        
        # Flag for interrupt handling
        self._interrupted = False
    
    def _get_log_dir(self) -> Path:
        parsed = urlparse(self.args.url)
        domain = parsed.netloc or parsed.path
        domain = domain.split(':')[0]
        domain = re.sub(r'[^a-zA-Z0-9\-\.]', '_', domain)
        log_dir = Path("logs") / domain
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
    
    def _setup_logging(self) -> None:
        setup_logging(self.args, self._log_dir)
        self.logger = logging.getLogger("WPFileScan")
    
    def _log_message(self, level: str, message: str, colored: bool = True) -> None:
        log_message(self.logger, level, message, colored)
    
    def _signal_handler(self, signum: int, frame: Any) -> None:
        if self._interrupted:
            os._exit(1)
        
        self._interrupted = True
        self._log_message('warning', Colors.colorize("Interrupt received. Saving progress...", Colors.WARNING))
        self._running = False
        self._shutdown_flag = True
        
        for future in self._executor_futures:
            future.cancel()
        
        self._save_progress()
        self._log_message('info', Colors.colorize("Progress saved. Exiting...", Colors.INFO))
        
        self._executor.shutdown(wait=False)
        os._exit(0)
    
    def _save_progress(self) -> None:
        try:
            self.state.timestamp = datetime.now().isoformat()
            progress_file = self._log_dir / self.PROGRESS_FILE
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.state.to_dict(), f, indent=4, ensure_ascii=False)
            self._log_message('info', Colors.colorize(f"Progress saved to: {progress_file}", Colors.INFO))
        except Exception as e:
            self._log_message('error', Colors.colorize(f"Error saving progress: {e}", Colors.ERROR))
    
    def _load_progress(self) -> bool:
        progress_file = self._log_dir / self.PROGRESS_FILE
        if not progress_file.exists():
            return False
        
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.state = ScanState.from_dict(data)
            self._log_message('info', Colors.colorize(f"Progress loaded from: {progress_file}", Colors.INFO))
            self._log_message('info', Colors.colorize(
                f"Previous stats: Total={self.state.statistics.total_requests}, "
                f"Found={self.state.statistics.success_count}, "
                f"404={self.state.statistics.not_found_count}", Colors.INFO
            ))
            return True
        except Exception as e:
            self._log_message('error', Colors.colorize(f"Error loading progress: {e}", Colors.ERROR))
            return False
    
    def _ensure_download_directory(self) -> bool:
        download_path = self.args.download_path or "downloads"
        try:
            Path(download_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            self._log_message('error', Colors.colorize(f"Could not create download directory: {e}", Colors.ERROR))
            return False
    
    def _check_url_with_retry(self, url: str, year: int, month_str: str, 
                               name_var: str, extension: str) -> Optional[bool]:
        attempt = 0
        
        while True:
            if not self._running or self._shutdown_flag:
                return None
            
            result = self._check_url_once(url, year, month_str, name_var, extension)
            
            if result is not None:
                return result
            
            if self.args.disable_retry or not self.retry_manager.should_retry(attempt):
                return False
            
            attempt += 1
            delay = self.retry_manager.get_delay()
            if self.args.verbose:
                self._log_message('debug', Colors.colorize(
                    f"Retry {attempt}/{self.retry_manager.max_retries} for {url} after {delay:.2f}s", 
                    Colors.INFO
                ))
            time.sleep(delay)
    
    def _check_url_once(self, url: str, year: int, month_str: str, 
                         name_var: str, extension: str) -> Optional[bool]:
        try:
            delay = random.uniform(
                self.args.delay_min or 0.01,
                self.args.delay_max or 0.1
            )
            time.sleep(delay)
            
            headers = build_headers(self.args)
            proxies = get_proxy(self.args)
            
            full_url = self.args.url.rstrip('/') + url
            if self.args.verbose:
                self._log_message('debug', Colors.colorize(f"Checking: {full_url}", Colors.INFO))
            
            try:
                response = self.session.get(
                    full_url,
                    headers=headers,
                    proxies=proxies,
                    timeout=self.args.timeout or 15,
                    stream=True,
                    allow_redirects=True
                )
                
                self.state.statistics.increment_total()
                
                if response.status_code == self.args.code:
                    self.state.statistics.increment_success(url)
                    self._handle_found_file(url, year, month_str, name_var, extension, headers, response)
                    response.close()
                    return True
                elif response.status_code == 404:
                    self.state.statistics.increment_not_found(url)
                    if self.args.verbose:
                        self._log_message('debug', Colors.colorize(f"404: {full_url}", Colors.INFO))
                    response.close()
                    return False
                elif response.status_code >= 500:
                    self.state.statistics.increment_error(url)
                    self._log_message('error', 
                        Colors.colorize_parts(
                            ("Server error ", Colors.ERROR),
                            (str(response.status_code), Colors.RED),
                            (" - ", None),
                            (url, Colors.YELLOW)
                        )
                    )
                    response.close()
                    return False
                else:
                    self.state.statistics.increment_other(url)
                    self._log_message('warning',
                        Colors.colorize_parts(
                            ("Status ", Colors.WARNING),
                            (str(response.status_code), Colors.RED),
                            (" - ", None),
                            (url, Colors.YELLOW)
                        )
                    )
                    response.close()
                    return False
                
            except requests.exceptions.Timeout as e:
                if self.args.verbose:
                    self._log_message('debug', Colors.colorize(f"Timeout: {full_url} - {str(e)[:50]}", Colors.WARNING))
                return None
                
            except requests.exceptions.ConnectionError as e:
                if self.args.verbose:
                    self._log_message('debug', Colors.colorize(f"Connection error: {full_url} - {str(e)[:50]}", Colors.WARNING))
                return None
                
            except requests.exceptions.RequestException as e:
                self.state.statistics.increment_error(url)
                self._log_message('error',
                    Colors.colorize_parts(
                        ("Request error", Colors.ERROR),
                        (f": {str(e)[:50]}", Colors.RED),
                        (" - ", None),
                        (url, Colors.YELLOW)
                    )
                )
                return False
                
            except Exception as e:
                self.state.statistics.increment_error(url)
                self._log_message('error',
                    Colors.colorize_parts(
                        ("Unexpected error", Colors.ERROR),
                        (f": {str(e)[:50]}", Colors.RED),
                        (" - ", None),
                        (url, Colors.YELLOW)
                    )
                )
                return False
                
        except Exception as e:
            self.state.statistics.increment_error(url)
            self._log_message('error',
                Colors.colorize_parts(
                    ("Critical error", Colors.ERROR),
                    (f": {str(e)[:50]}", Colors.RED),
                    (" - ", None),
                    (url, Colors.YELLOW)
                )
            )
            return False
    
    def _handle_found_file(self, url: str, year: int, month_str: str,
                          name_var: str, extension: str, headers: Dict[str, str],
                          response: requests.Response) -> None:
        found_msg = Colors.colorize_parts(
            ("[+] FOUND", Colors.SUCCESS),
            (": ", None),
            (url, Colors.GREEN)
        )
        print(found_msg)
        
        self._log_message('info', f"[+] FOUND: {url}", colored=False)
        
        if self.args.alert:
            try:
                cmd = self.args.alert.replace('{url}', url).replace('{file}', f"{name_var}{extension}")
                subprocess.Popen(cmd, shell=True)
                self._log_message('info', Colors.colorize(f"Alert executed: {cmd}", Colors.INFO))
            except Exception as e:
                self._log_message('error', Colors.colorize(f"Alert failed: {e}", Colors.ERROR))
        
        if self.args.enable_download:
            try:
                download_path = self.args.download_path or "downloads"
                Path(download_path).mkdir(parents=True, exist_ok=True)
                
                filename = f"{download_path}/{name_var}_{year}_{month_str}{extension}"
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                if percent % 10 < 1:
                                    print(Colors.colorize(
                                        f"   Downloading: {percent:.1f}% ({downloaded}/{total_size} bytes)",
                                        Colors.SUCCESS
                                    ))
                
                self._log_message('info', Colors.colorize(
                    f"   [+] Downloaded: {filename} ({total_size/1024:.1f} KB)",
                    Colors.SUCCESS
                ))
                    
            except Exception as e:
                self._log_message('error', Colors.colorize(
                    f"   [!] Download failed: {str(e)[:50]}",
                    Colors.ERROR
                ))
        else:
            self._log_message('info', Colors.colorize("   [i] Download disabled", Colors.INFO))
    
    def _print_stats(self) -> None:
        elapsed = time.time() - self.state.statistics.start_time
        stats = self.state.statistics
        
        stats_line = (
            f"[i] Stats: Elapsed={elapsed:.1f}s | "
            f"Total={stats.total_requests} | "
            f"Found={stats.success_count} | "
            f"404={stats.not_found_count} | "
            f"Errors={stats.error_count}"
        )
        
        if not self.args.no_truncate:
            sys.stdout.write(f"\r{Colors.colorize(stats_line, Colors.INFO)}\n")
            sys.stdout.flush()
        else:
            self._log_message('info', Colors.colorize(stats_line, Colors.INFO))

    def _build_task_list(self) -> List[Tuple[str, int, str, str, str]]:
        upload_path = self.args.path.strip('/')
        extensions = self.args.extensions.split(',') if self.args.extensions else []
        extensions = [ext.strip() for ext in extensions if ext.strip()]
        
        if not extensions:
            extensions = ['.zip']
        
        start_year = self.args.start_year
        end_year = self.args.end_year
        
        months = self.args.month if self.args.month else list(range(1, 13))
        if isinstance(months, int):
            months = [months]
        
        names_to_use = self.state.name_variations if self.state.use_all_variations else [self.state.name]
        
        tasks = []
        for name_var in names_to_use:
            for year in range(start_year, end_year + 1):
                for month in months:
                    month_str = f"{month:02d}"
                    for extension in extensions:
                        url = f"/{upload_path}/{year}/{month_str}/{name_var}{extension}"
                        tasks.append((url, year, month_str, name_var, extension))
        
        return tasks
    
    def scan(self, name: str, use_all_variations: bool = False, 
             resume: bool = False) -> None:
        try:
            self.state.name = name
            self.state.use_all_variations = use_all_variations
            
            if resume:
                if self._load_progress():
                    self._log_message('info', Colors.colorize(f"Resuming scan with name: {name}", Colors.INFO))
                else:
                    self._log_message('warning', Colors.colorize("No progress file found. Starting fresh.", Colors.WARNING))
            
            if not self.state.name_variations:
                self._log_message('info', Colors.colorize("Generating name variations...", Colors.INFO))
                self.state.name_variations = generate_name_variations(name, self.versions)
                self._log_message('info', Colors.colorize(f"Generated {len(self.state.name_variations)} variations", Colors.INFO))
            
            if self.args.enable_download:
                if not self._ensure_download_directory():
                    self._log_message('error', Colors.colorize("Cannot create download directory. Disabling download...", Colors.ERROR))
                    self.args.enable_download = False
            
            tasks = self._build_task_list()
            total_tasks = len(tasks)
            
            self._log_message('info', Colors.colorize(f"[i] Total tasks to check: {total_tasks}", Colors.INFO))
            self._log_message('info', Colors.colorize(f"[i] Using {len(self.state.name_variations)} name variation(s)", Colors.INFO))
            self._log_message('info', Colors.colorize(f"[i] File extensions: {', '.join(self.args.extensions.split(',')) if self.args.extensions else ['.zip']}", Colors.INFO))
            self._log_message('info', Colors.colorize(f"[i] Download mode: {'ENABLED' if self.args.enable_download else 'DISABLED'}", Colors.INFO))
            self._log_message('info', Colors.colorize(f"[i] Concurrent requests: {self.args.concurrent_requests or 20}", Colors.INFO))
            self._log_message('info', Colors.colorize(f"[i] Retry count: {self.args.retry_count if not self.args.disable_retry else 0}", Colors.INFO))
            print(Colors.colorize("-" * 80, Colors.HIGHLIGHT))
            
            self.state.statistics.start_time = time.time()
            processed = 0
            
            with ThreadPoolExecutor(max_workers=self.args.concurrent_requests or 20) as executor:
                future_to_task = {}
                
                for url, year, month_str, name_var, extension in tasks:
                    if not self._running or self._shutdown_flag:
                        break
                    future = executor.submit(self._check_url_with_retry, url, year, month_str, name_var, extension)
                    future_to_task[future] = (url, year, month_str, name_var, extension)
                    self._executor_futures.append(future)
                
                for future in as_completed(future_to_task):
                    if not self._running or self._shutdown_flag:
                        break
                    processed += 1
                    if processed % 100 == 0:
                        self._save_progress()
                    self._print_stats()
            
            self._save_progress()
            self._print_final_stats()
            
            if self.state.statistics.found_urls:
                self._save_results()
                
        except Exception as e:
            self._log_message('error', Colors.colorize(f"Fatal error during scan: {e}", Colors.ERROR))
            self._save_progress()
            raise
        finally:
            self.session.close()
            self._executor.shutdown(wait=False)
    
    def _print_final_stats(self) -> None:
        stats = self.state.statistics
        elapsed = time.time() - stats.start_time
        
        print(Colors.colorize("\n" + "=" * 80, Colors.SUCCESS))
        print(Colors.colorize("[+] SCAN COMPLETED!", Colors.SUCCESS))
        print(Colors.colorize(f"[+] Total time: {elapsed:.2f} seconds", Colors.SUCCESS))
        print(Colors.colorize("[+] FINAL STATS:", Colors.SUCCESS))
        print(f"    Total checked: {stats.total_requests}")
        print(f"    Found: {Colors.colorize(str(stats.success_count), Colors.SUCCESS)}")
        print(f"    Not found: {stats.not_found_count}")
        print(f"    Errors: {Colors.colorize(str(stats.error_count), Colors.ERROR)}")
        print(f"    Other status: {stats.other_status_count}")
        print(Colors.colorize("=" * 80, Colors.SUCCESS))
    
    def _save_results(self) -> None:
        try:
            self._log_dir.mkdir(parents=True, exist_ok=True)
            
            results_file = self._log_dir / f"found_files_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(results_file, 'w', encoding='utf-8') as f:
                f.write("WPFileScan Results\n")
                f.write("==================\n")
                f.write(f"Scan date: {datetime.now().isoformat()}\n")
                f.write(f"Base name: {self.state.name}\n")
                f.write(f"Total found: {len(self.state.statistics.found_urls)}\n\n")
                for url in self.state.statistics.found_urls:
                    f.write(f"{url}\n")
            
            self._log_message('info', Colors.colorize(f"Results saved to: {results_file}", Colors.INFO))
        except Exception as e:
            self._log_message('error', Colors.colorize(f"Could not save results: {e}", Colors.ERROR))