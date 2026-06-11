# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
import asyncio
import contextlib

import pytest

from aiperf.config.rate_sine import RateSineConfig
from aiperf.timing.rate_sine import RateSineController


def sine_config(delay: float = 0.0) -> RateSineConfig:
    return RateSineConfig(frequency=0.25, amplitude=10.0, delay=delay)


class TestRateSineController:
    def test_value_at_samples_sine_wave(self) -> None:
        controller = RateSineController(
            setter=lambda value: None,
            center_rate=100.0,
            config=sine_config(),
            update_interval=0.1,
        )

        assert controller.value_at(0.0) == pytest.approx(100.0)
        assert controller.value_at(1.0) == pytest.approx(110.0)
        assert controller.value_at(2.0) == pytest.approx(100.0)
        assert controller.value_at(3.0) == pytest.approx(90.0)

    @pytest.mark.asyncio
    async def test_start_waits_for_delay(self, time_traveler) -> None:
        values: list[float] = []
        controller = RateSineController(
            setter=values.append,
            center_rate=100.0,
            config=sine_config(delay=2.0),
            update_interval=0.5,
        )

        task = controller.start()
        await time_traveler.sleep(1.0)
        assert values == []

        await time_traveler.sleep(1.0)
        assert values == [100.0]

        controller.stop()
        with contextlib.suppress(asyncio.CancelledError):
            await task
