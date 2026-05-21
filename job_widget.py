"""
Job Management Widget for Streamlit Apps

Beispiel-Widget zur Integration von Phase 8 Job Manager
"""

import streamlit as st
import time
from typing import Optional, Callable, Any
from core_integration import get_job_manager, is_feature_enabled
from core.jobs import Job, JobPriority, JobStatus


def render_job_queue_widget(show_stats: bool = True, show_history: bool = True, auto_refresh: int = 5):
    """
    Rendere Job Queue Widget mit Stats und History
    
    Args:
        show_stats: Zeige Statistiken
        show_history: Zeige Job-Historie
        auto_refresh: Auto-Refresh Intervall in Sekunden (0 = aus)
    """
    if not is_feature_enabled('jobs'):
        st.warning("Job Manager ist deaktiviert")
        return
    
    job_mgr = get_job_manager()
    if not job_mgr:
        st.error("Job Manager nicht verfügbar")
        return
    
    st.markdown("###  Job Queue Status")
    
    # Statistics
    if show_stats:
        stats = job_mgr.get_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Pending", stats.get('pending', 0))
        with col2:
            st.metric("Running", stats.get('running', 0))
        with col3:
            st.metric("Completed", stats.get('completed', 0))
        with col4:
            st.metric("Failed", stats.get('failed', 0))
        
        # Success Rate
        total = stats.get('total', 0)
        if total > 0:
            success_rate = (stats.get('completed', 0) / total) * 100
            st.progress(success_rate / 100, text=f"Erfolgsquote: {success_rate:.1f}%")
    
    # Job History
    if show_history:
        st.markdown("**Aktive & Letzte Jobs:**")
        
        history = job_mgr.get_job_history(limit=10)
        
        if history:
            for job, result in history:
                render_job_card(job, result, job_mgr)
        else:
            st.info("Keine Jobs vorhanden")
    
    # Auto-Refresh
    if auto_refresh > 0:
        time.sleep(auto_refresh)
        st.rerun()


def render_job_card(job: Job, result: Any, job_mgr: Any):
    """Rendere einzelne Job-Karte"""
    status_config = {
        'completed': {'emoji': '✅', 'color': 'green'},
        'failed': {'emoji': '❌', 'color': 'red'},
        'running': {'emoji': '⏳', 'color': 'blue'},
        'pending': {'emoji': '⏸️', 'color': 'gray'},
        'cancelled': {'emoji': '🚫', 'color': 'orange'},
        'retrying': {'emoji': '🔄', 'color': 'yellow'},
    }
    
    status_str = result.status.value if hasattr(result.status, 'value') else str(result.status)
    config = status_config.get(status_str, {'emoji': '❓', 'color': 'gray'})
    
    with st.container():
        col1, col2, col3 = st.columns([6, 2, 2])
        
        with col1:
            job_name = job.name or f"Job {job.id[:8]}..."
            st.markdown(f"{config['emoji']} **{job_name}**")
            
            if result.progress > 0 and result.progress < 1.0:
                st.progress(result.progress, text=result.progress_message)
            elif result.progress_message:
                st.caption(result.progress_message)
        
        with col2:
            if result.duration_seconds:
                st.text(f"⏱ {result.duration_seconds:.2f}s")
            elif result.started_at:
                elapsed = (time.time() - result.started_at.timestamp())
                st.text(f"⏱ {elapsed:.2f}s")
        
        with col3:
            if status_str == 'running':
                if st.button("🚫", key=f"cancel_{job.id}", help="Job abbrechen"):
                    if job_mgr.cancel(job.id):
                        st.success("Job abgebrochen")
                        st.rerun()
        
        # Error Details
        if result.error:
            with st.expander("❌ Fehlerdetails"):
                st.error(result.error)
                if result.traceback:
                    st.code(result.traceback)
        
        st.markdown("---")


