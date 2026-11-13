import multiprocessing as mp
from multiprocessing import shared_memory
import ctypes
import gc
from harness import run_benchmark, emit_verify_tag

def fs_worker(shm_name: str, slot_idx: int, iters: int) -> None:
    # Attach to existing shared memory
    shm = shared_memory.SharedMemory(name=shm_name)
    
    # Create ctypes view over shm.buf
    arr = (ctypes.c_uint64 * 512).from_buffer(shm.buf)
    acc = arr[slot_idx]
    
    # Run heavy read-modify-write steps
    for _ in range(iters):
        acc = (acc * 6364136223846793005 + 1) & 0xFFFFFFFFFFFFFFFF
    arr[slot_idx] = acc
    
    # --- CRITICAL FIX FOR BufferError ---
    # Explicitly delete the exported buffer pointer / view reference
    del arr
    # Force garbage collection to release buffer exports immediately
    gc.collect()
    
    # Safe to close handle
    shm.close()

def run_stride_experiment(stride: int, p_cores: int, total_iters: int = 1_600_000) -> float:
    # Create shared memory block (4096 bytes / 512 uint64 slots)
    shm = shared_memory.SharedMemory(create=True, size=4096)
    iters_per_proc = total_iters // p_cores
    
    def job():
        processes = []
        for i in range(p_cores):
            slot = (i * stride) % 512
            p = mp.Process(target=fs_worker, args=(shm.name, slot, iters_per_proc))
            processes.append(p)
            p.start()
        for p in processes:
            p.join()

    stats = run_benchmark(job, warmup=1, runs=3)
    
    # Safe cleanup in parent process
    shm.close()
    shm.unlink()
    return stats.median_ms

if __name__ == "__main__":
    p_phys = 8
    strides = [1, 2, 4, 8, 16, 32]
    print("--- Stride Sweep (p = P_phys) ---")
    stride_results = {}
    
    for s in strides:
        med_ms = run_stride_experiment(s, p_phys)
        stride_results[s] = med_ms
        print(f"Stride {s:2d} ({s*8:3d} bytes): Median Time = {med_ms:.2f} ms")
    
    med_1 = stride_results[1]
    med_16 = stride_results[16]
    
    tag_1 = emit_verify_tag("PHASE1", 200103243, med_1, med_16)
    print(tag_1)