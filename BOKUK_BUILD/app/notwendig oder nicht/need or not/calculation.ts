/*
 * CalculationHandler
 *
 * Dieser Handler stellt die Brücke zwischen dem Electron‑Main‑Prozess
 * und der Python‑Berechnung zur Verfügung. Er registriert einen
 * IPC‑Handler unter dem Kanal 'perform-calculations', der das
 * Projekt‑Konfigurationsobjekt vom Renderer entgegennimmt, die Python
 * Berechnungs‑CLI (`calculations_cli.py`) als Child‑Process startet und
 * das Ergebnis als aufgelöstes Promise zurückliefert.
 */

import { ipcMain } from 'electron';
import { spawn } from 'child_process';
import * as path from 'path';

export class CalculationHandler {
  constructor() {
    // Registriere den IPC‑Handler. Der Channel‑Name sollte mit dem
    // Aufruf aus dem Renderer übereinstimmen (z. B. window.electronAPI.performCalculations).
    ipcMain.handle('perform-calculations', async (_event, projectData: any) => {
      return await this.performCalculations(projectData);
    });
  }

  /**
   * Startet einen Python‑Subprozess und ruft die perform_calculations‑Funktion auf.
   *
   * @param projectData Die Anlagen‑ und Kundendaten aus dem Frontend
   * @returns Ein Promise, das sich mit dem Ergebnis‑JSON auflöst
   */
  async performCalculations(projectData: any): Promise<any> {
    return new Promise((resolve, reject) => {
      // Pfad zur CLI: relativ zum aktuellen Modul. Passe den Pfad
      // ggf. an deine Projektstruktur an (z. B. '../python/calculations_cli.py').
      const scriptPath = path.join(__dirname, '../python/calculations_cli.py');

      const python = spawn('python3', [scriptPath]);

      // Erzeuge Eingabe‑Payload für die CLI
      const payload = JSON.stringify({
        project_data: projectData,
        texts: {},
        errors_list: [],
        simulation_duration_user: null,
        electricity_price_increase_user: null,
      });

      // Schreibe Payload in stdin und schließe den Stream
      python.stdin.write(payload);
      python.stdin.end();

      let stdout = '';
      let stderr = '';

      python.stdout.on('data', (chunk) => {
        stdout += chunk.toString();
      });
      python.stderr.on('data', (chunk) => {
        stderr += chunk.toString();
      });
      python.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(stderr || `Python process exited with code ${code}`));
        } else {
          try {
            const result = JSON.parse(stdout);
            resolve(result);
          } catch (err) {
            reject(err);
          }
        }
      });
    });
  }

  /**
   * Platzhalter für Live‑Vorschau. Implementiere analog zu performCalculations,
   * indem du eine entsprechende Python‑Funktion aufrufst.
   */
  async getLivePreview(config: any): Promise<any> {
    // Beispiel: passe hier den Funktionsaufruf und das Payload an.
    return Promise.resolve({});
  }
}