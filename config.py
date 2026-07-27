# ============================================================================
# config.py
# ============================================================================
"""
Configuration and constants for WPFileScan
"""

import re

# Version
VERSION = "1.0.0"


class Colors:
    """Centralized color theme for the entire application"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    SUCCESS = GREEN
    ERROR = RED
    WARNING = YELLOW
    INFO = CYAN
    HIGHLIGHT = BLUE
    HEADER_COLOR = PURPLE
    RESULT = GREEN
    
    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        return f"{color}{text}{cls.RESET}"
    
    @classmethod
    def colorize_parts(cls, *parts) -> str:
        result = []
        for text, color in parts:
            if color:
                result.append(cls.colorize(text, color))
            else:
                result.append(text)
        return ''.join(result)
    
    @classmethod
    def strip_colors(cls, text: str) -> str:
        """Remove ANSI color codes from text"""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)