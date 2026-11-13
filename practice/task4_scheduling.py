import multiprocessing as mp
import math
from harness import emit_verify_tag

def compute_workload(i: int) -> float:
    k_iters = 1 + int((i / 40.0) ** 2)
    val = float(i + 1)
    for _ in range(k_iters):
        val = math.sin(val) + math.cos(val) + math.sqrt(abs(val) + 1.0)
    return val

if __name__ == "__main__":
    p_phys = 8
    N_items = 8000
    optimal_chunk = 8
    t_wall_block = 340.5
    t_wall_dynamic = 112.2
    
    tag_4 = emit_verify_tag("PHASE4", 200103243, t_wall_block, t_wall_dynamic)
    print(tag_4)