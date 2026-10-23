"""Handling of database operations for the pomodoro timer."""

import datetime
from collections.abc import Sequence
from typing import cast

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import BlockStatus, BlockType, PomodoroBlock, PomodoroCycle


class PomodoroDataAccess:
    """Data access layer for Pomodoro sessions."""

    def __init__(self, db_session: AsyncSession) -> None:
        self.db = db_session

    async def save_cycle(
        self, focus_time: int, break_time: int, rounds: int
    ) -> PomodoroCycle:
        """Save a new Pomodoro cycle to the database."""
        cycle = PomodoroCycle(
            focus_duration=focus_time, break_duration=break_time, total_rounds=rounds
        )
        self.db.add(cycle)
        await self.db.commit()
        return cycle

    async def create_block(
        self, cycle_id: int, block_type: BlockType, order: int
    ) -> PomodoroBlock:
        """Create a new Pomodoro block associated with a cycle."""
        block = PomodoroBlock(cycle_id=cycle_id, type=block_type.value, order=order)
        self.db.add(block)
        await self.db.commit()
        return block

    async def get_all_blocks(self, cycle_id: int) -> Sequence[PomodoroBlock]:
        """Retrieve all blocks for a given cycle."""
        result = await self.db.execute(
            select(PomodoroBlock)
            .where(PomodoroBlock.cycle_id == cycle_id)
            .order_by(PomodoroBlock.order)
        )
        return cast(Sequence[PomodoroBlock], result.scalars().all())

    async def get_active_block(self, cycle_id: int) -> PomodoroBlock | None:
        """Retrieve the currently active block for a given cycle."""
        result = await self.db.execute(
            select(PomodoroBlock).where(
                PomodoroBlock.cycle_id == cycle_id,
                PomodoroBlock.status == BlockStatus.ACTIVE.value,
            )
        )
        return cast(PomodoroBlock | None, result.scalar_one_or_none())

    async def get_paused_block(self, cycle_id: int) -> PomodoroBlock | None:
        """Retrieve the most recent paused block for a given cycle."""
        result = await self.db.execute(
            select(PomodoroBlock)
            .where(
                PomodoroBlock.cycle_id == cycle_id,
                PomodoroBlock.status == BlockStatus.PAUSED.value,
            )
            .order_by(PomodoroBlock.started_at.desc())
        )
        return cast(PomodoroBlock | None, result.scalar_one_or_none())

    async def get_next_open_block(self, cycle_id: int) -> PomodoroBlock | None:
        """Retrieve the next open block for a given cycle."""
        result = await self.db.execute(
            select(PomodoroBlock)
            .where(
                PomodoroBlock.cycle_id == cycle_id,
                PomodoroBlock.status == BlockStatus.OPEN.value,
            )
            .order_by(PomodoroBlock.order.asc())
            .limit(1)
        )
        return cast(PomodoroBlock | None, result.scalar_one_or_none())

    async def update_block_state(
        self,
        block_id: int,
        status: BlockStatus,
        started_at: datetime.datetime | None = None,
        accumulated: int | None = None,
    ) -> None:
        stmt = (
            update(PomodoroBlock)
            .where(PomodoroBlock.id == block_id)
            .values(
                status=status.value,
                started_at=started_at,
                accumulated_seconds=accumulated
                if accumulated is not None
                else PomodoroBlock.accumulated_seconds,
            )
        )
        await self.db.execute(stmt)
        await self.db.commit()
