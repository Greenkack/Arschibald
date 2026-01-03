"""Job UI Components for Streamlit"""

import time

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

from .jobs import JobResult, JobStatus, get_job_manager, poll


def render_job_progress(
    job_id: str,
    poll_interval: float = 0.5,
    show_details: bool = True,
    container=None
) -> JobResult | None:
    """
    Render job progress with progress bar (no spinners)

    Args:
        job_id: Job ID to track
        poll_interval: Polling interval in seconds
        show_details: Show detailed progress information
        container: Optional Streamlit container to render in

    Returns:
        Final JobResult when job completes
    """
    if not STREAMLIT_AVAILABLE:
        raise ImportError("Streamlit is required for job UI")

    if container is None:
        container = st

    # Create placeholder for progress
    progress_placeholder = container.empty()
    status_placeholder = container.empty()
    details_placeholder = container.empty() if show_details else None

    while True:
        result = poll(job_id)

        if result is None:
            status_placeholder.warning("Job not found")
            return None

        # Update progress bar
        progress_placeholder.progress(
            result.progress,
            text=result.progress_message or f"Progress: {int(result.progress * 100)}%"
        )

        # Update status
        status_text = f"Status: {result.status.value}"
        if result.status == JobStatus.RUNNING:
            status_placeholder.info(status_text)
        elif result.status == JobStatus.COMPLETED:
            status_placeholder.success(status_text)
            progress_placeholder.empty()  # Clear progress bar
            return result
        elif result.status == JobStatus.FAILED:
            status_placeholder.error(f"{status_text} - {result.error}")
            progress_placeholder.empty()
            return result
        elif result.status == JobStatus.CANCELLED:
            status_placeholder.warning(status_text)
            progress_placeholder.empty()
            return result
        else:
            status_placeholder.info(status_text)

        # Show details if requested
        if show_details and details_placeholder and result.progress_details:
            details_placeholder.json(result.progress_details)

        # Poll interval
        if result.status in [
                JobStatus.RUNNING,
                JobStatus.QUEUED,
                JobStatus.PENDING,
                JobStatus.RETRYING]:
            time.sleep(poll_interval)
        else:
            break

    return result


def render_job_status_dashboard(container=None) -> None:
    """
    Render unified job status dashboard

    Args:
        container: Optional Streamlit container to render in
    """
    if not STREAMLIT_AVAILABLE:
        raise ImportError("Streamlit is required for job UI")

    if container is None:
        container = st

    manager = get_job_manager()

    # Get statistics
    try:
        from .job_repository import JobRepository
        repo = JobRepository()
        stats = repo.get_job_statistics()
    except Exception as e:
        logger.error("Failed to get job statistics", error=str(e))
        stats = {}

    # Display statistics
    col1, col2, col3, col4 = container.columns(4)

    with col1:
        st.metric("Total Jobs", stats.get('total', 0))

    with col2:
        st.metric("Running", stats.get('running', 0))

    with col3:
        st.metric("Queued", stats.get('queued', 0) + stats.get('pending', 0))

    with col4:
        st.metric("Failed", stats.get('failed', 0))

    # Show running jobs
    running_jobs = manager.get_running_jobs()

    if running_jobs:
        container.subheader("Running Jobs")

        for job in running_jobs:
            with container.expander(f"{job.name} ({job.id[:8]})"):
                result = poll(job.id)
                if result:
                    st.progress(result.progress, text=result.progress_message)
                    st.text(f"Status: {result.status.value}")
                    if result.progress_details:
                        st.json(result.progress_details)

    # Show queue size
    queue_size = manager.get_queue_size()
    if queue_size > 0:
        container.info(f"Jobs in queue: {queue_size}")

    # Show dead letter queue
    dead_letter = manager.get_dead_letter_queue()
    if dead_letter:
        container.subheader("Failed Jobs (Dead Letter Queue)")

        for job, result in dead_letter:
            with container.expander(f"{job.name} ({job.id[:8]}) - FAILED"):
                st.error(f"Error: {result.error}")
                if result.traceback:
                    st.code(result.traceback, language="python")

                if st.button(f"Retry {job.id[:8]}"):
                    # Reset retry count and re-enqueue
                    job.retry_count = 0
                    manager.enqueue(job)
                    st.success("Job re-queued")
                    st.rerun()


def create_job_progress_widget(
    job_id: str,
    title: str = "Job Progress",
    auto_refresh: bool = True,
    refresh_interval: int = 1
) -> None:
    """
    Create a self-refreshing job progress widget

    Args:
        job_id: Job ID to track
        title: Widget title
        auto_refresh: Auto-refresh the widget
        refresh_interval: Refresh interval in seconds
    """
    if not STREAMLIT_AVAILABLE:
        raise ImportError("Streamlit is required for job UI")

    st.subheader(title)

    result = poll(job_id)

    if result is None:
        st.warning("Job not found")
        return

    # Progress bar
    st.progress(
        result.progress,
        text=result.progress_message or f"Progress: {int(result.progress * 100)}%"
    )

    # Status badge
    if result.status == JobStatus.RUNNING:
        st.info(f"Status: {result.status.value}")
    elif result.status == JobStatus.COMPLETED:
        st.success(f"Status: {result.status.value}")
    elif result.status == JobStatus.FAILED:
        st.error(f"Status: {result.status.value}")
        if result.error:
            st.error(f"Error: {result.error}")
    elif result.status == JobStatus.CANCELLED:
        st.warning(f"Status: {result.status.value}")
    else:
        st.info(f"Status: {result.status.value}")

    # Details
    if result.progress_details:
        with st.expander("Details"):
            st.json(result.progress_details)

    # Timing information
    if result.started_at:
        st.text(f"Started: {result.started_at.strftime('%Y-%m-%d %H:%M:%S')}")

    if result.completed_at:
        st.text(
            f"Completed: {
                result.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")

    if result.duration_seconds:
        st.text(f"Duration: {result.duration_seconds:.2f}s")

    # Auto-refresh for running jobs
    if auto_refresh and result.status in [
            JobStatus.RUNNING,
            JobStatus.QUEUED,
            JobStatus.PENDING]:
        time.sleep(refresh_interval)
        st.rerun()


def cancel_job_button(job_id: str, label: str = "Cancel Job") -> bool:
    """
    Render a cancel job button

    Args:
        job_id: Job ID to cancel
        label: Button label

    Returns:
        True if job was cancelled
    """
    if not STREAMLIT_AVAILABLE:
        raise ImportError("Streamlit is required for job UI")

    from .jobs import cancel

    if st.button(label, key=f"cancel_{job_id}"):
        if cancel(job_id):
            st.success("Job cancelled successfully")
            return True
        st.error("Failed to cancel job")
        return False

    return False
