"""Company research agent: searches the web with Tavily, writes a brief with Claude."""

import os
import sys

import anthropic
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()  # reads .env in this folder, if present

# The Windows console defaults to cp1252, which mangles dashes and quotes.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")

MODEL = "claude-haiku-5-5"

PROMPT = """You are a research analyst. Using only the search results below, write a
short brief about {company}.

Use these sections, a few sentences each:
- What they do
- Products / services
- Size & footprint (funding, revenue, headcount, locations — whatever is known)
- Recent news
- Notable risks or open questions

Rules: only state what the sources support. If something is unknown, say so rather
than guessing. Cite source URLs inline like [1], [2] matching the numbering below.

SEARCH RESULTS
{results}"""


def require_key(name, where):
    key = os.environ.get(name)
    if not key:
        sys.exit(
            f"{name} is not set.\n"
            f"Get one at {where}, then add a line to a .env file in this folder:\n"
            f"    {name}=your-key-here\n"
            f"or set it for this shell:\n"
            f"    $env:{name} = 'your-key-here'"
        )
    return key


def search(company):
    """Find and read pages about the company."""
    tavily = TavilyClient(api_key=require_key("TAVILY_API_KEY", "https://tavily.com"))
    results = []
    for query in (
        f"{company} company overview what they do",
        f"{company} funding revenue employees",
        f"{company} news 2026",
    ):
        response = tavily.search(
            query=query,
            search_depth="advanced",
            max_results=3,
            include_raw_content=True,
        )
        results.extend(response["results"])
    return results


def format_results(results):
    """Number the sources and include page text, trimmed to keep the prompt sane."""
    chunks = []
    for i, r in enumerate(results, 1):
        body = (r.get("raw_content") or r.get("content") or "")[:4000]
        chunks.append(f"[{i}] {r['title']}\nURL: {r['url']}\n{body}")
    return "\n\n---\n\n".join(chunks)


def write_brief(company, results):
    client = anthropic.Anthropic(
        api_key=require_key("ANTHROPIC_API_KEY", "https://console.anthropic.com")
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        messages=[
            {
                "role": "user",
                "content": PROMPT.format(company=company, results=format_results(results)),
            }
        ],
    )
    return "".join(b.text for b in response.content if b.type == "text")


def research(company):
    print(f"Searching for {company}...", file=sys.stderr)
    results = search(company)
    print(f"Read {len(results)} pages. Writing brief...", file=sys.stderr)
    return write_brief(company, results)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python research_agent.py <company name>")
    print(research(" ".join(sys.argv[1:])))
