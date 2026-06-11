# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
import pytest
from pydantic import ValidationError

from aiperf.config.phases import PoissonPhase
from aiperf.config.rate_sine import RateSineConfig
from aiperf.plugin.enums import PhaseType


def test_rate_sine_rejects_amplitude_at_or_above_rate() -> None:
    with pytest.raises(ValidationError, match="amplitude must be less than rate"):
        PoissonPhase(
            name="profiling",
            type=PhaseType.POISSON,
            rate=10.0,
            requests=1,
            rate_sine=RateSineConfig(frequency=0.25, amplitude=10.0),
        )


def test_rate_sine_rejects_delay_before_rate_ramp_finishes() -> None:
    with pytest.raises(ValidationError, match="delay must be >= rate_ramp.duration"):
        PoissonPhase(
            name="profiling",
            type=PhaseType.POISSON,
            rate=10.0,
            requests=1,
            rate_ramp=5.0,
            rate_sine=RateSineConfig(frequency=0.25, amplitude=2.0, delay=4.0),
        )


def test_rate_sine_accepts_delay_after_rate_ramp_finishes() -> None:
    phase = PoissonPhase(
        name="profiling",
        type=PhaseType.POISSON,
        rate=10.0,
        requests=1,
        rate_ramp="5s",
        rate_sine=RateSineConfig(frequency=0.25, amplitude=2.0, delay="5s"),
    )

    assert phase.rate_sine is not None
    assert phase.rate_sine.delay == 5.0
