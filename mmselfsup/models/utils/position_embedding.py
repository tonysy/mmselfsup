# Copyright (c) OpenMMLab. All rights reserved.
from typing import Optional, Sequence, Union

import torch


def build_2d_sincos_position_embedding(
        patches_resolution: Union[int, Sequence[int]],
        embed_dims: int,
        temperature: Optional[int] = 10000.,
        cls_token: Optional[bool] = False) -> torch.Tensor:
    """The function is to build position embedding for model to obtain the
    position information of the image patches.

    Args:
        patches_resolution (Union[int, Sequence[int]]): The resolution of each
            patch.
        embed_dims (int): The dimension of the embedding vector.
        temperature (int, optional): The temperature parameter. Defaults to
            10000.
        cls_token (bool, optional): Whether to concatenate class token.
            Defaults to False.

    Returns:
        torch.Tensor: The position embedding vector.
    """

    if isinstance(patches_resolution, int):
        patches_resolution = (patches_resolution, patches_resolution)

    h, w = patches_resolution
    grid_w = torch.arange(w, dtype=torch.float32)
    grid_h = torch.arange(h, dtype=torch.float32)
    grid_w, grid_h = torch.meshgrid(grid_w, grid_h)
    assert embed_dims % 4 == 0, \
        'Embed dimension must be divisible by 4.'
    pos_dim = embed_dims // 4

    omega = torch.arange(pos_dim, dtype=torch.float32) / pos_dim
    omega = 1. / (temperature**omega)
    out_w = torch.einsum('m,d->md', [grid_w.flatten(), omega])
    out_h = torch.einsum('m,d->md', [grid_h.flatten(), omega])

    pos_emb = torch.cat(
        [
            torch.sin(out_w),
            torch.cos(out_w),
            torch.sin(out_h),
            torch.cos(out_h)
        ],
        dim=1,
    )[None, :, :]

    if cls_token:
        cls_token_pe = torch.zeros([1, 1, embed_dims], dtype=torch.float32)
        pos_emb = torch.cat([cls_token_pe, pos_emb], dim=1)

    return pos_emb


def build_1d_sincos_position_embedding(
        num_patches: int,
        embed_dims: int,
        temperature: Optional[int] = 10000.) -> torch.Tensor:
    """The function is to build 1d position embedding for model to obtain the
    position information of the input patches.

    Sinusoid encoding is a kind of relative position encoding method came from
    `Attention Is All You Need<https://arxiv.org/abs/1706.03762>`_.

    Args:
        num_patches (int): The number of the input patches.
        embed_dims (int): The dimension of the embedding vector.
        temperature (int, optional): The temperature parameter. Defaults to
            10000.
    """
    vector = torch.arange(embed_dims, dtype=torch.float64)
    vector = (vector - vector % 2) / embed_dims
    vector = torch.pow(temperature, -vector).view(1, -1)

    sinusoid_table = torch.arange(num_patches).view(-1, 1) * vector
    sinusoid_table[:, 0::2].sin_()  # dim 2i
    sinusoid_table[:, 1::2].cos_()  # dim 2i+1

    sinusoid_table = sinusoid_table.to(torch.float32)

    return sinusoid_table
