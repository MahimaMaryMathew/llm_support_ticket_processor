# Obstacle Log - Support Ticket Processor

## 1. LLM Returning Markdown in JSON Response
- **Issue:** The model occasionally wrapped its JSON output in ```json ... ``` markdown blocks, causing `json.JSONDecodeError` during parsing.
- **Solution:** Added a lightweight string-cleaning step in `classify_ticket()` to strip backticks and the `json` prefix before running `json.loads()`.

## 2. API Rate Limits / Network Failures
- **Issue:** Potential risk of script crashing if an API call times out or fails midway through processing a batch of tickets.
- **Solution:** Wrapped the API call and `json.loads()` inside a robust `try/except` block, returning a fallback dictionary with "Unclassified" values so the loop continues uninterrupted.
