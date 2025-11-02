import React, { useMemo, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

// ---------- Helpers ----------
const num = (v, d=0) => Number.isFinite(+v) ? +v : d
const pairs = (txt) => txt.split(/\n|,/).map(s=>s.trim()).filter(Boolean)
  .map(p => { const [a,b]=p.split(':').map(s=>s.trim()); return {x:+a,y:+b} })
  .filter(p => Number.isFinite(p.x)&&Number.isFinite(p.y))
  .sort((a,b)=>a.x-b.x)

const interp = (tbl, t) => {
  if (!tbl.length) return 2.2
  if (t <= tbl[0].x) return tbl[0].y
  if (t >= tbl[tbl.length-1].x) return tbl[tbl.length-1].y
  for (let i=0;i<tbl.length-1;i++){
    const a=tbl[i], b=tbl[i+1]
    if (t>=a.x && t<=b.x){
      const f = (t-a.x)/(b.x-a.x || 1)
      return a.y + f*(b.y-a.y)
    }
  }
  return tbl[tbl.length-1].y
}

const normBins = (bins) => {
  const s = bins.reduce((k,b)=>k+b.y,0) || 1
  return bins.map(b=>({x:b.x, y:b.y*100/s}))
}

// ---------- Defaults ----------
const D = {
  kwhBase: 97300,
  supplyC: 3.331,
  txC: 1.767,
  dfcNon: 6.062,
  dfcEH:  2.924,
  gasSupply: 0.52,
  gasDist:   0.2134,
  afue: 0.95,
  heatMMBtu: 37.5,
  seasonalCOP: 2.2,
  gross: 10354,
  credits: 2600
}

const DEFAULT_COP = `60:3.77
55:3.56
50:3.39
45:3.24
40:3.12
35:2.75
30:2.62
25:2.50
20:2.37
15:2.24
10:2.11
5:2.00
0:1.87
-5:1.74
-10:1.65`

const DEFAULT_BINS = `60:0
55:2
50:4
45:6
40:8
35:11
30:13
25:14
20:13
15:10
10:8
5:6
0:3
-5:1.5
-10:0.5`

export default function App(){
  const [f, setF] = useState({
    kwhBase: String(D.kwhBase),
    supplyC: String(D.supplyC),
    txC: String(D.txC),
    dfcNon: String(D.dfcNon),
    dfcEH:  String(D.dfcEH),
    gasSupply: String(D.gasSupply),
    gasDist:   String(D.gasDist),
    afue: String(D.afue),
    heatMMBtu: String(D.heatMMBtu),
    seasonalCOP: String(D.seasonalCOP),
    gross: String(D.gross),
    credits: String(D.credits),
  })
  const [useTable, setUseTable] = useState(true)
  const [copText, setCopText] = useState(DEFAULT_COP)
  const [binsText, setBinsText] = useState(DEFAULT_BINS)

  const calc = useMemo(()=>{
    const kwhBase = num(f.kwhBase, D.kwhBase)
    const supplyC = num(f.supplyC, D.supplyC)
    const txC     = num(f.txC, D.txC)
    const dfcNon  = num(f.dfcNon, D.dfcNon)
    const dfcEH   = num(f.dfcEH, D.dfcEH)
    const gasSupply = num(f.gasSupply, D.gasSupply)
    const gasDist   = num(f.gasDist, D.gasDist)
    const afue      = num(f.afue, D.afue)
    const heatMMBtu = num(f.heatMMBtu, D.heatMMBtu)
    const seasonalCOP = num(f.seasonalCOP, D.seasonalCOP)
    const gross = num(f.gross, D.gross)
    const credits = num(f.credits, D.credits)

    const gasAllIn = gasSupply + gasDist
    const allInNon = (supplyC + txC + dfcNon)/100
    const allInEH  = (supplyC + txC + dfcEH)/100

    // Baseline
    const baselineElec = kwhBase * allInNon
    const baselineGas  = (heatMMBtu/0.1/afue) * gasAllIn
    const baseline = baselineElec + baselineGas

    // All-electric
    let hpKWh = 0
    let hybrid = null, hybridGas=0, hybridHPkWh=0

    if (useTable){
      const table = pairs(copText)
      const bins  = normBins(pairs(binsText))
      for (const b of bins){
        const cop = interp(table, b.x)
        const mmbtu = heatMMBtu*(b.y/100)
        hpKWh += (mmbtu*293.071)/cop
      }
      // Hybrid choose cheapest by bin
      const costGasPerMMBtu = (1/0.1/afue)*gasAllIn
      let costHPsum=0, costGASsum=0
      for (const b of bins){
        const cop = interp(table, b.x)
        const mmbtu = heatMMBtu*(b.y/100)
        const kwhPerMMBtu = 293.071 / cop
        const costHPperMMBtu = kwhPerMMBtu * allInEH
        if (costHPperMMBtu <= costGasPerMMBtu){
          costHPsum += mmbtu*costHPperMMBtu
          hybridHPkWh += mmbtu*kwhPerMMBtu
        } else {
          costGASsum += mmbtu*costGasPerMMBtu
          hybridGas += mmbtu
        }
      }
      hybrid = kwhBase*allInEH + costHPsum + costGASsum
    } else {
      hpKWh = (heatMMBtu*293.071)/seasonalCOP
    }

    const allElectric = (kwhBase + hpKWh) * allInEH

    const savingsAll = baseline - allElectric
    const savingsHybrid = hybrid!=null ? baseline - hybrid : null
    const net = gross - credits
    const paybackAll = savingsAll>0 ? net/savingsAll : null
    const paybackHybrid = (savingsHybrid && savingsHybrid>0) ? net/savingsHybrid : null
    const dfcSavings = kwhBase * ((dfcNon - dfcEH)/100)

    const gasHeatCost = (heatMMBtu/0.1/afue)*gasAllIn
    const hpHeatCost  = hpKWh * allInEH
    const fuelSwitch  = gasHeatCost - hpHeatCost

    const chart = [
      { name:'Baseline (Gas+AC)', cost: Math.round(baseline) },
      { name:'All-Electric HP',   cost: Math.round(allElectric) },
      ...(hybrid!=null ? [{ name:'Hybrid (cheapest)', cost: Math.round(hybrid)}] : []),
    ]

    return {
      baseline: Math.round(baseline),
      allElectric: Math.round(allElectric),
      hybrid: hybrid!=null ? Math.round(hybrid) : null,
      savingsAll: Math.round(savingsAll),
      savingsHybrid: savingsHybrid!=null ? Math.round(savingsHybrid) : null,
      paybackAll: paybackAll ? +paybackAll.toFixed(1) : null,
      paybackHybrid: paybackHybrid ? +paybackHybrid.toFixed(1) : null,
      dfcSavings: Math.round(dfcSavings),
      gasHeatCost: Math.round(gasHeatCost),
      hpHeatCost: Math.round(hpHeatCost),
      fuelSwitch: Math.round(fuelSwitch),
      chart
    }
  }, [f, useTable, copText, binsText])

  const set = (k) => (e) => setF(s => ({...s, [k]: e.target.value}))
  const reset = () => setF(Object.fromEntries(Object.entries(D).map(([k,v])=>[k,String(v)])))

  return (
    <div className="container">
      <h1>Heat Pump Break-Even & Payback</h1>
      <p className="note">No login needed. Enter your inputs or use the Chicago defaults and compare Baseline vs All-Electric vs Hybrid (bin-by-bin).</p>

      <div className="grid grid-3" style={{gridTemplateColumns:'repeat(auto-fit, minmax(260px, 1fr))'}}>
        <div className="card">
          <h2>Electricity</h2>
          <label>Annual non-heating kWh</label><input value={f.kwhBase} onChange={set('kwhBase')} />
          <div className="grid grid-3">
            <div><label>Supply (¢/kWh)</label><input value={f.supplyC} onChange={set('supplyC')} /></div>
            <div><label>TX (¢/kWh)</label><input value={f.txC} onChange={set('txC')} /></div>
            <div><label>DFC non-elec (¢/kWh)</label><input value={f.dfcNon} onChange={set('dfcNon')} /></div>
          </div>
          <label>DFC electric-heat (¢/kWh)</label><input value={f.dfcEH} onChange={set('dfcEH')} />
        </div>

        <div className="card">
          <h2>Gas & Heating</h2>
          <div className="grid grid-2">
            <div><label>Gas supply ($/therm)</label><input value={f.gasSupply} onChange={set('gasSupply')} /></div>
            <div><label>Gas delivery ($/therm)</label><input value={f.gasDist} onChange={set('gasDist')} /></div>
          </div>
          <div className="grid grid-2">
            <div><label>AFUE (0–1)</label><input value={f.afue} onChange={set('afue')} /></div>
            <div><label>Heat load (MMBtu/yr)</label><input value={f.heatMMBtu} onChange={set('heatMMBtu')} /></div>
          </div>
          <div className="row" style={{marginTop:8}}>
            <input type="checkbox" id="usetable" checked={useTable} onChange={()=>setUseTable(v=>!v)} />
            <label htmlFor="usetable">Use COP table + hybrid switching</label>
          </div>
          {!useTable && (<><label>Seasonal COP</label><input value={f.seasonalCOP} onChange={set('seasonalCOP')} /></>)}
        </div>

        <div className="card">
          <h2>Project Costs</h2>
          <div className="grid grid-2">
            <div><label>Gross install ($)</label><input value={f.gross} onChange={set('gross')} /></div>
            <div><label>Tax credits ($)</label><input value={f.credits} onChange={set('credits')} /></div>
          </div>
          <div className="row" style={{marginTop:10}}>
            <button className="btn secondary" onClick={reset}>Use Defaults</button>
          </div>
        </div>
      </div>

      {useTable && (
        <div className="grid grid-2" style={{gridTemplateColumns:'repeat(auto-fit, minmax(320px, 1fr))', marginTop:16}}>
          <div className="card">
            <h2>COP Table (°F:COP)</h2>
            <textarea rows="10" value={copText} onChange={e=>setCopText(e.target.value)} />
            <p className="note">One per line or comma-separated. We linearly interpolate.</p>
          </div>
          <div className="card">
            <h2>Weather Bins (°F:% of heating)</h2>
            <textarea rows="10" value={binsText} onChange={e=>setBinsText(e.target.value)} />
            <p className="note">We normalize to 100%. Defaults approximate Chicago.</p>
          </div>
        </div>
      )}

      <div className="grid grid-2" style={{gridTemplateColumns:'repeat(auto-fit, minmax(320px, 1fr))', marginTop:16}}>
        <div className="card">
          <h2>Results</h2>
          <div className="grid grid-2">
            <div className="pill muted"><div className="note">Baseline (Gas+AC)</div><div style={{fontSize:22,fontWeight:700}}>${(calc.baseline).toLocaleString()}</div></div>
            <div className="pill muted"><div className="note">All-Electric HP</div><div style={{fontSize:22,fontWeight:700}}>${(calc.allElectric).toLocaleString()}</div></div>
            {calc.hybrid!==null && <div className="pill muted" style={{gridColumn:'1 / -1'}}><div className="note">Hybrid (cheapest)</div><div style={{fontSize:22,fontWeight:700}}>${(calc.hybrid).toLocaleString()}</div></div>}
          </div>

          <div className="grid grid-2" style={{marginTop:8}}>
            <div className="pill good">
              <div className="note">Annual savings vs Baseline</div>
              <div style={{fontSize:22,fontWeight:700}}>${(calc.savingsAll).toLocaleString()}</div>
            </div>
            <div className="pill muted">
              <div className="note">Simple payback (All-Electric)</div>
              <div style={{fontSize:22,fontWeight:700}}>{calc.paybackAll ? `${calc.paybackAll} yrs` : '—'}</div>
            </div>
          </div>

          <div className="pill muted" style={{marginTop:8}}>
            <div className="note">DFC savings on base kWh (delivery only)</div>
            <div style={{fontSize:20,fontWeight:700}}>${(calc.dfcSavings).toLocaleString()}/yr</div>
          </div>

          <div className="pill muted" style={{marginTop:8}}>
            <div className="note">Heating cost comparison (isolates fuel switch)</div>
            <div>Gas heat: ${calc.gasHeatCost.toLocaleString()} &nbsp; | &nbsp; HP heat: ${calc.hpHeatCost.toLocaleString()} &nbsp; → &nbsp; Fuel-switch savings: <b>${Math.max(0,calc.fuelSwitch).toLocaleString()}</b></div>
          </div>
        </div>

        <div className="card">
          <h2>Cost Comparison</h2>
          <div style={{width:'100%', height:300}}>
            <ResponsiveContainer>
              <BarChart data={calc.chart}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(v)=>`$${Number(v).toLocaleString()}`} />
                <Bar dataKey="cost" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}
