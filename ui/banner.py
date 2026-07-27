from config import Colors, VERSION


def print_banner() -> None:
    
    banner_text = [
        r"▗▖ ▗▖▗▄▄▖ ▗▄▄▄▖▗▄▄▄▖▗▖   ▗▄▄▄▖ ▗▄▄▖ ▗▄▄▖ ▗▄▖ ▗▖  ▗▖",
        r"▐▌ ▐▌▐▌ ▐▌▐▌     █  ▐▌   ▐▌   ▐▌   ▐▌   ▐▌ ▐▌▐▛▚▖▐▌",
        r"▐▌ ▐▌▐▛▀▘ ▐▛▀▀▘  █  ▐▌   ▐▛▀▀▘ ▝▀▚▖▐▌   ▐▛▀▜▌▐▌ ▝▜▌",
        r"▐▙█▟▌▐▌   ▐▌   ▗▄█▄▖▐▙▄▄▖▐▙▄▄▖▗▄▄▞▘▝▚▄▄▖▐▌ ▐▌▐▌  ▐",
    ]
    
    colors = [Colors.CYAN, Colors.BLUE, Colors.PURPLE, Colors.YELLOW]
    
    print()
    for i, line in enumerate(banner_text):
        color = colors[i % len(colors)]
        print(Colors.colorize(line, color))
    
    version = (f"{Colors.BOLD}{Colors.colorize('WPFileScan', Colors.CYAN)}{Colors.RESET} "
               f"{Colors.BOLD}{Colors.colorize(f'v{VERSION}', Colors.YELLOW)}{Colors.RESET} "
               f"{Colors.colorize('WordPress Brute Force File Finder', Colors.GREEN)}")
    
    separator = f"     >{Colors.colorize('+' * 40, Colors.CYAN)}<     "
    
    print(separator)
    print(version)
    
    repo_link = "https://github.com/inject3r/WPFileScan"
    print(Colors.colorize(f"GitHub: {repo_link}", Colors.BLUE))
    print()