def render_job_submission_form(
    job_name: str,
    job_function: Callable,
    function_name: str,
    param_config: dict[str, dict[str, Any]],
    priority: JobPriority = JobPriority.NORMAL,
    max_retries: int = 3
):
    """
    Rendere Formular zur Job-Erstellung
    
    Args:
        job_name: Name des Jobs
        job_function: Job-Funktion
        function_name: Name für Registrierung
        param_config: Parameter-Konfiguration
            {'param_name': {'type': 'text'|'number'|'select', 'label': 'Label', 'options': [...], 'default': ...}}
        priority: Job-Priorität
        max_retries: Max. Wiederholungen
    
    Example:
        render_job_submission_form(
            job_name="PDF-Generierung",
            job_function=generate_pdf_worker,
            function_name='generate_pdf',
            param_config={
                'project_id': {'type': 'number', 'label': 'Projekt-ID', 'default': 0},
                'firma_index': {'type': 'select', 'label': 'Firma', 'options': list(range(7)), 'default': 0}
            },
            priority=JobPriority.HIGH
        )
    """
    if not is_feature_enabled('jobs'):
        st.warning("Job Manager ist deaktiviert")
        return None
    
    st.markdown(f"### ➕ {job_name} erstellen")
    
    with st.form(key=f"job_form_{function_name}"):
        # Parameter-Inputs
        params = {}
        
        for param_name, config in param_config.items():
            param_type = config.get('type', 'text')
            label = config.get('label', param_name)
            default = config.get('default')
            
            if param_type == 'text':
                params[param_name] = st.text_input(label, value=default or "")
            elif param_type == 'number':
                params[param_name] = st.number_input(label, value=default or 0)
            elif param_type == 'select':
                options = config.get('options', [])
                params[param_name] = st.selectbox(label, options, index=options.index(default) if default in options else 0)
            elif param_type == 'checkbox':
                params[param_name] = st.checkbox(label, value=default or False)
        
        # Priority
        priority_options = {
            'Niedrig': JobPriority.LOW,
            'Normal': JobPriority.NORMAL,
            'Hoch': JobPriority.HIGH,
            'Kritisch': JobPriority.CRITICAL
        }
        selected_priority = st.selectbox(
            "Priorität",
            options=list(priority_options.keys()),
            index=1  # Normal
        )
        
        # Submit
        submitted = st.form_submit_button(" Job starten")
        
        if submitted:
            try:
                job_mgr = get_job_manager()
                
                # Register function if not already registered
                if function_name not in job_mgr.function_registry:
                    job_mgr.register_function(function_name, job_function)
                
                # Create job
                job = Job(
                    name=job_name,
                    function_name=function_name,
                    kwargs=params,
                    priority=priority_options[selected_priority],
                    max_retries=max_retries
                )
                
                job_id = job_mgr.enqueue(job)
                
                st.success(f"Job gestartet! ID: {job_id[:8]}...")
                
                # Store in session for tracking
                if 'active_jobs' not in st.session_state:
                    st.session_state['active_jobs'] = []
                st.session_state['active_jobs'].append(job_id)
                
                st.rerun()
                
                return job_id
            
            except Exception as e:
                st.error(f"Fehler beim Starten des Jobs: {e}")
                return None


def render_job_tracker(job_ids: list[str], show_download: bool = False):
    """
    Tracke mehrere Jobs gleichzeitig
    
    Args:
        job_ids: Liste von Job-IDs
        show_download: Zeige Download-Button für completed Jobs
    """
    if not is_feature_enabled('jobs'):
        return
    
    job_mgr = get_job_manager()
    if not job_mgr:
        return
    
    st.markdown("###  Job Tracking")
    
    completed_count = 0
    running_count = 0
    failed_count = 0
    
    for job_id in job_ids:
        result = job_mgr.poll(job_id)
        
        if not result:
            continue
        
        status = result.status.value if hasattr(result.status, 'value') else str(result.status)
        
        if status == 'completed':
            completed_count += 1
        elif status == 'running':
            running_count += 1
        elif status == 'failed':
            failed_count += 1
        
        # Progress für jeden Job
        with st.container():
            col1, col2 = st.columns([8, 2])
            
            with col1:
                st.text(f"Job {job_id[:8]}... - {status}")
                
                if result.progress > 0:
                    st.progress(result.progress, text=result.progress_message)
            
            with col2:
                if status == 'completed' and show_download and result.result:
                    if isinstance(result.result, dict) and 'pdf_path' in result.result:
                        with open(result.result['pdf_path'], 'rb') as f:
                            st.download_button(
                                label="",
                                data=f,
                                file_name=f"job_{job_id[:8]}.pdf",
                                mime="application/pdf",
                                key=f"download_{job_id}"
                            )
    
    # Summary
    total = len(job_ids)
    st.markdown("---")
    st.markdown(f"**Gesamt:** {total} | **Fertig:** {completed_count} | **Laufend:** {running_count} | **Fehler:** {failed_count}")
    
    # Progress gesamt
    if total > 0:
        overall_progress = completed_count / total
        st.progress(overall_progress, text=f"{completed_count}/{total} Jobs fertig")
        
        # Auto-Refresh wenn noch Jobs laufen
        if running_count > 0:
            time.sleep(2)
            st.rerun()


