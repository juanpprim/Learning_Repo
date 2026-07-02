"""Minimal PyTorch DDP training skeleton.

Run with:
    torchrun --nproc_per_node=2 src/train_ddp.py
"""
import os

import torch
import torch.distributed as dist
import torch.nn as nn
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, DistributedSampler, TensorDataset


class ToyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(20, 64), nn.ReLU(), nn.Linear(64, 2))

    def forward(self, x):
        return self.net(x)


def setup():
    dist.init_process_group(backend="gloo")  # use "nccl" for multi-GPU
    local_rank = int(os.environ["LOCAL_RANK"])
    torch.manual_seed(0)
    return local_rank


def main():
    local_rank = setup()

    # TODO: replace with a real dataset
    X = torch.randn(1000, 20)
    y = torch.randint(0, 2, (1000,))
    dataset = TensorDataset(X, y)
    sampler = DistributedSampler(dataset)
    loader = DataLoader(dataset, batch_size=32, sampler=sampler)

    model = ToyModel()
    model = DDP(model)

    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss()

    for epoch in range(3):
        sampler.set_epoch(epoch)
        for xb, yb in loader:
            optimizer.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            optimizer.step()

        if dist.get_rank() == 0:
            print(f"epoch {epoch} loss {loss.item():.4f}")

    dist.destroy_process_group()


if __name__ == "__main__":
    main()
