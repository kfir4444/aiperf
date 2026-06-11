# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Request-rate sine wave shaping configuration."""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import BeforeValidator, ConfigDict, Field

from aiperf.config.base import BaseConfig
from aiperf.config.loader.duration import _parse_duration


def _normalize_delay(v: Any) -> Any:
    """Normalize delay shorthand to seconds."""
    return _parse_duration(v)


class RateSineConfig(BaseConfig):
    """Configuration for sinusoidal request-rate modulation."""

    model_config = ConfigDict(extra="forbid")

    frequency: Annotated[
        float,
        Field(
            gt=0.0,
            description="Sine wave frequency in cycles per second.",
        ),
    ]
    amplitude: Annotated[
        float,
        Field(
            gt=0.0,
            description="Absolute request-rate delta in QPS around the configured rate.",
        ),
    ]
    delay: Annotated[
        float,
        BeforeValidator(_normalize_delay),
        Field(
            ge=0.0,
            default=0.0,
            description="Seconds after phase start before sine modulation begins.",
        ),
    ]
