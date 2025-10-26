"""Real-time Pricing Update System

This module provides event-driven pricing recalculation with debounced updates,
change detection, and notification system for real-time pricing updates.
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class PricingEventType(Enum):
    """Types of pricing events that trigger updates"""
    COMPONENT_CHANGED = "component_changed"
    QUANTITY_CHANGED = "quantity_changed"
    MODIFICATION_CHANGED = "modification_changed"
    PRODUCT_PRICE_CHANGED = "product_price_changed"
    MARGIN_CHANGED = "margin_changed"
    VAT_CHANGED = "vat_changed"
    SYSTEM_TYPE_CHANGED = "system_type_changed"
    CACHE_INVALIDATED = "cache_invalidated"


class UpdatePriority(Enum):
    """Priority levels for pricing updates"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class PricingEvent:
    """Represents a pricing change event"""
    event_type: PricingEventType
    event_data: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    priority: UpdatePriority = UpdatePriority.NORMAL
    source: str | None = None
    system_type: str | None = None

    def __hash__(self) -> int:
        """Make event hashable for deduplication"""
        return hash((self.event_type, self.source, self.system_type))


@dataclass
class UpdateRequest:
    """Represents a pending update request"""
    request_id: str
    events: list[PricingEvent]
    calculation_data: dict[str, Any]
    system_type: str
    priority: UpdatePriority
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: datetime | None = None
    callback: Callable | None = None


class ChangeDetector:
    """Detects changes in pricing-related data"""

    def __init__(self):
        self._previous_states: dict[str, str] = {}
        self._change_thresholds = {
            "quantity": 0.01,  # Minimum quantity change to trigger update
            "price": 0.01,     # Minimum price change (in euros)
            "percentage": 0.1  # Minimum percentage change
        }

    def detect_changes(self, current_data: dict[str, Any],
                       context: str = "default") -> list[PricingEvent]:
        """Detect changes in pricing data

        Args:
            current_data: Current pricing data
            context: Context identifier for change detection

        Returns:
            List of detected pricing events
        """
        events = []

        try:
            # Generate hash of current data
            current_hash = self._hash_data(current_data)
            previous_hash = self._previous_states.get(context)

            if previous_hash is None:
                # First time seeing this context
                self._previous_states[context] = current_hash
                return events

            if current_hash == previous_hash:
                # No changes detected
                return events

            # Data has changed, analyze specific changes
            events.extend(self._analyze_component_changes(
                current_data, context))
            events.extend(self._analyze_modification_changes(
                current_data, context))
            events.extend(self._analyze_system_changes(current_data, context))

            # Update stored state
            self._previous_states[context] = current_hash

        except Exception as e:
            logger.error(f"Error detecting changes: {e}")

        return events

    def _hash_data(self, data: dict[str, Any]) -> str:
        """Generate hash for data comparison"""
        try:
            # Create normalized data for consistent hashing
            normalized = {
                "components": sorted([
                    {
                        "id": comp.get("product_id", comp.get("model_name", "")),
                        "qty": comp.get("quantity", 1)
                    }
                    for comp in data.get("components", [])
                ], key=lambda x: str(x["id"])),
                "modifications": data.get("modifications", {}),
                "system_type": data.get("system_type", "pv"),
                "vat_rate": data.get("vat_rate", 19.0)
            }

            data_str = json.dumps(normalized, sort_keys=True, default=str)
            return hashlib.md5(data_str.encode()).hexdigest()

        except Exception as e:
            logger.error(f"Error hashing data: {e}")
            return str(hash(str(data)))

    def _analyze_component_changes(self, data: dict[str, Any],
                                   context: str) -> list[PricingEvent]:
        """Analyze component-specific changes"""
        events = []

        try:
            components = data.get("components", [])

            # Only generate events if we detect actual changes
            # The main change detection is done by hash comparison
            # This method is called only when hash indicates changes

            # Generate a generic component change event since we know something
            # changed
            if components:
                events.append(PricingEvent(
                    event_type=PricingEventType.COMPONENT_CHANGED,
                    event_data={
                        "components": components,
                        "context": context
                    },
                    priority=UpdatePriority.HIGH,
                    source="component_analysis"
                ))

        except Exception as e:
            logger.error(f"Error analyzing component changes: {e}")

        return events

    def _analyze_modification_changes(self, data: dict[str, Any],
                                      context: str) -> list[PricingEvent]:
        """Analyze pricing modification changes"""
        events = []

        try:
            modifications = data.get("modifications", {})

            # Only generate events if modifications exist and we know something
            # changed
            if modifications:
                events.append(PricingEvent(
                    event_type=PricingEventType.MODIFICATION_CHANGED,
                    event_data={
                        "modifications": modifications,
                        "context": context
                    },
                    priority=UpdatePriority.NORMAL,
                    source="modification_analysis"
                ))

        except Exception as e:
            logger.error(f"Error analyzing modification changes: {e}")

        return events

    def _analyze_system_changes(self, data: dict[str, Any],
                                context: str) -> list[PricingEvent]:
        """Analyze system-level changes"""
        events = []

        try:
            # Only generate system change events if we detect actual changes
            # This is called only when hash comparison indicates changes
            system_type = data.get("system_type", "pv")

            # Generate a generic system change event
            events.append(PricingEvent(
                event_type=PricingEventType.SYSTEM_TYPE_CHANGED,
                event_data={
                    "system_type": system_type,
                    "context": context
                },
                priority=UpdatePriority.NORMAL,
                source="system_analysis"
            ))

        except Exception as e:
            logger.error(f"Error analyzing system changes: {e}")

        return events

    def _is_significant_change(self, value: Any, change_type: str) -> bool:
        """Check if a change is significant enough to trigger update"""
        try:
            threshold = self._change_thresholds.get(change_type, 0.01)

            if isinstance(value, (int, float)):
                return abs(value) >= threshold

            return True  # Non-numeric changes are always significant

        except Exception:
            return True