def render_job_manager_admin():
    """Rendere Admin-Panel für Job Manager"""
    if not is_feature_enabled('jobs'):
        st.warning("Job Manager ist deaktiviert")
        return
    
    job_mgr = get_job_manager()
    if not job_mgr:
        st.error("Job Manager nicht verfügbar")
        return
    
    st.markdown("##  Job Manager Administration")
    
    # Statistics
    stats = job_mgr.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Jobs", stats.get('total', 0))
    with col2:
        st.metric("Workers", f"{stats.get('workers_active', 0)}/{stats.get('workers', 0)}")
    with col3:
        st.metric("Dead Letter Queue", stats.get('dead_letter', 0))
    with col4:
        success_rate = 0
        total = stats.get('total', 0)
        if total > 0:
            success_rate = (stats.get('completed', 0) / total) * 100
        st.metric("Erfolgsquote", f"{success_rate:.2f}%")
    
    # Management Actions
    st.markdown("### Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(" Dead Letter Queue leeren"):
            job_mgr.clear_dead_letter_queue()
            st.success("Dead Letter Queue geleert")
            st.rerun()
    
    with col2:
        if st.button(" Alte Jobs löschen (7 Tage)"):
            count = job_mgr.cleanup_old_results(retention_days=7)
            st.success(f"{count} alte Jobs gelöscht")
            st.rerun()
    
    with col3:
        if st.button("🔄 Aktualisieren"):
            st.rerun()
    
    # Running Jobs
    st.markdown("### Laufende Jobs")
    running_jobs = job_mgr.get_running_jobs()
    
    if running_jobs:
        for job in running_jobs:
            result = job_mgr.poll(job.id)
            if result:
                render_job_card(job, result, job_mgr)
    else:
        st.info("Keine laufenden Jobs")
    
    # Dead Letter Queue
    if stats.get('dead_letter', 0) > 0:
        st.markdown("###  Dead Letter Queue")
        
        dlq = job_mgr.get_dead_letter_queue()
        
        for job, result in dlq:
            with st.expander(f"❌ {job.name} ({job.id[:8]}...)"):
                st.error(f"**Fehler:** {result.error}")
                st.text(f"Retries: {job.retry_count}/{job.max_retries}")
                
                if result.traceback:
                    st.code(result.traceback)


# Example Usage
if __name__ == "__main__":
    st.set_page_config(page_title="Job Manager Widget Demo", layout="wide")
    
    st.title("Job Manager Widget Demo")
    
    tab1, tab2, tab3 = st.tabs([" Queue Status", "➕ Job erstellen", "⚙️ Admin"])
    
    with tab1:
        render_job_queue_widget(show_stats=True, show_history=True, auto_refresh=0)
    
    with tab2:
        # Beispiel: PDF-Generierung
        def generate_test_pdf(project_id, firma_index):
            import time
            time.sleep(2)  # Simuliere Arbeit
            return {'pdf_path': f'/tmp/test_project_{project_id}_firma_{firma_index}.pdf', 'success': True}
        
        render_job_submission_form(
            job_name="Test PDF-Generierung",
            job_function=generate_test_pdf,
            function_name='generate_test_pdf',
            param_config={
                'project_id': {'type': 'number', 'label': 'Projekt-ID', 'default': 123},
                'firma_index': {'type': 'select', 'label': 'Firma', 'options': list(range(7)), 'default': 0}
            },
            priority=JobPriority.HIGH
        )
        
        # Job Tracker
        if 'active_jobs' in st.session_state and st.session_state['active_jobs']:
            st.markdown("---")
            render_job_tracker(st.session_state['active_jobs'], show_download=True)
    
    with tab3:
        render_job_manager_admin()
