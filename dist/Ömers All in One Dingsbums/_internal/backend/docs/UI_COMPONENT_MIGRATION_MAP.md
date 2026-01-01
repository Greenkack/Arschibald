# UI Component Migration Map

## Task 238: Complete UI Component Migration

This document maps all Streamlit components to their React/PrimeReact equivalents.

## Component Mapping

### Input Components

| Streamlit | React/PrimeReact | Notes |
|-----------|------------------|-------|
| `st.text_input()` | `<InputText />` | PrimeReact InputText |
| `st.number_input()` | `<GermanNumberInput />` | Custom component with German formatting |
| `st.text_area()` | `<InputTextarea />` | PrimeReact InputTextarea |
| `st.selectbox()` | `<Dropdown />` | PrimeReact Dropdown |
| `st.multiselect()` | `<MultiSelect />` | PrimeReact MultiSelect |
| `st.slider()` | `<GermanSlider />` | Custom slider with German number display |
| `st.checkbox()` | `<Checkbox />` | PrimeReact Checkbox |
| `st.radio()` | `<RadioButton />` | PrimeReact RadioButton |
| `st.date_input()` | `<Calendar />` | PrimeReact Calendar |
| `st.time_input()` | `<Calendar timeOnly />` | PrimeReact Calendar with timeOnly |
| `st.color_picker()` | `<ColorPicker />` | PrimeReact ColorPicker |
| `st.file_uploader()` | Native File Dialog | Electron native dialog |

### Display Components

| Streamlit | React/PrimeReact | Notes |
|-----------|------------------|-------|
| `st.dataframe()` | `<DataTable />` | PrimeReact DataTable |
| `st.table()` | `<DataTable />` | PrimeReact DataTable (simple mode) |
| `st.metric()` | `<MetricCard />` | Custom metric card component |
| `st.json()` | `<pre><code>` | Syntax highlighted JSON |
| `st.code()` | `<pre><code>` | Syntax highlighted code |
| `st.markdown()` | `<ReactMarkdown />` | react-markdown library |
| `st.latex()` | `<MathJax />` | MathJax for LaTeX |
| `st.image()` | `<Image />` | PrimeReact Image |
| `st.audio()` | `<audio>` | HTML5 audio element |
| `st.video()` | `<video>` | HTML5 video element |

### Chart Components

| Streamlit | React/Recharts | Notes |
|-----------|----------------|-------|
| `st.plotly_chart()` | `<ResponsiveContainer>` | Recharts components |
| `st.line_chart()` | `<LineChart />` | Recharts LineChart |
| `st.bar_chart()` | `<BarChart />` | Recharts BarChart |
| `st.area_chart()` | `<AreaChart />` | Recharts AreaChart |
| `st.scatter_chart()` | `<ScatterChart />` | Recharts ScatterChart |
| `st.map()` | `<MapContainer />` | Leaflet or Google Maps |

### Layout Components

| Streamlit | React/PrimeReact | Notes |
|-----------|------------------|-------|
| `st.columns()` | CSS Grid / Flexbox | Custom layout |
| `st.tabs()` | `<TabView />` | PrimeReact TabView |
| `st.expander()` | `<Accordion />` | PrimeReact Accordion |
| `st.container()` | `<div>` | Standard div container |
| `st.sidebar` | `<Sidebar />` | PrimeReact Sidebar |
| `st.empty()` | Conditional rendering | React conditional |
| `st.form()` | `<form>` | HTML form with React Hook Form |

### Feedback Components

| Streamlit | React/PrimeReact | Notes |
|-----------|------------------|-------|
| `st.success()` | `<Message severity="success" />` | PrimeReact Message |
| `st.error()` | `<Message severity="error" />` | PrimeReact Message |
| `st.warning()` | `<Message severity="warn" />` | PrimeReact Message |
| `st.info()` | `<Message severity="info" />` | PrimeReact Message |
| `st.spinner()` | `<ProgressSpinner />` | PrimeReact ProgressSpinner |
| `st.progress()` | `<ProgressBar />` | PrimeReact ProgressBar |
| `st.toast()` | Toast service | PrimeReact Toast |
| `st.balloons()` | Custom animation | CSS animation |

### Action Components

| Streamlit | React/PrimeReact | Notes |
|-----------|------------------|-------|
| `st.button()` | `<Button />` | PrimeReact Button |
| `st.download_button()` | `<Button />` + download | Button with download handler |
| `st.link_button()` | `<Button />` + link | Button with navigation |
| `st.form_submit_button()` | `<Button type="submit" />` | Form submit button |

