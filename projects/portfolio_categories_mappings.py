"""
╔══════════════════════════════════════════════════════════════════════╗
║                     SHARED PORTFOLIO CONFIGURATION                   ║
╚══════════════════════════════════════════════════════════════════════╝

Single source of truth for portfolio structure across all scripts:
- portfolio-risk-var-cvar.py
- institutional-risk-signal.py

Last updated: 2026-02-02
Dashboard source: fetch-ibkr-positions-dashboard.xlsx (K4-K23)
"""

# =============================================================================
# PORTFOLIO CATEGORY MAPPING (2026 Structure)
# =============================================================================
# Source of truth: fetch-ibkr-positions-dashboard.xlsx
# Synced with Dashboard columns K4-K23

SYMBOL_MAPPING = {
    'global_triads': [
        '82846',    # K5: China ETF
        'DHL',      # K6: Dividend
        'ES3',      # K7: Singapore banks
        'VWRA',     # K8: VT USD
        'WORLD',    # K9: VT, no EM, hedged
        'XMME',     # K10: EM, unhedged
    ],
    'four_horsemen': [
        'CSNDX',    # K12: Nasdaq
        'EQCH',     # K13: Nasdaq, hedged
        'CBUK',     # K14: China Tech, unhedged
        'HEAL',     # K15: Biotic
        'INRA',     # K16: Energy
        'GRDU',     # K17: Clean energy / infrastructure
        'LOCK',     # K18: Security
    ],
    'cash_cow': [
        # Source of truth: fetch-ibkr-positions-dashboard.xlsx → IncomeStrategy sheet
        'SPY', 'ADBE', 'AMD', 'CRM', 'CSCO', 'ORCL',
        'COST', 'PEP', 'WMT', 'XOM', 'JPM', 'V',
        'LLY', 'UNH', 'AAPL', 'AMZN', 'GOOGL', 'META',
        'MSFT', 'NVDA', 'TSLA', 'QQQ', 'CMG', 'NFLX',
        'SMH',
    ],
    'alpha': [
        # K20: Theme stocks, speculation
        'BITO', 'CELH', 'CHA', 'IBKR', 'LKNCY',
        'SE',    # Auto-added: SEA LTD-ADR
        'SE',    # Auto-added: SEA LTD-ADR
    ],
    'omega': [],  # K21: SPY/QQQ/ES options only (loaded dynamically in Phase 2)
    'vault': ['GSD'],  # K22: Gold (Singapore Gold)
    'war_chest': [],  # K23: Cash (tracked in Dashboard, not in positions file)
}

# =============================================================================
# TARGET ALLOCATIONS BY REGIME
# =============================================================================
# Used by institutional-risk-signal.py for regime-based allocation guidance
# Aligned with institutional risk scoring

TARGET_ALLOCATIONS = {
    'ALL_CLEAR': {
        'global_triads': 0.30, 'four_horsemen': 0.30, 'cash_cow': 0.25,
        'alpha': 0.02, 'omega': 0.025, 'vault': 0.05, 'war_chest': 0.05
    },
    'NORMAL': {
        'global_triads': 0.30, 'four_horsemen': 0.27, 'cash_cow': 0.225,
        'alpha': 0.016, 'omega': 0.01, 'vault': 0.07, 'war_chest': 0.10
    },
    'ELEVATED': {
        'global_triads': 0.30, 'four_horsemen': 0.21, 'cash_cow': 0.125,
        'alpha': 0.01, 'omega': 0.01, 'vault': 0.10, 'war_chest': 0.24
    },
    'HIGH': {
        'global_triads': 0.24, 'four_horsemen': 0.09, 'cash_cow': 0.0,
        'alpha': 0.0, 'omega': 0.02, 'vault': 0.15, 'war_chest': 0.33
    },
    'EXTREME': {
        'global_triads': 0.09, 'four_horsemen': 0.0, 'cash_cow': 0.0,
        'alpha': 0.0, 'omega': 0.03, 'vault': 0.25, 'war_chest': 0.39
    }
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
