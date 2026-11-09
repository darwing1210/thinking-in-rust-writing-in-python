"""A tiny Result type. Not a framework — just Ok | Err as values."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Ok[T]:
    value: T


@dataclass(frozen=True)
class Err[E]:
    error: E


type Result[T, E] = Ok[T] | Err[E]