class DebouncedUpdateManager:
    """Manages debounced updates to prevent excessive calculations"""

    def __init__(self, debounce_delay: float = 0.5, max_delay: float = 5.0):
        """Initialize debounced update manager

        Args:
            debounce_delay: Delay in seconds before processing updates
            max_delay: Maximum delay before forcing an update
        """
        self.debounce_delay = debounce_delay
        self.max_delay = max_delay
        self._pending_updates: dict[str, UpdateRequest] = {}
        self._update_timers: dict[str, threading.Timer] = {}
        self._lock = threading.RLock()
        self._is_running = True

        # Start cleanup thread
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_expired_updates, daemon=True)
        self._cleanup_thread.start()

    def schedule_update(self, request: UpdateRequest,
                        force_immediate: bool = False) -> None:
        """Schedule a debounced update

        Args:
            request: Update request to schedule
            force_immediate: Whether to force immediate execution
        """
        with self._lock:
            if not self._is_running:
                return

            context_key = f"{request.system_type}_{request.request_id}"

            # Cancel existing timer for this context
            if context_key in self._update_timers:
                self._update_timers[context_key].cancel()
                del self._update_timers[context_key]

            # Merge with existing request if present
            if context_key in self._pending_updates:
                existing_request = self._pending_updates[context_key]
                request = self._merge_update_requests(
                    existing_request, request)

            self._pending_updates[context_key] = request

            if force_immediate or request.priority == UpdatePriority.CRITICAL:
                # Execute immediately
                self._execute_update(context_key)
            else:
                # Check if we've exceeded max delay
                time_since_creation = datetime.now() - request.created_at
                if time_since_creation.total_seconds() >= self.max_delay:
                    self._execute_update(context_key)
                else:
                    # Schedule debounced execution
                    delay = min(
                        self.debounce_delay,
                        self.max_delay -
                        time_since_creation.total_seconds())

                    timer = threading.Timer(
                        delay, self._execute_update, args=[context_key])
                    timer.start()
                    self._update_timers[context_key] = timer

    def _merge_update_requests(self, existing: UpdateRequest,
                               new: UpdateRequest) -> UpdateRequest:
        """Merge two update requests"""
        # Use higher priority
        priority = max([existing.priority, new.priority],
                       key=lambda p: p.value)

        # Merge events (deduplicate)
        all_events = existing.events + new.events
        unique_events = list({event: event for event in all_events}.values())

        # Use newer calculation data
        calculation_data = new.calculation_data

        # Use newer callback if available
        callback = new.callback or existing.callback

        return UpdateRequest(
            request_id=new.request_id,
            events=unique_events,
            calculation_data=calculation_data,
            system_type=new.system_type,
            priority=priority,
            created_at=existing.created_at,  # Keep original creation time
            callback=callback
        )

    def _execute_update(self, context_key: str) -> None:
        """Execute a pending update"""
        with self._lock:
            if context_key not in self._pending_updates:
                return

            request = self._pending_updates.pop(context_key)

            # Remove timer if exists
            if context_key in self._update_timers:
                del self._update_timers[context_key]

        try:
            # Execute the update
            if request.callback:
                request.callback(request)

            logger.debug(f"Executed update for context: {context_key}")

        except Exception as e:
            logger.error(f"Error executing update for {context_key}: {e}")

    def _cleanup_expired_updates(self) -> None:
        """Clean up expired update requests"""
        while self._is_running:
            try:
                time.sleep(10)  # Check every 10 seconds

                with self._lock:
                    current_time = datetime.now()
                    expired_keys = []

                    for key, request in self._pending_updates.items():
                        age = current_time - request.created_at
                        if age.total_seconds() > self.max_delay * 2:  # Double max delay
                            expired_keys.append(key)

                    for key in expired_keys:
                        if key in self._pending_updates:
                            del self._pending_updates[key]
                        if key in self._update_timers:
                            self._update_timers[key].cancel()
                            del self._update_timers[key]

                    if expired_keys:
                        logger.info(
                            f"Cleaned up {
                                len(expired_keys)} expired update requests")

            except Exception as e:
                logger.error(f"Error in cleanup thread: {e}")

    def shutdown(self) -> None:
        """Shutdown the update manager"""
        with self._lock:
            self._is_running = False

            # Cancel all pending timers
            for timer in self._update_timers.values():
                timer.cancel()

            self._update_timers.clear()
            self._pending_updates.clear()


