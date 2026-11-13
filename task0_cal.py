import time
import multiprocessing as mp
from harness import emit_verify_tag

STUDENT_ID = 200103243          # <-- replace with your numeric Student ID
N = 2_000_000           # 2 x 10^6 clock reads


def main():
    now = time.perf_counter_ns
    for _ in range(10_000):          # warm-up
        now()

    t0 = now()
    for _ in range(N):
        now()
    t1 = now()

    total_ns = t1 - t0
    avg_ns = total_ns / N

    print(f"mp.cpu_count()          : {mp.cpu_count()}")
    print(f"Clock reads             : {N}")
    print(f"Total elapsed           : {total_ns / 1e6:.3f} ms")
    print(f"Avg call latency        : {avg_ns:.2f} ns")
    print(emit_verify_tag("PHASE0", STUDENT_ID, avg_ns, float(mp.cpu_count())))


if __name__ == "__main__":
    main()