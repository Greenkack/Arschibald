import React, { useState, useEffect, useCallback, useRef } from 'react';

// PrimeReact Core Components
import { Steps } from 'primereact/steps';
import { Card } from 'primereact/card';
import { Panel } from 'primereact/panel';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { InputNumber } from 'primereact/inputnumber';
import { Dropdown } from 'primereact/dropdown';
import { Checkbox } from 'primereact/checkbox';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Tag } from 'primereact/tag';
import { Message } from 'primereact/message';
import { Tooltip } from 'primereact/tooltip';
import { Divider } from 'primereact/divider';
import { ProgressBar } from 'primereact/progressbar';
import { Fieldset } from 'primereact/fieldset';
import { InputTextarea } from 'primereact/inputtextarea';
import { RadioButton } from 'primereact/radiobutton';
import { Slider } from 'primereact/slider';
import { SelectButton } from 'primereact/selectbutton';
import { MultiSelect } from 'primereact/multiselect';
import { AutoComplete } from 'primereact/autocomplete';
import { Calendar } from 'primereact/calendar';
import { FileUpload } from 'primereact/fileupload';
import { TabView, TabPanel } from 'primereact/tabview';
import { Accordion, AccordionTab } from 'primereact/accordion';
import { Toast } from 'primereact/toast';
import { Dialog } from 'primereact/dialog';
import { ConfirmDialog } from 'primereact/confirmdialog';
import { Sidebar } from 'primereact/sidebar';
import { ScrollPanel } from 'primereact/scrollpanel';
import { Chip } from 'primereact/chip';
import { Avatar } from 'primereact/avatar';
import { Badge } from 'primereact/badge';
import { BlockUI } from 'primereact/blockui';
import { Skeleton } from 'primereact/skeleton';
import { ProgressSpinner } from 'primereact/progressspinner';
import { Messages } from 'primereact/messages';
import { Galleria } from 'primereact/galleria';
import { Image } from 'primereact/image';
import { Carousel } from 'primereact/carousel';
import { Timeline } from 'primereact/timeline';
import { Tree } from 'primereact/tree';
import { Menu } from 'primereact/menu';
import { Menubar } from 'primereact/menubar';
import { ContextMenu } from 'primereact/contextmenu';
import { MegaMenu } from 'primereact/megamenu';
import { PanelMenu } from 'primereact/panelmenu';
import { TieredMenu } from 'primereact/tieredmenu';
import { BreadCrumb } from 'primereact/breadcrumb';
import { Paginator } from 'primereact/paginator';
import { DataView } from 'primereact/dataview';
import { VirtualScroller } from 'primereact/virtualscroller';
import { PickList } from 'primereact/picklist';
import { OrderList } from 'primereact/orderlist';
import { OrganizationChart } from 'primereact/organizationchart';
import { TreeTable } from 'primereact/treetable';
import { ToggleButton } from 'primereact/togglebutton';
import { SplitButton } from 'primereact/splitbutton';
import { SpeedDial } from 'primereact/speeddial';
import { Knob } from 'primereact/knob';
import { Rating } from 'primereact/rating';
import { ColorPicker } from 'primereact/colorpicker';
import { CascadeSelect } from 'primereact/cascadeselect';
import { TriStateCheckbox } from 'primereact/tristatecheckbox';
import { ListBox } from 'primereact/listbox';
import { InputMask } from 'primereact/inputmask';
import { InputSwitch } from 'primereact/inputswitch';

// PrimeReact CSS
import 'primereact/resources/themes/saga-blue/theme.css';
import 'primereact/resources/primereact.min.css';
import 'primeicons/primeicons.css';

// Component CSS
import './ModernSolarCalculator.css';

// Types from existing system
import { Project, Customer } from '../packages/core/src/types/db';

// Product interfaces matching Python logic
interface Product {
  id?: number;
  category: string;
  model_name: string;
  brand: string;
  price_euro: number;
  capacity_w?: number;
  storage_power_kw?: number;
  power_kw?: number;
  max_cycles?: number;
  warranty_years?: number;
  length_m?: number;
  width_m?: number;
  weight_kg?: number;
  efficiency_percent?: number;
  origin_country?: string;
  description?: string;
  pros?: string;
  cons?: string;
  rating?: number;
  image_base64?: string;
  additional_cost_netto?: number;
}

interface CalculationResults {
  anlage_kwp: number;
  total_inverter_power_kw: number;
  base_matrix_price_netto: number;
  total_investment_netto: number;
  total_investment_brutto: number;
  annual_pv_production_kwh: number;
  einspeiseverguetung_total_euro: number;
  final_price?: number;
}

