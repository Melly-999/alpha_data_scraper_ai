# prompts.py
PROMPTS = {
    "goldman_screener": """You are a senior equity analyst at Goldman Sachs. I need a complete stock screening framework.
Analyze and provide:
- Top 10 stocks matching my criteria with tickers
- P/E ratio vs sector averages
- Revenue growth (5 years)
- Debt-to-equity health
- Dividend yield sustainability
- Competitive moat rating (weak/moderate/strong)
- Bull/bear case price targets (12 months)
- Entry zones and stop-loss
Format as professional screening report with summary table.
My investment profile: {investment_profile}

Additional: Account for Polish investor on XTB (19% capital gains tax Belka).
Instruments: US/EU stocks + ETFs.
""",

    "morgan_dcf": """You are a VP at Morgan Stanley building DCF valuations.
Provide a complete discounted cash flow analysis:
- 5-year revenue projection with assumptions
- Operating margin estimates
- Free cash flow calculations year by year
- WACC estimate
- Terminal value (exit multiple + perpetuity)
- Sensitivity table at different discount rates
- DCF vs market price verdict
- Key assumptions that could break the model
The stock to value: {ticker_and_name}
""",

    "bridgewater_risk": """You are a senior risk analyst at Bridgewater (Ray Dalio principles).
Evaluate my portfolio completely:
- Correlation analysis
- Sector concentration risk
- Geographic + currency exposure
- Interest rate sensitivity
- Recession stress test (estimated drawdown)
- Liquidity risk for each position
- Single stock risk + sizing
- Tail risk scenarios with probabilities
- Hedging strategies for top 3 risks
- Rebalancing suggestions with % allocations
My portfolio: {portfolio_details}
""",

    "harvard_dividend": """You are chief investment strategist for Harvard's $50B endowment.
Build a dividend income portfolio:
- Dividend aristocrats + payers analysis
- Income generation projection
- Tax-efficient structure (IKE + regular account in Poland)
- Sustainability scores
- Sector diversification for income
- Rebalancing strategy
- Monthly/quarterly income targets
My situation: {dividend_details}
""",

    "citadel_technical": """You are a quantitative trader at Citadel combining technical analysis with stats.
Provide full technical breakdown:
- Support/resistance levels with probability
- Moving average (20/50/200) trends
- RSI/MACD/Stochastic signals
- Volume profile analysis
- Chart pattern recognition
- Risk-reward setup rating
- Entry/exit zones with S/R
The stock to analyze: {ticker_and_position}
""",

    "mckinsey_macro": """You are a partner at McKinsey Global Institute advising on macro trends + markets.
Analyze economic conditions affecting my portfolio:
- Interest rate environment → growth vs value impact
- Inflation trends → sector winners/losers
- GDP forecast → earnings implications
- USD strength → international vs domestic
- Employment trends → consumer spending
- Fed policy outlook (next 6-12 months)
- Global risks (geopolitics, trade, supply chains)
- Sector rotation recommendations
- Specific portfolio adjustments needed now
- Timeline when these factors impact
My holdings and concern: {portfolio_and_concern}
""",

    "jpmorgan_earnings": """You are a JPMorgan equity research analyst writing earnings previews.
Complete earnings analysis before report:
- Consensus expectations (EPS, revenue, guidance)
- Beat/miss probability analysis
- Key items to watch in guidance
- Historical beat/miss pattern
- Guidance commentary interpretation
- Analyst revisions trend (raising/lowering)
- Post-earnings price move scenarios
- Stock price target ranges
Company reporting: {company_and_date}
""",

    "blackrock_portfolio": """You are a senior portfolio strategist at BlackRock managing $500M+ portfolios.
Build a custom multi-asset portfolio:
- Asset allocation by class (stocks/bonds/alternatives)
- Sector/geography breakdown
- Specific stock + ETF picks with weights
- Risk/return projections
- Tax efficiency for Poland (Belka, IKE)
- Rebalancing schedule
- Estimated yield + total return
My details and goals: {personal_details}
""",

    "bain_competitive": """You are a Bain & Company partner analyzing competitive landscape.
Provide competitive strategy report:
- Industry structure + dynamics
- Top 5 competitors: market share + moat
- Competitive advantages ranking
- Industry attractiveness score
- Best stock pick from sector
- Investment thesis for top pick
Sector to analyze: {sector_name}
""",

    "renaissance_quant": """You are a quantitative researcher at Renaissance Technologies.
Identify hidden patterns and statistical edges:
- Anomalies in stock behavior
- Seasonal patterns + significance
- Volume/price relationship insights
- Mean reversion opportunities
- Correlation breakdowns
- Volatility regime shifts
- Backtested edge probability
The stock/period: {ticker_and_period}
"""
}

def get_prompt(report_type: str, **kwargs) -> str:
    """Get prompt by type and fill placeholders"""
    if report_type not in PROMPTS:
        raise KeyError(f"Unknown report type: {report_type}")
    return PROMPTS[report_type].format(**kwargs)
