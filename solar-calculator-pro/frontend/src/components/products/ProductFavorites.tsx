/**
 * Product Favorites Component
 * 
 * Display and manage favorite products
 */

import React from 'react';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { Image } from 'primereact/image';
import { Tag } from 'primereact/tag';
import { Product } from '../../pages/Products';
import './ProductFavorites.css';

interface ProductFavoritesProps {
  products: Product[];
  onAddToComparison: (product: Product) => void;
  onToggleFavorite: (productId: number) => void;
  comparisonCount: number;
}

const ProductFavorites: React.FC<ProductFavoritesProps> = ({
  products,
  onAddToComparison,
  onToggleFavorite,
  comparisonCount
}) => {
  if (products.length === 0) {
    return (
      <div className="favorites-empty">
        <i className="pi pi-star" style={{ fontSize: '3rem', color: 'var(--text-color-secondary)' }} />
        <h3>No Favorite Products</h3>
        <p>Click the star icon on products to add them to your favorites</p>
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
    <div className="product-favorites">
      <div className="favorites-header">
        <h3>{products.length} Favorite Product{products.length > 1 ? 's' : ''}</h3>
      </div>

      <div className="favorites-grid">
        {products.map((product) => (
          <Card key={product.id} className="favorite-card">
            <div className="favorite-card-content">
              <div className="product-image-container">
                {product.image_url ? (
                  <Image
                    src={product.image_url}
                    alt={product.model_name}
                    width="100"
                    preview
                  />
                ) : (
                  <div className="no-image-medium">
                    <i className="pi pi-image" />
                  </div>
                )}
              </div>

              <div className="product-info">
                <h4 className="product-name">{product.model_name}</h4>
                {product.brand && (
                  <p className="product-brand">{product.brand}</p>
                )}
                <Tag value={product.category} severity="info" className="category-tag" />
                <div className="product-price">{formatPrice(product.price_euro)}</div>
              </div>

              <div className="product-actions">
                <Button
                  icon="pi pi-star-fill"
                  className="p-button-rounded p-button-text favorite-button"
                  onClick={() => onToggleFavorite(product.id)}
                  tooltip="Remove from favorites"
                  tooltipOptions={{ position: 'top' }}
                />
                <Button
                  icon="pi pi-clone"
                  className="p-button-rounded p-button-text"
                  onClick={() => onAddToComparison(product)}
                  disabled={comparisonCount >= 4}
                  tooltip={comparisonCount < 4 ? 'Add to comparison' : 'Comparison limit reached'}
                  tooltipOptions={{ position: 'top' }}
                />
                <Button
                  icon="pi pi-eye"
                  className="p-button-rounded p-button-text"
                  tooltip="View details"
                  tooltipOptions={{ position: 'top' }}
                />
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default ProductFavorites;
