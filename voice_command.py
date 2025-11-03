"""
Voice Command Module for Agent
================================

Provides Speech-to-Text functionality for Agent control.
Uses browser's built-in speech recognition when available.
"""

import streamlit as st
import streamlit.components.v1 as components


def render_voice_input_ui():
    """
    Renders browser-based voice input interface
    """
    voice_component = components.html("""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .voice-container {
                text-align: center;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 15px;
                color: white;
            }
            .voice-btn {
                width: 100px;
                height: 100px;
                border-radius: 50%;
                background: rgba(255,255,255,0.2);
                border: 3px solid white;
                font-size: 40px;
                cursor: pointer;
                transition: all 0.3s;
            }
            .voice-btn:hover {
                transform: scale(1.1);
                background: rgba(255,255,255,0.3);
            }
            .voice-btn.listening {
                animation: pulse 1.5s infinite;
                background: rgba(255,255,255,0.4);
            }
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
            .voice-status {
                margin-top: 20px;
                font-size: 18px;
                font-weight: bold;
            }
            .voice-transcript {
                margin-top: 15px;
                padding: 15px;
                background: rgba(0,0,0,0.3);
                border-radius: 10px;
                min-height: 60px;
                font-size: 16px;
            }
        </style>
    </head>
    <body>
        <div class="voice-container">
            <button id="voiceBtn" class="voice-btn" onclick="toggleVoice()">🎤</button>
            <div class="voice-status" id="status">Klicken Sie auf das Mikrofon</div>
            <div class="voice-transcript" id="transcript">...</div>
        </div>
        
        <script>
            let recognition;
            let isListening = false;
            
            function initSpeechRecognition() {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                
                if (!SpeechRecognition) {
                    document.getElementById('status').textContent = 'Spracherkennung nicht verfügbar';
                    return null;
                }
                
                recognition = new SpeechRecognition();
                recognition.lang = 'de-DE';
                recognition.continuous = false;
                recognition.interimResults = true;
                
                recognition.onstart = function() {
                    document.getElementById('voiceBtn').classList.add('listening');
                    document.getElementById('status').textContent = 'Höre zu...';
                };
                
                recognition.onresult = function(event) {
                    const transcript = Array.from(event.results)
                        .map(result => result[0].transcript)
                        .join('');
                    
                    document.getElementById('transcript').textContent = transcript;
                    
                    if (event.results[0].isFinal) {
                        // Send to Streamlit
                        if (window.Streamlit) {
                            window.Streamlit.setComponentValue({
                                action: 'voice_input',
                                text: transcript
                            });
                        }
                    }
                };
                
                recognition.onerror = function(event) {
                    console.error('Speech recognition error:', event.error);
                    document.getElementById('status').textContent = 'Fehler: ' + event.error;
                    isListening = false;
                    document.getElementById('voiceBtn').classList.remove('listening');
                };
                
                recognition.onend = function() {
                    isListening = false;
                    document.getElementById('voiceBtn').classList.remove('listening');
                    document.getElementById('status').textContent = 'Aufnahme beendet';
                };
                
                return recognition;
            }
            
            function toggleVoice() {
                if (!recognition) {
                    recognition = initSpeechRecognition();
                    if (!recognition) return;
                }
                
                if (isListening) {
                    recognition.stop();
                } else {
                    isListening = true;
                    recognition.start();
                }
            }
            
            // Initialize on load
            window.onload = function() {
                if (!initSpeechRecognition()) {
                    document.getElementById('voiceBtn').disabled = true;
                    document.getElementById('voiceBtn').style.opacity = '0.5';
                }
            };
        </script>
    </body>
    </html>
    """, height=300)
    
    return voice_component


def integrate_voice_with_agent(voice_result):
    """
    Integrates voice input result with agent
    """
    if voice_result and isinstance(voice_result, dict):
        if voice_result.get('action') == 'voice_input':
            text = voice_result.get('text', '')
            if text:
                # Store in session for agent to use
                st.session_state['agent_voice_input'] = text
                return text
    return None
