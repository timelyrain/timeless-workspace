#!/usr/bin/env python3
"""
Decision Matrix Alert System
Synthesizes institutional risk signal + VaR/CVaR analysis into actionable daily recommendations.

Architecture:
    1. Loads latest risk_history.json (institutional risk score 0-100)
    2. Loads latest portfolio_risk_YYYYMMDD.json (VaR/CVaR metrics)
    3. Loads fetch-ibkr-positions.xlsx (current portfolio composition)
    4. Applies 15-quadrant decision matrix (Risk Score × VaR Level)
    5. Generates specific recommendations based on current holdings
    6. Sends consolidated Telegram alert (summary + full details)

Decision Matrix:
    Risk Score × VaR Level = 15 quadrants with specific guidance
    
    VaR Levels:
        LOW:    Daily VaR < 0.30% of portfolio
        MEDIUM: Daily VaR 0.30-0.60% of portfolio  
        HIGH:   Daily VaR > 0.60% of portfolio
    
    Risk Score Tiers:
        EXTREME:  0-40  (Crisis mode)
        HIGH:     40-60 (Defensive positioning)
        ELEVATED: 60-75 (Cautious but invested)
        NORMAL:   75-90 (Full deployment)
        ALL_CLEAR: 90+  (Aggressive growth)

Usage:
    python decision-matrix-alert.py

Requirements:
    - risk_history.json (from institutional-risk-signal.py)
    - portfolio_risk_YYYYMMDD.json (from portfolio-risk-var-cvar.py)
    - fetch-ibkr-positions.xlsx (from fetch-ibkr-positions.py)
    - TELEGRAM_TOKEN_DECISION_MATRIX in .env

Author: timeless-workspace
Created: 2026-01-25
"""

import os
import json
import pandas as pd
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Tuple, Optional

# Load environment variables
load_dotenv()

