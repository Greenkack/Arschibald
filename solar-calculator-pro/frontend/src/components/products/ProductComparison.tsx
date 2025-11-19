/**
 * Product Comparison Component
 * 
 * Side-by-side product comparison
 */

import React from 'react';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { Image } from 'primereact/image';
import { Divider } from 'primereact/divider';
import { Product } from '../../pages/Products';
import './ProductComparison.css';

interface ProductComparisonProps {
  products: Product[];
  onRemove: (productId: number) => void;
  onClear: () => void;
}

const ProductComparison: React.FC<ProductComparisonProps> = ({
  products,
  onRemove,
  onClear
}) => {
  if (products.length === 0) {
    return (
      <div className="comparison-empty">
        <i className="pi pi-clone" style={{ fontSize: '3rem', color: 'var(--text-color-secondary)' }} />
        <h3>No Products to Compare</h3>
        <p>Add products from the catalog to compare them side by side</p>
      </div>
    );
  }

  const formatPrice = (price?: number) => {
    if (!price) return '-';
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR'
    }).format(price);
  };

  return (
    <div className="product-comparison">
      <div className="comparison-header">
        <h3>Comparing {products.length} Product{products.length > 1 ? 's' : ''}</h3>
        <Button
          label="Clear All"
          icon="pi pi-times"
          onClick={onClear}
          outlined
          severity="danger"
        />
      </div>

      <div className="comparison-grid">
        {products.map((product) => (
          <Card key={product.id} className="comparison-card">
            <div className="comparison-card-header">
              <Button
                icon="pi pi-times"
                className="p-button-rounded p-button-text p-button-danger"
                onClick={() => onRemove(product.id)}
                tooltip="Remove from comparison"
              />
            </div>

            <div className="comparison-card-body">
              <div className="product-image-large">
                {prod
uct.image_url ? (
                  <Image
                    src={product.image_url}
                    alt={product.model_name}
                    width="150"
                    preview
                  />
                ) : (
                  <div className="no-image-large">
                    <i className="pi pi-image" />
                  </div>
                )}
              </div>

              <h4 className="product-name">{product.model_name}</h4>
              {product.brand && (
                <p className="product-brand">{product.brand}</p>
              )}

              <Divider />

              <div className="product-details">
                <div className="detail-row">
                  <span className="detail-label">Category:</span>
                  <span className="detail-value">{product.category}</span>
                </div>

                <div className="detail-row">
                  <span className="detail-label">Price:</span>
                  <span className="detail-value price">{formatPrice(product.price_euro)}</span>
                </div>

                {product.description && (
                  <div className="detail-row">
                    <span className="detail-label">Description:</span>
                    <span className="detail-value">{product.description}</span>
                  </div>
                )}

                {product.specifications && Object.keys(product.specifications).length > 0 && (
                  <>
                    <Divider />
                    <h5>Specifications</h5>
                    {Object.entries(product.specifications).map(([key, value]) => (
                      <div key={key} className="detail-row">
                        <span className="detail-label">{key}:</span>
                        <span className="detail-value">{String(value)}</span>
                      </div>
                    ))}
                  </>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default ProductComparison;
