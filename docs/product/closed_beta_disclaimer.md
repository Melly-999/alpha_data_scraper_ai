# MellyTrade Closed Beta Disclaimer

## Purpose

MellyTrade Closed Beta is a read-only AI trading research terminal for educational, research, and product-testing purposes.

It is designed to help users understand:
- market context
- advisory scanner output
- risk posture
- audit events
- broker/systems status
- demo/fallback behavior

## What MellyTrade is

MellyTrade is:
- a read-only research terminal
- a dry-run demo environment
- a signal explanation and observability tool
- a risk-first product prototype
- a closed beta for feedback and UI/workflow validation

## What MellyTrade is not

MellyTrade is not:
- a live trading bot
- an execution platform
- a broker
- a financial advisor
- a personal investment recommendation service
- a guaranteed-profit product
- a replacement for independent analysis
- a regulated investment advisory service

## No investment advice

All content shown by MellyTrade is for educational and research purposes only.

MellyTrade does not provide:
- personal investment advice
- individualized recommendations
- guaranteed outcomes
- guaranteed profits
- tax advice
- legal advice
- financial planning advice

Users are responsible for their own decisions.

## No live trading

Closed Beta must remain:

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk<=1%
```

MellyTrade Closed Beta does not place, modify, cancel, or execute orders.

## No broker execution

Broker-related surfaces are read-only or safe-disconnected.

The beta must not:
- connect to live broker execution
- place market orders
- place limit orders
- cancel orders
- modify orders
- bypass risk policy
- expose account IDs or credentials

## Demo / fallback data

Closed Beta may show seeded, synthetic, or fallback data.

Users must treat demo/fallback data as:
- non-live
- non-executable
- educational
- not financial advice
- not suitable for real trading decisions

## Human review required

Any scanner output or signal-like data is advisory only.

Human review is always required.

Scanner labels such as:
- `WATCH`
- `HOLD`
- `LONG_SETUP`
- `SHORT_SETUP`
- `NO_TRADE`

are research labels only and are not instructions to trade.

## User responsibility

Users are responsible for:
- understanding the read-only nature of the beta
- not treating demo output as live market advice
- not entering trades based solely on MellyTrade output
- reporting bugs or confusing wording
- protecting their own broker credentials and accounts

## Safety posture

The required safety posture is:

```text
autotrade=false
dry_run=true
read_only=true
live_orders_blocked=true
max risk<=1%
```
