"""
╔══════════════════════════════════════════════════════════════════════╗
║                     SHARED PORTFOLIO CONFIGURATION                   ║
╚══════════════════════════════════════════════════════════════════════╝

Single source of truth for portfolio structure across all scripts:
- portfolio-risk-var-cvar.py
- institutional-risk-signal.py

Last updated: 2026-06-26
Dashboard source: fetch-ibkr-positions-dashboard.xlsx → Dashboard sheet
  col A = Ticker, col B = Category, col D = Cost USD, col E = Market USD
"""

# =============================================================================
# PORTFOLIO CATEGORY MAPPING (Dashboard categorization)
# =============================================================================
# Source of truth: fetch-ibkr-positions-dashboard.xlsx → Dashboard sheet
# Categories match Dashboard column B exactly.

SYMBOL_MAPPING = {
    'china':           ['82846'],
    'gold':            ['AEM', 'GSD', 'NEM'],
    'crypto':          ['BITO'],
    'us':              ['BRK B', 'CSNDX'],
    'dividend':        ['DHL', 'ES3'],
    'developed_ex_us': ['EXUS'],
    'theme':           ['GRDU', 'HY9H', 'INRA', 'SE'],
    'global':          ['SPYI', 'VWRA'],
    'emerging_markets':['XMME'],
    'cash':            [],  # USD cash — tracked as Dashboard 'Cash' row
}

# =============================================================================
# EXCHANGE MAPPING
# =============================================================================
# IBKR Exchange codes to yfinance ticker suffixes
# Used by portfolio-risk-var-cvar.py for historical data fetching

EXCHANGE_SUFFIX_MAP = {
    'SEHK': '.HK',      # Hong Kong Stock Exchange
    'NASDAQ': '',       # US NASDAQ
    'NYSE': '',         # US NYSE
    'ARCA': '',         # NYSE Arca
    'CBOE': '',         # CBOE Options
    'CME': '',          # CME Options
    'PINK': '',         # OTC Pink Sheets
    'SGX': '.SI',       # Singapore Exchange
    'LSEETF': '.L',     # London Stock Exchange ETF
    'AEB': '.AS',       # Amsterdam (Euronext)
    'IBIS': '.DE',      # Germany (Xetra) 
    'IBIS2': '.DE',     # Germany (Xetra)
    'SBF': '.PA',       # France (Euronext Paris)
    'EBS': '.SW',       # Switzerland (SIX Swiss Exchange)
}
