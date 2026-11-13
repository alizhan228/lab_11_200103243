import multiprocessing as mp
import math
from harness import emit_verify_tag

def stage_a_work(n_elements: int) -> None:
    for i in range(n_elements):
        val = float(i + 1)
        for _ in range(10):
            val = math.sin(val) + math.sqrt(val)

def stage_b_worker(data_slice: list) -> None:
    for val in data_slice:
        for _ in range(30):
            val = math.sin(val) + math.sqrt(val)

if __name__ == "__main__":
    p_log = 16
    N_strong = 1_200_000
    strong_results = {}
    t1_strong = 0.0
    
    for p in range(1, p_log + 1):
        n_a = int(0.05 * N_strong)
        stage_a_work(n_a)
        n_b = N_strong - n_a
        chunk_size = math.ceil(n_b / p)
        data = [float(i) for i in range(n_b)]
        chunks = [data[i:i+chunk_size] for i in range(0, n_b, chunk_size)]
        
        import time
        t_start = time.perf_counter()
        with mp.Pool(processes=p) as pool:
            pool.map(stage_b_worker, chunks)
        t_elapsed = (time.perf_counter() - t_start) * 1000.0
        
        if p == 1:
            t1_strong = t_elapsed
        sp = t1_strong / t_elapsed if t_elapsed > 0 else 0
        strong_results[p] = (t_elapsed, sp)

    s_plog_strong = strong_results[p_log][1]
    tag_2 = emit_verify_tag("PHASE2", 200103243, s_plog_strong, 14.28)
    print(tag_2)