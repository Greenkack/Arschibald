"""
css_template_manager.py
Verwaltet CSS-Template-Integration in Streamlit
"""

import os
from pathlib import Path

import streamlit as st


class CSSTemplateManager:
    """Verwaltet CSS-Template-Integration in Streamlit ohne bestehende Funktionen zu beeinträchtigen"""

    def __init__(self, template_dir: str = "static/css"):
        self.template_dir = Path(template_dir)
        self.loaded_templates: dict[str, str] = {}
        self.intro_enabled = True
        self.context_menu_enabled = True

    def load_template_css(self, template_name: str) -> str:
        """Lädt CSS-Template aus Datei"""
        css_path = self.template_dir / f"{template_name}.css"

        if css_path.exists():
            try:
                with open(css_path, encoding='utf-8') as f:
                    css_content = f.read()
                    self.loaded_templates[template_name] = css_content
                    return css_content
            except Exception as e:
                print(f"⚠️ Fehler beim Laden von {css_path}: {e}")
                return ""
        else:
            print(f"⚠️ Template nicht gefunden: {css_path}")
            return ""

    def load_all_templates(self) -> str:
        """Lädt alle CSS-Templates im Template-Verzeichnis"""
        if not self.template_dir.exists():
            os.makedirs(self.template_dir, exist_ok=True)
            print(f"✅ Template-Verzeichnis erstellt: {self.template_dir}")
            return ""

        combined_css = ""
        css_files = sorted(self.template_dir.glob("*.css"))

        for css_file in css_files:
            template_name = css_file.stem
            css_content = self.load_template_css(template_name)
            if css_content:
                combined_css += f"\n/* === {
                    template_name.upper()} === */\n{css_content}\n"

        return combined_css

    def inject_css(self, css_content: str) -> None:
        """Injiziert CSS in Streamlit mit höchster Priorität"""
        if css_content:
            import time
            timestamp = int(time.time())

            # Methode 1: Direkt als <style> Tag (normale Priorität)
            st.markdown(
                f'<style id="custom-css-{timestamp}">\n{css_content}\n</style>',
                unsafe_allow_html=True)

            # Methode 2: Über JavaScript in <head> einfügen (höchste Priorität)
            # Dies überschreibt ALLE anderen Styles
            css_escaped = css_content.replace('`', '\\`').replace('${', '\\${')
            js_injector = f"""
            <script>
            (function() {{
                // Entferne alte Versionen
                const oldStyles = document.querySelectorAll('style[id^="modern-ui-styles"]');
                oldStyles.forEach(el => el.remove());

                // Erstelle neuen <style> Tag
                const style = document.createElement('style');
                style.id = 'modern-ui-styles-{timestamp}';
                style.textContent = `{css_escaped}`;

                // Füge in <head> ein (höchste Priorität)
                document.head.appendChild(style);

                console.log('✅ Modernes UI CSS injiziert: {timestamp}');
            }})();
            </script>
            """

            st.components.v1.html(js_injector, height=0)
            print(
                f"✅ CSS injiziert: {
                    len(css_content)} Zeichen (via JS + Markdown)")

    def inject_intro_overlay(
            self,
            app_name: str = "Ihre App",
            duration_ms: int = 1200) -> None:
        """
        Injiziert Intro Overlay (wird nur einmal pro Browser angezeigt)

        Args:
            app_name: Name der App für das Intro
            duration_ms: Dauer des Intros in Millisekunden
        """
        if not self.intro_enabled:
            return

        intro_html = f"""
        <div id="intro-overlay">
          <div class="logo-glow">{app_name} lädt …</div>
          <div class="intro-bar"><span></span></div>
        </div>
        <script>
          const seen = localStorage.getItem('intro_seen');
          const ov = document.getElementById('intro-overlay');
          if(seen==='1'){{ ov.classList.add('hidden'); }}
          setTimeout(()=>{{
            ov.classList.add('hidden');
            localStorage.setItem('intro_seen','1');
          }}, {duration_ms});
        </script>
        """
        st.components.v1.html(intro_html, height=0)

    def inject_context_menu(self, menu_items: list | None = None) -> None:
        """
        Injiziert Custom Context Menu (Rechtsklick-Menü)

        Args:
            menu_items: Liste von Menü-Items (icon, label, action)
                        Wenn None, werden Standard-Items verwendet
        """
        if not self.context_menu_enabled:
            return

        # Standard-Menü
        if menu_items is None:
            menu_html = """
            <div id="cxmenu">
              <div class="item" onclick="window.scrollTo({top:0,behavior:'smooth'})">⬆️ Zum Anfang</div>
              <div class="item" onclick="navigator.clipboard.writeText(window.getSelection().toString());">📋 Auswahl kopieren</div>
              <div class="item" onclick="location.reload()">🔄 Neu laden</div>
            </div>
            """
        else:
            # Custom Menü
            items_html = "\n".join(
                [
                    f'<div class="item" onclick="{
                        item.get(
                            "action",
                            "")}">{
                        item.get(
                            "icon",
                            "")} {
                        item.get(
                            "label",
                            "")}</div>' for item in menu_items])
            menu_html = f'<div id="cxmenu">{items_html}</div>'

        menu_script = """
        <script>
          const menu = document.getElementById('cxmenu');
          if (menu) {
            document.addEventListener('contextmenu', (e)=>{
              e.preventDefault();
              menu.style.left = e.pageX + 'px';
              menu.style.top  = e.pageY + 'px';
              menu.style.display = 'block';
            });
            document.addEventListener('click', ()=> menu.style.display='none');
            window.addEventListener('blur', ()=> menu.style.display='none');
          }
        </script>
        """

        st.components.v1.html(menu_html + menu_script, height=0)

    def inject_into_streamlit(self,
                              load_intro: bool = True,
                              load_context_menu: bool = True,
                              app_name: str = "Ihre App") -> int:
        """
        Injiziert alle CSS-Templates und optionale Komponenten in Streamlit

        Args:
            load_intro: Intro Overlay laden
            load_context_menu: Context Menu laden
            app_name: App-Name für Intro

        Returns:
            Anzahl der geladenen Templates
        """
        # 1. CSS-Templates laden
        all_css = self.load_all_templates()

        # 2. CSS injizieren
        if all_css:
            self.inject_css(all_css)

        # 3. Optional: Intro Overlay
        if load_intro:
            self.inject_intro_overlay(app_name=app_name)

        # 4. Optional: Context Menu
        if load_context_menu:
            self.inject_context_menu()

        return len(self.loaded_templates)

    def disable_intro(self) -> None:
        """Deaktiviert Intro Overlay"""
        self.intro_enabled = False

    def disable_context_menu(self) -> None:
        """Deaktiviert Context Menu"""
        self.context_menu_enabled = False

    def get_plotly_theme_config(self) -> dict:
        """
        Gibt Plotly-Theme-Konfiguration zurück, die zum CSS passt

        Returns:
            Dict mit Plotly Layout-Optionen
        """
        return {
            "template": "plotly_dark",
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font": {
                "family": "Nunito, sans-serif",
                "color": "#E6F7FF"},
            "colorway": [
                "#00E5FF",
                "#00BCD4",
                "#38E1B0",
                "#8A7FFF",
                "#50C4FF",
                "#7EE0FF"],
            "margin": {
                "l": 10,
                "r": 10,
                "t": 30,
                "b": 10},
        }

    def apply_plotly_theme(self, fig):
        """
        Wendet das moderne Theme auf ein Plotly Figure an

        Args:
            fig: Plotly Figure Objekt

        Returns:
            Modifiziertes Figure Objekt
        """
        theme = self.get_plotly_theme_config()
        fig.update_layout(**theme)
        return fig


# Globale Instanz für einfache Verwendung
_css_manager = None


def get_css_manager() -> CSSTemplateManager:
    """Gibt die globale CSS-Manager-Instanz zurück"""
    global _css_manager
    if _css_manager is None:
        _css_manager = CSSTemplateManager()
    return _css_manager
