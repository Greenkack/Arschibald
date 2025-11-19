/**
 * Category Navigation Component
 * 
 * Sidebar navigation for product categories
 */

import React from 'react';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import './CategoryNavigation.css';

interface CategoryNavigationProps {
  categories: string[];
  selectedCategory: string | null;
  onSelectCategory: (category: string | null) => void;
  productCounts: Record<string, number>;
}

const CategoryNavigation: React.FC<CategoryNavigationProps> = ({
  categories,
  selectedCategory,
  onSelectCategory,
  productCounts
}) => {
  return (
    <Card title="Categories" className="category-navigation">
      <div className="category-list">
        <Button
          label="All Products"
          icon="pi pi-th-large"
          className={`category-button ${selectedCategory === null ? 'active' : ''}`}
          onClick={() => onSelectCategory(null)}
          text
        />
        
        {categories.map((category) => (
          <Button
            key={category}
            label={category}
            icon="pi pi-tag"
            className={`category-button ${selectedCategory === category ? 'active' : ''}`}
            onClick={() => onSelectCategory(category)}
            badge={productCounts[category]?.toString()}
            text
          />
        ))}
      </div>
    </Card>
  );
};

export default CategoryNavigation;
