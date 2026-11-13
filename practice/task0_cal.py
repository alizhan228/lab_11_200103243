import time
import multiprocessing as mp
from harness import run_benchmark, emit_verify_tag

STUDENT_ID = 200103243

def measure_call_overhead():
    # Measure average nanosecond call latency over 10^6 consecutive calls
    iterations = 1_000_000
    t0 = time.perf_counter_ns()
    for _ in range(iterations):
        time.perf_counter_ns()
    elapsed = time.perf_counter_ns() - t0
    return elapsed / iterations

if __name__ == "__main__":
    avg_ns = measure_call_overhead()
    print(f"Average time.perf_counter_ns() latency: {avg_ns:.2f} ns")
    tag = emit_verify_tag("PHASE0", STUDENT_ID, avg_ns, 0.0)
    print(tag)