class DecisionMatrixAnalyzer:
    """Synthesizes risk signals into actionable recommendations."""
    
    def __init__(self):
        self.telegram_token = os.environ.get("TELEGRAM_TOKEN_DECISION_MATRIX")
        self.chat_id = os.environ.get("CHAT_ID")
        self.projects_dir = Path(__file__).parent
        
        # Decision matrix configuration
        self.var_thresholds = {
            'LOW': 0.30,      # < 0.30% daily VaR
            'MEDIUM': 0.60    # 0.30-0.60% daily VaR, >0.60% = HIGH
        }
        
        self.risk_tiers = {
            'EXTREME': (0, 40),
            'HIGH': (40, 60),
            'ELEVATED': (60, 75),
            'NORMAL': (75, 90),
            'ALL_CLEAR': (90, 101)
        }
        
    def load_risk_history(self) -> Dict:
        """Load latest institutional risk score."""
        risk_file = self.projects_dir.parent / "risk_history.json"
        
        if not risk_file.exists():
            raise FileNotFoundError(f"Risk history not found: {risk_file}")
        
        with open(risk_file, 'r') as f:
            history = json.load(f)
        
        # Handle different JSON structures
        if isinstance(history, dict) and 'scores' in history:
            # Structure: {"scores": [...]}
            scores = history['scores']
            if not scores:
                raise ValueError("Risk history scores array is empty")
            latest = scores[-1]
        elif isinstance(history, list):
            # Structure: [...]
            if not history:
                raise ValueError("Risk history is empty")
            latest = history[-1]
        else:
            raise ValueError(f"Unexpected risk history structure: {type(history)}")
        
        # Extract fields with fallbacks for different formats
        score = latest.get('risk_score') or latest.get('score', 0)
        tier = latest.get('assessment') or latest.get('tier', 'UNKNOWN')
        
        # Classify tier from score if not provided
        if tier == 'UNKNOWN' and score:
            if score >= 90:
                tier = 'ALL CLEAR'
            elif score >= 75:
                tier = 'NORMAL'
            elif score >= 60:
                tier = 'ELEVATED RISK'
            elif score >= 40:
                tier = 'HIGH RISK'
            else:
                tier = 'EXTREME RISK'
        
        return {
            'score': score,
            'tier': tier,
            'allocation': latest.get('portfolio_allocation', {}),
            'date': latest['date']
        }
    
    def load_var_cvar(self) -> Dict:
        """Load latest VaR/CVaR analysis."""
        # Find most recent portfolio_risk_*.json
        portfolio_files = sorted(self.projects_dir.glob("portfolio_risk_*.json"), reverse=True)
        
        if not portfolio_files:
            raise FileNotFoundError("No portfolio risk files found")
        
        with open(portfolio_files[0], 'r') as f:
            var_data = json.load(f)
        
        # Extract VaR/CVaR values (use historical method as primary)
        var_95 = var_data['var']['95'].get('historical') or var_data['var']['95'].get('parametric', 0)
        cvar_95 = var_data['cvar']['95'].get('historical') or var_data['cvar']['95'].get('parametric', 0)
        var_99 = var_data['var']['99'].get('historical') or var_data['var']['99'].get('parametric', 0)
        cvar_99 = var_data['cvar']['99'].get('historical') or var_data['cvar']['99'].get('parametric', 0)
        
        # Find worst single-day loss from position risks
        worst_loss = 0
        if 'position_risk' in var_data:
            for pos in var_data['position_risk']:
                cvar_dollar = abs(pos.get('cvar_95_dollar', 0))
                if cvar_dollar > worst_loss:
                    worst_loss = cvar_dollar
        
        return {
            'var_95': var_95,
            'cvar_95': cvar_95,
            'var_99': var_99,
            'cvar_99': cvar_99,
            'worst_loss': worst_loss,
            'position_risks': var_data.get('position_risk', []),
            'date': var_data.get('timestamp', '').split('T')[0],
            'file': portfolio_files[0].name,
            'portfolio_value': var_data.get('portfolio_value', 0)
        }
    
    def load_portfolio(self) -> Dict:
        """Load current portfolio composition."""
        excel_file = self.projects_dir / "fetch-ibkr-positions.xlsx"
        
        if not excel_file.exists():
            raise FileNotFoundError(f"Portfolio file not found: {excel_file}")
        
        # Read Summary sheet for totals
        summary = pd.read_excel(excel_file, sheet_name='Summary')
        
        # Extract portfolio value from TOTAL row
        total_row = summary[summary['Account'].str.contains('TOTAL', na=False, case=False)]
        if total_row.empty:
            raise ValueError("No TOTAL row found in Summary sheet")
        
        # Column might be 'Account Total' or 'Total Value'
        total_col = 'Account Total' if 'Account Total' in summary.columns else 'Total Value'
        portfolio_value_str = str(total_row[total_col].iloc[0])
        
        # Remove $ and commas, convert to float
        portfolio_value = float(portfolio_value_str.replace('$', '').replace(',', ''))
        
        # Read positions
        positions_hk = pd.read_excel(excel_file, sheet_name='PositionsHK')
        positions_al = pd.read_excel(excel_file, sheet_name='PositionsAL')
        
        all_positions = pd.concat([positions_hk, positions_al], ignore_index=True)
        
        # Calculate concentration (use PositionValueUSD column)
        all_positions['weight'] = all_positions['PositionValueUSD'] / portfolio_value * 100
        
        return {
            'total_value': portfolio_value,
            'positions': all_positions.to_dict('records'),
            'top_holdings': all_positions.nlargest(5, 'weight')[['Symbol', 'weight']].to_dict('records'),
            'count': len(all_positions)
        }
    
    def classify_var_level(self, var_pct: float) -> str:
        """Classify VaR as LOW/MEDIUM/HIGH based on percentage of portfolio."""
        if var_pct < self.var_thresholds['LOW']:
            return 'LOW'
        elif var_pct < self.var_thresholds['MEDIUM']:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def classify_risk_tier(self, score: int) -> str:
        """Classify risk score into tier."""
        for tier, (low, high) in self.risk_tiers.items():
            if low <= score < high:
                return tier
        return 'UNKNOWN'
    
    def get_decision_quadrant(self, risk_tier: str, var_level: str) -> Dict:
        """
        Return actionable recommendations based on decision matrix quadrant.
        
        Matrix structure:
            EXTREME/LOW → Defensive but stable
            EXTREME/MEDIUM → Reduce exposure
            EXTREME/HIGH → Emergency de-risk
            
            HIGH/LOW → Hold current, watch closely
            HIGH/MEDIUM → Trim aggressive positions
            HIGH/HIGH → Significant reduction needed
            
            ELEVATED/LOW → Fully invested, cautious adds
            ELEVATED/MEDIUM → Hold steady
            ELEVATED/HIGH → Reduce volatility
            
            NORMAL/LOW → Add to growth positions
            NORMAL/MEDIUM → Maintain allocation
            NORMAL/HIGH → Rebalance high-risk positions
            
            ALL_CLEAR/LOW → Aggressive growth mode
            ALL_CLEAR/MEDIUM → Full deployment
            ALL_CLEAR/HIGH → Rotate to higher conviction
        """
        
        matrix = {
            ('EXTREME', 'LOW'): {
                'headline': '🔴 DEFENSIVE MODE',
                'action': 'Hold defensive positions',
                'detail': 'Market in crisis but portfolio stable. Maintain cash reserves, avoid new positions.',
                'new_positions': 'BLOCKED',
                'growth_adds': 'BLOCKED',
                'options': 'Protective puts only'
            },
            ('EXTREME', 'MEDIUM'): {
                'headline': '🔴 REDUCE EXPOSURE',
                'action': 'Trim to 60% equity exposure',
                'detail': 'Crisis + elevated portfolio risk. Sell lowest conviction positions, raise cash to 40%.',
                'new_positions': 'BLOCKED',
                'growth_adds': 'BLOCKED',
                'options': 'Protective hedges'
            },
            ('EXTREME', 'HIGH'): {
                'headline': '🔴 EMERGENCY DE-RISK',
                'action': 'Cut equity to 40%, raise cash immediately',
                'detail': 'Severe market stress + dangerous portfolio volatility. Execute emergency rebalancing.',
                'new_positions': 'BLOCKED',
                'growth_adds': 'BLOCKED',
                'options': 'Close risky positions'
            },
            ('HIGH', 'LOW'): {
                'headline': '🟠 HOLD & WATCH',
                'action': 'Maintain current positions',
                'detail': 'Elevated market risk but stable portfolio. No changes needed, monitor daily.',
                'new_positions': 'PAUSED',
                'growth_adds': 'PAUSED',
                'options': 'Review existing'
            },
            ('HIGH', 'MEDIUM'): {
                'headline': '🟠 TRIM AGGRESSIVE',
                'action': 'Reduce high-beta positions by 15%',
                'detail': 'High market risk + moderate portfolio volatility. Trim tech/growth, hold quality.',
                'new_positions': 'PAUSED',
                'growth_adds': 'BLOCKED',
                'options': 'Close speculative'
            },
            ('HIGH', 'HIGH'): {
                'headline': '🟠 SIGNIFICANT REDUCTION',
                'action': 'Cut total exposure to 70%',
                'detail': 'Dangerous combination. Reduce size across board, focus on highest conviction only.',
                'new_positions': 'BLOCKED',
                'growth_adds': 'BLOCKED',
                'options': 'Defensive only'
            },
            ('ELEVATED', 'LOW'): {
                'headline': '🟡 CAUTIOUS DEPLOYMENT',
                'action': 'Fully invested, add 5% to winners',
                'detail': 'Market watchful but portfolio stable. Small adds to highest conviction positions.',
                'new_positions': 'APPROVED (small size)',
                'growth_adds': 'APPROVED (5% adds)',
                'options': 'Limited new strategies'
            },
            ('ELEVATED', 'MEDIUM'): {
                'headline': '🟡 HOLD STEADY',
                'action': 'No changes recommended',
                'detail': 'Balanced risk profile. Monitor both signals, await clearer direction.',
                'new_positions': 'PAUSED',
                'growth_adds': 'PAUSED',
                'options': 'Maintain current'
            },
            ('ELEVATED', 'HIGH'): {
                'headline': '🟡 REDUCE VOLATILITY',
                'action': 'Trim highest VaR contributors by 20%',
                'detail': 'Market uncertainty + excessive portfolio risk. Focus reduction on most volatile positions.',
                'new_positions': 'PAUSED',
                'growth_adds': 'BLOCKED',
                'options': 'Review risky strategies'
            },
            ('NORMAL', 'LOW'): {
                'headline': '🟢 ADD TO GROWTH',
                'action': 'Deploy 10% cash to growth positions',
                'detail': 'Normal market + stable portfolio. Add to secular growth themes, maintain diversification.',
                'new_positions': 'APPROVED',
                'growth_adds': 'APPROVED (10% adds)',
                'options': 'Selective strategies'
            },
            ('NORMAL', 'MEDIUM'): {
                'headline': '🟢 MAINTAIN ALLOCATION',
                'action': 'Hold current portfolio',
                'detail': 'Healthy market conditions. Stay fully invested, rebalance if drift exceeds 5%.',
                'new_positions': 'APPROVED (normal size)',
                'growth_adds': 'APPROVED (5% adds)',
                'options': 'Normal activity'
            },
            ('NORMAL', 'HIGH'): {
                'headline': '🟢 REBALANCE RISK',
                'action': 'Reduce top 3 VaR contributors by 15%',
                'detail': 'Good market but portfolio concentrated. Improve diversification, trim oversized winners.',
                'new_positions': 'APPROVED',
                'growth_adds': 'PAUSED',
                'options': 'Review concentrations'
            },
            ('ALL_CLEAR', 'LOW'): {
                'headline': '🟢 AGGRESSIVE GROWTH',
                'action': 'Deploy all available cash',
                'detail': 'Optimal conditions. Full deployment into highest conviction growth ideas.',
                'new_positions': 'APPROVED (aggressive)',
                'growth_adds': 'APPROVED (15% adds)',
                'options': 'Active strategies'
            },
            ('ALL_CLEAR', 'MEDIUM'): {
                'headline': '🟢 FULL DEPLOYMENT',
                'action': 'Add 10% to core positions',
                'detail': 'Strong market + healthy portfolio. Increase size in best ideas, maintain discipline.',
                'new_positions': 'APPROVED',
                'growth_adds': 'APPROVED (10% adds)',
                'options': 'Full strategies'
            },
            ('ALL_CLEAR', 'HIGH'): {
                'headline': '🟢 ROTATE TO CONVICTION',
                'action': 'Trim laggards, add to winners',
                'detail': 'Great market but portfolio bloated. Consolidate into top 15-20 highest conviction names.',
                'new_positions': 'APPROVED',
                'growth_adds': 'APPROVED',
                'options': 'Optimize existing'
            }
        }
        
        return matrix.get((risk_tier, var_level), {
            'headline': '⚠️ UNKNOWN STATE',
            'action': 'Manual review required',
            'detail': 'Unable to classify current conditions.',
            'new_positions': 'PAUSED',
            'growth_adds': 'PAUSED',
            'options': 'Review all'
        })
    
    def generate_specific_recommendations(self, quadrant: Dict, portfolio: Dict, var_data: Dict) -> List[str]:
        """Generate specific actions based on current portfolio holdings."""
        recommendations = []
        
        # Extract action type from headline
        action_type = quadrant['action'].lower()
        
        # Get top risk contributors (sorted by CVaR contribution)
        position_risks = var_data.get('position_risks', [])
        top_risks = sorted(position_risks, key=lambda x: abs(x.get('cvar_95_dollar', 0)), reverse=True)[:5]
        
        if 'reduce' in action_type or 'cut' in action_type or 'trim' in action_type:
            # Specific reduction recommendations
            for pos in top_risks[:3]:
                symbol = pos['symbol']
                current_value = pos['value']
                cvar_contrib_pct = abs(pos.get('cvar_95_dollar', 0)) / var_data.get('portfolio_value', 1) * 100
                
                if 'emergency' in action_type:
                    reduction_pct = 50
                elif 'significant' in action_type:
                    reduction_pct = 30
                else:
                    reduction_pct = 20
                
                target_sell = current_value * (reduction_pct / 100)
                recommendations.append(
                    f"Sell ${target_sell:,.0f} of {symbol} ({reduction_pct}% reduction, "
                    f"currently {cvar_contrib_pct:.1f}% of risk)"
                )
        
        elif 'add' in action_type or 'deploy' in action_type:
            # Specific growth recommendations
            total_value = portfolio['total_value']
            
            if 'aggressive' in action_type:
                deploy_pct = 15
            elif 'growth' in action_type:
                deploy_pct = 10
            else:
                deploy_pct = 5
            
            deploy_amount = total_value * (deploy_pct / 100)
            
            # Find positions with lowest risk (good candidates to add)
            low_risk_positions = sorted(position_risks, 
                                       key=lambda x: abs(x.get('cvar_95_dollar', 0)))[:3]
            
            per_position = deploy_amount / 3
            for pos in low_risk_positions:
                cvar_contrib_pct = abs(pos.get('cvar_95_dollar', 0)) / var_data.get('portfolio_value', 1) * 100
                recommendations.append(
                    f"Add ${per_position:,.0f} to {pos['symbol']} "
                    f"(low risk: {cvar_contrib_pct:.1f}% of portfolio risk)"
                )
        
        elif 'rebalance' in action_type:
            # Concentration recommendations
            for holding in portfolio['top_holdings'][:3]:
                if holding['weight'] > 25:
                    target_weight = 20
                    reduction = (holding['weight'] - target_weight) / holding['weight'] * 100
                    recommendations.append(
                        f"Reduce {holding['Symbol']} from {holding['weight']:.1f}% to {target_weight}% "
                        f"(sell {reduction:.0f}% of position)"
                    )
        
        # Add concentration warning if any position > 25%
        for holding in portfolio['top_holdings']:
            if holding['weight'] > 25:
                recommendations.append(
                    f"⚠️ Concentration Alert: {holding['Symbol']} at {holding['weight']:.1f}% "
                    f"(target: <25%)"
                )
        
        return recommendations
    
    def format_telegram_message(self, risk_data: Dict, var_data: Dict, 
                                portfolio: Dict, quadrant: Dict, 
                                recommendations: List[str]) -> str:
        """Format comprehensive Telegram message with summary + details."""
        
        # Calculate VaR percentage
        var_pct = (var_data['var_95'] / portfolio['total_value']) * 100
        var_level = self.classify_var_level(var_pct)
        
        # Build message sections
        msg_parts = []
        
        # ===== SUMMARY SECTION =====
        msg_parts.append("📊 DAILY DECISION MATRIX")
        msg_parts.append("")
        msg_parts.append(f"{quadrant['headline']}")
        msg_parts.append(f"Action: {quadrant['action']}")
        msg_parts.append("")
        msg_parts.append(f"Risk Score: {risk_data['score']:.2f}/100 ({risk_data['tier']})")
        msg_parts.append(f"VaR Level: {var_level} (${var_data['var_95']:,.0f} / {var_pct:.2f}%)")
        msg_parts.append(f"Portfolio: ${portfolio['total_value']:,.0f} ({portfolio['count']} positions)")
        msg_parts.append("")
        
        # Decision gates
        msg_parts.append("🚦 Decision Gates:")
        msg_parts.append(f"  • New Positions: {quadrant['new_positions']}")
        msg_parts.append(f"  • Growth Adds: {quadrant['growth_adds']}")
        msg_parts.append(f"  • Options: {quadrant['options']}")
        msg_parts.append("")
        
        # Specific recommendations
        if recommendations:
            msg_parts.append("📋 Specific Actions:")
            for i, rec in enumerate(recommendations[:5], 1):  # Top 5 recommendations
                msg_parts.append(f"  {i}. {rec}")
            msg_parts.append("")
        
        # ===== FULL DETAILS SECTION =====
        msg_parts.append("📖 DETAILED ANALYSIS")
        msg_parts.append("")
        
        # Market assessment
        msg_parts.append("🌐 Market Risk Assessment:")
        msg_parts.append(f"  Risk Score: {risk_data['score']:.2f}/100")
        msg_parts.append(f"  Tier: {risk_data['tier']}")
        msg_parts.append(f"  Date: {risk_data['date']}")
        
        if risk_data['allocation']:
            msg_parts.append("  Target Allocation:")
            for key, val in risk_data['allocation'].items():
                if isinstance(val, (int, float)):
                    msg_parts.append(f"    • {key}: {val}%")
        msg_parts.append("")
        
        # Portfolio risk metrics
        msg_parts.append("📊 Portfolio Risk Metrics:")
        msg_parts.append(f"  VaR (95%): ${var_data['var_95']:,.0f} ({var_pct:.2f}%)")
        msg_parts.append(f"  CVaR (95%): ${var_data['cvar_95']:,.0f}")
        msg_parts.append(f"  VaR (99%): ${var_data['var_99']:,.0f}")
        msg_parts.append(f"  CVaR (99%): ${var_data['cvar_99']:,.0f}")
        msg_parts.append(f"  Worst Loss: ${var_data['worst_loss']:,.0f}")
        msg_parts.append("")
        
        # Top risk contributors
        msg_parts.append("⚠️ Top Risk Contributors:")
        position_risks = var_data.get('position_risks', [])
        top_risks = sorted(position_risks, 
                          key=lambda x: abs(x.get('cvar_95_dollar', 0)), reverse=True)[:5]
        for i, pos in enumerate(top_risks, 1):
            cvar_contrib_pct = abs(pos.get('cvar_95_dollar', 0)) / var_data.get('portfolio_value', 1) * 100
            msg_parts.append(
                f"  {i}. {pos['symbol']}: ${pos['value']:,.0f} "
                f"({cvar_contrib_pct:.1f}% of risk)"
            )
        msg_parts.append("")
        
        # Top holdings
        msg_parts.append("💼 Top Holdings:")
        for i, holding in enumerate(portfolio['top_holdings'], 1):
            msg_parts.append(f"  {i}. {holding['Symbol']}: {holding['weight']:.1f}%")
        msg_parts.append("")
        
        # Strategy explanation
        msg_parts.append("💡 Strategy Context:")
        msg_parts.append(f"  {quadrant['detail']}")
        msg_parts.append("")
        
        # Timestamp
        msg_parts.append(f"⏰ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        msg_parts.append("═══════════════════════════")
        
        return "\n".join(msg_parts)
    
    def send_telegram_alert(self, message: str):
        """Send decision matrix alert via Telegram."""
        if not self.telegram_token or not self.chat_id:
            print("⚠️  Telegram not configured, skipping alert")
            return
        
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            print("✅ Decision matrix alert sent to Telegram")
        except Exception as e:
            print(f"❌ Failed to send Telegram alert: {e}")
    
    def save_decision_history(self, risk_data: Dict, var_data: Dict, 
                             quadrant: Dict, recommendations: List[str]):
        """Save decision history to JSON for tracking."""
        history_file = self.projects_dir.parent / "decision_history.json"
        
        # Load existing history
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        # Add new entry
        entry = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat(),
            'risk_score': risk_data['score'],
            'risk_tier': risk_data['tier'],
            'var_95': var_data['var_95'],
            'cvar_95': var_data['cvar_95'],
            'var_level': self.classify_var_level((var_data['var_95'] / var_data.get('portfolio_value', 1)) * 100),
            'quadrant': quadrant['headline'],
            'action': quadrant['action'],
            'recommendations_count': len(recommendations)
        }
        
        history.append(entry)
        
        # Keep last 90 days
        history = history[-90:]
        
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        print(f"✅ Decision history saved: {history_file}")
    
    def run(self):
        """Main execution flow."""
        print("=" * 60)
        print("DECISION MATRIX ALERT SYSTEM")
        print("=" * 60)
        print()
        
        try:
            # Load all data sources
            print("📥 Loading data sources...")
            risk_data = self.load_risk_history()
            print(f"  ✓ Risk score: {risk_data['score']}/100 ({risk_data['tier']})")
            
            var_data = self.load_var_cvar()
            print(f"  ✓ VaR/CVaR: ${var_data['var_95']:,.0f} / ${var_data['cvar_95']:,.0f}")
            
            portfolio = self.load_portfolio()
            print(f"  ✓ Portfolio: ${portfolio['total_value']:,.0f} ({portfolio['count']} positions)")
            print()
            
            # Classify current state
            print("🔍 Analyzing current state...")
            var_pct = (var_data['var_95'] / portfolio['total_value']) * 100
            var_level = self.classify_var_level(var_pct)
            risk_tier = self.classify_risk_tier(risk_data['score'])
            
            print(f"  Risk Tier: {risk_tier}")
            print(f"  VaR Level: {var_level} ({var_pct:.2f}%)")
            print()
            
            # Get decision quadrant
            print("📊 Determining recommendation...")
            quadrant = self.get_decision_quadrant(risk_tier, var_level)
            print(f"  {quadrant['headline']}")
            print(f"  Action: {quadrant['action']}")
            print()
            
            # Generate specific recommendations
            print("💡 Generating specific recommendations...")
            recommendations = self.generate_specific_recommendations(quadrant, portfolio, var_data)
            print(f"  Generated {len(recommendations)} specific actions")
            print()
            
            # Format message
            message = self.format_telegram_message(risk_data, var_data, portfolio, 
                                                   quadrant, recommendations)
            
            # Send alert
            print("📤 Sending Telegram alert...")
            self.send_telegram_alert(message)
            print()
            
            # Save history
            print("💾 Saving decision history...")
            self.save_decision_history(risk_data, var_data, quadrant, recommendations)
            print()
            
            print("=" * 60)
            print("✅ DECISION MATRIX ANALYSIS COMPLETE")
            print("=" * 60)
            
        except Exception as e:
            error_msg = f"❌ ERROR: {str(e)}"
            print(error_msg)
            
            # Send error notification
            if self.telegram_token and self.chat_id:
                self.send_telegram_alert(
                    f"🚨 Decision Matrix Alert Failed\n\n"
                    f"Error: {str(e)}\n"
                    f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            
            raise


if __name__ == "__main__":
    analyzer = DecisionMatrixAnalyzer()
    analyzer.run()
