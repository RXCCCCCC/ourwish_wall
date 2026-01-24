#!/usr/bin/env python3
"""
Simple load tester: send N requests (optionally concurrent) and summarize results.
Usage:
  python scripts/stress_test.py --url http://localhost:5000 --count 50 --concurrency 10

Notes:
- Installs: `pip install requests` if not already available.
- Use responsibly on your own server.
"""

import argparse
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
import statistics


def do_request(i, url, timeout):
    start = time.perf_counter()
    try:
        r = requests.get(url, timeout=timeout)
        elapsed = time.perf_counter() - start
        return (i, r.status_code, elapsed, None)
    except Exception as e:
        elapsed = time.perf_counter() - start
        return (i, None, elapsed, str(e))


def main():
    p = argparse.ArgumentParser(description='Simple HTTP load tester')
    p.add_argument('--url', required=True, help='Target URL to GET')
    p.add_argument('--count', type=int, default=50, help='Total number of requests')
    p.add_argument('--concurrency', type=int, default=10, help='Number of concurrent workers')
    p.add_argument('--timeout', type=float, default=10.0, help='Per-request timeout (seconds)')
    p.add_argument('--log', default='stress_log.txt', help='Optional per-request log output')
    args = p.parse_args()

    print(f"Target: {args.url}  Requests: {args.count}  Concurrency: {args.concurrency}")
    start_all = time.perf_counter()

    results = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as exc:
        futures = [exc.submit(do_request, i, args.url, args.timeout) for i in range(args.count)]
        for fut in as_completed(futures):
            results.append(fut.result())

    total_time = time.perf_counter() - start_all

    # Analyze
    statuses = Counter()
    errors = []
    latencies = []
    for i, status, elapsed, err in results:
        if err:
            errors.append((i, err))
        else:
            statuses[status] += 1
            latencies.append(elapsed)

    success_count = sum(count for code, count in statuses.items() if 200 <= code < 300)
    total = len(results)

    print('\n--- Summary ---')
    print(f'Total requests: {total}')
    print(f'Success (2xx): {success_count}')
    print(f'Status distribution: {dict(statuses)}')
    print(f'Errors: {len(errors)}')
    if latencies:
        print(f'Latency (s) - min: {min(latencies):.3f}, max: {max(latencies):.3f}, mean: {statistics.mean(latencies):.3f}, median: {statistics.median(latencies):.3f}')
    print(f'Total wall time: {total_time:.3f}s')

    # Save log
    try:
        with open(args.log, 'w', encoding='utf-8') as fh:
            fh.write('index,status,elapsed,error\n')
            for i, status, elapsed, err in results:
                fh.write(f'{i},{status if status is not None else "",}{elapsed:.6f},{err if err else ""}\n')
        print(f'Per-request log written to {args.log}')
    except Exception as e:
        print('Failed to write log:', e)

    if errors:
        print('\nSample errors:')
        for i, err in errors[:10]:
            print(f'  #{i}: {err}')


if __name__ == '__main__':
    main()
