"""
Portfolio Risk Analyzer - VaR & CVaR Calculator (2026 Edition)
================================================================

Calculates Value at Risk (VaR) and Conditional VaR (CVaR) for IBKR portfolio positions
with 7-category breakdown aligned with institutional-risk-signal.py.

PORTFOLIO STRUCTURE (2026):
- Global Triads: Strategic core ETFs (82846, DHL, ES3, VWRA, VT, XMNE)
- Four Horsemen: Growth engine ETFs (CSNDX, CTEC, HEAL, INRA, GRID)
- Cash Cow: Income strategy stocks (mega-caps for options wheel)
- The Alpha: Speculation (theme stocks, long calls)
- The Omega: Insurance (SPY/QQQ bear spreads only)
- The Vault: Gold (GSD - WisdomTree Gold)
- War Chest: Cash reserves

PHASE 2 COMPLETE: Full portfolio coverage
- Stocks & ETFs: Global Triads, Four Horsemen, Alpha, Vault (23 positions)
- Options: Cash Cow income strategies + Omega bear spreads (15 positions)
- Delta-adjusted VaR for options (captures directional risk)
- Theta decay tracking (annual cost/income estimates)

FEATURES:
- Historical VaR/CVaR (95% and 99% confidence)
- Parametric VaR (assumes normal distribution)
- Portfolio-level AND category-level risk metrics
- Per-position risk analysis
- Daily Telegram alerts with category breakdown
- Risk tracking over time

METHODOLOGY:
- VaR: "What's the maximum loss at X% confidence?"
- CVaR: "When things go bad, what's the average loss?"
- Uses 252 trading days (1 year) of historical data
- Accounts for correlations between positions

USAGE:
python portfolio-risk-var-cvar.py

OUTPUT:
- Console report with VaR/CVaR by category
- Telegram alert with category risk summary
- JSON file: portfolio_risk_YYYYMMDD.json

Author: KHK Intelligence
Date: February 2, 2026 (Synced with institutional-risk-signal.py v2.0)
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from scipy import stats

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN_VAR_CVAR")
CHAT_ID = os.environ.get("CHAT_ID")

# Portfolio Category Mapping (2026 Structure - Synced with institutional-risk-signal.py)
SYMBOL_MAPPING = {
    'global_triads': ['82846', 'DHL', 'ES3', 'VWRA', 'VWCE', 'VT', 'VXUS', 'XMNE'],
    'four_horsemen': ['CSNDX', 'CTEC', 'HEAL', 'INRA', 'GRID'],
    'cash_cow': [
        'SPY', 'QQQ', 'ADBE', 'AMD', 'CRM', 'CSCO', 'ORCL', 'COST', 'PEP', 'WMT', 
        'XOM', 'JPM', 'V', 'LLY', 'UNH', 'AAPL', 'AMZN', 'GOOGL', 'META', 'MSFT', 
        'NVDA', 'TSLA'
    ],
    'alpha': ['LCID'],  # Theme stocks
    'omega': [],  # SPY/QQQ options only (Phase 2)
    'vault': ['GSD'],  # Gold (WisdomTree Gold)
    'war_chest': [],  # Cash (not tracked in stock positions)
}

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
POSITIONS_FILE = os.path.join(SCRIPT_DIR, 'fetch-ibkr-positions.xlsx')
CONFIDENCE_LEVELS = [0.95, 0.99]  # 95% and 99% confidence
TIME_HORIZON = 1  # 1-day VaR
HISTORICAL_DAYS = 252  # 1 year of trading days

# IBKR Exchange to yfinance suffix mapping
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

def send_telegram_alert(message, token, chat_id):
    """Send alert to Telegram"""
    if not token or not chat_id:
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if not response.ok:
            print(f"  ⚠️  Telegram API error: {response.status_code}")
        return response.ok
    except Exception as e:
        print(f"  ⚠️  Telegram request failed: {str(e)}")
        return False

class PortfolioRiskAnalyzer:
    """Calculate VaR and CVaR for portfolio positions"""
    
    def __init__(self, positions_file):
        self.positions_file = positions_file
        self.positions = None
        self.returns = None
        self.portfolio_value = 0
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'portfolio_value': 0,
            'var': {},
            'cvar': {},
            'position_risk': [],
            'category_risk': {},  # NEW: Category-level risk breakdown
            'correlations': {}
        }
    
    def _categorize_symbol(self, symbol):
        """Classify symbol into one of the 7 portfolio categories"""
        for category, symbols in SYMBOL_MAPPING.items():
            if symbol in symbols:
                return category
        return 'uncategorized'  # Fallback for unknown symbols
    
    def _extract_underlying_symbol(self, option_symbol):
        """Extract underlying symbol from option symbol
        Examples:
        - 'SPY   261218P00505000' → 'SPY'
        - 'QQQ   261218P00425000' → 'QQQ'
        - 'GOOGL 260227P00310000' → 'GOOGL'
        - 'EW2G6 P6525' → 'ES=F' (ES futures)
        """
        symbol_str = str(option_symbol).strip()
        
        # ES futures options (EW prefix) → ES futures
        if symbol_str.startswith('EW'):
            return 'ES=F'
        
        # Standard options: extract first word (underlying symbol)
        parts = symbol_str.split()
        if parts:
            return parts[0].strip()
        
        return symbol_str
    
    def _estimate_option_delta(self, quantity, option_type):
        """Estimate option delta based on position side and option type
        
        Simplified delta assumptions:
        - Long calls: +0.50 delta (ATM approximation)
        - Short calls: -0.50 delta
        - Long puts: -0.40 delta (protective puts typically OTM)
        - Short puts: +0.40 delta (cash-secured puts typically OTM)
        
        For spreads (quantity indicates long + short legs), net delta is calculated automatically.
        
        Returns: delta multiplier for position
        """
        if pd.isna(option_type) or pd.isna(quantity):
            return 0
        
        is_long = quantity > 0
        is_call = str(option_type).upper() == 'C'
        
        if is_call:
            return 0.50 if is_long else -0.50
        else:  # Put
            return -0.40 if is_long else 0.40
    
    def load_positions(self):
        """Load positions from Excel file - Phase 2: Stocks/ETFs + Options"""
        print("📂 Loading positions...")
        
        try:
            # Load both accounts
            df_hk = pd.read_excel(self.positions_file, sheet_name='PositionsHK')
            df_al = pd.read_excel(self.positions_file, sheet_name='PositionsAL')
            
            # Combine positions
            df = pd.concat([df_hk, df_al], ignore_index=True)
            
            # Separate stocks and options
            stocks_df = df[df['AssetClass'] == 'STK'].copy()
            options_df = df[df['AssetClass'].isin(['OPT', 'FOP'])].copy()
            
            # Process stocks/ETFs
            stocks_agg = stocks_df.groupby('Symbol').agg({
                'Description': 'first',
                'Quantity': 'sum',
                'MarkPrice': 'first',
                'PositionValueUSD': 'sum',
                'CurrencyPrimary': 'first',
                'ListingExchange': 'first'
            }).reset_index()
            
            stocks_agg['YFinanceTicker'] = stocks_agg.apply(
                lambda row: self._map_to_yfinance_ticker(row['Symbol'], row['ListingExchange']),
                axis=1
            )
            stocks_agg['Category'] = stocks_agg['Symbol'].apply(self._categorize_symbol)
            stocks_agg['AssetClass'] = 'STK'
            
            # Process options
            options_agg = options_df.groupby(['Symbol', 'Strike', 'Expiry', 'Put/Call']).agg({
                'Description': 'first',
                'Quantity': 'sum',
                'MarkPrice': 'first',
                'PositionValueUSD': 'sum',
                'CurrencyPrimary': 'first',
                'ListingExchange': 'first',
                'AssetClass': 'first',
                'Multiplier': 'first'
            }).reset_index()
            
            # Categorize options: SPY/QQQ/ES = Omega, others = Cash Cow
            options_agg['Category'] = options_agg['Symbol'].apply(
                lambda s: 'omega' if any(x in str(s) for x in ['SPY', 'QQQ', 'ES', 'EW']) else 'cash_cow'
            )
            
            # Extract underlying symbol for options (for tracking underlying price)
            options_agg['UnderlyingSymbol'] = options_agg['Symbol'].apply(self._extract_underlying_symbol)
            options_agg['YFinanceTicker'] = options_agg['UnderlyingSymbol']
            
            # Calculate delta-adjusted notional for options
            # Delta-adjusted notional = quantity * contracts * strike * delta * multiplier
            options_agg['OptionDelta'] = options_agg.apply(
                lambda row: self._estimate_option_delta(row['Quantity'], row['Put/Call']),
                axis=1
            )
            
            # For options: notional = quantity × strike × multiplier × delta
            options_agg['DeltaAdjustedNotional'] = (
                options_agg['Quantity'] * 
                options_agg['Strike'] * 
                options_agg['Multiplier'] * 
                options_agg['OptionDelta']
            )
            
            # Estimate theta decay (annual cost/income)
            # For short options: positive theta (income), for long options: negative theta (cost)
            # Rule of thumb: 30-40% of option value decays over life of option
            # Simplified: assume 35% decay rate for typical ATM/OTM options
            options_agg['ThetaDecayAnnual'] = options_agg.apply(
                lambda row: -row['PositionValueUSD'] * 0.35 if row['Quantity'] > 0 
                else -row['PositionValueUSD'] * 0.35,  # Both long (cost) and short (income) show as cost/income
                axis=1
            )
            
            # Combine stocks and options
            stocks_cols = ['Symbol', 'YFinanceTicker', 'Description', 'Quantity', 'MarkPrice', 
                          'PositionValueUSD', 'CurrencyPrimary', 'ListingExchange', 'Category', 'AssetClass']
            options_cols = ['Symbol', 'YFinanceTicker', 'Description', 'Quantity', 'MarkPrice', 
                           'PositionValueUSD', 'CurrencyPrimary', 'ListingExchange', 'Category', 'AssetClass',
                           'Strike', 'Expiry', 'Put/Call', 'Multiplier', 'UnderlyingSymbol', 
                           'OptionDelta', 'DeltaAdjustedNotional', 'ThetaDecayAnnual']
            
            self.positions = pd.concat([
                stocks_agg[stocks_cols],
                options_agg[options_cols]
            ], ignore_index=True)
            
            # Calculate portfolio value
            self.portfolio_value = self.positions['PositionValueUSD'].sum()
            
            # Calculate position weights
            self.positions['Weight'] = self.positions['PositionValueUSD'] / self.portfolio_value
            
            # Count stocks vs options
            num_stocks = len(self.positions[self.positions['AssetClass'] == 'STK'])
            num_options = len(self.positions[self.positions['AssetClass'].isin(['OPT', 'FOP'])])
            
            print(f"  ✓ Loaded {num_stocks} stock/ETF positions + {num_options} options positions")
            print(f"  ✓ Portfolio value: ${self.portfolio_value:,.2f}")
            
            # Show category breakdown
            category_summary = self.positions.groupby('Category').agg({
                'PositionValueUSD': 'sum',
                'Symbol': 'count'
            }).rename(columns={'Symbol': 'Count'})
            category_summary['Percentage'] = (category_summary['PositionValueUSD'] / self.portfolio_value * 100)
            
            print(f"\n  📊 Category Breakdown:")
            for category, row in category_summary.iterrows():
                print(f"     {category:20s}: ${row['PositionValueUSD']:>12,.0f} ({row['Percentage']:>5.1f}%) - {int(row['Count'])} positions")
            
            # Show options theta summary for Cash Cow and Omega
            options_pos = self.positions[self.positions['AssetClass'].isin(['OPT', 'FOP'])]
            if len(options_pos) > 0:
                total_theta = options_pos['ThetaDecayAnnual'].sum()
                cash_cow_theta = options_pos[options_pos['Category'] == 'cash_cow']['ThetaDecayAnnual'].sum()
                omega_theta = options_pos[options_pos['Category'] == 'omega']['ThetaDecayAnnual'].sum()
                
                print(f"\n  📊 Options Theta Decay (Annual Est.):")
                if abs(cash_cow_theta) > 0:
                    theta_sign = "📈" if cash_cow_theta > 0 else "📉"
                    print(f"     Cash Cow   : {theta_sign} ${cash_cow_theta:>10,.0f} ({'income' if cash_cow_theta > 0 else 'cost'})")
                if abs(omega_theta) > 0:
                    theta_sign = "📈" if omega_theta > 0 else "📉"
                    print(f"     Omega      : {theta_sign} ${omega_theta:>10,.0f} ({'income' if omega_theta > 0 else 'cost'})")
                if abs(total_theta) > 0:
                    print(f"     Total      : ${total_theta:>10,.0f} (net {'income' if total_theta > 0 else 'cost'})")
            
            # Show exchange mapping summary
            exchange_counts = self.positions['ListingExchange'].value_counts()
            print(f"\n  ✓ Exchanges: {dict(exchange_counts)}")
            
            return True
            
        except Exception as e:
            print(f"  ✗ Error loading positions: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _map_to_yfinance_ticker(self, symbol, exchange):
        """Map IBKR symbol + exchange to yfinance ticker format"""
        # Handle special case for 82846 -> 82846.HK (CNH-denominated share class)
        if symbol == '82846':
            return '82846.HK'
        
        # Get suffix from exchange mapping
        suffix = EXCHANGE_SUFFIX_MAP.get(exchange, '')
        
        # Return ticker with suffix (if any)
        return f"{symbol}{suffix}" if suffix else symbol
    
    def fetch_historical_data(self):
        """Fetch historical price data for all positions (stocks + options with delta adjustment)"""
        print(f"\n📊 Fetching {HISTORICAL_DAYS} days of historical data...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=HISTORICAL_DAYS + 50)  # Extra buffer for weekends
        
        returns_data = {}
        failed_symbols = []
        
        # Group options by underlying to avoid duplicate fetches
        underlying_cache = {}
        
        for idx, row in self.positions.iterrows():
            symbol = row['Symbol']
            yf_ticker = row['YFinanceTicker']
            exchange = row['ListingExchange']
            asset_class = row['AssetClass']
            
            try:
                # Check if we already fetched this underlying
                if yf_ticker in underlying_cache:
                    print(f"  Using cached data for {symbol} (underlying: {yf_ticker})...")
                    returns = underlying_cache[yf_ticker].copy()
                else:
                    print(f"  Fetching {symbol} ({yf_ticker} @ {exchange})...", end='')
                    ticker = yf.Ticker(yf_ticker)
                    hist = ticker.history(start=start_date, end=end_date)
                    
                    if len(hist) < 100:  # Need minimum data
                        print(f" ⚠️  Insufficient data ({len(hist)} days)")
                        failed_symbols.append(symbol)
                        continue
                    
                    # Calculate daily returns
                    returns = hist['Close'].pct_change(fill_method=None).dropna()
                    returns = returns.tail(HISTORICAL_DAYS)
                    
                    # Cache for reuse by other options on same underlying
                    underlying_cache[yf_ticker] = returns.copy()
                    
                    print(f" ✓ ({len(returns)} days)")
                
                # For options: Apply delta adjustment to returns
                if asset_class in ['OPT', 'FOP'] and not pd.isna(row.get('OptionDelta')):
                    delta = row['OptionDelta']
                    # Option return = delta × underlying return
                    returns = returns * delta
                    returns_data[symbol] = returns
                else:
                    # Stocks/ETFs: Use returns as-is
                    returns_data[symbol] = returns
                
            except Exception as e:
                print(f" ✗ Error: {e}")
                failed_symbols.append(symbol)
        
        if failed_symbols:
            print(f"\n  ⚠️  Failed to fetch: {', '.join(failed_symbols)}")
            # Remove failed positions
            self.positions = self.positions[~self.positions['Symbol'].isin(failed_symbols)]
            # Recalculate weights
            self.positions['Weight'] = self.positions['PositionValueUSD'] / self.positions['PositionValueUSD'].sum()
        
        # Create returns DataFrame
        self.returns = pd.DataFrame(returns_data)
        
        print(f"\n  ✓ Historical data ready: {len(self.returns)} days, {len(self.returns.columns)} positions")
        return True
    
    def calculate_historical_var_cvar(self, confidence=0.95):
        """Calculate Historical VaR and CVaR with delta-adjusted notional for options"""
        
        # For VaR calculation, we need to use delta-adjusted notional for options
        # instead of market value, since options risk is proportional to underlying movement
        
        # Calculate exposure-based weights
        positions_with_exposure = self.positions.copy()
        
        # For options: use delta-adjusted notional; for stocks: use position value
        positions_with_exposure['RiskExposure'] = positions_with_exposure.apply(
            lambda row: abs(row.get('DeltaAdjustedNotional', row['PositionValueUSD'])) 
            if row['AssetClass'] in ['OPT', 'FOP'] and not pd.isna(row.get('DeltaAdjustedNotional'))
            else abs(row['PositionValueUSD']),
            axis=1
        )
        
        # Calculate weights based on risk exposure
        total_exposure = positions_with_exposure['RiskExposure'].sum()
        positions_with_exposure['ExposureWeight'] = positions_with_exposure['RiskExposure'] / total_exposure
        
        # Get weights aligned with returns
        weights = positions_with_exposure.set_index('Symbol')['ExposureWeight']
        
        # Align weights with returns columns
        aligned_weights = weights.reindex(self.returns.columns).fillna(0)
        
        # Portfolio returns = weighted sum
        portfolio_returns = (self.returns * aligned_weights.values).sum(axis=1)
        
        # Sort returns (losses are negative)
        sorted_returns = portfolio_returns.sort_values()
        
        # VaR: Find the percentile
        var_percentile = 1 - confidence
        var_index = int(len(sorted_returns) * var_percentile)
        var_return = sorted_returns.iloc[var_index]
        
        # CVaR: Average of returns worse than VaR
        cvar_return = sorted_returns.iloc[:var_index].mean()
        
        # Convert to dollar amounts
        var_dollar = abs(var_return * self.portfolio_value)
        cvar_dollar = abs(cvar_return * self.portfolio_value)
        
        return {
            'var_return': var_return,
            'var_dollar': var_dollar,
            'cvar_return': cvar_return,
            'cvar_dollar': cvar_dollar,
            'worst_return': sorted_returns.iloc[0],
            'worst_dollar': abs(sorted_returns.iloc[0] * self.portfolio_value)
        }
    
    def calculate_parametric_var_cvar(self, confidence=0.95):
        """Calculate Parametric VaR/CVaR (assumes normal distribution)"""
        # Calculate portfolio returns
        weights = self.positions.set_index('Symbol')['Weight']
        aligned_weights = weights.reindex(self.returns.columns).fillna(0)
        portfolio_returns = (self.returns * aligned_weights.values).sum(axis=1)
        
        # Mean and std of portfolio returns
        mu = portfolio_returns.mean()
        sigma = portfolio_returns.std()
        
        # VaR using normal distribution
        z_score = stats.norm.ppf(1 - confidence)
        var_return = mu + z_score * sigma
        var_dollar = abs(var_return * self.portfolio_value)
        
        # CVaR formula for normal distribution
        pdf_at_var = stats.norm.pdf(z_score)
        cvar_return = mu - sigma * (pdf_at_var / (1 - confidence))
        cvar_dollar = abs(cvar_return * self.portfolio_value)
        
        return {
            'var_return': var_return,
            'var_dollar': var_dollar,
            'cvar_return': cvar_return,
            'cvar_dollar': cvar_dollar,
            'mean_return': mu,
            'std_return': sigma
        }
    
    def calculate_position_risk(self):
        """Calculate individual position contributions to portfolio risk"""
        print("\n📈 Calculating position-level risk...")
        
        position_risks = []
        
        for _, pos in self.positions.iterrows():
            symbol = pos['Symbol']
            
            if symbol not in self.returns.columns:
                continue
            
            returns = self.returns[symbol]
            
            # Historical VaR/CVaR for this position
            sorted_returns = returns.sort_values()
            var_95_index = int(len(sorted_returns) * 0.05)
            var_95_return = sorted_returns.iloc[var_95_index]
            cvar_95_return = sorted_returns.iloc[:var_95_index].mean()
            
            # Convert to dollars
            position_value = pos['PositionValueUSD']
            var_95_dollar = abs(var_95_return * position_value)
            cvar_95_dollar = abs(cvar_95_return * position_value)
            
            position_risks.append({
                'symbol': symbol,
                'description': pos['Description'],
                'value': position_value,
                'weight': pos['Weight'],
                'var_95_pct': var_95_return,
                'var_95_dollar': var_95_dollar,
                'cvar_95_pct': cvar_95_return,
                'cvar_95_dollar': cvar_95_dollar,
                'volatility': returns.std()
            })
        
        # Sort by CVaR (riskiest first)
        position_risks.sort(key=lambda x: x['cvar_95_dollar'], reverse=True)
        
        return position_risks
    
    def calculate_category_risk(self):
        """Calculate VaR/CVaR for each portfolio category"""
        print("\n📊 Calculating category-level risk...")
        
        category_risks = {}
        
        # Group positions by category
        for category in SYMBOL_MAPPING.keys():
            cat_positions = self.positions[self.positions['Category'] == category]
            
            if len(cat_positions) == 0:
                continue
            
            # Calculate category value and weight
            cat_value = cat_positions['PositionValueUSD'].sum()
            cat_weight = cat_value / self.portfolio_value
            
            # Get symbols in this category that have returns data
            cat_symbols = [s for s in cat_positions['Symbol'].tolist() if s in self.returns.columns]
            
            if len(cat_symbols) == 0:
                continue
            
            # Calculate category returns (weighted by position size within category)
            cat_pos_subset = cat_positions[cat_positions['Symbol'].isin(cat_symbols)]
            cat_pos_subset['CatWeight'] = cat_pos_subset['PositionValueUSD'] / cat_value
            
            # Weighted sum of returns within category
            cat_returns = pd.Series(0.0, index=self.returns.index)
            for _, pos in cat_pos_subset.iterrows():
                if pos['Symbol'] in self.returns.columns:
                    cat_returns += self.returns[pos['Symbol']] * pos['CatWeight']
            
            # Calculate 95% VaR/CVaR for category
            sorted_returns = cat_returns.sort_values()
            var_idx = int(len(sorted_returns) * 0.05)
            
            if var_idx == 0 or len(sorted_returns) < 30:  # Need minimum data points
                continue
                
            var_return = sorted_returns.iloc[var_idx]
            cvar_return = sorted_returns.iloc[:var_idx].mean()
            
            # Skip if returns are all zeros or invalid
            if pd.isna(var_return) or pd.isna(cvar_return) or cat_returns.std() == 0:
                continue
            
            var_dollar = abs(var_return * cat_value)
            cvar_dollar = abs(cvar_return * cat_value)
            volatility = cat_returns.std()
            
            category_risks[category] = {
                'value': cat_value,
                'weight': cat_weight,
                'var_95_dollar': var_dollar,
                'cvar_95_dollar': cvar_dollar,
                'var_95_pct': abs(var_return),
                'cvar_95_pct': abs(cvar_return),
                'volatility': volatility,
                'positions': len(cat_positions)
            }
        
        return category_risks
    
    def run_analysis(self):
        """Run full risk analysis"""
        print("=" * 80)
        print("📊 PORTFOLIO RISK ANALYZER - VaR & CVaR")
        print("=" * 80)
        
        # Load positions
        if not self.load_positions():
            return False
        
        # Fetch historical data
        if not self.fetch_historical_data():
            return False
        
        # Calculate VaR/CVaR for each confidence level
        print("\n" + "=" * 80)
        print("💰 PORTFOLIO-LEVEL RISK METRICS")
        print("=" * 80)
        
        for confidence in CONFIDENCE_LEVELS:
            print(f"\n📊 {confidence*100:.0f}% CONFIDENCE LEVEL")
            print("-" * 80)
            
            # Historical VaR/CVaR
            hist_result = self.calculate_historical_var_cvar(confidence)
            print(f"\n  Historical Method:")
            print(f"    VaR:  ${hist_result['var_dollar']:>10,.2f} ({hist_result['var_return']:>6.2%})")
            print(f"    CVaR: ${hist_result['cvar_dollar']:>10,.2f} ({hist_result['cvar_return']:>6.2%})")
            print(f"    Worst case: ${hist_result['worst_dollar']:>10,.2f} ({hist_result['worst_return']:>6.2%})")
            
            # Parametric VaR/CVaR
            param_result = self.calculate_parametric_var_cvar(confidence)
            print(f"\n  Parametric Method (Normal Distribution):")
            print(f"    VaR:  ${param_result['var_dollar']:>10,.2f} ({param_result['var_return']:>6.2%})")
            print(f"    CVaR: ${param_result['cvar_dollar']:>10,.2f} ({param_result['cvar_return']:>6.2%})")
            
            # Store results (Historical + Parametric only)
            conf_key = f"{confidence*100:.0f}"
            self.results['var'][conf_key] = {
                'historical': hist_result['var_dollar'],
                'parametric': param_result['var_dollar']
            }
            self.results['cvar'][conf_key] = {
                'historical': hist_result['cvar_dollar'],
                'parametric': param_result['cvar_dollar']
            }
        
        # Position-level risk
        position_risks = self.calculate_position_risk()
        self.results['position_risk'] = position_risks
        
        # Category-level risk
        category_risks = self.calculate_category_risk()
        self.results['category_risk'] = category_risks
        
        # Add worst loss (single worst day from historical data)
        self.results['worst_loss'] = hist_result['worst_dollar']
        
        # Display category risk breakdown
        print("\n" + "=" * 80)
        print("📂 CATEGORY-LEVEL RISK (Aligned with institutional-risk-signal.py)")
        print("=" * 80)
        
        # Sort categories by CVaR (highest risk first)
        sorted_categories = sorted(category_risks.items(), key=lambda x: x[1]['cvar_95_dollar'], reverse=True)
        
        for category, risk in sorted_categories:
            print(f"\n📊 {category.upper().replace('_', ' ')}")
            print(f"   Value: ${risk['value']:>12,.2f} ({risk['weight']:>6.2%} of portfolio)")
            print(f"   95% VaR:  ${risk['var_95_dollar']:>10,.2f} ({risk['var_95_pct']:>6.2%})")
            print(f"   95% CVaR: ${risk['cvar_95_dollar']:>10,.2f} ({risk['cvar_95_pct']:>6.2%})")
            print(f"   Volatility: {risk['volatility']:>6.2%} daily | Positions: {risk['positions']}")
        
        print("\n" + "=" * 80)
        print("🎯 TOP 10 RISKIEST POSITIONS (by CVaR)")
        print("=" * 80)
        
        for i, pos in enumerate(position_risks[:10], 1):
            print(f"\n{i}. {pos['symbol']} - {pos['description'][:40]}")
            print(f"   Value: ${pos['value']:>12,.2f} ({pos['weight']:>6.2%} of portfolio)")
            print(f"   95% VaR:  ${pos['var_95_dollar']:>10,.2f} ({pos['var_95_pct']:>6.2%})")
            print(f"   95% CVaR: ${pos['cvar_95_dollar']:>10,.2f} ({pos['cvar_95_pct']:>6.2%})")
            print(f"   Volatility: {pos['volatility']:>6.2%} daily")
        
        # Store portfolio value
        self.results['portfolio_value'] = self.portfolio_value
        
        return True
    
    def save_results(self):
        """Save results to JSON file"""
        filename = f"portfolio_risk_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to {filename}")
    
    def send_telegram_summary(self):
        """Send risk summary to Telegram"""
        print("\n📱 Sending Telegram alert...")
        
        # Build message
        message = f"📊 *DAILY PORTFOLIO VaR\CVaR RISK REPORT*\n"
        message += f"_{datetime.now().strftime('%B %d, %Y')}_\n\n"
        message += f"📈 *Positions:* {len(self.positions)} stocks/ETFs\n\n"
        
        # 95% Confidence metrics
        var_95_hist = self.results['var']['95']['historical']
        cvar_95_hist = self.results['cvar']['95']['historical']
        
        message += f"*🎯 95% CONFIDENCE (1-DAY)*\n"
        message += f"VaR (Historical): ${var_95_hist:,.2f} ({var_95_hist/self.portfolio_value:.2%})\n"
        message += f"CVaR (Historical): ${cvar_95_hist:,.2f} ({cvar_95_hist/self.portfolio_value:.2%})\n"
        message += f"\n"
        
        message += f"*💡 Interpretation:*\n"
        message += f"• 95% of days, loss won't exceed ${var_95_hist:,.0f}\n"
        message += f"• In worst 5% of days, avg loss is ${cvar_95_hist:,.0f}\n\n"
        
        # Category risk breakdown
        message += f"*📂 CATEGORY RISK (CVaR @ 95%):*\n"
        sorted_categories = sorted(self.results['category_risk'].items(), 
                                  key=lambda x: x[1]['cvar_95_dollar'], reverse=True)
        for category, risk in sorted_categories[:5]:  # Top 5 riskiest categories
            cat_name = category.replace('_', ' ').title()
            message += f"• {cat_name}: ${risk['cvar_95_dollar']:,.0f} ({risk['weight']:.1%})\n"
        
        message += f"\n*⚠️ TOP 3 RISKY POSITIONS:*\n"
        for i, pos in enumerate(self.results['position_risk'][:3], 1):
            message += f"{i}. {pos['symbol']}: CVaR ${pos['cvar_95_dollar']:,.0f}\n"
        
        # Add options summary
        options_pos = self.positions[self.positions['AssetClass'].isin(['OPT', 'FOP'])]
        if len(options_pos) > 0:
            total_theta = options_pos['ThetaDecayAnnual'].sum()
            cash_cow_theta = options_pos[options_pos['Category'] == 'cash_cow']['ThetaDecayAnnual'].sum()
            omega_theta = options_pos[options_pos['Category'] == 'omega']['ThetaDecayAnnual'].sum()
            
            message += f"\n*📊 OPTIONS THETA (Annual):*\n"
            if abs(cash_cow_theta) > 0:
                message += f"• Cash Cow: ${cash_cow_theta:,.0f} ({'income' if cash_cow_theta > 0 else 'cost'})\n"
            if abs(omega_theta) > 0:
                message += f"• Omega: ${omega_theta:,.0f} ({'income' if omega_theta > 0 else 'cost'})\n"
            message += f"• Net: ${total_theta:,.0f} ({abs(total_theta)/self.portfolio_value*100:.2f}% of portfolio)\n"
        
        message += f"\n━━━━━━━━━━━━━━━\n"
        
        # Count positions
        num_stocks = len(self.positions[self.positions['AssetClass'] == 'STK'])
        num_options = len(options_pos)
        
        message += f"📊 Phase 2 Complete: Full Portfolio\n"
        message += f"• {num_stocks} stocks/ETFs + {num_options} options\n"
        message += f"• Delta-adjusted VaR for options\n"
        message += f"• Synced with institutional-risk-signal.py v2.0"
        
        if send_telegram_alert(message, TELEGRAM_TOKEN, CHAT_ID):
            print("  ✓ Telegram alert sent")
        else:
            print("  ✗ Failed to send Telegram alert")

if __name__ == "__main__":
    analyzer = PortfolioRiskAnalyzer(POSITIONS_FILE)
    
    if analyzer.run_analysis():
        analyzer.save_results()
        analyzer.send_telegram_summary()
        
        print("\n" + "=" * 80)
        print("✅ Analysis Complete!")
        print("=" * 80)
    else:
        print("\n❌ Analysis failed")
        sys.exit(1)
