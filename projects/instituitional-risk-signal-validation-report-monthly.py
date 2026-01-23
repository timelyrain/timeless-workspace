"""
╔══════════════════════════════════════════════════════════════════════╗
║              RISK SIGNAL VALIDATION - Walk-Forward Analysis          ║
╚══════════════════════════════════════════════════════════════════════╝

Validates risk signal accuracy using existing data - no additional API calls.
Compares risk scores vs actual SPY forward returns to measure predictive power.

Run this monthly to validate the system is working as intended.
"""

import json
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path

class ValidationAnalyzer:
    """Analyze risk signal performance using walk-forward validation"""
    
    def __init__(self, history_file='risk_history.json'):
        self.history_file = history_file
        self.history = self._load_history()
        self.report_lines = []
    
    def _load_history(self):
        """Load risk history from JSON"""
        if Path(self.history_file).exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return {'scores': []}
    
    def generate_validation_report(self):
        """Generate comprehensive validation report"""
        print("\n" + "="*80)
        print("RISK SIGNAL VALIDATION - Walk-Forward Analysis")
        print("="*80 + "\n")
        
        if not self.history.get('scores') or len(self.history['scores']) < 7:
            print("❌ Insufficient data: Need at least 7 days of history")
            print(f"   Current history: {len(self.history.get('scores', []))} days")
            return None
        
        # Get SPY data
        spy = self._get_spy_data()
        if spy is None:
            print("❌ Could not fetch SPY data")
            return None
        
        self.report_lines = [
            "╔══════════════════════════════════════════════════════════════════════╗",
            "║              RISK SIGNAL VALIDATION REPORT                           ║",
            f"║              Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}                            ║",
            "╚══════════════════════════════════════════════════════════════════════╝",
            ""
        ]
        
        # Analysis sections
        self._analyze_score_correlation(spy)
        self._analyze_regime_accuracy(spy)
        self._analyze_alert_timing(spy)
        self._analyze_false_signals()
        
        # Generate report
        report = "\n".join(self.report_lines)
        
        # Save to file
        report_file = f"validation_report_{datetime.now().strftime('%Y%m')}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(report)
        print(f"\n✅ Validation report saved to {report_file}")
        return report
    
    def _get_spy_data(self):
        """Fetch SPY historical data (only dates we need)"""
        try:
            scores = self.history['scores']
            if not scores:
                return None
            
            start_date = min(s['date'] for s in scores)
            # Add 30 days forward for forward returns
            end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            spy = yf.Ticker('SPY').history(start=start_date, end=end_date)
            print(f"✅ Loaded SPY data: {len(spy)} days")
            return spy
        except Exception as e:
            print(f"❌ Error fetching SPY: {e}")
            return None
    
    def _analyze_score_correlation(self, spy):
        """Analyze correlation between risk score and forward returns"""
        self.report_lines.extend([
            "📊 SCORE vs FORWARD RETURNS CORRELATION",
            "=" * 70,
            ""
        ])
        
        scores = self.history['scores']
        
        # Calculate forward returns for different periods
        results = []
        for period_days, label in [(5, '1-week'), (21, '1-month')]:
            correlations = []
            
            for score_entry in scores:
                date = score_entry['date']
                score = score_entry['score']
                
                # Get SPY price on this date and forward date
                try:
                    current_price = spy.loc[date:date]['Close'].iloc[0]
                    future_date = (datetime.strptime(date, '%Y-%m-%d') + 
                                   timedelta(days=period_days)).strftime('%Y-%m-%d')
                    
                    if future_date in spy.index.strftime('%Y-%m-%d'):
                        future_price = spy.loc[future_date:future_date]['Close'].iloc[0]
                        forward_return = ((future_price - current_price) / current_price) * 100
                        correlations.append({'score': score, 'return': forward_return})
                except:
                    continue
            
            if len(correlations) >= 5:
                df = pd.DataFrame(correlations)
                corr = df['score'].corr(df['return'])
                avg_return = df['return'].mean()
                
                # Separate by regime
                high_score = df[df['score'] >= 75]['return'].mean()
                low_score = df[df['score'] < 60]['return'].mean()
                
                results.append({
                    'period': label,
                    'correlation': corr,
                    'avg_return': avg_return,
                    'high_score_return': high_score,
                    'low_score_return': low_score,
                    'samples': len(correlations)
                })
        
        if results:
            for r in results:
                self.report_lines.extend([
                    f"{r['period'].upper()} Forward Returns:",
                    f"  • Correlation: {r['correlation']:.3f} (higher score = {'higher' if r['correlation'] > 0 else 'lower'} returns)",
                    f"  • Avg return: {r['avg_return']:.2f}%",
                    f"  • High risk score (≥75): {r['high_score_return']:.2f}%",
                    f"  • Low risk score (<60): {r['low_score_return']:.2f}%",
                    f"  • Samples: {r['samples']} days",
                    ""
                ])
            
            # Interpretation
            corr_1w = results[0]['correlation'] if len(results) > 0 else 0
            if corr_1w > 0.3:
                self.report_lines.append("✅ STRONG: Risk score predicts forward returns well")
            elif corr_1w > 0:
                self.report_lines.append("⚠️  WEAK: Low correlation, signals need refinement")
            else:
                self.report_lines.append("❌ INVERSE: Higher scores predicting lower returns (check logic!)")
        else:
            self.report_lines.append("⚠️  Insufficient data for correlation analysis")
        
        self.report_lines.append("")
    
    def _analyze_regime_accuracy(self, spy):
        """Check if regime changes aligned with market moves"""
        self.report_lines.extend([
            "🎚️ REGIME CHANGE ACCURACY",
            "=" * 70,
            ""
        ])
        
        scores = sorted(self.history['scores'], key=lambda x: x['date'])
        
        regime_changes = []
        prev_regime = None
        
        for score_entry in scores:
            score = score_entry['score']
            date = score_entry['date']
            
            # Map score to regime
            if score >= 90:
                regime = 'ALL CLEAR'
            elif score >= 75:
                regime = 'NORMAL'
            elif score >= 60:
                regime = 'ELEVATED'
            elif score >= 40:
                regime = 'HIGH RISK'
            else:
                regime = 'EXTREME RISK'
            
            if prev_regime and regime != prev_regime:
                regime_changes.append({
                    'date': date,
                    'from': prev_regime,
                    'to': regime,
                    'score': score
                })
            
            prev_regime = regime
        
        if regime_changes:
            self.report_lines.append(f"Regime changes detected: {len(regime_changes)}")
            self.report_lines.append("")
            
            for change in regime_changes[-5:]:  # Last 5 changes
                date = change['date']
                
                # Check SPY drawdown after regime downgrade
                try:
                    if change['to'] in ['HIGH RISK', 'EXTREME RISK', 'ELEVATED']:
                        future_date = (datetime.strptime(date, '%Y-%m-%d') + 
                                       timedelta(days=21)).strftime('%Y-%m-%d')
                        
                        current_price = spy.loc[date:date]['Close'].iloc[0]
                        future_prices = spy.loc[date:future_date]['Close']
                        
                        if len(future_prices) > 0:
                            max_dd = ((future_prices.min() - current_price) / current_price) * 100
                            
                            self.report_lines.extend([
                                f"📅 {date}: {change['from']} → {change['to']} (Score: {change['score']:.1f})",
                                f"   SPY max drawdown next 21 days: {max_dd:.2f}%",
                                f"   {'✅ Correct signal' if max_dd < -3 else '⚠️  False alarm' if max_dd > 0 else '○ Neutral'}",
                                ""
                            ])
                except:
                    self.report_lines.append(f"📅 {date}: {change['from']} → {change['to']} (Score: {change['score']:.1f})")
                    self.report_lines.append("   (Future data not yet available)")
                    self.report_lines.append("")
        else:
            self.report_lines.append("No regime changes in historical period")
        
        self.report_lines.append("")
    
    def _analyze_alert_timing(self, spy):
        """Check if alerts preceded market moves"""
        self.report_lines.extend([
            "🚨 ALERT TIMING ANALYSIS",
            "=" * 70,
            ""
        ])
        
        if 'alerts' not in self.history or not self.history['alerts']:
            self.report_lines.append("No alerts in history yet")
            self.report_lines.append("")
            return
        
        alerts = self.history['alerts']
        critical_alerts = [a for a in alerts if a.get('type') in 
                           ['HIDDEN DANGER', 'CREDIT WARNING', 'LIQUIDITY DRAIN']]
        
        if critical_alerts:
            self.report_lines.append(f"Critical alerts sent: {len(critical_alerts)}")
            self.report_lines.append("")
            
            for alert in critical_alerts[-3:]:  # Last 3 critical alerts
                date = alert['date']
                alert_type = alert['type']
                
                try:
                    current_price = spy.loc[date:date]['Close'].iloc[0]
                    future_date = (datetime.strptime(date, '%Y-%m-%d') + 
                                   timedelta(days=5)).strftime('%Y-%m-%d')
                    future_price = spy.loc[future_date:future_date]['Close'].iloc[0]
                    
                    forward_return = ((future_price - current_price) / current_price) * 100
                    
                    self.report_lines.extend([
                        f"🚨 {date}: {alert_type}",
                        f"   SPY 5-day return: {forward_return:.2f}%",
                        f"   {'✅ Good call' if forward_return < -2 else '⚠️  Market rallied' if forward_return > 2 else '○ Neutral'}",
                        ""
                    ])
                except:
                    self.report_lines.append(f"🚨 {date}: {alert_type} (future data pending)")
                    self.report_lines.append("")
        else:
            self.report_lines.append("No critical alerts sent yet")
        
        self.report_lines.append("")
    
    def _analyze_false_signals(self):
        """Identify false positives/negatives"""
        self.report_lines.extend([
            "⚖️  SIGNAL QUALITY METRICS",
            "=" * 70,
            ""
        ])
        
        scores = self.history['scores']
        if len(scores) < 7:
            self.report_lines.append("Insufficient data for quality metrics")
            self.report_lines.append("")
            return
        
        # Calculate score stability
        score_values = [s['score'] for s in scores]
        score_std = np.std(score_values)
        score_mean = np.mean(score_values)
        
        # Check for whipsaws (rapid regime changes)
        regime_flips = 0
        prev_regime = None
        for s in scores:
            regime = 'HIGH' if s['score'] < 60 else 'NORMAL' if s['score'] < 75 else 'LOW'
            if prev_regime and regime != prev_regime:
                regime_flips += 1
            prev_regime = regime
        
        self.report_lines.extend([
            f"Score Statistics:",
            f"  • Mean: {score_mean:.1f}/100",
            f"  • Std Dev: {score_std:.1f} ({'stable' if score_std < 10 else 'volatile'})",
            f"  • Range: {min(score_values):.1f} - {max(score_values):.1f}",
            f"  • Regime changes: {regime_flips} ({'low' if regime_flips < 3 else 'high'} whipsaw)",
            "",
            f"Data Quality:",
            f"  • Days tracked: {len(scores)}",
            f"  • Start date: {scores[0]['date']}",
            f"  • Latest: {scores[-1]['date']}",
            ""
        ])
        
        # Recommendations
        if score_std > 15:
            self.report_lines.append("⚠️  High volatility in scores - consider smoothing or threshold adjustment")
        if regime_flips > 5:
            self.report_lines.append("⚠️  Frequent regime changes - may need wider thresholds to reduce whipsaw")
        if score_mean > 80:
            self.report_lines.append("✅ System showing healthy market conditions overall")
        elif score_mean < 50:
            self.report_lines.append("⚠️  Persistent high risk - validate signals aren't too pessimistic")
        
        self.report_lines.append("")


def main():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║         RISK SIGNAL VALIDATION - Walk-Forward Analysis               ║
║         No Additional API Calls - Uses Existing Data Only            ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    analyzer = ValidationAnalyzer()
    analyzer.generate_validation_report()
    
    print("\n✅ Validation complete. Run this monthly to track signal quality.\n")


if __name__ == "__main__":
    main()
