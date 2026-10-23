"""Business logic for the Pomodoro timer service."""

import datetime
import logging
from collections.abc import Sequence

from .data_access import PomodoroDataAccess
from .models import BlockStatus, BlockType, PomodoroBlock, PomodoroCycle

logger = logging.getLogger(__name__)


class PomodoroService:
    """Service layer for Pomodoro sessions."""

    def __init__(self, data_access: PomodoroDataAccess) -> None:
        self.data_access = data_access

    async def create_cycle(
        self, focus_time: int, break_time: int, rounds: int
    ) -> PomodoroCycle:
        logger.debug(
            "Creating Pomodoro cycle: focus_time=%s, break_time=%s, rounds=%s",
            focus_time,
            break_time,
            rounds,
        )
        cycle = await self.data_access.save_cycle(focus_time, break_time, rounds)
        for i in range(rounds):
            await self.data_access.create_block(cycle.id, BlockType.FOCUS, i * 2)
            await self.data_access.create_block(cycle.id, BlockType.BREAK, i * 2 + 1)
        logger.debug("Created Pomodoro cycle: cycle_id=%s", cycle.id)
        return cycle

    async def start_block(self, cycle_id: int, block_id: int) -> None:
        # ensure no other block is active
        active = await self.data_access.get_active_block(cycle_id)
        if active:
            logger.debug(
                "Cannot start block: cycle_id=%s, block_id=%s, active_block_id=%s",
                cycle_id,
                block_id,
                active.id,
            )
            raise ValueError("Another block is already active.")

        await self.data_access.update_block_state(
            block_id,
            status=BlockStatus.ACTIVE,
            started_at=datetime.datetime.now(datetime.UTC),
        )
        logger.debug("Started block: cycle_id=%s, block_id=%s", cycle_id, block_id)

    async def pause_block(self, block_id: int, accumulated_seconds: int = 0) -> None:
        active = await self.data_access.get_active_block(block_id)
        if not active:
            logger.debug("Cannot pause block: block_id=%s is not active", block_id)
            raise ValueError("No active block found to pause.")

        # Calculate time spent since started_at
        spent = (
            datetime.datetime.now(datetime.UTC) - active.started_at
        ).total_seconds()
        new_accumulated = accumulated_seconds + int(spent)

        await self.data_access.update_block_state(
            active.id,
            status=BlockStatus.PAUSED,
            started_at=None,
            accumulated=new_accumulated,
        )
        logger.debug(
            "Paused block: block_id=%s, accumulated_seconds=%s",
            active.id,
            new_accumulated,
        )

    async def resume_block(self, block_id: int | None) -> None:
        if block_id is None:
            raise ValueError("Provide block_id to resume a paused block.")

        active = await self.data_access.get_active_block(block_id)
        if active:
            logger.debug("Cannot resume block: block_id=%s is already active", block_id)
            raise ValueError("Another block is already active.")

        await self.data_access.update_block_state(
            block_id,
            status=BlockStatus.ACTIVE,
            started_at=datetime.datetime.now(datetime.UTC),
        )
        logger.debug("Resumed block: block_id=%s", block_id)

    async def skip_block(self, cycle_id: int) -> None:
        active = await self.data_access.get_active_block(cycle_id)
        if not active:
            logger.debug("Cannot skip block: cycle_id=%s has no active block", cycle_id)
            raise ValueError("No active block found to skip.")

        await self.data_access.update_block_state(
            active.id, status=BlockStatus.SKIPPED, started_at=None
        )
        logger.debug("Skipped block: cycle_id=%s, block_id=%s", cycle_id, active.id)

    async def get_active_block_with_transition(
        self, cycle_id: int
    ) -> PomodoroBlock | None:
        active = await self.data_access.get_active_block(cycle_id)
        if not active or active.status != BlockStatus.ACTIVE:
            logger.debug(
                "No active transition: cycle_id=%s, block_id=%s",
                cycle_id,
                active.id if active else None,
            )
            return active

        # Check if time is up
        elapsed = (
            datetime.datetime.now(datetime.UTC) - active.started_at
        ).total_seconds() + active.accumulated_seconds
        if elapsed >= active.duration_seconds:
            # Time is up! Complete this block and start the next
            logger.debug(
                "Block duration reached: cycle_id=%s, block_id=%s, elapsed=%s",
                cycle_id,
                active.id,
                elapsed,
            )
            await self.data_access.update_block_state(active.id, BlockStatus.COMPLETED)
            return await self.activate_next_block(cycle_id)

        logger.debug(
            "Active block still running: cycle_id=%s, block_id=%s, elapsed=%s",
            cycle_id,
            active.id,
            elapsed,
        )
        return active

    async def activate_next_block(self, cycle_id: int) -> PomodoroBlock | None:
        next_block = await self.data_access.get_next_open_block(cycle_id)
        if next_block:
            await self.data_access.update_block_state(
                next_block.id,
                BlockStatus.ACTIVE,
                started_at=datetime.datetime.now(datetime.UTC),
            )
            logger.debug(
                "Activated next block: cycle_id=%s, block_id=%s",
                cycle_id,
                next_block.id,
            )
            return next_block
        logger.debug("No open blocks remain: cycle_id=%s", cycle_id)
        return None  # Cycle finished

    async def get_cycle_status(self, cycle_id: int) -> Sequence[PomodoroBlock]:
        blocks = await self.data_access.get_all_blocks(cycle_id)
        logger.debug(
            "Retrieved cycle status: cycle_id=%s, block_count=%s",
            cycle_id,
            len(blocks),
        )
        return blocks