interface ProjectDetails {
  module_quantity: number;
  selected_module_brand?: string;
  selected_module_name?: string;
  selected_module_id?: number;
  selected_module_capacity_w: number;
  anlage_kwp: number;
  selected_inverter_brand?: string;
  selected_inverter_name?: string;
  selected_inverter_id?: number;
  selected_inverter_quantity: number;
  selected_inverter_power_kw_single: number;
  selected_inverter_power_kw: number;
  selected_inverter_power_w_total: number;
  selected_inverter_power_w_single: number;
  include_storage: boolean;
  selected_storage_brand?: string;
  selected_storage_name?: string;
  selected_storage_id?: number;
  selected_storage_storage_power_kw: number;
}

interface ModernSolarCalculatorProps {
  project?: Partial<Project>;
  customer: Customer;
  mode: 'add' | 'edit';
  onSave: (project: Omit<Project, 'id'>) => void;
  onCancel: () => void;
  texts?: Record<string, string>;
}

export const ModernSolarCalculator: React.FC<ModernSolarCalculatorProps> = ({
  project,
  customer,
  mode,
  onSave,
  onCancel,
  texts = {}
}) => {
  // Multi-step wizard state
  const [activeStep, setActiveStep] = useState<number>(0);
  const toast = useRef<Toast>(null);
  
  // Product data state
  const [moduleProducts, setModuleProducts] = useState<Product[]>([]);
  const [inverterProducts, setInverterProducts] = useState<Product[]>([]);
  const [storageProducts, setStorageProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  
  // Project details state (matching Python logic exactly)
  const [projectDetails, setProjectDetails] = useState<ProjectDetails>({
    module_quantity: project?.module_quantity || 20,
    selected_module_brand: undefined,
    selected_module_name: undefined,
    selected_module_id: project?.selected_module_id || undefined,
    selected_module_capacity_w: 0,
    anlage_kwp: 0,
    selected_inverter_brand: undefined,
    selected_inverter_name: undefined,
    selected_inverter_id: project?.selected_inverter_id || undefined,
    selected_inverter_quantity: 1,
    selected_inverter_power_kw_single: 0,
    selected_inverter_power_kw: 0,
    selected_inverter_power_w_total: 0,
    selected_inverter_power_w_single: 0,
    include_storage: Boolean(project?.include_storage || false),
    selected_storage_brand: undefined,
    selected_storage_name: undefined,
    selected_storage_id: project?.selected_storage_id || undefined,
    selected_storage_storage_power_kw: project?.selected_storage_storage_power_kw || 5.0
  });

  // Calculation results
  const [calculationResults, setCalculationResults] = useState<CalculationResults>({
    anlage_kwp: 0,
    total_inverter_power_kw: 0,
    base_matrix_price_netto: 0,
    total_investment_netto: 0,
    total_investment_brutto: 0,
    annual_pv_production_kwh: 0,
    einspeiseverguetung_total_euro: 0
  });

  // Form data state
  const [formData, setFormData] = useState<Omit<Project, 'id'>>({
    customer_id: customer.id!,
    project_name: project?.project_name || '',
    project_status: project?.project_status || 'Neu',
    roof_type: project?.roof_type || '',
    roof_covering_type: project?.roof_covering_type || '',
    free_roof_area_sqm: project?.free_roof_area_sqm || 0,
    roof_orientation: project?.roof_orientation || '',
    roof_inclination_deg: project?.roof_inclination_deg || 0,
    building_height_gt_7m: project?.building_height_gt_7m || 0,
    annual_consumption_kwh: project?.annual_consumption_kwh || 0,
    costs_household_euro_mo: project?.costs_household_euro_mo || 0,
    annual_heating_kwh: project?.annual_heating_kwh || 0,
    costs_heating_euro_mo: project?.costs_heating_euro_mo || 0,
    anlage_type: project?.anlage_type || 'Aufdach',
    feed_in_type: project?.feed_in_type || 'Volleinspeisung',
    module_quantity: projectDetails.module_quantity,
    selected_module_id: projectDetails.selected_module_id,
    selected_inverter_id: projectDetails.selected_inverter_id,
    include_storage: projectDetails.include_storage ? 1 : 0,
    selected_storage_id: projectDetails.selected_storage_id,
    selected_storage_storage_power_kw: projectDetails.selected_storage_storage_power_kw,
    include_additional_components: project?.include_additional_components || 0,
    selected_wallbox_id: project?.selected_wallbox_id || undefined,
    selected_ems_id: project?.selected_ems_id || undefined,
    selected_optimizer_id: project?.selected_optimizer_id || undefined,
    selected_carport_id: project?.selected_carport_id || undefined,
    selected_notstrom_id: project?.selected_notstrom_id || undefined,
    selected_tierabwehr_id: project?.selected_tierabwehr_id || undefined,
    visualize_roof_in_pdf: project?.visualize_roof_in_pdf || 0,

  });

  // Step configuration for wizard
  const steps = [
    { 
      label: 'Anzahl PV Module',
      icon: 'pi pi-th-large',
      command: () => setActiveStep(0)
    },
    { 
      label: 'PV Module & Wechselrichter',
      icon: 'pi pi-bolt',
      command: () => setActiveStep(1)
    },
    { 
      label: 'Speicher & Zusatzkomponenten',
      icon: 'pi pi-battery-2',
      command: () => setActiveStep(2)
    },
    { 
      label: 'Überprüfung & Berechnung',
      icon: 'pi pi-calculator',
      command: () => setActiveStep(3)
    }
  ];

  // Helper functions matching Python logic
  const getTextLocal = useCallback((key: string, fallback: string): string => {
    return texts[key] || fallback;
  }, [texts]);

  const productsByCategory = useCallback((category: string): Product[] => {
    switch (category) {
      case 'Modul': return moduleProducts;
      case 'Wechselrichter': return inverterProducts;
      case 'Batteriespeicher': return storageProducts;
      default: return [];
    }
  }, [moduleProducts, inverterProducts, storageProducts]);

  const brandsFromProducts = useCallback((products: Product[]): string[] => {
    const brands = [...new Set(products.map(p => p.brand).filter(Boolean))];
    return brands.sort();
  }, []);

  const filterModelsByBrand = useCallback((products: Product[], brand?: string): Product[] => {
    if (!brand) return products;
    return products.filter(p => p.brand?.toLowerCase() === brand.toLowerCase());
  }, []);

  const getProductByModelName = useCallback((modelName: string): Product | undefined => {
    const allProducts = [...moduleProducts, ...inverterProducts, ...storageProducts];
    return allProducts.find(p => p.model_name === modelName);
  }, [moduleProducts, inverterProducts, storageProducts]);

  // Calculation functions matching Python logic
  const calculateAnlageKwp = useCallback((): number => {
    return ((projectDetails.module_quantity || 0) * (projectDetails.selected_module_capacity_w || 0)) / 1000.0;
  }, [projectDetails.module_quantity, projectDetails.selected_module_capacity_w]);

  const calculateTotalInverterPower = useCallback((): number => {
    return (projectDetails.selected_inverter_power_kw_single || 0) * (projectDetails.selected_inverter_quantity || 1);
  }, [projectDetails.selected_inverter_power_kw_single, projectDetails.selected_inverter_quantity]);

  const performCalculations = useCallback(() => {
    const anlage_kwp = calculateAnlageKwp();
    const total_inverter_power_kw = calculateTotalInverterPower();
    
    // Simplified calculations - in real app, these would call backend APIs
    const base_matrix_price_netto = anlage_kwp * 1200; // €/kWp base price
    const storage_cost = projectDetails.include_storage ? projectDetails.selected_storage_storage_power_kw * 800 : 0;
    const total_investment_netto = base_matrix_price_netto + storage_cost;
    const total_investment_brutto = total_investment_netto * 1.19; // 19% MwSt
    const annual_pv_production_kwh = anlage_kwp * 950; // kWh/kWp per year (simplified)
    const einspeiseverguetung_total_euro = annual_pv_production_kwh * 0.082; // €/kWh feed-in tariff

    const newResults: CalculationResults = {
      anlage_kwp,
      total_inverter_power_kw,
      base_matrix_price_netto,
      total_investment_netto,
      total_investment_brutto,
      annual_pv_production_kwh,
      einspeiseverguetung_total_euro,
      final_price: total_investment_brutto
    };

    setCalculationResults(newResults);
    
    // Update project details with calculated values
    setProjectDetails(prev => ({
      ...prev,
      anlage_kwp,
      selected_inverter_power_kw: total_inverter_power_kw,
      selected_inverter_power_w_total: total_inverter_power_kw * 1000,
      selected_inverter_power_w_single: projectDetails.selected_inverter_power_kw_single * 1000
    }));

    // Update form data
    setFormData(prev => ({
      ...prev,
      module_quantity: projectDetails.module_quantity,
      selected_module_id: projectDetails.selected_module_id,
      selected_inverter_id: projectDetails.selected_inverter_id,
      include_storage: projectDetails.include_storage ? 1 : 0,
      selected_storage_id: projectDetails.selected_storage_id,
      selected_storage_storage_power_kw: projectDetails.selected_storage_storage_power_kw
    }));
  }, [projectDetails, calculateAnlageKwp, calculateTotalInverterPower]);

  // Update calculations whenever project details change
  useEffect(() => {
    performCalculations();
  }, [performCalculations]);

  // Load products (simplified - in real app would fetch from API)
  useEffect(() => {
    setLoading(true);
    
    // Mock product data
    const mockModules: Product[] = [
      { id: 1, category: 'Modul', model_name: 'JA Solar JAM72S30', brand: 'JA Solar', price_euro: 180, capacity_w: 540, warranty_years: 25, efficiency_percent: 21.2 },
      { id: 2, category: 'Modul', model_name: 'Jinko Tiger Neo 78HL4', brand: 'Jinko Solar', price_euro: 190, capacity_w: 575, warranty_years: 25, efficiency_percent: 22.5 },
      { id: 3, category: 'Modul', model_name: 'LONGi Solar Hi-MO X6', brand: 'LONGi Solar', price_euro: 200, capacity_w: 560, warranty_years: 25, efficiency_percent: 22.8 },
      { id: 4, category: 'Modul', model_name: 'Trina Solar Vertex S', brand: 'Trina Solar', price_euro: 185, capacity_w: 550, warranty_years: 25, efficiency_percent: 21.8 }
    ];

    const mockInverters: Product[] = [
      { id: 5, category: 'Wechselrichter', model_name: 'SMA Sunny Boy 5.0', brand: 'SMA', price_euro: 1200, power_kw: 5.0, warranty_years: 10, efficiency_percent: 97.1 },
      { id: 6, category: 'Wechselrichter', model_name: 'Fronius Symo 8.2-3-M', brand: 'Fronius', price_euro: 1800, power_kw: 8.2, warranty_years: 10, efficiency_percent: 98.1 },
      { id: 7, category: 'Wechselrichter', model_name: 'Huawei SUN2000-10KTL', brand: 'Huawei', price_euro: 1500, power_kw: 10.0, warranty_years: 10, efficiency_percent: 98.6 },
      { id: 8, category: 'Wechselrichter', model_name: 'Kostal PLENTICORE plus 7', brand: 'Kostal', price_euro: 1400, power_kw: 7.0, warranty_years: 10, efficiency_percent: 97.3 }
    ];

    const mockStorage: Product[] = [
      { id: 9, category: 'Batteriespeicher', model_name: 'BYD Battery-Box Premium HVS 10.24', brand: 'BYD', price_euro: 6500, storage_power_kw: 10.24, max_cycles: 6000, warranty_years: 10 },
      { id: 10, category: 'Batteriespeicher', model_name: 'Huawei LUNA2000-15-S0', brand: 'Huawei', price_euro: 8000, storage_power_kw: 15.0, max_cycles: 8000, warranty_years: 10 },
      { id: 11, category: 'Batteriespeicher', model_name: 'Sonnen sonnenBatterie 10', brand: 'Sonnen', price_euro: 9500, storage_power_kw: 11.0, max_cycles: 10000, warranty_years: 15 },
      { id: 12, category: 'Batteriespeicher', model_name: 'Tesla Powerwall 2', brand: 'Tesla', price_euro: 7200, storage_power_kw: 13.5, max_cycles: 5000, warranty_years: 10 }
    ];

    setTimeout(() => {
      setModuleProducts(mockModules);
      setInverterProducts(mockInverters);
      setStorageProducts(mockStorage);
      setLoading(false);
    }, 500);
  }, []);

  // Event handlers
  const handleModuleQuantityChange = (value: number | null) => {
    const newQuantity = Math.max(0, value || 0);
    setProjectDetails(prev => ({
      ...prev,
      module_quantity: newQuantity
    }));
  };

  const handleModuleBrandChange = (brand: string | null) => {
    setProjectDetails(prev => ({
      ...prev,
      selected_module_brand: brand || undefined,
      selected_module_name: undefined,
      selected_module_id: undefined,
      selected_module_capacity_w: 0
    }));
  };

  const handleModuleModelChange = (modelName: string | null) => {
    const product = getProductByModelName(modelName || '');
    setProjectDetails(prev => ({
      ...prev,
      selected_module_name: modelName || undefined,
      selected_module_id: product?.id,
      selected_module_capacity_w: product?.capacity_w || 0
    }));
  };

  const handleInverterBrandChange = (brand: string | null) => {
    setProjectDetails(prev => ({
      ...prev,
      selected_inverter_brand: brand || undefined,
      selected_inverter_name: undefined,
      selected_inverter_id: undefined,
      selected_inverter_power_kw_single: 0
    }));
  };

  const handleInverterModelChange = (modelName: string | null) => {
    const product = getProductByModelName(modelName || '');
    setProjectDetails(prev => ({
      ...prev,
      selected_inverter_name: modelName || undefined,
      selected_inverter_id: product?.id,
      selected_inverter_power_kw_single: product?.power_kw || 0
    }));
  };

  const handleInverterQuantityChange = (value: number | null) => {
    const newQuantity = Math.max(1, value || 1);
    setProjectDetails(prev => ({
      ...prev,
      selected_inverter_quantity: newQuantity
    }));
  };

  const handleStorageToggle = (checked: boolean) => {
    setProjectDetails(prev => ({
      ...prev,
      include_storage: checked,
      selected_storage_brand: checked ? prev.selected_storage_brand : undefined,
      selected_storage_name: checked ? prev.selected_storage_name : undefined,
      selected_storage_id: checked ? prev.selected_storage_id : undefined
    }));
  };

  const handleStorageBrandChange = (brand: string | null) => {
    setProjectDetails(prev => ({
      ...prev,
      selected_storage_brand: brand || undefined,
      selected_storage_name: undefined,
      selected_storage_id: undefined
    }));
  };

  const handleStorageModelChange = (modelName: string | null) => {
    const product = getProductByModelName(modelName || '');
    setProjectDetails(prev => ({
      ...prev,
      selected_storage_name: modelName || undefined,
      selected_storage_id: product?.id,
      selected_storage_storage_power_kw: product?.storage_power_kw || prev.selected_storage_storage_power_kw
    }));
  };

  const handleStorageCapacityChange = (value: number | null) => {
    const newCapacity = Math.max(0, value || 0);
    setProjectDetails(prev => ({
      ...prev,
      selected_storage_storage_power_kw: newCapacity
    }));
  };

  const handleSave = () => {
    // Validate required fields
    if (projectDetails.module_quantity === 0) {
      toast.current?.show({ severity: 'error', summary: 'Fehler', detail: 'Anzahl PV Module muss größer als 0 sein' });
      return;
    }

    if (!projectDetails.selected_module_id) {
      toast.current?.show({ severity: 'error', summary: 'Fehler', detail: 'Bitte wählen Sie ein PV Modul aus' });
      return;
    }

    if (!projectDetails.selected_inverter_id) {
      toast.current?.show({ severity: 'error', summary: 'Fehler', detail: 'Bitte wählen Sie einen Wechselrichter aus' });
      return;
    }

    onSave(formData);
    toast.current?.show({ severity: 'success', summary: 'Erfolgreich', detail: 'Projekt wurde gespeichert' });
  };

  // Navigation functions
  const nextStep = () => {
    if (activeStep < steps.length - 1) {
      setActiveStep(activeStep + 1);
    }
  };

  const prevStep = () => {
    if (activeStep > 0) {
      setActiveStep(activeStep - 1);
    }
  };

  // Get dropdown options
  const getModuleBrandOptions = () => {
    const brands = brandsFromProducts(moduleProducts);
    return brands.map(brand => ({ label: brand, value: brand }));
  };

  const getModuleModelOptions = () => {
    const filtered = filterModelsByBrand(moduleProducts, projectDetails.selected_module_brand);
    return filtered.map(product => ({ label: product.model_name, value: product.model_name }));
  };

  const getInverterBrandOptions = () => {
    const brands = brandsFromProducts(inverterProducts);
    return brands.map(brand => ({ label: brand, value: brand }));
  };

  const getInverterModelOptions = () => {
    const filtered = filterModelsByBrand(inverterProducts, projectDetails.selected_inverter_brand);
    return filtered.map(product => ({ label: product.model_name, value: product.model_name }));
  };

  const getStorageBrandOptions = () => {
    const brands = brandsFromProducts(storageProducts);
    return brands.map(brand => ({ label: brand, value: brand }));
  };

  const getStorageModelOptions = () => {
    const filtered = filterModelsByBrand(storageProducts, projectDetails.selected_storage_brand);
    return filtered.map(product => ({ label: product.model_name, value: product.model_name }));
  };

  // Render step content
  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return renderModuleQuantityStep();
      case 1:
        return renderModuleInverterStep();
      case 2:
        return renderStorageStep();
      case 3:
        return renderReviewStep();
      default:
        return null;
    }
  };

  const renderModuleQuantityStep = () => (
    <Card title="Anzahl PV Module" className="p-mb-3">
      <div className="p-fluid p-grid">
        <div className="p-col-12 p-md-6">
          <label htmlFor="moduleQuantity" className="p-mb-2 p-d-block">
            {getTextLocal('module_quantity_label', 'Anzahl PV Module')}
          </label>
          <div className="p-inputgroup">
            <Button 
              icon="pi pi-minus" 
              onClick={() => handleModuleQuantityChange(projectDetails.module_quantity - 1)}
              disabled={projectDetails.module_quantity <= 0}
              className="p-button-outlined"
            />
            <InputNumber
              id="moduleQuantity"
              value={projectDetails.module_quantity}
              onValueChange={(e) => handleModuleQuantityChange(e.value ?? null)}
              min={0}
              max={200}
              showButtons={false}
              className="p-text-center"
            />
            <Button 
              icon="pi pi-plus" 
              onClick={() => handleModuleQuantityChange(projectDetails.module_quantity + 1)}
              className="p-button-outlined"
            />
          </div>
          <small className="p-d-block p-mt-2">
            Empfohlen: 15-30 Module für ein Einfamilienhaus
          </small>
        </div>
        
        <div className="p-col-12 p-md-6">
          <div className="p-p-4 info-panel">
            <h5>Aktuelle Auswahl</h5>
            <p><strong>Module:</strong> {projectDetails.module_quantity}</p>
            <p><strong>Geschätzte Leistung:</strong> {calculateAnlageKwp().toFixed(2)} kWp</p>
            {projectDetails.selected_module_capacity_w > 0 && (
              <p><strong>Modulleistung:</strong> {projectDetails.selected_module_capacity_w} Wp</p>
            )}
          </div>
        </div>
      </div>
      
      <Divider />
      
      <div className="p-text-right">
        <Button 
          label="Weiter" 
          icon="pi pi-arrow-right" 
          iconPos="right"
          onClick={nextStep}
          disabled={projectDetails.module_quantity === 0}
        />
      </div>
    </Card>
  );

  const renderModuleInverterStep = () => (
    <>
      <Card title="PV Module Auswahl" className="p-mb-3">
        <div className="p-fluid p-grid">
          <div className="p-col-12 p-md-6">
            <label htmlFor="moduleBrand" className="p-mb-2 p-d-block">
              {getTextLocal('module_brand_label', 'PV Modul Hersteller')}
            </label>
            <Dropdown
              id="moduleBrand"
              value={projectDetails.selected_module_brand}
              options={getModuleBrandOptions()}
              onChange={(e) => handleModuleBrandChange(e.value)}
              placeholder="Bitte wählen..."
              filter
              showClear
            />
          </div>
          
          <div className="p-col-12 p-md-6">
            <label htmlFor="moduleModel" className="p-mb-2 p-d-block">
              {getTextLocal('module_model_label', 'PV Modul Modell')}
            </label>
            <Dropdown
              id="moduleModel"
              value={projectDetails.selected_module_name}
              options={getModuleModelOptions()}
              onChange={(e) => handleModuleModelChange(e.value)}
              placeholder="Erst Hersteller wählen..."
              disabled={!projectDetails.selected_module_brand}
              filter
              showClear
            />
          </div>
        </div>
        
        {projectDetails.selected_module_capacity_w > 0 && (
          <Message 
            severity="info" 
            text={`Leistung pro Modul: ${projectDetails.selected_module_capacity_w} Wp`}
            className="p-mt-3 p-mb-0"
          />
        )}
        
        <Message 
          severity="success" 
          text={`Anlagengröße: ${calculateAnlageKwp().toFixed(2)} kWp`}
          className="p-mt-2 p-mb-0"
        />
      </Card>

      <Card title="Wechselrichter Auswahl" className="p-mb-3">
        <div className="p-fluid p-grid">
          <div className="p-col-12 p-md-4">
            <label htmlFor="inverterBrand" className="p-mb-2 p-d-block">
              {getTextLocal('inverter_brand_label', 'Wechselrichter Hersteller')}
            </label>
            <Dropdown
              id="inverterBrand"
              value={projectDetails.selected_inverter_brand}
              options={getInverterBrandOptions()}
              onChange={(e) => handleInverterBrandChange(e.value)}
              placeholder="Bitte wählen..."
              filter
              showClear
            />
          </div>
          
          <div className="p-col-12 p-md-5">
            <label htmlFor="inverterModel" className="p-mb-2 p-d-block">
              {getTextLocal('inverter_model_label', 'Wechselrichter Modell')}
            </label>
            <Dropdown
              id="inverterModel"
              value={projectDetails.selected_inverter_name}
              options={getInverterModelOptions()}
              onChange={(e) => handleInverterModelChange(e.value)}
              placeholder="Erst Hersteller wählen..."
              disabled={!projectDetails.selected_inverter_brand}
              filter
              showClear
            />
          </div>
          
          <div className="p-col-12 p-md-3">
            <label htmlFor="inverterQuantity" className="p-mb-2 p-d-block">
              {getTextLocal('inverter_quantity_label', 'Anzahl WR')}
            </label>
            <InputNumber
              id="inverterQuantity"
              value={projectDetails.selected_inverter_quantity}
              onValueChange={(e) => handleInverterQuantityChange(e.value ?? null)}
              min={1}
              max={10}
              showButtons
              buttonLayout="horizontal"
              step={1}
            />
          </div>
        </div>
        
        {projectDetails.selected_inverter_power_kw_single > 0 && (
          <div className="p-mt-3">
            <Message 
              severity="info" 
              text={`WR Leistung gesamt: ${calculateTotalInverterPower().toFixed(1)} kW`}
              className="p-mb-2"
            />
            {projectDetails.selected_inverter_quantity > 1 && (
              <small className="p-d-block">
                {projectDetails.selected_inverter_quantity} × {projectDetails.selected_inverter_power_kw_single} kW je WR
              </small>
            )}
          </div>
        )}
      </Card>
      
      <Divider />
      
      <div className="p-d-flex p-jc-between">
        <Button 
          label="Zurück" 
          icon="pi pi-arrow-left"
          onClick={prevStep}
          className="p-button-secondary"
        />
        <Button 
          label="Weiter" 
          icon="pi pi-arrow-right" 
          iconPos="right"
          onClick={nextStep}
          disabled={!projectDetails.selected_module_id || !projectDetails.selected_inverter_id}
        />
      </div>
    </>
  );

  const renderStorageStep = () => (
    <>
      <Card title="Batteriespeicher" className="p-mb-3">
        <div className="p-field-checkbox p-mb-4">
          <Checkbox
            id="includeStorage"
            checked={projectDetails.include_storage}
            onChange={(e) => handleStorageToggle(e.checked || false)}
          />
          <label htmlFor="includeStorage" className="p-ml-2">
            {getTextLocal('include_storage_label', 'Batteriespeicher einplanen')}
          </label>
        </div>
        
        {projectDetails.include_storage && (
          <div className="p-fluid p-grid">
            <div className="p-col-12 p-md-4">
              <label htmlFor="storageBrand" className="p-mb-2 p-d-block">
                {getTextLocal('storage_brand_label', 'Speicher Hersteller')}
              </label>
              <Dropdown
                id="storageBrand"
                value={projectDetails.selected_storage_brand}
                options={getStorageBrandOptions()}
                onChange={(e) => handleStorageBrandChange(e.value)}
                placeholder="Bitte wählen..."
                filter
                showClear
              />
            </div>
            
            <div className="p-col-12 p-md-5">
              <label htmlFor="storageModel" className="p-mb-2 p-d-block">
                {getTextLocal('storage_model_label', 'Speicher Modell')}
              </label>
              <Dropdown
                id="storageModel"
                value={projectDetails.selected_storage_name}
                options={getStorageModelOptions()}
                onChange={(e) => handleStorageModelChange(e.value)}
                placeholder="Erst Hersteller wählen..."
                disabled={!projectDetails.selected_storage_brand}
                filter
                showClear
              />
            </div>
            
            <div className="p-col-12 p-md-3">
              <label htmlFor="storageCapacity" className="p-mb-2 p-d-block">
                {getTextLocal('storage_capacity_manual_label', 'Gewünschte Gesamtkapazität (kWh)')}
              </label>
              <InputNumber
                id="storageCapacity"
                value={projectDetails.selected_storage_storage_power_kw}
                onValueChange={(e) => handleStorageCapacityChange(e.value ?? null)}
                min={0}
                max={100}
                minFractionDigits={1}
                maxFractionDigits={1}
                step={0.1}
                showButtons
                buttonLayout="horizontal"
              />
            </div>
          </div>
        )}
        
        {projectDetails.include_storage && projectDetails.selected_storage_name && (
          <Message 
            severity="info" 
            text={`Ausgewählter Speicher: ${projectDetails.selected_storage_name} (${projectDetails.selected_storage_storage_power_kw} kWh)`}
            className="p-mt-3 p-mb-0"
          />
        )}
      </Card>
      
      <Divider />
      
      <div className="p-d-flex p-jc-between">
        <Button 
          label="Zurück" 
          icon="pi pi-arrow-left"
          onClick={prevStep}
          className="p-button-secondary"
        />
        <Button 
          label="Weiter" 
          icon="pi pi-arrow-right" 
          iconPos="right"
          onClick={nextStep}
        />
      </div>
    </>
  );

  const renderReviewStep = () => (
    <>
      <Card title="Überprüfung & Berechnung" className="p-mb-3">
        <TabView>
          <TabPanel header="Konfiguration">
            <div className="p-grid">
              <div className="p-col-12 p-md-6">
                <Fieldset legend="PV Module">
                  <p><strong>Anzahl:</strong> {projectDetails.module_quantity}</p>
                  <p><strong>Hersteller:</strong> {projectDetails.selected_module_brand || 'Nicht ausgewählt'}</p>
                  <p><strong>Modell:</strong> {projectDetails.selected_module_name || 'Nicht ausgewählt'}</p>
                  <p><strong>Leistung pro Modul:</strong> {projectDetails.selected_module_capacity_w} Wp</p>
                  <p><strong>Gesamtleistung:</strong> {calculateAnlageKwp().toFixed(2)} kWp</p>
                </Fieldset>
              </div>
              
              <div className="p-col-12 p-md-6">
                <Fieldset legend="Wechselrichter">
                  <p><strong>Hersteller:</strong> {projectDetails.selected_inverter_brand || 'Nicht ausgewählt'}</p>
                  <p><strong>Modell:</strong> {projectDetails.selected_inverter_name || 'Nicht ausgewählt'}</p>
                  <p><strong>Anzahl:</strong> {projectDetails.selected_inverter_quantity}</p>
                  <p><strong>Leistung gesamt:</strong> {calculateTotalInverterPower().toFixed(1)} kW</p>
                </Fieldset>
              </div>
              
              {projectDetails.include_storage && (
                <div className="p-col-12">
                  <Fieldset legend="Batteriespeicher">
                    <div className="p-grid">
                      <div className="p-col-6">
                        <p><strong>Hersteller:</strong> {projectDetails.selected_storage_brand || 'Nicht ausgewählt'}</p>
                        <p><strong>Modell:</strong> {projectDetails.selected_storage_name || 'Nicht ausgewählt'}</p>
                      </div>
                      <div className="p-col-6">
                        <p><strong>Kapazität:</strong> {projectDetails.selected_storage_storage_power_kw} kWh</p>
                      </div>
                    </div>
                  </Fieldset>
                </div>
              )}
            </div>
          </TabPanel>
          
          <TabPanel header="Berechnung">
            <div className="p-grid">
              <div className="p-col-12 p-md-6">
                <Fieldset legend="Technische Daten">
                  <p><strong>Anlagengröße:</strong> {calculationResults.anlage_kwp.toFixed(2)} kWp</p>
                  <p><strong>WR Leistung:</strong> {calculationResults.total_inverter_power_kw.toFixed(1)} kW</p>
                  <p><strong>Jahresertrag (geschätzt):</strong> {calculationResults.annual_pv_production_kwh.toLocaleString()} kWh</p>
                  {projectDetails.include_storage && (
                    <p><strong>Speicherkapazität:</strong> {projectDetails.selected_storage_storage_power_kw} kWh</p>
                  )}
                </Fieldset>
              </div>
              
              <div className="p-col-12 p-md-6">
                <Fieldset legend="Wirtschaftliche Daten">
                  <p><strong>Basis-Preis (netto):</strong> {calculationResults.base_matrix_price_netto.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}</p>
                  <p><strong>Investition (netto):</strong> {calculationResults.total_investment_netto.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}</p>
                  <p><strong>Investition (brutto):</strong> {calculationResults.total_investment_brutto.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}</p>
                  <p><strong>Einspeisevergütung (jährlich):</strong> {calculationResults.einspeiseverguetung_total_euro.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}</p>
                </Fieldset>
              </div>
            </div>
            
            <Divider />
            
            <div className="p-text-center p-p-4 total-price-panel">
              <h4 className="p-mb-2">Gesamtpreis</h4>
              <div className="price-display">
                {calculationResults.total_investment_brutto.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}
              </div>
              <small className="p-d-block p-mt-2">
                inkl. 19% MwSt. | {(calculationResults.total_investment_brutto / calculationResults.anlage_kwp).toFixed(0)} €/kWp
              </small>
            </div>
          </TabPanel>
          
          <TabPanel header="Projektdaten">
            <div className="p-fluid p-grid">
              <div className="p-col-12 p-md-6">
                <label htmlFor="projectName" className="p-mb-2 p-d-block">Projektname</label>
                <InputText
                  id="projectName"
                  value={formData.project_name}
                  onChange={(e) => setFormData(prev => ({ ...prev, project_name: e.target.value }))}
                  placeholder="Name des Projekts eingeben..."
                />
              </div>
              
              <div className="p-col-12 p-md-6">
                <label htmlFor="projectStatus" className="p-mb-2 p-d-block">Status</label>
                <Dropdown
                  id="projectStatus"
                  value={formData.project_status}
                  options={[
                    { label: 'Neu', value: 'Neu' },
                    { label: 'In Bearbeitung', value: 'In Bearbeitung' },
                    { label: 'Angebot erstellt', value: 'Angebot erstellt' },
                    { label: 'Beauftragt', value: 'Beauftragt' },
                    { label: 'Abgeschlossen', value: 'Abgeschlossen' }
                  ]}
                  onChange={(e) => setFormData(prev => ({ ...prev, project_status: e.value }))}
                  placeholder="Status wählen..."
                />
              </div>
            </div>
          </TabPanel>
        </TabView>
      </Card>
      
      <Divider />
      
      <div className="p-d-flex p-jc-between p-ai-center">
        <Button 
          label="Zurück" 
          icon="pi pi-arrow-left"
          onClick={prevStep}
          className="p-button-secondary"
        />
        
        <div className="p-d-flex p-ai-center">
          <Button 
            label="Abbrechen" 
            icon="pi pi-times"
            onClick={onCancel}
            className="p-button-outlined p-mr-2"
          />
          <Button 
            label="Projekt speichern" 
            icon="pi pi-check"
            onClick={handleSave}
            className="p-button-success"
            disabled={!projectDetails.selected_module_id || !projectDetails.selected_inverter_id}
          />
        </div>
      </div>
    </>
  );

  if (loading) {
    return (
      <div className="p-d-flex p-jc-center p-ai-center loading-container">
        <ProgressSpinner />
        <span className="p-ml-3">Lade Produktdaten...</span>
      </div>
    );
  }

  return (
    <div className="modern-solar-calculator">
      <Toast ref={toast} />
      
      <Card>
        <div className="p-mb-4">
          <h2 className="p-mb-3">Solar Calculator - {customer.company_name || `${customer.first_name} ${customer.last_name}`}</h2>
          <Steps 
            model={steps} 
            activeIndex={activeStep}
            onSelect={(e) => setActiveStep(e.index)}
            readOnly={false}
            className="p-mb-4"
          />
        </div>
        
        <div className="step-content">
          {renderStepContent()}
        </div>
      </Card>
      

    </div>
  );
};

export default ModernSolarCalculator;
