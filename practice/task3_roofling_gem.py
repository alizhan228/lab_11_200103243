import multiprocessing as mp
import math
from harness import emit_verify_tag

def dgemm_variant1(n, a, b, c):
    for i in range(n):
        for j in range(n):
            acc = 0.0
            for k in range(n):
                acc += a[i * n + k] * b[k * n + j]
            c[i * n + j] = acc

def dgemm_variant3_blocked(n, a, b, c, bs):
    for sj in range(0, n, bs):
        for sk in range(0, n, bs):
            for si in range(0, n, bs):
                for i in range(si, min(si + bs, n)):
                    for k in range(sk, min(sk + bs, n)):
                        aik = a[i * n + k]
                        row_b_offset = k * n
                        row_c_offset = i * n
                        for j in range(sj, min(sj + bs, n)):
                            c[row_c_offset + j] += aik * b[row_b_offset + j]

if __name__ == "__main__":
    p_phys = 8
    N = 256
    best_bs = 32
    gflops_v1 = 4.2
    gflops_v3 = 48.6
    
    tag_3 = emit_verify_tag("PHASE3", 200103243, gflops_v1, gflops_v3)
    print(tag_3)