### Dialog Components

| Streamlit | React/PrimeReact | Notes |
|-----------|------------------|-------|
| `st.dialog()` | `<Dialog />` | PrimeReact Dialog |
| `st.popover()` | `<OverlayPanel />` | PrimeReact OverlayPanel |
| Modal dialogs | `<Dialog modal />` | PrimeReact modal Dialog |
| Confirmation | `<ConfirmDialog />` | PrimeReact ConfirmDialog |

## Custom Components

### GermanNumberInput

```tsx
import { InputNumber } from 'primereact/inputnumber';

interface GermanNumberInputProps {
  value: number;
  onChange: (value: number) => void;
  suffix?: string;
  minFractionDigits?: number;
  maxFractionDigits?: number;
}

export const GermanNumberInput: React.FC<GermanNumberInputProps> = ({
  value,
  onChange,
  suffix,
  minFractionDigits = 2,
  maxFractionDigits = 2
}) => {
  return (
    <InputNumber
      value={value}
      onValueChange={(e) => onChange(e.value || 0)}
      locale="de-DE"
      suffix={suffix}
      minFractionDigits={minFractionDigits}
      maxFractionDigits={maxFractionDigits}
    />
  );
};
```

### GermanSlider

```tsx
import { Slider } from 'primereact/slider';
import { formatGermanNumber } from '../utils/germanFormatter';

interface GermanSliderProps {
  value: number;
  onChange: (value: number) => void;
  min: number;
  max: number;
  step?: number;
  suffix?: string;
}

export const GermanSlider: React.FC<GermanSliderProps> = ({
  value,
  onChange,
  min,
  max,
  step = 1,
  suffix = ''
}) => {
  return (
    <div className="german-slider">
      <Slider
        value={value}
        onChange={(e) => onChange(e.value as number)}
        min={min}
        max={max}
        step={step}
      />
      <span className="slider-value">
        {formatGermanNumber(value)}{suffix}
      </span>
    </div>
  );
};
```

### MetricCard

```tsx
interface MetricCardProps {
  label: string;
  value: number | string;
  delta?: number;
  deltaColor?: 'green' | 'red' | 'gray';
  suffix?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  delta,
  deltaColor = 'gray',
  suffix = ''
}) => {
  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value">
        {typeof value === 'number' ? formatGermanNumber(value) : value}
        {suffix}
      </div>
      {delta !== undefined && (
        <div className={`metric-delta ${deltaColor}`}>
          {delta > 0 ? '+' : ''}{formatGermanNumber(delta)}
        </div>
      )}
    </div>
  );
};
```

## Session State Migration

### Streamlit Session State → Zustand Store

| st.session_state | Zustand Store | Notes |
|------------------|---------------|-------|
| `st.session_state.user` | `useAuthStore().user` | Auth store |
| `st.session_state.project` | `useProjectStore().currentProject` | Project store |
| `st.session_state.calculation_results` | `useCalculationStore().results` | Calculation store |
| `st.session_state.selected_products` | `useProductStore().selected` | Product store |
| `st.session_state.pdf_options` | `usePDFStore().options` | PDF store |
| `st.session_state.theme` | `useUIStore().theme` | UI store |

## Migration Checklist

### Phase 1: Core Components ✅
- [x] InputText
- [x] InputNumber (GermanNumberInput)
- [x] Dropdown
- [x] Button
- [x] DataTable

### Phase 2: Layout Components ✅
- [x] Sidebar
- [x] TabView
- [x] Accordion
- [x] Dialog

### Phase 3: Chart Components ✅
- [x] LineChart
- [x] BarChart
- [x] PieChart
- [x] AreaChart

### Phase 4: Form Components ✅
- [x] Form validation (React Hook Form + Zod)
- [x] File upload (native dialogs)
- [x] Date/Time pickers

### Phase 5: Feedback Components ✅
- [x] Toast notifications
- [x] Progress indicators
- [x] Messages/Alerts

## Requirements Coverage

- **7.1**: All Streamlit components migrated ✅
- **7.2**: Price matrix components ✅
- **7.3**: PDF generation components ✅
- **7.4**: Chart components ✅
- **7.5**: Form components ✅
- **7.6**: File handling components ✅
