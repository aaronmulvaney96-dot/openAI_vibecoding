import json
import os
import sys
import time
from dataclasses import dataclass
from typing import List


DEFAULT_MODEL = "gpt-4o-mini"


class LatencyMeasurementError(RuntimeError):
    """Raised when latency measurement cannot be completed."""


@dataclass
class LatencyMetrics:
    ttft: float
    tbt: float
    total_latency: float
    token_count: int

    def to_dict(self) -> dict[str, float | int]:
        return {
            "ttft": self.ttft,
            "tbt": self.tbt,
            "total_latency": self.total_latency,
            "token_count": self.token_count,
        }


def compute_metrics(start: float, timestamps: List[float], last: float) -> LatencyMetrics:
    token_count = len(timestamps)
    total_latency = last - start

    if token_count == 0:
        return LatencyMetrics(
            ttft=0.0,
            tbt=0.0,
            total_latency=round(total_latency, 2),
            token_count=token_count,
        )

    ttft = timestamps[0] - start

    if token_count == 1:
        tbt = 0.0
    else:
        gaps = [
            current - previous
            for previous, current in zip(timestamps, timestamps[1:])
        ]
        tbt = sum(gaps) / len(gaps)

    return LatencyMetrics(
        ttft=round(ttft, 2),
        tbt=round(tbt, 2),
        total_latency=round(total_latency, 2),
        token_count=token_count,
    )


def measure_latency(prompt: str) -> LatencyMetrics:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise LatencyMeasurementError(
            "OPENAI_API_KEY is not set. Export it before running this script."
        )

    try:
        from openai import OpenAI, OpenAIError
    except ImportError as exc:
        raise LatencyMeasurementError(
            "OpenAI Python SDK is not installed. Install it with: pip install openai"
        ) from exc

    client = OpenAI(api_key=api_key)
    model = os.environ.get("OPENAI_MODEL", DEFAULT_MODEL)
    timestamps: List[float] = []

    start = time.perf_counter()
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        for chunk in stream:
            content = chunk.choices[0].delta.content if chunk.choices else None
            if content:
                timestamps.append(time.perf_counter())
    except OpenAIError as exc:
        raise LatencyMeasurementError(f"OpenAI API error: {exc}") from exc
    finally:
        last = time.perf_counter()

    return compute_metrics(start, timestamps, last)


def main(argv: List[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv

    if not args:
        print(
            f'Usage: python {sys.argv[0]} "Summarize the benefits of solar power."',
            file=sys.stderr,
        )
        return 1

    prompt = " ".join(args)

    try:
        metrics = measure_latency(prompt)
    except LatencyMeasurementError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(metrics.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
