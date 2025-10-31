import React, { FC, useContext, useEffect } from 'react';
import { Slider } from 'primereact/slider';
import { InputNumber } from 'primereact/inputnumber';
import { AppContext } from './AppContext';

/**
 * Sidebar‑Komponente für die Live‑Preisberechnung.
 *
 * Diese Komponente stellt zwei Eingabefelder (Rabatt und Aufschlag) bereit und
 * berechnet den finalen Preis basierend auf dem Basispreis aus dem Kontext.
 */
export const LivePricingSidebar: FC = () => {
  const { state, dispatch } = useContext(AppContext);
  const { pricing } = state;

  // Aktualisiere finalen Preis bei Änderungen
  useEffect(() => {
    const finalPrice =
      pricing.baseCost *
      (1 - (pricing.discountPercent || 0) / 100) *
      (1 + (pricing.surchargePercent || 0) / 100);
    dispatch({ type: 'UPDATE_PRICING', payload: { finalPrice } });
  }, [pricing.baseCost, pricing.discountPercent, pricing.surchargePercent, dispatch]);

  return (
    <aside className="p-p-3 p-mb-3" style={{ width: '100%' }}>
      <h3>Preisberechnung</h3>
      <div className="p-field p-mb-3">
        <label htmlFor="discount">Rabatt (%)</label>
        <InputNumber
          id="discount"
          value={pricing.discountPercent}
          min={0}
          max={50}
          onValueChange={(e) =>
            dispatch({ type: 'UPDATE_PRICING', payload: { discountPercent: e.value || 0 } })
          }
          mode="decimal"
          suffix="%"
          showButtons
        />
      </div>
      <div className="p-field p-mb-3">
        <label htmlFor="surcharge">Aufschlag (%)</label>
        <InputNumber
          id="surcharge"
          value={pricing.surchargePercent}
          min={0}
          max={50}
          onValueChange={(e) =>
            dispatch({ type: 'UPDATE_PRICING', payload: { surchargePercent: e.value || 0 } })
          }
          mode="decimal"
          suffix="%"
          showButtons
        />
      </div>
      <div className="p-field">
        <strong>Basispreis:</strong> {pricing.baseCost.toFixed(2)} €
      </div>
      <div className="p-field">
        <strong>Endpreis:</strong> {pricing.finalPrice.toFixed(2)} €
      </div>
    </aside>
  );
};