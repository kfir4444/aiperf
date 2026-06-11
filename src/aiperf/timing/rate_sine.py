# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Continuous request-rate sine wave controller."""

from __future__ import annotations

import asyncio
import math
import time
from collections.abc import Callable

from aiperf.config.rate_sine import RateSineConfig


class RateSineController:
    """Apply sinusoidal request-rate updates until stopped."""

    def __init__(
        self,
        setter: Callable[[float], None],
        center_rate: float,
        config: RateSineConfig,
        update_interval: float,
    ) -> None:
        self._setter = setter
        self._center_rate = center_rate
        self._config = config
        self._update_interval = update_interval
        self._task: asyncio.Task | None = None

    @property
    def is_running(self) -> bool:
        """Return True if the sine controller task is currently running."""
        return self._task is not None and not self._task.done()

    def start(self) -> asyncio.Task:
        """Start request-rate sine modulation in a background task."""
        self._task = asyncio.create_task(self._run())
        return self._task

    def stop(self) -> None:
        """Stop sine modulation early."""
        if self._task is not None and not self._task.done():
            self._task.cancel()

    def value_at(self, elapsed_sec: float) -> float:
        """Return the sine-modulated request rate at elapsed modulation time."""
        return self._center_rate + self._config.amplitude * math.sin(
            2.0 * math.pi * self._config.frequency * elapsed_sec
        )

    async def _run(self) -> None:
        try:
            if self._config.delay > 0:
                await asyncio.sleep(self._config.delay)

            sine_start = time.perf_counter()
            self._setter(self.value_at(0.0))

            while True:
                await asyncio.sleep(self._update_interval)
                elapsed = time.perf_counter() - sine_start
                self._setter(self.value_at(elapsed))
        except asyncio.CancelledError:
            pass
