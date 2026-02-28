# Copyright (C) 2026 Matteo Zeccoli Marazzini
#
# This file is part of escapy.
#
# escapy is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# escapy is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for
# more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with escapy. If not, see <https://www.gnu.org/licenses/>.

"""Core type definitions used throughout the escapy library."""

from dataclasses import dataclass

__all__ = ["Position", "Room"]


@dataclass
class Position:
    """A 2D position expressed as normalised fractions of the game area.

    Both *x* and *y* are expected to be in the range ``[0.0, 1.0]``, where
    ``(0.0, 0.0)`` is the top-left corner and ``(1.0, 1.0)`` is the
    bottom-right corner of the game area.
    """

    #: Horizontal fraction (0.0 = left edge, 1.0 = right edge).
    x: float
    #: Vertical fraction (0.0 = top edge, 1.0 = bottom edge).
    y: float


type Room = dict[str, Position]
"""Mapping of object IDs to their positions within a room."""
