# Client Proposal — Hacker News Frontpage QA

**Subject:** Re: Hacker News Frontpage QA

Hi [Client Name],

I saw you need reliable Hacker News extraction for your PostgreSQL database. The primary bottleneck with HN is its legacy HTML table layout; relying on basic scrapers often breaks when non-standard rows (like "Ask HN" or sponsored jobs) lack domains or points.

I've built a headless Playwright + Pandas pipeline that robustly pairs DOM elements without fragile XPaths, cleanses the text, and enforces strict schema typing (e.g., dynamically casting "discuss" to 0 comments). See the attached 30-row hn_top30.csv and passing Pytest verification log.

A couple of quick questions before we scale this:

- How frequently will this cron job run against the site?
- Do you need historical pagination, or just the live top 30?

We operate on a strict 3-milestone escrow structure: 35% Kickoff (Schema Lock), 40% Core Build (Verified Demo), and 25% Handover (Docker/Repo + IP Transfer).

Let me know if you are ready to review the architecture.
