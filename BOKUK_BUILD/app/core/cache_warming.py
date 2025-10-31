"""Cache Warming System for Proactive Cache Population"""

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

from .cache import CacheKeys, get_or_compute


@dataclass
class WarmingTask:
    """Cache warming task definition"""
    task_id: str
    name: str
    cache_key: str
    compute_fn: Callable[[], Any]
    ttl: int | None = None
    tags: set[str] = field(default_factory=set)
    priority: int = 0  # Higher = more important
    schedule: str | None = None  # Cron-like schedule
    enabled: bool = True
    last_run: datetime | None = None
    next_run: datetime | None = None
    run_count: int = 0
    avg_duration_ms: float = 0.0

    def should_run(self) -> bool:
        """Check if task should run now"""
        if not self.enabled:
            return False

        if self.next_run is None:
            return True

        return datetime.now() >= self.next_run

    def update_schedule(self, interval_minutes: int = 60) -> None:
        """Update next run time"""
        self.next_run = datetime.now() + timedelta(minutes=interval_minutes)


class UsagePatternTracker:
    """Track cache usage patterns for intelligent warming"""

    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self._access_log: list[tuple[str, datetime]] = []
        self._access_counts: dict[str, int] = {}
        self._lock = threading.RLock()

    def record_access(self, key: str) -> None:
        """Record cache key access"""
        with self._lock:
            now = datetime.now()
            self._access_log.append((key, now))

            # Trim history
            if len(self._access_log) > self.history_size:
                self._access_log = self._access_log[-self.history_size:]

            # Update counts
            self._access_counts[key] = self._access_counts.get(key, 0) + 1

    def get_hot_keys(self, top_n: int = 10) -> list[tuple[str, int]]:
        """Get most frequently accessed keys"""
        with self._lock:
            sorted_keys = sorted(
                self._access_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            return sorted_keys[:top_n]

    def get_access_frequency(
        self,
        key: str,
        window_minutes: int = 60
    ) -> float:
        """Get access frequency for key (accesses per minute)"""
        with self._lock:
            cutoff = datetime.now() - timedelta(minutes=window_minutes)
            recent_accesses = [
                k for k, t in self._access_log
                if k == key and t >= cutoff
            ]
            return len(recent_accesses) / \
                window_minutes if window_minutes > 0 else 0

    def predict_next_access(self, key: str) -> datetime | None:
        """Predict when key will be accessed next (simplified)"""
        with self._lock:
            # Get recent accesses for this key
            key_accesses = [
                t for k, t in self._access_log if k == key
            ]

            if len(key_accesses) < 2:
                return None

            # Calculate average interval
            intervals = []
            for i in range(1, len(key_accesses)):
                interval = (key_accesses[i] -
                            key_accesses[i - 1]).total_seconds()
                intervals.append(interval)

            avg_interval = sum(intervals) / len(intervals)

            # Predict next access
            last_access = key_accesses[-1]
            return last_access + timedelta(seconds=avg_interval)

    def clear(self) -> None:
        """Clear usage history"""
        with self._lock:
            self._access_log.clear()
            self._access_counts.clear()


class CacheWarmingEngine:
    """Engine for proactive cache warming with performance optimization"""

    def __init__(self):
        self._tasks: dict[str, WarmingTask] = {}
        self._usage_tracker = UsagePatternTracker()
        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.RLock()
        self._performance_stats = {
            "total_warmings": 0,
            "total_duration_ms": 0,
            "avg_duration_ms": 0,
            "fastest_ms": float('inf'),
            "slowest_ms": 0
        }
        # Track last preload per user
        self._user_preload_cache: dict[str, datetime] = {}
        self._critical_data_keys: set[str] = set()  # Track critical data keys

    def register_task(
            self,
            task: WarmingTask,
            is_critical: bool = False) -> None:
        """
        Register cache warming task

        Args:
            task: Warming task to register
            is_critical: If True, mark as critical data for priority warming
        """
        with self._lock:
            self._tasks[task.task_id] = task
            if is_critical:
                self._critical_data_keys.add(task.cache_key)

        logger.info(
            "Cache warming task registered",
            task_id=task.task_id,
            name=task.name,
            priority=task.priority,
            is_critical=is_critical
        )

    def unregister_task(self, task_id: str) -> bool:
        """Unregister warming task"""
        with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                logger.info("Cache warming task unregistered", task_id=task_id)
                return True
        return False

    def warm_key(
        self,
        key: str,
        compute_fn: Callable[[], Any],
        ttl: int | None = None,
        tags: set[str] = None,
        force: bool = False
    ) -> bool:
        """
        Warm a specific cache key with performance tracking

        Args:
            key: Cache key to warm
            compute_fn: Function to compute value
            ttl: Time to live
            tags: Cache tags
            force: If True, recompute even if cached

        Returns:
            True if warming succeeded
        """
        try:
            start_time = time.time()

            # Use get_or_compute with force_refresh
            value = get_or_compute(
                key=key,
                fn=compute_fn,
                ttl=ttl,
                tags=tags,
                force_refresh=force
            )

            duration_ms = (time.time() - start_time) * 1000

            # Update performance stats
            with self._lock:
                self._performance_stats["total_warmings"] += 1
                self._performance_stats["total_duration_ms"] += duration_ms
                self._performance_stats["avg_duration_ms"] = (
                    self._performance_stats["total_duration_ms"] /
                    self._performance_stats["total_warmings"]
                )
                self._performance_stats["fastest_ms"] = min(
                    self._performance_stats["fastest_ms"],
                    duration_ms
                )
                self._performance_stats["slowest_ms"] = max(
                    self._performance_stats["slowest_ms"],
                    duration_ms
                )

            logger.info(
                "Cache key warmed",
                key=key,
                duration_ms=int(duration_ms),
                forced=force
            )

            return True

        except Exception as e:
            logger.error(
                "Cache warming failed",
                key=key,
                error=str(e)
            )
            return False

    def warm_critical_data(self, parallel: bool = False) -> dict[str, Any]:
        """
        Warm critical data based on registered tasks with optimization

        Args:
            parallel: If True, warm tasks in parallel (experimental)

        Returns:
            Results dictionary with warming statistics
        """
        results = {
            "total": 0,
            "succeeded": 0,
            "failed": 0,
            "skipped": 0,
            "tasks": [],
            "total_duration_ms": 0
        }

        start_time = time.time()

        with self._lock:
            # Filter only critical tasks or high priority tasks
            critical_tasks = [
                task for task in self._tasks.values()
                if task.cache_key in self._critical_data_keys or task.priority >= 50
            ]

            # Sort by priority (highest first)
            sorted_tasks = sorted(
                critical_tasks,
                key=lambda t: t.priority,
                reverse=True
            )

        for task in sorted_tasks:
            results["total"] += 1

            if not task.should_run():
                results["skipped"] += 1
                continue

            # Execute warming
            task_start = time.time()
            success = self.warm_key(
                key=task.cache_key,
                compute_fn=task.compute_fn,
                ttl=task.ttl,
                tags=task.tags,
                force=True
            )

            duration_ms = (time.time() - task_start) * 1000

            # Update task stats
            task.last_run = datetime.now()
            task.run_count += 1
            task.avg_duration_ms = (
                (task.avg_duration_ms * (task.run_count - 1) + duration_ms)
                / task.run_count
            )
            task.update_schedule()

            if success:
                results["succeeded"] += 1
            else:
                results["failed"] += 1

            results["tasks"].append({
                "task_id": task.task_id,
                "name": task.name,
                "success": success,
                "duration_ms": int(duration_ms)
            })

        results["total_duration_ms"] = int((time.time() - start_time) * 1000)

        logger.info(
            "Critical data warming completed",
            total=results["total"],
            succeeded=results["succeeded"],
            failed=results["failed"],
            duration_ms=results["total_duration_ms"]
        )

        return results

    def warm_user_data(
        self,
        user_id: str,
        force: bool = False,
        preload_forms: bool = True
    ) -> dict[str, Any]:
        """
        Warm user-specific cache data with intelligent preloading

        Args:
            user_id: User ID to warm data for
            force: Force refresh even if recently warmed
            preload_forms: Also preload user's recent forms

        Returns:
            Results dictionary with warming statistics
        """
        # Check if recently warmed (optimization)
        with self._lock:
            last_preload = self._user_preload_cache.get(user_id)
            if not force and last_preload:
                time_since_preload = (
                    datetime.now() - last_preload).total_seconds()
                if time_since_preload < 300:  # 5 minutes
                    logger.debug(
                        "User data recently warmed, skipping",
                        user_id=user_id,
                        seconds_ago=int(time_since_preload)
                    )
                    return {
                        "user_id": user_id,
                        "skipped": True,
                        "reason": "recently_warmed"
                    }

        results = {
            "user_id": user_id,
            "keys_warmed": [],
            "succeeded": 0,
            "failed": 0,
            "duration_ms": 0
        }

        start_time = time.time()

        # Define user-specific keys to warm
        keys_to_warm = [
            (
                CacheKeys.user_session(user_id),
                lambda: self._load_user_session(user_id),
                "session"
            ),
            (
                CacheKeys.navigation(user_id),
                lambda: self._load_user_navigation(user_id),
                "navigation"
            ),
        ]

        # Optionally add form data
        if preload_forms:
            recent_forms = self._get_user_recent_forms(user_id)
            for form_id in recent_forms[:5]:  # Limit to 5 most recent
                keys_to_warm.append((
                    CacheKeys.form_data(form_id, user_id),
                    lambda fid=form_id: self._load_user_form(user_id, fid),
                    f"form:{form_id}"
                ))

        for key, compute_fn, key_type in keys_to_warm:
            success = self.warm_key(
                key=key,
                compute_fn=compute_fn,
                tags={"user", f"user:{user_id}"}
            )

            if success:
                results["succeeded"] += 1
                results["keys_warmed"].append({"key": key, "type": key_type})
            else:
                results["failed"] += 1

        results["duration_ms"] = int((time.time() - start_time) * 1000)

        # Update preload cache
        with self._lock:
            self._user_preload_cache[user_id] = datetime.now()

        logger.info(
            "User data warmed",
            user_id=user_id,
            succeeded=results["succeeded"],
            duration_ms=results["duration_ms"]
        )

        return results

    def warm_by_usage_patterns(
        self,
        top_n: int = 10,
        min_access_frequency: float = 0.1
    ) -> dict[str, Any]:
        """
        Warm cache based on usage patterns with frequency filtering

        Args:
            top_n: Number of top keys to warm
            min_access_frequency: Minimum accesses per minute to consider

        Returns:
            Results dictionary with warming statistics
        """
        hot_keys = self._usage_tracker.get_hot_keys(top_n)

        results = {
            "total": 0,
            "succeeded": 0,
            "failed": 0,
            "skipped": 0,
            "keys": [],
            "duration_ms": 0
        }

        start_time = time.time()

        for key, access_count in hot_keys:
            # Check access frequency
            frequency = self._usage_tracker.get_access_frequency(
                key, window_minutes=60)

            if frequency < min_access_frequency:
                results["skipped"] += 1
                logger.debug(
                    "Skipping low-frequency key",
                    key=key,
                    frequency=frequency
                )
                continue

            results["total"] += 1

            # Find matching task
            task = None
            with self._lock:
                for t in self._tasks.values():
                    if t.cache_key == key:
                        task = t
                        break

            if task:
                success = self.warm_key(
                    key=task.cache_key,
                    compute_fn=task.compute_fn,
                    ttl=task.ttl,
                    tags=task.tags
                )

                if success:
                    results["succeeded"] += 1
                else:
                    results["failed"] += 1

                results["keys"].append({
                    "key": key,
                    "access_count": access_count,
                    "frequency": round(frequency, 2),
                    "success": success
                })

        results["duration_ms"] = int((time.time() - start_time) * 1000)

        logger.info(
            "Pattern-based warming completed",
            total=results["total"],
            succeeded=results["succeeded"],
            duration_ms=results["duration_ms"]
        )

        return results

    def start_background_warming(
        self,
        interval_minutes: int = 60,
        enable_pattern_warming: bool = True,
        enable_critical_warming: bool = True
    ) -> None:
        """
        Start background cache warming with configurable options

        Args:
            interval_minutes: Interval between warming cycles
            enable_pattern_warming: Enable usage pattern-based warming
            enable_critical_warming: Enable critical data warming
        """
        with self._lock:
            if self._running:
                logger.warning("Background warming already running")
                return

            self._running = True
            self._thread = threading.Thread(
                target=self._warming_loop,
                args=(
                    interval_minutes,
                    enable_pattern_warming,
                    enable_critical_warming),
                daemon=True)
            self._thread.start()

        logger.info(
            "Background cache warming started",
            interval_minutes=interval_minutes,
            pattern_warming=enable_pattern_warming,
            critical_warming=enable_critical_warming
        )

    def stop_background_warming(self) -> None:
        """Stop background cache warming"""
        with self._lock:
            self._running = False

        if self._thread:
            self._thread.join(timeout=5)

        logger.info("Background cache warming stopped")

    def _warming_loop(
        self,
        interval_minutes: int,
        enable_pattern_warming: bool,
        enable_critical_warming: bool
    ) -> None:
        """
        Background warming loop with optimized execution

        Args:
            interval_minutes: Interval between cycles
            enable_pattern_warming: Enable pattern-based warming
            enable_critical_warming: Enable critical data warming
        """
        cycle_count = 0

        while self._running:
            try:
                cycle_start = time.time()
                cycle_count += 1

                logger.info(
                    "Starting warming cycle",
                    cycle=cycle_count,
                    interval_minutes=interval_minutes
                )

                # Warm critical data (high priority)
                if enable_critical_warming:
                    critical_results = self.warm_critical_data()
                    logger.debug(
                        "Critical warming completed", succeeded=critical_results.get(
                            "succeeded", 0), duration_ms=critical_results.get(
                            "total_duration_ms", 0))

                # Warm by usage patterns (adaptive)
                if enable_pattern_warming:
                    pattern_results = self.warm_by_usage_patterns(
                        top_n=10,
                        min_access_frequency=0.1
                    )
                    logger.debug(
                        "Pattern warming completed",
                        succeeded=pattern_results.get("succeeded", 0),
                        duration_ms=pattern_results.get("duration_ms", 0)
                    )

                cycle_duration = time.time() - cycle_start

                logger.info(
                    "Warming cycle completed",
                    cycle=cycle_count,
                    duration_seconds=int(cycle_duration)
                )

                # Sleep until next warming
                time.sleep(interval_minutes * 60)

            except Exception as e:
                logger.error(
                    "Cache warming loop error",
                    error=str(e),
                    cycle=cycle_count
                )
                # Sleep a bit before retrying
                time.sleep(60)

    def _load_user_session(self, user_id: str) -> Any:
        """Load user session data"""
        try:
            from .session_repository import SessionRepository
            repo = SessionRepository()
            return repo.get_session_by_user(user_id)
        except Exception:
            return None

    def _load_user_navigation(self, user_id: str) -> Any:
        """Load user navigation data"""
        return {"user_id": user_id, "history": []}

    def _load_user_form(self, user_id: str, form_id: str) -> Any:
        """Load user form data"""
        try:
            from .form_manager import FormManager
            manager = FormManager()
            return manager.load_form(form_id, user_id)
        except Exception:
            return None

    def _get_user_recent_forms(self, user_id: str) -> list[str]:
        """Get list of user's recent form IDs"""
        try:
            from .form_manager import FormManager
            manager = FormManager()
            # This would query the database for recent forms
            # For now, return empty list
            return []
        except Exception:
            return []

    def get_performance_stats(self) -> dict[str, Any]:
        """Get warming performance statistics"""
        with self._lock:
            stats = self._performance_stats.copy()

            # Add derived metrics
            if stats["total_warmings"] > 0:
                stats["efficiency_score"] = (
                    100 * (1 - min(stats["avg_duration_ms"] / 1000, 1))
                )
            else:
                stats["efficiency_score"] = 0

            return stats

    def get_stats(self) -> dict[str, Any]:
        """Get comprehensive warming engine statistics"""
        with self._lock:
            return {
                "tasks": len(self._tasks),
                "critical_keys": len(self._critical_data_keys),
                "running": self._running,
                "users_preloaded": len(self._user_preload_cache),
                "performance": self.get_performance_stats(),
                "task_details": [
                    {
                        "task_id": task.task_id,
                        "name": task.name,
                        "enabled": task.enabled,
                        "priority": task.priority,
                        "is_critical": task.cache_key in self._critical_data_keys,
                        "run_count": task.run_count,
                        "avg_duration_ms": round(task.avg_duration_ms, 2),
                        "last_run": (
                            task.last_run.isoformat()
                            if task.last_run
                            else None
                        ),
                        "next_run": (
                            task.next_run.isoformat()
                            if task.next_run
                            else None
                        )
                    }
                    for task in self._tasks.values()
                ]
            }

    def optimize_schedules(self) -> dict[str, Any]:
        """
        Optimize warming schedules based on usage patterns and performance

        Returns:
            Optimization results
        """
        results = {
            "tasks_optimized": 0,
            "schedules_adjusted": []
        }

        with self._lock:
            for task in self._tasks.values():
                # Get access frequency for this key
                frequency = self._usage_tracker.get_access_frequency(
                    task.cache_key,
                    window_minutes=60
                )

                # Adjust schedule based on frequency
                old_interval = 60  # Default
                if frequency > 1.0:  # More than 1 access per minute
                    new_interval = 15  # Warm every 15 minutes
                elif frequency > 0.5:
                    new_interval = 30  # Warm every 30 minutes
                elif frequency > 0.1:
                    new_interval = 60  # Warm every hour
                else:
                    new_interval = 120  # Warm every 2 hours

                task.update_schedule(new_interval)
                results["tasks_optimized"] += 1
                results["schedules_adjusted"].append({
                    "task_id": task.task_id,
                    "frequency": round(frequency, 3),
                    "interval_minutes": new_interval
                })

        logger.info(
            "Warming schedules optimized",
            tasks_optimized=results["tasks_optimized"]
        )

        return results


# Global warming engine
_warming_engine: CacheWarmingEngine | None = None
_engine_lock = threading.Lock()


def get_warming_engine() -> CacheWarmingEngine:
    """Get global cache warming engine"""
    global _warming_engine
    with _engine_lock:
        if _warming_engine is None:
            _warming_engine = CacheWarmingEngine()
    return _warming_engine


def register_warming_task(task: WarmingTask) -> None:
    """Register cache warming task"""
    engine = get_warming_engine()
    engine.register_task(task)


def warm_cache(
    key: str,
    compute_fn: Callable[[], Any],
    ttl: int | None = None,
    tags: set[str] = None,
    force: bool = False
) -> bool:
    """
    Warm specific cache key

    Args:
        key: Cache key to warm
        compute_fn: Function to compute value
        ttl: Time to live in seconds
        tags: Cache tags for invalidation
        force: If True, recompute even if cached

    Returns:
        True if warming succeeded
    """
    engine = get_warming_engine()
    return engine.warm_key(key, compute_fn, ttl, tags, force)


def warm_critical_data() -> dict[str, Any]:
    """Warm all critical data"""
    engine = get_warming_engine()
    return engine.warm_critical_data()


def warm_user_data(user_id: str) -> dict[str, Any]:
    """Warm user-specific data"""
    engine = get_warming_engine()
    return engine.warm_user_data(user_id)


def start_cache_warming(
    interval_minutes: int = 60,
    enable_pattern_warming: bool = True,
    enable_critical_warming: bool = True
) -> None:
    """
    Start background cache warming

    Args:
        interval_minutes: Interval between warming cycles
        enable_pattern_warming: Enable usage pattern-based warming
        enable_critical_warming: Enable critical data warming
    """
    engine = get_warming_engine()
    engine.start_background_warming(
        interval_minutes,
        enable_pattern_warming,
        enable_critical_warming
    )


def stop_cache_warming() -> None:
    """Stop background cache warming"""
    engine = get_warming_engine()
    engine.stop_background_warming()


def get_warming_stats() -> dict[str, Any]:
    """Get warming engine statistics"""
    engine = get_warming_engine()
    return engine.get_stats()


def get_warming_performance() -> dict[str, Any]:
    """Get warming performance statistics"""
    engine = get_warming_engine()
    return engine.get_performance_stats()


def optimize_warming_schedules() -> dict[str, Any]:
    """Optimize warming schedules based on usage patterns"""
    engine = get_warming_engine()
    return engine.optimize_schedules()


def warm_user_data_optimized(
    user_id: str,
    force: bool = False,
    preload_forms: bool = True
) -> dict[str, Any]:
    """
    Warm user-specific data with optimization

    Args:
        user_id: User ID to warm data for
        force: Force refresh even if recently warmed
        preload_forms: Also preload user's recent forms

    Returns:
        Results dictionary
    """
    engine = get_warming_engine()
    return engine.warm_user_data(user_id, force, preload_forms)


def register_critical_task(task: WarmingTask) -> None:
    """Register a critical cache warming task"""
    engine = get_warming_engine()
    engine.register_task(task, is_critical=True)
