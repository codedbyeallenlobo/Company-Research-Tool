# Company Research Agent

Takes a company name, searches the web with Tavily, and writes a short brief with Claude Haiku.

## Setup

```bash
pip install -r requirements.txt
```

Set two keys in your environment:

- `ANTHROPIC_API_KEY` — from console.anthropic.com
- `TAVILY_API_KEY` — from tavily.com

## Usage

```bash
python research_agent.py "Anthropic"
```

Progress goes to stderr, the brief to stdout — so you can redirect it:

```bash
python research_agent.py "Stripe" > stripe.md
```

## How it works

1. Three Tavily searches (overview, financials, recent news), 3 results each, with
   `include_raw_content` so the full page text comes back in the same call.
2. The pages are numbered and trimmed to 4k characters each.
3. One Claude Haiku call writes the brief with inline `[n]` citations.
