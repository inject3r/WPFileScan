# WPFileScan ![](https://img.shields.io/badge/version-1.0.0-blue.svg)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-yellow.svg)](https://www.python.org/) [![License](https://img.shields.io/badge/license-MIT-red.svg)](https://github.com/inject3r/WPFileScan/blob/master/LICENSE) [![GitHub](https://img.shields.io/badge/github-inject3r/WPFileScan-blue.svg)](https://github.com/inject3r/WPFileScan) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/inject3r/WPFileScan/pulls)

WPFileScan is an open source penetration testing tool that automates the process of discovering WordPress uploaded files through intelligent brute force techniques. It comes with a powerful name variation engine, support for multiple file extensions, concurrent request handling, resume functionality, and a broad range of features including proxy support, Tor anonymity, custom headers, and file download capabilities.

## Installation

You can download the latest tarball by clicking [here](https://github.com/inject3r/WPFileScan/tarball/master) or latest zipball by clicking [here](https://github.com/inject3r/WPFileScan/zipball/master).

Preferably, you can download WPFileScan by cloning the [Git](https://github.com/inject3r/WPFileScan) repository:

```bash
git clone --depth 1 https://github.com/inject3r/WPFileScan.git
cd WPFileScan
pip install -r requirements.txt
```

WPFileScan works out of the box with [Python](https://www.python.org/download/) version **3.8+** on any platform.

## Usage

To get a list of basic options and switches use:

```bash
python main.py -h
```

To get a list of all options and switches use:

```bash
python main.py -hh
```

### Basic Scan

```bash
python main.py -u https://example.com -path /wp-content/uploads -n backup -ext .zip,.rar -sy 2022 -ey 2026
```

### Scan with Specific Months

```bash
python main.py -u https://example.com -path /wp-content/uploads -n backup -ext .zip -sy 2022 -ey 2026 --month 7 --month 12
```

### Scan with Version Numbers

```bash
python main.py -u https://example.com -path /wp-content/uploads -n backup -ext .zip -sy 2022 -ey 2026 --versions "1.0.1,1.3.3,1.0.0"
```

### Download Found Files

```bash
python main.py -u https://example.com -path /wp-content/uploads -n backup -ext .zip -sy 2022 -ey 2026 --enable-download
```

### Resume from Progress

```bash
python main.py -u https://example.com -path /wp-content/uploads -n backup -ext .zip -sy 2022 -ey 2026 -r
```

### Using Proxy

```bash
python main.py -u https://example.com -path /wp-content/uploads -n backup -ext .zip -sy 2022 -ey 2026 --proxy socks5://127.0.0.1:1080
```

### Using Tor

```bash
python main.py -u https://example.com -path /wp-content/uploads -n backup -ext .zip -sy 2022 -ey 2026 --tor
```

## Docker

```bash
git clone https://github.com/inject3r/WPFileScan.git
cd WPFileScan
docker build -t wpfilescan .
docker run --rm wpfilescan -u https://example.com -path /wp-content/uploads -n backup -ext .zip -sy 2022 -ey 2026
```

## Features

- Brute force scanning of WordPress uploads directory
- Support for multiple file extensions (.zip, .rar, .7z, .tar.gz)
- Name variations with priority ordering (simple names, numbers, versions)
- Date-based scanning (year and month)
- Concurrent requests with configurable threads
- Resume functionality with progress saving
- File download capability
- Proxy support (HTTP, HTTPS, SOCKS5)
- Tor anonymity network support
- Custom headers and cookies
- Random User-Agent rotation
- Mobile User-Agent emulation
- Verbose logging
- Colored console output
- Log files without ANSI colors for clean reading
- Organized logs per domain

## Name Variation Priority

The tool generates name variations in the following priority order:

1. **Simple names** - No numbers, no versions (e.g., `backup`, `Backup`, `BACKUP`)
2. **Names with numbers** - 1-10 in various formats (e.g., `backup-1`, `backup1`, `backup (1)`)
3. **Names with versions** - Version numbers from config (e.g., `backup-1.0.1`, `backup1.0.1`)
4. **Combined** - Version + number (e.g., `backup-1.0.1-1`, `backup1.0.1-1`)

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/inject3r/WPFileScan/blob/master/LICENSE) file for details.

## Disclaimer

This tool is for educational and authorized testing purposes only. Use responsibly and only on systems you have permission to test. The authors are not responsible for any misuse or damage caused by this tool.