class PricingUpdateNotifier:
    """Notification system for pricing changes"""

    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)
        self._global_subscribers: list[Callable] = []
        self._notification_history: deque = deque(maxlen=100)
        self._lock = threading.RLock()

    def subscribe(self, callback: Callable,
                  event_types: list[PricingEventType] | None = None,
                  system_types: list[str] | None = None) -> str:
        """Subscribe to pricing update notifications

        Args:
            callback: Function to call on updates
            event_types: Specific event types to subscribe to
            system_types: Specific system types to subscribe to

        Returns:
            Subscription ID for unsubscribing
        """
        with self._lock:
            subscription_id = f"sub_{id(callback)}_{int(time.time())}"

            if event_types is None and system_types is None:
                # Global subscription - store callback with ID
                self._global_subscribers.append((callback, subscription_id))
            else:
                # Specific subscription - store callback with ID
                key = self._create_subscription_key(event_types, system_types)
                self._subscribers[key].append((callback, subscription_id))

            logger.debug(f"Added subscription: {subscription_id}")
            return subscription_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from notifications

        Args:
            subscription_id: ID returned from subscribe()

        Returns:
            True if successfully unsubscribed
        """
        with self._lock:
            # Try to remove from global subscribers
            for i in range(len(self._global_subscribers) - 1, -1, -1):
                callback, sub_id = self._global_subscribers[i]
                if sub_id == subscription_id:
                    del self._global_subscribers[i]
                    return True

            # Try to remove from specific subscribers
            for key in list(self._subscribers.keys()):
                callbacks = self._subscribers[key]
                for i in range(len(callbacks) - 1, -1, -1):
                    callback, sub_id = callbacks[i]
                    if sub_id == subscription_id:
                        del callbacks[i]
                        if not callbacks:  # Remove empty list
                            del self._subscribers[key]
                        return True

            return False

    def notify(self, events: list[PricingEvent],
               calculation_result: dict[str, Any] | None = None) -> None:
        """Notify subscribers of pricing events

        Args:
            events: List of pricing events
            calculation_result: Optional calculation result data
        """
        with self._lock:
            notification_data = {
                "events": events,
                "calculation_result": calculation_result,
                "timestamp": datetime.now()
            }

            # Add to history
            self._notification_history.append(notification_data)

            # Notify global subscribers
            for callback, sub_id in self._global_subscribers:
                try:
                    callback(notification_data)
                except Exception as e:
                    logger.error(f"Error in global notification callback: {e}")

            # Notify specific subscribers
            for event in events:
                matching_keys = self._find_matching_subscription_keys(event)

                for key in matching_keys:
                    for callback, sub_id in self._subscribers.get(key, []):
                        try:
                            callback(notification_data)
                        except Exception as e:
                            logger.error(
                                f"Error in specific notification callback: {e}")

    def get_notification_history(
            self, limit: int = 50) -> list[dict[str, Any]]:
        """Get recent notification history

        Args:
            limit: Maximum number of notifications to return

        Returns:
            List of recent notifications
        """
        with self._lock:
            return list(self._notification_history)[-limit:]

    def _create_subscription_key(self,
                                 event_types: list[PricingEventType] | None,
                                 system_types: list[str] | None) -> str:
        """Create subscription key from criteria"""
        event_str = ",".join(sorted([et.value for et in event_types or []]))
        system_str = ",".join(sorted(system_types or []))
        return f"events:{event_str}|systems:{system_str}"

    def _find_matching_subscription_keys(
            self, event: PricingEvent) -> list[str]:
        """Find subscription keys that match an event"""
        matching_keys = []

        for key in self._subscribers.keys():
            if self._key_matches_event(key, event):
                matching_keys.append(key)

        return matching_keys

    def _key_matches_event(self, key: str, event: PricingEvent) -> bool:
        """Check if subscription key matches event"""
        try:
            parts = key.split("|")
            events_part = parts[0].replace("events:", "")
            systems_part = parts[1].replace("systems:", "")

            # Check event type match
            if events_part and event.event_type.value not in events_part.split(
                    ","):
                return False

            # Check system type match
            if systems_part and event.system_type and event.system_type not in systems_part.split(
                    ","):
                return False

            return True

        except Exception:
            return False


class RealTimePricingUpdateSystem:
    """Main real-time pricing update system"""

    def __init__(self, debounce_delay: float = 0.5, max_delay: float = 5.0):
        """Initialize real-time pricing update system

        Args:
            debounce_delay: Delay in seconds before processing updates
            max_delay: Maximum delay before forcing an update
        """
        self.change_detector = ChangeDetector()
        self.update_manager = DebouncedUpdateManager(debounce_delay, max_delay)
        self.notifier = PricingUpdateNotifier()
        self._pricing_engines: dict[str, Any] = {}
        self._is_running = True

        logger.info("Initialized RealTimePricingUpdateSystem")

    def register_pricing_engine(self, system_type: str, engine: Any) -> None:
        """Register a pricing engine for a system type

        Args:
            system_type: System type identifier
            engine: Pricing engine instance
        """
        self._pricing_engines[system_type] = engine
        logger.info(
            f"Registered pricing engine for system type: {system_type}")

    def trigger_update(self, calculation_data: dict[str, Any],
                       system_type: str = "pv",
                       context: str = "default",
                       force_immediate: bool = False,
                       callback: Callable | None = None) -> str:
        """Trigger a pricing update

        Args:
            calculation_data: Current calculation data
            system_type: System type for calculation
            context: Context identifier for change detection
            force_immediate: Whether to force immediate execution
            callback: Optional callback for update completion

        Returns:
            Update request ID
        """
        try:
            # Detect changes
            events = self.change_detector.detect_changes(
                calculation_data, context)

            if not events and not force_immediate:
                logger.debug(
                    "No significant changes detected, skipping update")
                return ""

            # Determine priority
            priority = UpdatePriority.CRITICAL if force_immediate else self._calculate_priority(
                events)

            # Create update request
            request_id = f"update_{int(time.time() *
                                       1000)}_{hash(str(calculation_data)) %
                                               10000}"

            update_request = UpdateRequest(
                request_id=request_id,
                events=events,
                calculation_data=calculation_data,
                system_type=system_type,
                priority=priority,
                callback=callback or self._default_update_callback
            )

            # Schedule update
            self.update_manager.schedule_update(
                update_request, force_immediate)

            logger.debug(
                f"Triggered pricing update: {request_id} with {
                    len(events)} events")
            return request_id

        except Exception as e:
            logger.error(f"Error triggering pricing update: {e}")
            return ""

    def subscribe_to_updates(self, callback: Callable,
                             event_types: list[PricingEventType] | None = None,
                             system_types: list[str] | None = None) -> str:
        """Subscribe to pricing update notifications

        Args:
            callback: Function to call on updates
            event_types: Specific event types to subscribe to
            system_types: Specific system types to subscribe to

        Returns:
            Subscription ID
        """
        return self.notifier.subscribe(callback, event_types, system_types)

    def unsubscribe_from_updates(self, subscription_id: str) -> bool:
        """Unsubscribe from pricing update notifications

        Args:
            subscription_id: Subscription ID to remove

        Returns:
            True if successfully unsubscribed
        """
        return self.notifier.unsubscribe(subscription_id)

    def get_update_history(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get recent update history

        Args:
            limit: Maximum number of updates to return

        Returns:
            List of recent updates
        """
        return self.notifier.get_notification_history(limit)

    def shutdown(self) -> None:
        """Shutdown the update system"""
        self._is_running = False
        self.update_manager.shutdown()
        logger.info("RealTimePricingUpdateSystem shutdown complete")

    def _calculate_priority(
            self,
            events: list[PricingEvent]) -> UpdatePriority:
        """Calculate priority based on events"""
        if not events:
            return UpdatePriority.LOW

        max_priority = max(
            (event.priority for event in events), key=lambda p: p.value)
        return max_priority

    def _default_update_callback(self, request: UpdateRequest) -> None:
        """Default callback for update completion"""
        try:
            system_type = request.system_type
            calculation_data = request.calculation_data

            # Get pricing engine
            engine = self._pricing_engines.get(system_type)
            if not engine:
                logger.warning(
                    f"No pricing engine registered for system type: {system_type}")
                # Still notify subscribers even without engine
                self.notifier.notify(request.events, {
                    "error": f"No pricing engine for {system_type}",
                    "system_type": system_type,
                    "request_id": request.request_id
                })
                return

            # Calculate pricing
            result = engine.generate_final_price(calculation_data)

            # Convert result to dictionary for notification
            result_data = {
                "base_price": result.base_price,
                "final_price_net": result.final_price_net,
                "final_price_gross": result.final_price_gross,
                "total_discounts": result.total_discounts,
                "total_surcharges": result.total_surcharges,
                "vat_amount": result.vat_amount,
                "component_count": len(
                    result.components),
                "dynamic_keys": result.dynamic_keys,
                "metadata": result.metadata,
                "calculation_timestamp": result.calculation_timestamp.isoformat(),
                "system_type": system_type,
                "request_id": request.request_id}

            # Notify subscribers
            self.notifier.notify(request.events, result_data)

            logger.debug(f"Completed pricing update: {request.request_id}")

        except Exception as e:
            logger.error(f"Error in default update callback: {e}")
            # Still notify subscribers about the error
            self.notifier.notify(request.events, {
                "error": str(e),
                "system_type": request.system_type,
                "request_id": request.request_id
            })


# Global instance
_global_update_system: RealTimePricingUpdateSystem | None = None


def get_real_time_update_system() -> RealTimePricingUpdateSystem:
    """Get global real-time update system instance"""
    global _global_update_system
    if _global_update_system is None:
        _global_update_system = RealTimePricingUpdateSystem()
    return _global_update_system


def reset_update_system() -> None:
    """Reset global update system (mainly for testing)"""
    global _global_update_system
    if _global_update_system:
        _global_update_system.shutdown()
    _global_update_system = None
