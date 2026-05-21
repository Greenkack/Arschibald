/**
 * Product Catalog Component
 * 
 * Main product list with DataTable
 */

import React, { useState } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Tag } from 'primereact/tag';
import { Image } from 'primereact/image';
import { Product } from '../../pages/Products';
import './ProductCatalog.css';

interface ProductCatalogProps {
  products: Product[];
  loading: boolean;
  onAddToComparison: (product: Product) => void;
  onToggleFavorite: (productId: number) => void;
  favoriteIds: number[];
  comparisonCount: number;
}

const ProductCatalog: React.FC<ProductCatalogProps> = ({
  products,
  loading,
  onAddToComparison,
  onToggleFavorite,
  favoriteIds,
  comparisonCount
}) => {
  const [selectedProducts, setSelectedProducts] = useState<Product[]>([]);

  const imageBodyTemplate = (product: Product) => {
    return (
      <div className="product-image-cell">
        {product.image_url ? (
          <Image
            src={product.image_url}
            alt={product.model_name}
            width="60"
            height="60"
            preview
          />
        ) : (
          <div className="no-image">
            <i className="pi pi-image" />
          </div>
        )}
      </div>
    );
  };

  const nameBodyTemplate = (product: Product) => {
    return (
      <div className="product-name-cell">
        <div className="product-model">{product.model_name}</div>
        {product.brand && (
          <div className="product-brand">{product.brand}</div>
        )}
      </div>
    );
  };

  const categoryBodyTemplate = (product: Product) => {
    return <Tag value={product.category} severity="info" />;
  };

  const priceBodyTemplate = (product: Product) => {
    if (!product.price_euro) return '-';
    
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR'
    }).format(product.price_euro);
  };

  const actionsBodyTemplate = (product: Product) => {
    const isFavorite = favoriteIds.includes(product.id);
    const canAddToComparison = comparisonCount < 4;

    return (
      <div className="product-actions">
        <Button
          icon={isFavorite ? 'pi pi-star-fill' : 'pi pi-star'}
          className={`p-button-rounded p-button-text ${isFavorite ? 'favorite-active' : ''}`}
          onClick={() => onToggleFavorite(product.id)}
          tooltip={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
          tooltipOptions={{ position: 'top' }}
        />
        <Button
          icon="pi pi-clone"
          className="p-button-rounded p-button-text"
          onClick={() => onAddToComparison(product)}
          disabled={!canAddToComparison}
          tooltip={canAddToComparison ? 'Add to comparison' : 'Comparison limit reached (4 max)'}
          tooltipOptions={{ position: 'top' }}
        />
        <Button
          icon="pi pi-eye"
          className="p-button-rounded p-button-text"
          tooltip="View details"
          tooltipOptions={{ position: 'top' }}
        />
      </div>
    );
  };

  return (
    <div className="product-catalog">
      <DataTable
        value={products}
        loading={loading}
        paginator
        rows={20}
        rowsPerPageOptions={[10, 20, 50, 100]}
        selection={selectedProducts}
        onSelectionChange={(e) => setSelectedProducts(e.value)}
        dataKey="id"
        emptyMessage="No products found"
        className="product-table"
        stripedRows
        showGridlines
      >
        <Column
          selectionMode="multiple"
          headerStyle={{ width: '3rem' }}
          exportable={false}
        />
        <Column
          field="image_url"
          header="Image"
          body={imageBodyTemplate}
          style={{ width: '100px' }}
        />
        <Column
          field="model_name"
          header="Product"
          body={nameBodyTemplate}
          sortable
          filter
          filterPlaceholder="Search by name"
        />
        <Column
          field="category"
          header="Category"
          body={categoryBodyTemplate}
          sortable
          filter
          filterPlaceholder="Search by category"
        />
        <Column
          field="price_euro"
          header="Price"
          body={priceBodyTemplate}
          sortable
          style={{ width: '120px' }}
        />
        <Column
          header="Actions"
          body={actionsBodyTemplate}
          exportable={false}
          style={{ width: '150px' }}
        />
      </DataTable>
    </div>
  );
};

export default ProductCatalog;
