/**
 * Product Search Component
 * 
 * Advanced search with filters for products
 */

import React, { useState } from 'react';
import { Card } from 'primereact/card';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import { Dropdown } from 'primereact/dropdown';
import { InputNumber } from 'primereact/inputnumber';
import { Accordion, AccordionTab } from 'primereact/accordion';
import { SearchFilters } from '../../pages/Products';
import './ProductSearch.css';

interface ProductSearchProps {
  onSearch: (query: string, filters: SearchFilters) => void;
  categories: string[];
  initialFilters: SearchFilters;
}

const ProductSearch: React.FC<ProductSearchProps> = ({
  onSearch,
  categories,
  initialFilters
}) => {
  const [query, setQuery] = useState<string>('');
  const [filters, setFilters] = useState<SearchFilters>(initialFilters);

  const handleSearch = () => {
    onSearch(query, filters);
  };

  const handleClearFilters = () => {
    setQuery('');
    setFilters({});
    onSearch('', {});
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <Card className="product-search">
      <div className="search-bar">
        <span className="p-input-icon-left flex-1">
          <i className="pi pi-search" />
          <InputText
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Search products by name, brand, or description..."
            className="w-full"
          />
        </span>
        <Button
          label="Search"
          icon="pi pi-search"
          onClick={handleSearch}
        />
        <Button
          label="Clear"
          icon="pi pi-times"
          onClick={handleClearFilters}
          outlined
        />
      </div>

      <Accordion className="filters-accordion">
        <AccordionTab header="Advanced Filters">
          <div className="filters-grid">
            <div className="filter-field">
              <label>Category</label>
              <Dropdown
                value={filters.category}
                options={categories.map(c => ({ label: c, value: c }))}
                onChange={(e) => setFilters({ ...filters, category: e.value })}
                placeholder="Select category"
                showClear
                className="w-full"
              />
            </div>

            <div className="filter-field">
              <label>Brand</label>
              <InputText
                value={filters.brand || ''}
                onChange={(e) => setFilters({ ...filters, brand: e.target.value })}
                placeholder="Enter brand name"
                className="w-full"
              />
            </div>

            <div className="filter-field">
              <label>Min Price (€)</label>
              <InputNumber
                value={filters.price_min}
                onValueChange={(e) => setFilters({ ...filters, price_min: e.value || undefined })}
                placeholder="0"
                mode="currency"
                currency="EUR"
                locale="de-DE"
                className="w-full"
              />
            </div>

            <div className="filter-field">
              <label>Max Price (€)</label>
              <InputNumber
                value={filters.price_max}
                onValueChange={(e) => setFilters({ ...filters, price_max: e.value || undefined })}
                placeholder="10000"
                mode="currency"
                currency="EUR"
                locale="de-DE"
                className="w-full"
              />
            </div>
          </div>

          <div className="filter-actions">
            <Button
              label="Apply Filters"
              icon="pi pi-check"
              onClick={handleSearch}
            />
          </div>
        </AccordionTab>
      </Accordion>
    </Card>
  );
};

export default ProductSearch;
