from pathlib import Path
from uuid import uuid7

import pytest
from portalocker import LOCK_EX, LOCK_NB, Lock, LockException

from tests.fakes.fake_pipeline import FakeOrchestrator, FakeRunManager
from vidsift.config.loader import load_config
from vidsift.features.video_processing.repository import \
    VideoProcessingRepository
from vidsift.runtime.lock_manager import LockManager
from vidsift.runtime.scheduler import BackgroundServiceManager
from vidsift.shared.run_manager import RunManager


@pytest.fixture()
def fake_config():
    return load_config(Path(f"{Path(__file__).parent.parent.parent}/fakes/fake_config.toml"))

@pytest.fixture()
def video_db(tmp_path, fake_config):
    return VideoProcessingRepository(db_path=tmp_path / "test.db", config=fake_config)

@pytest.fixture()
def default_orchestrator():
    return FakeOrchestrator()

@pytest.fixture()
def run_manager():
    return FakeRunManager()


class StopScheduler(Exception):
    pass


def test_scheduler_runs_pipeline_repeatedly(
    monkeypatch,
    fake_config,
    default_orchestrator,
    run_manager,
):
    scheduler = BackgroundServiceManager(
        orchestrator=default_orchestrator,
        config=fake_config,
        run_id=uuid7()
    )

    sleep_calls = 0

    def fake_sleep(_):
        nonlocal sleep_calls
        sleep_calls += 1

        if sleep_calls == 2:
            raise StopScheduler()

    monkeypatch.setattr(
        "vidsift.runtime.scheduler.sleep",
        fake_sleep,
    )

    monkeypatch.setattr(
        "vidsift.runtime.scheduler.RunManager",
        lambda run_id: run_manager,
    )

    with pytest.raises(StopScheduler):
        scheduler.run(sleep_interval=1)

    assert default_orchestrator.calls == 2
    assert run_manager.runs_started == 2
    assert run_manager.runs_ended == 2

def test_failed_pipeline_releases_lock(
    fake_config,
    monkeypatch,
    tmp_path
):
    lock_path = (Path(tmp_path) / "vidsift.lock")
    orchestrator = FakeOrchestrator(fail_after=1)
    scheduler = BackgroundServiceManager(
        orchestrator=orchestrator,
        config=fake_config,
        run_id=uuid7()
    )

    monkeypatch.setattr(
        "vidsift.runtime.scheduler.RunManager",
        lambda run_id: RunManager(lock_file_path=tmp_path / "test.lock", run_id=run_id)    )
    with pytest.raises(RuntimeError):
        scheduler.run(sleep_interval=1)
    try:
        with Lock(lock_path, flags=LOCK_EX | LOCK_NB):
            locked = False
    except LockException:
        locked = True
    assert not locked

def test_scheduler_releases_lock_during_cooldown(
    fake_config,
    monkeypatch,
    tmp_path,
):
    lock_path = tmp_path / "test.lock"

    monkeypatch.setattr(
        "vidsift.runtime.scheduler.RunManager",
        lambda run_id: RunManager(lock_file_path=lock_path, run_id=run_id)
    )

    orchestrator = FakeOrchestrator(fail_after=2)

    scheduler = BackgroundServiceManager(
        orchestrator=orchestrator,
        config=fake_config,
        locking_interval=0,
        run_id=uuid7()
    )

    sleep_calls = 0

    def fake_sleep(_):
        nonlocal sleep_calls
        sleep_calls += 1

        if sleep_calls == 1:
            second_lock_manager = LockManager(
                sleep_interval=0,
                lock_file_path=lock_path,
            )

            second_lock_manager.acquire(run_id=uuid7())
            second_lock_manager.release()

    monkeypatch.setattr(
        "vidsift.runtime.scheduler.sleep",
        fake_sleep,
    )

    with pytest.raises(RuntimeError):
        scheduler.run(sleep_interval=10)
