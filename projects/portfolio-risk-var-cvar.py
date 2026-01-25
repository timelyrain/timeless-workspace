"""
Portfolio Risk Analyzer - VaR & CVaR Calculator
================================================

Calculates Value at Risk (VaR) and Conditional VaR (CVaR) for IBKR portfolio positions.

PHASE 1: Stocks & ETFs only (Global ETF + Growth Engine)
PHASE 2: Options (Income Strategy, Buy) - Coming later

FEATURES:
- Historical VaR/CVaR (95% and 99% confidence)
- Monte Carlo VaR/CVaR (10,000 simulations)
- Parametric VaR (assumes normal distribution)
- Portfolio-level and per-position risk metrics
- Daily Telegram alerts
- Risk tracking over time

METHODOLOGY:
- VaR: "What's the maximum loss at X% confidence?"
- CVaR: "When things go bad, what's the average loss?"
- Uses 252 trading days (1 year) of historical data
- Accounts for correlations between positions

USAGE:
python portfolio-risk-var-cvar.py

OUTPUT:
- Console report with VaR/CVaR metrics
- Telegram alert with daily risk summary
- JSON file: portfolio_risk_YYYYMMDD.json

Author: KHK Intelligence
Date: January 25, 2026
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

# Configuration
POSITIONS_FILE = 'fetch-ibkr-positions.xlsx'
CONFIDENCE_LEVELS = [0.95, 0.99]  # 95% and 99% confidence
TIME_HORIZON = 1  # 1-day VaR
HISTORICAL_DAYS = 252  # 1 year of trading days
MONTE_CARLO_SIMS = 10000

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
            'correlations': {}
        }
    
    def load_positions(self):
        """Load positions from Excel file - Phase 1: Stocks/ETFs only"""
        print("📂 Loading positions...")
        
        try:
            # Load both accounts
            df_hk = pd.read_excel(self.positions_file, sheet_name='PositionsHK')
            df_al = pd.read_excel(self.positions_file, sheet_name='PositionsAL')
            
            # Combine positions
            df = pd.concat([df_hk, df_al], ignore_index=True)
            
            # Filter for stocks/ETFs only (Phase 1)
            df = df[df['AssetClass'] == 'STK'].copy()
            
            # Aggregate duplicate symbols across accounts
            df_agg = df.groupby('Symbol').agg({
                'Description': 'first',
                'Quantity': 'sum',
                'MarkPrice': 'first',
                'PositionValueUSD': 'sum',
                'CurrencyPrimary': 'first',
                'ListingExchange': 'first'
            }).reset_index()
            
            # Map symbols to yfinance tickers using ListingExchange
            df_agg['YFinanceTicker'] = df_agg.apply(
                lambda row: self._map_to_yfinance_ticker(row['Symbol'], row['ListingExchange']),
                axis=1
            )
            
            # Keep relevant columns
            self.positions = df_agg[['Symbol', 'YFinanceTicker', 'Description', 'Quantity', 
                                    'MarkPrice', 'PositionValueUSD', 'CurrencyPrimary', 
                                    'ListingExchange']].copy()
            
            # Calculate portfolio value
            self.portfolio_value = self.positions['PositionValueUSD'].sum()
            
            # Calculate position weights
            self.positions['Weight'] = self.positions['PositionValueUSD'] / self.portfolio_value
            
            print(f"  ✓ Loaded {len(self.positions)} stock/ETF positions")
            print(f"  ✓ Portfolio value: ${self.portfolio_value:,.2f}")
            
            # Show exchange mapping summary
            exchange_counts = self.positions['ListingExchange'].value_counts()
            print(f"  ✓ Exchanges: {dict(exchange_counts)}")
            
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
        """Fetch historical price data for all positions"""
        print(f"\n📊 Fetching {HISTORICAL_DAYS} days of historical data...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=HISTORICAL_DAYS + 50)  # Extra buffer for weekends
        
        returns_data = {}
        failed_symbols = []
        
        for idx, row in self.positions.iterrows():
            symbol = row['Symbol']
            yf_ticker = row['YFinanceTicker']
            exchange = row['ListingExchange']
            
            try:
                print(f"  Fetching {symbol} ({yf_ticker} @ {exchange})...", end='')
                ticker = yf.Ticker(yf_ticker)
                hist = ticker.history(start=start_date, end=end_date)
                
                if len(hist) < 100:  # Need minimum data
                    print(f" ⚠️  Insufficient data ({len(hist)} days)")
                    failed_symbols.append(symbol)
                    continue
                
                # Calculate daily returns
                returns = hist['Close'].pct_change(fill_method=None).dropna()
                returns_data[symbol] = returns.tail(HISTORICAL_DAYS)
                
                print(f" ✓ ({len(returns_data[symbol])} days)")
                
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
        """Calculate Historical VaR and CVaR"""
        # Calculate portfolio returns (weighted sum of individual returns)
        weights = self.positions.set_index('Symbol')['Weight']
        
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
    
    def calculate_monte_carlo_var_cvar(self, confidence=0.95, num_sims=MONTE_CARLO_SIMS):
        """Calculate Monte Carlo VaR/CVaR through simulation"""
        print(f"\n🎲 Running Monte Carlo simulation ({num_sims:,} scenarios)...")
        
        # Calculate covariance matrix
        cov_matrix = self.returns.cov()
        
        # Add small regularization to diagonal for numerical stability
        cov_matrix += np.eye(len(cov_matrix)) * 1e-8
        
        # Get weights aligned with returns
        weights = self.positions.set_index('Symbol')['Weight']
        aligned_weights = weights.reindex(self.returns.columns).fillna(0).values
        
        # Mean returns
        mean_returns = self.returns.mean().values
        
        # Simulate returns
        simulated_portfolio_returns = []
        
        try:
            for i in range(num_sims):
                # Generate correlated random returns
                random_returns = np.random.multivariate_normal(mean_returns, cov_matrix)
                # Calculate portfolio return
                portfolio_return = np.dot(aligned_weights, random_returns)
                simulated_portfolio_returns.append(portfolio_return)
        except np.linalg.LinAlgError:
            print("  ⚠️  Covariance matrix issue, using Cholesky decomposition...")
            # Alternative: Use Cholesky decomposition
            try:
                L = np.linalg.cholesky(cov_matrix)
                for i in range(num_sims):
                    z = np.random.standard_normal(len(mean_returns))
                    random_returns = mean_returns + L @ z
                    portfolio_return = np.dot(aligned_weights, random_returns)
                    simulated_portfolio_returns.append(portfolio_return)
            except:
                print("  ✗ Monte Carlo simulation failed - skipping")
                return None
        
        # Convert to array and sort
        sim_returns = np.array(simulated_portfolio_returns)
        sim_returns_sorted = np.sort(sim_returns)
        
        # VaR: Find percentile
        var_percentile = 1 - confidence
        var_index = int(num_sims * var_percentile)
        var_return = sim_returns_sorted[var_index]
        
        # CVaR: Average of worse scenarios
        cvar_return = sim_returns_sorted[:var_index].mean()
        
        # Convert to dollars
        var_dollar = abs(var_return * self.portfolio_value)
        cvar_dollar = abs(cvar_return * self.portfolio_value)
        
        print(f"  ✓ Simulation complete")
        
        return {
            'var_return': var_return,
            'var_dollar': var_dollar,
            'cvar_return': cvar_return,
            'cvar_dollar': cvar_dollar,
            'worst_sim': sim_returns_sorted[0],
            'worst_sim_dollar': abs(sim_returns_sorted[0] * self.portfolio_value)
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
            
            # Monte Carlo VaR/CVaR
            mc_result = self.calculate_monte_carlo_var_cvar(confidence)
            if mc_result:
                print(f"\n  Monte Carlo Method ({MONTE_CARLO_SIMS:,} simulations):")
                print(f"    VaR:  ${mc_result['var_dollar']:>10,.2f} ({mc_result['var_return']:>6.2%})")
                print(f"    CVaR: ${mc_result['cvar_dollar']:>10,.2f} ({mc_result['cvar_return']:>6.2%})")
                print(f"    Worst sim: ${mc_result['worst_sim_dollar']:>10,.2f} ({mc_result['worst_sim']:>6.2%})")
                
                # Store results
                conf_key = f"{confidence*100:.0f}"
                self.results['var'][conf_key] = {
                    'historical': hist_result['var_dollar'],
                    'parametric': param_result['var_dollar'],
                    'monte_carlo': mc_result['var_dollar']
                }
                self.results['cvar'][conf_key] = {
                    'historical': hist_result['cvar_dollar'],
                    'parametric': param_result['cvar_dollar'],
                    'monte_carlo': mc_result['cvar_dollar']
                }
            else:
                # Store results without Monte Carlo
                conf_key = f"{confidence*100:.0f}"
                self.results['var'][conf_key] = {
                    'historical': hist_result['var_dollar'],
                    'parametric': param_result['var_dollar'],
                    'monte_carlo': None
                }
                self.results['cvar'][conf_key] = {
                    'historical': hist_result['cvar_dollar'],
                    'parametric': param_result['cvar_dollar'],
                    'monte_carlo': None
                }
        
        # Position-level risk
        position_risks = self.calculate_position_risk()
        self.results['position_risk'] = position_risks
        
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
        var_95_mc = self.results['var']['95'].get('monte_carlo')
        cvar_95_mc = self.results['cvar']['95'].get('monte_carlo')
        
        message += f"*🎯 95% CONFIDENCE (1-DAY)*\n"
        message += f"VaR (Historical): ${var_95_hist:,.2f} ({var_95_hist/self.portfolio_value:.2%})\n"
        message += f"CVaR (Historical): ${cvar_95_hist:,.2f} ({cvar_95_hist/self.portfolio_value:.2%})\n"
        if var_95_mc:
            message += f"VaR (Monte Carlo): ${var_95_mc:,.2f}\n"
            message += f"CVaR (Monte Carlo): ${cvar_95_mc:,.2f}\n\n"
        else:
            message += f"\n"
        
        message += f"*💡 Interpretation:*\n"
        message += f"• 95% of days, loss won't exceed ${var_95_hist:,.0f}\n"
        message += f"• In worst 5% of days, avg loss is ${cvar_95_hist:,.0f}\n\n"
        
        # Top 3 risky positions
        message += f"*⚠️ TOP 3 RISKY POSITIONS:*\n"
        for i, pos in enumerate(self.results['position_risk'][:3], 1):
            message += f"{i}. {pos['symbol']}: CVaR ${pos['cvar_95_dollar']:,.0f}\n"
        
        message += f"\n━━━━━━━━━━━━━━━\n"
        message += f"📊 Phase 1: Stocks/ETFs only\n"
        message += f"🔜 Phase 2: Options coming soon"
        
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
