# ============================================================================
# utils/logger.py
# ============================================================================
"""
Logging utilities for WPFileScan
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

from config import Colors


def setup_logging(args, log_dir: Path) -> None:
    """Setup logging with colored console and plain file output"""
    logger = logging.getLogger("WPFileScan")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(console_handler)
    
    # File handler without colors
    if not args.no_logging:
        log_file = log_dir / f"wp_filescan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG if args.verbose else logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        logger.addHandler(file_handler)


def log_message(logger, level: str, message: str, colored: bool = True) -> None:
    """Log message with optional colors for console"""
    if colored:
        getattr(logger, level)(message)
    else:
        clean_msg = Colors.strip_colors(message)
        getattr(logger, level)(clean_msg)