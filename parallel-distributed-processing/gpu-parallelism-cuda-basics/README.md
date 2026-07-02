# GPU Parallelism & CUDA Basics

## Objectives
- Understand SIMT execution: threads, blocks, grids, and why GPUs excel at
  data-parallel workloads.
- Write and launch a simple CUDA kernel with Numba (no C++ required).
- Compare CPU vs. GPU performance for an embarrassingly parallel workload.
- Understand memory transfer cost (host <-> device) as the usual bottleneck.

## Key concepts
- Threads, blocks, grids; how a kernel maps work across the GPU.
- Host memory vs. device memory, and the cost of transferring data between them.
- Embarrassingly parallel vs. inherently sequential workloads (Amdahl's law intuition).
- `numba.cuda` as a low-barrier entry point vs. writing raw CUDA C++.

## Resources
- Numba docs — CUDA: https://numba.readthedocs.io/en/stable/cuda/index.html
- NVIDIA "An Even Easier Introduction to CUDA": https://developer.nvidia.com/blog/even-easier-introduction-cuda/
- CUDA C++ Programming Guide (reference, not required reading end-to-end): https://docs.nvidia.com/cuda/cuda-c-programming-guide/

## Checklist
- [ ] Confirm GPU availability (`nvidia-smi`, `numba.cuda.is_available()`) —
      if no GPU is available, note that and use Google Colab's free GPU runtime.
- [ ] Write a Numba `@cuda.jit` kernel for an elementwise operation (e.g. vector add).
- [ ] Benchmark it against the equivalent NumPy CPU operation at increasing sizes.
- [ ] Explicitly manage host/device memory transfer and observe its cost vs.
      compute time for a small vs. large array.
- [ ] Identify the crossover array size where GPU wins despite transfer overhead.

## Mini-project
Implement one non-trivial elementwise or reduction operation (e.g. a distance
matrix computation) as both a NumPy CPU version and a Numba CUDA version, and
plot wall-clock time vs. input size for both, marking the crossover point.
