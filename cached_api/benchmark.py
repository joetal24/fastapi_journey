import time
import requests
import statistics

BASE_URL = "http://localhost:8001"

def warmup():
    requests.get(f"{BASE_URL}/plot/VOL001", timeout=5)

def benchmark_cached_vs_uncached(plot_id, num_requests=20):
    r = requests.get(f"{BASE_URL}/plot/{plot_id}", timeout=5)
    payload = r.json()
    if not payload.get("data"):
        return
    miss_latency = payload.get("db_latency_ms", 500)

    hit_latencies = []
    for _ in range(num_requests):
        start = time.time()
        r = requests.get(f"{BASE_URL}/plot/{plot_id}", timeout=5)
        hit_latencies.append((time.time() - start) * 1000)

    avg_hit = statistics.mean(hit_latencies)
    min_hit = min(hit_latencies)
    max_hit = max(hit_latencies)

    print(f"\n  {plot_id} — Latency Comparison:")
    print(f"    Cache miss (DB): {miss_latency:.1f} ms")
    print(f"    Cache hit avg:   {avg_hit:.2f} ms")
    print(f"    Speedup:         {miss_latency / max(avg_hit, 0.01):.1f}x faster")
    print(f"    Hit range:       {min_hit:.2f}–{max_hit:.2f} ms")

if __name__ == "__main__":
    print("=== Cache Performance Benchmark ===")
    print("Ensure the API is running on", BASE_URL)
    warmup()
    benchmark_cached_vs_uncached("VOL001")
    benchmark_cached_vs_uncached("VOL002")
    benchmark_cached_vs_uncached("VOL003")
    print()
