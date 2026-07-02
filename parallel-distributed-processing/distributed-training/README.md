# Distributed Model Training (PyTorch DDP)

## Objectives
- Understand data-parallel distributed training: each process gets a model
  replica and a data shard, gradients are synced (all-reduce) each step.
- Launch a multi-process training job with `torchrun`.
- Understand the difference between data parallelism and model/pipeline
  parallelism, and when each is needed.

## Key concepts

> **Deep dive:** open [`key_concepts.html`](key_concepts.html) in a browser for animated explanations of each concept below.
- `DistributedDataParallel` (DDP): replica per process, gradient all-reduce.
- Process groups, world size, rank, local rank.
- `DistributedSampler` to shard data correctly across processes (avoid duplication).
- Data parallelism (fits when the model fits on one GPU) vs. model/pipeline
  parallelism (needed when the model itself doesn't fit).
- Gradient accumulation as a cheaper alternative to more GPUs for larger effective batch size.

## Resources
- PyTorch docs — DDP tutorial: https://pytorch.org/tutorials/intermediate/ddp_tutorial.html
- PyTorch docs — `torchrun`: https://pytorch.org/docs/stable/elastic/run.html
- "Multi-GPU training with PyTorch DDP" walkthrough (search current PyTorch tutorials).

## Checklist
- [ ] Read through `src/train_ddp.py` in this folder and understand each DDP
      setup step (process group init, model wrap, sampler).
- [ ] Run it locally with `torchrun --nproc_per_node=<N> src/train_ddp.py`
      (N can be 1-2 even on CPU/single-GPU to see the mechanics — real speedup
      needs multiple GPUs, e.g. via a cloud multi-GPU instance or Colab).
- [ ] Confirm the `DistributedSampler` shards data without overlap across ranks.
- [ ] Compare a training run's wall-clock time at world_size=1 vs. world_size=2+
      (if multiple GPUs are available).

## Mini-project
Take a small model (e.g. a CNN on CIFAR-10 or an MLP on a tabular dataset),
train it single-process, then convert to DDP and run multi-process, recording
throughput (samples/sec) at each world size in this README.
