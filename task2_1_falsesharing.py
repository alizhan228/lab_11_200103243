import ctypes
import multiprocessing as mp
from multiprocessing import shared_memory

from harness import run_benchmark, emit_verify_tag

STUDENT_ID = 200103243          # <-- your numeric Student ID
P_PHYS = 8                # <-- from your Task 1.1 table
P_LOG = mp.cpu_count()    # logical threads
M = 24_000_000            # 2.4 x 10^7 total accumulation steps
N_SLOTS = 512             # 4096 bytes / 8 bytes per uint64


def fs_worker(shm_name: str, slot_idx: int, iters: int) -> None:
    shm = shared_memory.SharedMemory(name=shm_name)
    arr = (ctypes.c_uint64 * N_SLOTS).from_buffer(shm.buf)
    acc = arr[slot_idx]
    mask = 0xFFFFFFFFFFFFFFFF
    mult = 6364136223846793005
    for i in range(iters):
        acc = (acc * mult + (i | 1)) & mask
        arr[slot_idx] = acc          # direct store to the shared cache line
    del arr                          # release buffer export before closing
    shm.close()


def run_once(p: int, stride: int) -> None:
    shm = shared_memory.SharedMemory(create=True, size=4096)
    try:
        shm.buf[:] = bytes(4096)
        per = M // p
        procs = [mp.Process(target=fs_worker, args=(shm.name, t * stride, per))
                 for t in range(p)]
        for pr in procs:
            pr.start()
        for pr in procs:
            pr.join()
    finally:
        shm.close()
        shm.unlink()


def bench(p: int, stride: int):
    if (p - 1) * stride >= N_SLOTS:
        return None                  # slot would fall outside the 4096 B block
    return run_benchmark(lambda: run_once(p, stride), warmup_runs=2, timed_runs=7)


def mops(ms: float) -> float:
    return M / (ms * 1e3)            # M ops / (ms/1000 s) / 1e6


def proc_counts():
    ps, p = [], 1
    while p <= P_LOG:
        ps.append(p)
        p *= 2
    if ps[-1] != P_LOG:
        ps.append(P_LOG)
    return ps


def karp_flatt(sp: float, p: int) -> float:
    return (1 / sp - 1 / p) / (1 - 1 / p)


def main():
    print(f"P_phys={P_PHYS}  P_log={P_LOG}  M={M}\n")

    # ---- Table 1A: stride sweep at p = P_phys ----
    print("Table 1A: stride sweep (p = P_phys)")
    print(f"{'stride':>6} {'bytes':>6} {'median(ms)':>11} {'IQR(ms)':>9} {'Mops/s':>8}")
    med = {}
    for s in [1, 2, 4, 8, 16, 32]:
        st = bench(P_PHYS, s)
        if st is None:
            print(f"{s:>6} {s*8:>6}   skipped (index out of range)")
            continue
        med[s] = st.median_ms
        print(f"{s:>6} {s*8:>6} {st.median_ms:>11.1f} {st.iqr_ms:>9.1f} {mops(st.median_ms):>8.2f}")

    keys = sorted(med)
    drops = [(med[a] / med[b], b) for a, b in zip(keys, keys[1:])]
    ratio, knee = max(drops)
    print(f"\nLargest drop: x{ratio:.2f} at stride {knee} -> {knee*8} bytes separation\n")

    # ---- Table 1B: process scaling at stride 1 and stride 16 ----
    for s in (1, 16):
        print(f"Table 1B: scaling, stride={s} ({s*8} B)")
        print(f"{'p':>3} {'Tp(ms)':>10} {'IQR':>8} {'Sp':>7} {'Ep':>6} {'Karp-Flatt e':>13}")
        t1 = None
        for p in proc_counts():
            st = bench(p, s)
            if st is None:
                print(f"{p:>3}   skipped (index out of range)")
                continue
            if p == 1:
                t1 = st.median_ms
            sp = t1 / st.median_ms
            ep = sp / p
            e = f"{karp_flatt(sp, p):>13.4f}" if p >= 2 else f"{'-':>13}"
            print(f"{p:>3} {st.median_ms:>10.1f} {st.iqr_ms:>8.1f} {sp:>7.2f} {ep:>6.2f} {e}")
        print()

    print(emit_verify_tag("PHASE1", STUDENT_ID, med[1], med[16]))


if __name__ == "__main__":
    main()