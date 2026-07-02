# Python Concurrency: Threading, Multiprocessing, Asyncio

## Objectives
- Understand the GIL and why it makes threading useless for CPU-bound work but
  fine for I/O-bound work.
- Use `multiprocessing` to parallelize CPU-bound work across cores.
- Use `asyncio` for high-concurrency I/O-bound work (many network calls).
- Pick the right tool for a given workload and justify the choice.

## Key concepts

> **Deep dive:** open [`key_concepts.html`](key_concepts.html) in a browser for animated explanations of each concept below.
- Global Interpreter Lock (GIL): what it does and doesn't block.
- `threading` vs. `multiprocessing` vs. `asyncio` — CPU-bound vs. I/O-bound.
- Process pools (`ProcessPoolExecutor`) and serialization overhead (pickling).
- `async`/`await`, event loop, coroutines vs. threads.
- Race conditions, locks, and why shared state is harder across processes than threads.

## Resources
- Python docs — concurrency: https://docs.python.org/3/library/concurrency.html
- Real Python — "Speed Up Your Python Program With Concurrency": https://realpython.com/python-concurrency/
- Python docs — asyncio: https://docs.python.org/3/library/asyncio.html

## Checklist
- [ ] Benchmark a CPU-bound task (e.g. computing primes) with plain loop vs.
      threading vs. multiprocessing — observe threading doesn't help.
- [ ] Benchmark an I/O-bound task (e.g. many HTTP requests) with sync vs.
      threading vs. asyncio — observe asyncio/threading both help, sync doesn't.
- [ ] Parallelize a CPU-bound batch job with `ProcessPoolExecutor` and measure
      speedup vs. core count.
- [ ] Write an `asyncio` script that fetches 20 URLs concurrently with a
      concurrency limit (semaphore).

## Mini-project
Take a CPU-bound workload (e.g. image resizing or a numeric simulation) and an
I/O-bound workload (e.g. calling a slow mock API), parallelize each with the
right tool, and write a short benchmark table (workload x approach x wall time)
in this README.
