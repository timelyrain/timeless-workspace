"""
╔══════════════════════════════════════════════════════════════════════╗
║                     SHARED PORTFOLIO CONFIGURATION                   ║
╚══════════════════════════════════════════════════════════════════════╝

Single source of truth for portfolio structure across all scripts:
- portfolio-risk-var-cvar.py
- institutional-risk-signal.py

Last updated: 2026-02-02
Dashboard source: fetch-ibkr-positions-dashboard.xlsx (F2-F18, total B19)
"""

# =============================================================================
# PORTFOLIO CATEGORY MAPPING (2026 Structure)
# =============================================================================
# Source of truth: fetch-ibkr-positions-dashboard.xlsx
# Synced with Dashboard: Actual $ in col F, rows 2-18; total in B19

SYMBOL_MAPPING = {
    'global_triads': [
        '82846',    # row3: China ETF
        'DHL',      # row4: Dividend
        'ES3',      # row5: Singapore banks
        'VWRA',     # row6: VT USD
        #'WORLD',    # VT, no EM, hedged
        'XMME',     # row7: EM, unhedged
    ],
    'four_horsemen': [
        #'CSNDX',    # Nasdaq
        'EQCH',     # row9: Nasdaq, hedged
        'CBUK',     # row10: China Tech, unhedged
        '9807',     # row11: China Robotics (HK)
        #'HEAL',     # Biotic
        'INRA',     # row12: Energy
        'GRDU',     # row13: Clean energy / infrastructure
        #'LOCK',     # Security
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
        # row15: Theme stocks, speculation
        'BITO',
        '9807',    # Auto-added: GLOBAL X CHINA ROBOTICS
        'IBKR',    # Auto-added: INTERACTIVE BROKERS GRO-CL A
        'HY9H',    # Auto-added: SK HYNIX INC-GDS
        'NEM',    # Auto-added: NEWMONT CORP
    ],
    'omega': [],  # row16: SPY/QQQ/ES options only (loaded dynamically in Phase 2)
    'vault': ['GSD', 'AEM'],  # row17: Gold (GSD: Singapore Gold ETF, AEM: Agnico Eagle Mines)
    'war_chest': [],  # row18: Cash (tracked in Dashboard, not in positions file)
}

# =============================================================================
# TARGET ALLOCATIONS BY REGIME
# =============================================================================
# Used by institutional-risk-signal.py for regime-based allocation guidance
# Aligned with institutional risk scoring

TARGET_ALLOCATIONS = {
'ALL_CLEAR': {
    'global_triads': 0.28, 'four_horsemen': 0.25, 'cash_cow': 0.20,
    'alpha': 0.05, 'omega': 0.02, 'vault': 0.05, 'war_chest': 0.15
},
'NORMAL': {
    'global_triads': 0.28, 'four_horsemen': 0.225, 'cash_cow': 0.225,
    'alpha': 0.04, 'omega': 0.01, 'vault': 0.08, 'war_chest': 0.10
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
