/**
 * Notification Preferences Component
 * 
 * Allows users to configure notification settings including:
 * - Enable/disable notifications
 * - Notification types
 * - Sound settings
 * - Do Not Disturb mode
 * - Quiet hours
 */

import React, { useEffect, useState } from 'react';
import { InputSwitch } from 'primereact/inputswitch';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { Divider } from 'primereact/divider';
import { Calendar } from 'primereact/calendar';
import { Message } from 'primereact/message';
import { useNotifications } from '../../hooks/useNotifications';
import './NotificationPreferences.css';

export const NotificationPreferences: React.FC = () => {
  const {
    isSupported,
    preferences,
    updatePreferences,
    setEnabled,
    setDoNotDisturb,
    setQuietHours,
    test
  } = useNotifications();

  const [localPreferences, setLocalPreferences] = useState(preferences);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<{ severity: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    setLocalPreferences(preferences);
  }, [preferences]);

  if (!isSupported) {
    return (
      <Card title="Benachrichtigungen">
        <Message 
          severity="warn" 
          text="Benachrichtigungen werden in dieser Umgebung nicht unterstützt." 
        />
      </Card>
    );
  }

  if (!localPreferences) {
    return (
      <Card title="Benachrichtigungen">
        <Message severity="info" text="Lade Einstellungen..." />
      </Card>
    );
  }

  const handleToggle = (key: string, value: boolean) => {
    setLocalPreferences({
      ...localPreferences,
      [key]: value
    });
  };

  const handleQuietHoursToggle = (value: boolean) => {
    setLocalPreferences({
      ...localPreferences,
      quietHours: {
        ...localPreferences.quietHours,
        enabled: value
      }
    });
  };

  const handleQuietHoursTime = (field: 'start' | 'end', value: string) => {
    setLocalPreferences({
      ...localPreferences,
      quietHours: {
        ...localPreferences.quietHours,
        [field]: value
      }
    });
  };

  const handleSave = async () => {
    setIsSaving(true);
    setSaveMessage(null);

    try {
      await updatePreferences(localPreferences);
      setSaveMessage({
        severity: 'success',
        text: 'Einstellungen erfolgreich gespeichert'
      });
    } catch (error) {
      setSaveMessage({
        severity: 'error',
        text: 'Fehler beim Speichern der Einstellungen'
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleTest = async () => {
    await test();
  };

  const handleQuickToggle = async (action: 'enable' | 'disable' | 'dnd') => {
    setIsSaving(true);
    try {
      if (action === 'enable') {
        await setEnabled(true);
      } else if (action === 'disable') {
        await setEnabled(false);
      } else if (action === 'dnd') {
        await setDoNotDisturb(!localPreferences.doNotDisturb);
      }
      setSaveMessage({
        severity: 'success',
        text: 'Einstellung aktualisiert'
      });
    } catch (error) {
      setSaveMessage({
        severity: 'error',
        text: 'Fehler beim Aktualisieren'
      });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="notification-preferences">
      <Card title="Benachrichtigungseinstellungen">
        {saveMessage && (
          <Message 
            severity={saveMessage.severity} 
            text={saveMessage.text} 
            className="mb-3"
          />
        )}

        {/* Quick Actions */}
        <div className="quick-actions mb-4">
          <h3>Schnellaktionen</h3>
          <div className="button-group">
            <Button
              label="Alle aktivieren"
              icon="pi pi-check"
              onClick={() => handleQuickToggle('enable')}
              disabled={isSaving}
              className="p-button-success"
            />
            <Button
              label="Alle deaktivieren"
              icon="pi pi-times"
              onClick={() => handleQuickToggle('disable')}
              disabled={isSaving}
              className="p-button-danger"
            />
            <Button
              label={localPreferences.doNotDisturb ? 'Nicht stören AUS' : 'Nicht stören EIN'}
              icon="pi pi-moon"
              onClick={() => handleQuickToggle('dnd')}
              disabled={isSaving}
              className={localPreferences.doNotDisturb ? 'p-button-warning' : 'p-button-secondary'}
            />
            <Button
              label="Test-Benachrichtigung"
              icon="pi pi-bell"
              onClick={handleTest}
              disabled={isSaving}
              className="p-button-info"
            />
          </div>
        </div>

        <Divider />

        {/* General Settings */}
        <div className="setting-section">
          <h3>Allgemeine Einstellungen</h3>
          
          <div className="setting-item">
            <label htmlFor="enabled">Benachrichtigungen aktiviert</label>
            <InputSwitch
              id="enabled"
              checked={localPreferences.enabled}
              onChange={(e) => handleToggle('enabled', e.value)}
            />
          </div>

          <div className="setting-item">
            <label htmlFor="sound">Ton abspielen</label>
            <InputSwitch
              id="sound"
              checked={localPreferences.sound}
              onChange={(e) => handleToggle('sound', e.value)}
              disabled={!localPreferences.enabled}
            />
          </div>

          <div className="setting-item">
            <label htmlFor="doNotDisturb">Nicht stören</label>
            <InputSwitch
              id="doNotDisturb"
              checked={localPreferences.doNotDisturb}
              onChange={(e) => handleToggle('doNotDisturb', e.value)}
              disabled={!localPreferences.enabled}
            />
          </div>
        </div>

        <Divider />

        {/* Notification Types */}
        <div className="setting-section">
          <h3>Benachrichtigungstypen</h3>
          
          <div className="setting-item">
            <label htmlFor="calculationComplete">Berechnung abgeschlossen</label>
            <InputSwitch
              id="calculationComplete"
              checked={localPreferences.calculationComplete}
              onChange={(e) => handleToggle('calculationComplete', e.value)}
              disabled={!localPreferences.enabled}
            />
          </div>

          <div className="setting-item">
            <label htmlFor="updateAvailable">Update verfügbar</label>
            <InputSwitch
              id="updateAvailable"
              checked={localPreferences.updateAvailable}
              onChange={(e) => handleToggle('updateAvailable', e.value)}
              disabled={!localPreferences.enabled}
            />
          </div>

          <div className="setting-item">
            <label htmlFor="errors">Fehler</label>
            <InputSwitch
              id="errors"
              checked={localPreferences.errors}
              onChange={(e) => handleToggle('errors', e.value)}
              disabled={!localPreferences.enabled}
            />
          </div>

          <div className="setting-item">
            <label htmlFor="warnings">Warnungen</label>
            <InputSwitch
              id="warnings"
              checked={localPreferences.warnings}
              onChange={(e) => handleToggle('warnings', e.value)}
              disabled={!localPreferences.enabled}
            />
          </div>

          <div className="setting-item">
            <label htmlFor="info">Informationen</label>
            <InputSwitch
              id="info"
              checked={localPreferences.info}
              onChange={(e) => handleToggle('info', e.value)}
              disabled={!localPreferences.enabled}
            />
          </div>
        </div>

        <Divider />

        {/* Quiet Hours */}
        <div className="setting-section">
          <h3>Ruhezeiten</h3>
          
          <div className="setting-item">
            <label htmlFor="quietHoursEnabled">Ruhezeiten aktivieren</label>
            <InputSwitch
              id="quietHoursEnabled"
              checked={localPreferences.quietHours.enabled}
              onChange={(e) => handleQuietHoursToggle(e.value)}
              disabled={!localPreferences.enabled}
            />
          </div>

          {localPreferences.quietHours.enabled && (
            <div className="quiet-hours-config">
              <div className="time-input">
                <label htmlFor="quietStart">Von</label>
                <input
                  type="time"
                  id="quietStart"
                  value={localPreferences.quietHours.start}
                  onChange={(e) => handleQuietHoursTime('start', e.target.value)}
                  disabled={!localPreferences.enabled}
                />
              </div>

              <div className="time-input">
                <label htmlFor="quietEnd">Bis</label>
                <input
                  type="time"
                  id="quietEnd"
                  value={localPreferences.quietHours.end}
                  onChange={(e) => handleQuietHoursTime('end', e.target.value)}
                  disabled={!localPreferences.enabled}
                />
              </div>

              <p className="quiet-hours-info">
                Während der Ruhezeiten werden keine Benachrichtigungen angezeigt.
              </p>
            </div>
          )}
        </div>

        <Divider />

        {/* Save Button */}
        <div className="save-section">
          <Button
            label="Einstellungen speichern"
            icon="pi pi-save"
            onClick={handleSave}
            disabled={isSaving}
            loading={isSaving}
            className="p-button-primary"
          />
        </div>
      </Card>
    </div>
  );
};
