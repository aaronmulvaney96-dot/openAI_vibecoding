# Stream Latency CLI

Measure basic latency metrics for streamed OpenAI Chat Completions responses.

## What It Measures

- `ttft`: time to first streamed content chunk
- `tbt`: average time between streamed content chunks
- `total_latency`: total time from request start to stream end
- `token_count`: number of streamed chunks that contained content

Each streamed chunk with content is treated as one token for measurement.

## Setup

Install the OpenAI Python SDK:

```bash
pip install openai
```

Set your API key:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

Optionally choose a model:

```bash
export OPENAI_MODEL="gpt-4o-mini"
```

## Usage

```bash
python3 stream_latency.py "Summarize the benefits of solar power."
```

You can also provide the key inline for a single run:

```bash
OPENAI_API_KEY="your_api_key_here" python3 stream_latency.py "Summarize the benefits of solar power."
```

## Example Output

```json
{
  "ttft": 0.72,
  "tbt": 0.04,
  "total_latency": 2.31,
  "token_count": 42
}
```

Latency values are reported in seconds and rounded to two decimal places.

## Notes

Keep API keys out of source files and version control. If a key is exposed, revoke it and create a new one.
