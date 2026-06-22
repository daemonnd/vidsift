from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class RunContext:
    run_id: UUID


_current_run_context: ContextVar[Optional[RunContext]] = ContextVar(
    "_current_run_context",
    default=None
)

def set_run_context(ctx: RunContext) -> Token:
    return _current_run_context.set(ctx)

def get_run_context() -> Optional[RunContext]:
    return _current_run_context.get()

def reset_run_context(token: Token):
    _current_run_context.reset(token)
