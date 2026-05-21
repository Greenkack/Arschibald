/**
 * ProductManagement Page - Task 50
 * 
 * Complete product management interface with:
 * - Product creation form
 * - Product edit interface
 * - Bulk product import
 * - Product image management
 * - Product specifications editor
 */

import React, { useState, useEffect, useRef } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { Toast } from 'primereact/toast';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import { InputText } from 'primereact/inputtext';
import { Dropdown } from 'primereact/dropdown';
import { Tag } from 'primereact/tag';
import { Toolbar } from 'primereact/toolbar';
import ProductForm, { ProductFormData } from '../components/products/ProductForm';
import ProductBulkImport from '../components/products/ProductBulkImport';
import api from '../services/api';
import './ProductManagement.css';

interface Product {
  id: number;
  category: string;
  model_name: string;
  brand?: string;
  price_euro?: number;
  description?: string;
  specifications?: Record<string, any>;
  image_url?: string;
  company_id?: number;
  created_at?: string;
  updated_at?: string;
}

const ProductManagement: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedProducts, setSelectedProducts] = useState<Product[]>([]);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showBulkImportDialog, setShowBulkImportDialog] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [globalFilter, setGlobalFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null);
  const toastRef = useRef<Toast>(null);

  useEffect(() => {
    loadProducts();
    loadCategories();
  }, []);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const response = await api.get('/products');
      setProducts(response.data.products || []);
    } catch (error) {
      console.error('Failed to load products:', error);
      toastRef.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load products',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const response = await api.get('/products/categories/list');
      setCategories(response.data.categories || []);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  };

  const handleCreateProduct = async (data: ProductFormData) => {
    try {
      await api.post('/products', data);
      
      toastRef.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: 'Product created successfully',
        life: 3000
      });
      
      setShowCreateDialog(false);
      loadProducts();
    } catch (error) {
      console.error('Failed to create product:', error);
      toastRef.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to create product',
        life: 3000
      });
      throw error;
    }
  };

  const handleUpdateProduct = async (data: ProductFormData) => {
    if (!editingProduct) return;

    try {
      await api.put(`/products/${editingProduct.id}`, data);
      
      toastRef.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: 'Product updated successfully',
        life: 3000
      });
      
      setShowEditDialog(false);
      setEditingProduct(null);
      loadProducts();
    } catch (error) {
      console.error('Failed to update product:', error);
      toastRef.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to update product',
        life: 3000
      });
      throw error;
    }
  };

  const handleDeleteProduct = (product: Product) => {
    confirmDialog({
      message: `Are you sure you want to delete "${product.model_name}"?`,
      header: 'Confirm Delete',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        try {
          await api.delete(`/products/${product.id}`);
          
          toastRef.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: 'Product deleted successfully',
            life: 3000
          });
          
          loadProducts();
        } catch (error) {
          console.error('Failed to delete product:', error);
          toastRef.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to delete product',
            life: 3000
          });
        }
      }
    });
  };

  const handleBulkDelete = () => {
    if (selectedProducts.length === 0) return;

    confirmDialog({
      message: `Are you sure you want to delete ${selectedProducts.length} products?`,
      header: 'Confirm Bulk Delete',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        try {
          const deletePromises = selectedProducts.map(product =>
            api.delete(`/products/${product.id}`)
          );
          
          await Promise.all(deletePromises);
          
          toastRef.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: `${selectedProducts.length} products deleted successfully`,
            life: 3000
          });
          
          setSelectedProducts([]);
          loadProducts();
        } catch (error) {
          console.error('Failed to delete products:', error);
          toastRef.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to delete some products',
            life: 3000
          });
        }
      }
    });
  };

  const handleBulkImport = async (products: any[]) => {
    try {
      const createPromises = products.map(product =>
        api.post('/products', product)
      );
      
      await Promise.all(createPromises);
      
      toastRef.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: `${products.length} products imported successfully`,
        life: 3000
      });
      
      setShowBulkImportDialog(false);
      loadProducts();
    } catch (error) {
      console.error('Failed to import products:', error);
      toastRef.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to import products',
        life: 3000
      });
      throw error;
    }
  };

  const handleEditProduct = (product: Product) => {
    setEditingProduct(product);
    setShowEditDialog(true);
  };

  const imageBodyTemplate = (rowData: Product) => {
    if (rowData.image_url) {
      return (
        <img 
          src={rowData.image_url} 
          alt={rowData.model_name}
          className="product-image-thumbnail"
        />
      );
    }
    return <span className="pi pi-image" style={{ fontSize: '2rem', color: '#ccc' }} />;
  };

  const priceBodyTemplate = (rowData: Product) => {
    if (rowData.price_euro !== undefined && rowData.price_euro !== null) {
      return new Intl.NumberFormat('de-DE', {
        style: 'currency',
        currency: 'EUR'
      }).format(rowData.price_euro);
    }
    return '-';
  };

  const categoryBodyTemplate = (rowData: Product) => {
    return <Tag value={rowData.category} />;
  };

  const actionsBodyTemplate = (rowData: Product) => {
    return (
      <div className="action-buttons">
        <Button
          icon="pi pi-pencil"
          className="p-button-rounded p-button-text"
          onClick={() => handleEditProduct(rowData)}
          tooltip="Edit"
          tooltipOptions={{ position: 'top' }}
        />
        <Button
          icon="pi pi-trash"
          className="p-button-rounded p-button-text p-button-danger"
          onClick={() => handleDeleteProduct(rowData)}
          tooltip="Delete"
          tooltipOptions={{ position: 'top' }}
        />
      </div>
    );
  };

  const leftToolbarTemplate = () => {
    return (
      <div className="toolbar-left">
        <Button
          label="New Product"
          icon="pi pi-plus"
          className="p-button-success"
          onClick={() => setShowCreateDialog(true)}
        />
        <Button
          label="Bulk Import"
          icon="pi pi-upload"
          className="p-button-info"
          onClick={() => setShowBulkImportDialog(true)}
        />
        {selectedProducts.length > 0 && (
          <Button
            label={`Delete (${selectedProducts.length})`}
            icon="pi pi-trash"
            className="p-button-danger"
            onClick={handleBulkDelete}
          />
        )}
      </div>
    );
  };

  const rightToolbarTemplate = () => {
    return (
      <div className="toolbar-right">
        <Dropdown
          value={categoryFilter}
          options={[
            { label: 'All Categories', value: null },
            ...categories.map(cat => ({ label: cat, value: cat }))
          ]}
          onChange={(e) => setCategoryFilter(e.value)}
          placeholder="Filter by Category"
          className="category-filter"
        />
        <span className="p-input-icon-left">
          <i className="pi pi-search" />
          <InputText
            value={globalFilter}
            onChange={(e) => setGlobalFilter(e.target.value)}
            placeholder="Search products..."
          />
        </span>
      </div>
    );
  };

  const filteredProducts = products.filter(product => {
    if (categoryFilter && product.category !== categoryFilter) {
      return false;
    }
    return true;
  });

  return (
    <div className="product-management-page">
      <Toast ref={toastRef} />
      <ConfirmDialog />

      <div className="page-header">
        <h1>Product Management</h1>
        <p>Create, edit, and manage your product catalog</p>
      </div>

      <Toolbar 
        left={leftToolbarTemplate} 
        right={rightToolbarTemplate}
        className="products-toolbar"
      />

      <DataTable
        value={filteredProducts}
        selection={selectedProducts}
        onSelectionChange={(e) => setSelectedProducts(e.value)}
        dataKey="id"
        paginator
        rows={20}
        rowsPerPageOptions={[10, 20, 50, 100]}
        loading={loading}
        globalFilter={globalFilter}
        emptyMessage="No products found"
        className="products-table"
      >
        <Column selectionMode="multiple" style={{ width: '3rem' }} />
        <Column 
          header="Image" 
          body={imageBodyTemplate} 
          style={{ width: '100px' }} 
        />
        <Column 
          field="category" 
          header="Category" 
          body={categoryBodyTemplate}
          sortable 
          style={{ width: '150px' }} 
        />
        <Column 
          field="model_name" 
          header="Model Name" 
          sortable 
          filter 
          filterPlaceholder="Search by name"
        />
        <Column 
          field="brand" 
          header="Brand" 
          sortable 
          filter 
          filterPlaceholder="Search by brand"
          style={{ width: '150px' }} 
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
          style={{ width: '120px' }} 
        />
      </DataTable>

      <Dialog
        visible={showCreateDialog}
        onHide={() => setShowCreateDialog(false)}
        header="Create New Product"
        modal
        className="product-dialog"
        style={{ width: '900px' }}
      >
        <ProductForm
          categories={categories}
          onSubmit={handleCreateProduct}
          onCancel={() => setShowCreateDialog(false)}
        />
      </Dialog>

      <Dialog
        visible={showEditDialog}
        onHide={() => {
          setShowEditDialog(false);
          setEditingProduct(null);
        }}
        header="Edit Product"
        modal
        className="product-dialog"
        style={{ width: '900px' }}
      >
        {editingProduct && (
          <ProductForm
            product={editingProduct}
            categories={categories}
            onSubmit={handleUpdateProduct}
            onCancel={() => {
              setShowEditDialog(false);
              setEditingProduct(null);
            }}
          />
        )}
      </Dialog>

      <Dialog
        visible={showBulkImportDialog}
        onHide={() => setShowBulkImportDialog(false)}
        header="Bulk Import Products"
        modal
        className="bulk-import-dialog"
        style={{ width: '1200px' }}
      >
        <ProductBulkImport
          onImport={handleBulkImport}
          onCancel={() => setShowBulkImportDialog(false)}
        />
      </Dialog>
    </div>
  );
};

export default ProductManagement;
