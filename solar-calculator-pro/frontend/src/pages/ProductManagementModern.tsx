/**
 * Modern Product Management Page with shadcn/ui
 * 
 * Complete product management with DataTable, CRUD operations, bulk import
 */

import React, { useState, useEffect } from 'react';
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table';
import { Package, Plus, Pencil, Trash2, Upload, Search, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { toast } from 'sonner';
import ProductForm, { ProductFormData } from '../components/products/ProductForm';
import ProductBulkImport from '../components/products/ProductBulkImport';
import api from '../services/api';

interface Product {
  id: number;
  category: string;
  model_name: string;
  brand?: string;
  price_euro?: number;
  description?: string;
  specifications?: Record<string, unknown>;
  image_url?: string;
  company_id?: number;
  created_at?: string;
  updated_at?: string;
}

const ProductManagementModern: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedProducts, setSelectedProducts] = useState<Product[]>([]);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showBulkImportDialog, setShowBulkImportDialog] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [globalFilter, setGlobalFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [deleteProduct, setDeleteProduct] = useState<Product | null>(null);
  const [showBulkDeleteDialog, setShowBulkDeleteDialog] = useState(false);

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
      toast.error('Failed to load products');
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
      toast.success('Product created successfully');
      setShowCreateDialog(false);
      loadProducts();
    } catch (error) {
      console.error('Failed to create product:', error);
      toast.error('Failed to create product');
      throw error;
    }
  };

  const handleUpdateProduct = async (data: ProductFormData) => {
    if (!editingProduct) return;

    try {
      await api.put(`/products/${editingProduct.id}`, data);
      toast.success('Product updated successfully');
      setShowEditDialog(false);
      setEditingProduct(null);
      loadProducts();
    } catch (error) {
      console.error('Failed to update product:', error);
      toast.error('Failed to update product');
      throw error;
    }
  };

  const handleDeleteProduct = async () => {
    if (!deleteProduct) return;

    try {
      await api.delete(`/products/${deleteProduct.id}`);
      toast.success('Product deleted successfully');
      setDeleteProduct(null);
      loadProducts();
    } catch (error) {
      console.error('Failed to delete product:', error);
      toast.error('Failed to delete product');
    }
  };

  const handleBulkDelete = async () => {
    if (selectedProducts.length === 0) return;

    try {
      const deletePromises = selectedProducts.map(product =>
        api.delete(`/products/${product.id}`)
      );
      
      await Promise.all(deletePromises);
      toast.success(`${selectedProducts.length} products deleted successfully`);
      setSelectedProducts([]);
      setShowBulkDeleteDialog(false);
      loadProducts();
    } catch (error) {
      console.error('Failed to delete products:', error);
      toast.error('Failed to delete some products');
    }
  };

  const handleBulkImport = async (products: Product[]) => {
    try {
      const createPromises = products.map(product =>
        api.post('/products', product)
      );
      
      await Promise.all(createPromises);
      toast.success(`${products.length} products imported successfully`);
      setShowBulkImportDialog(false);
      loadProducts();
    } catch (error) {
      console.error('Failed to import products:', error);
      toast.error('Failed to import products');
      throw error;
    }
  };

  const formatPrice = (price?: number) => {
    if (price !== undefined && price !== null) {
      return new Intl.NumberFormat('de-DE', {
        style: 'currency',
        currency: 'EUR'
      }).format(price);
    }
    return '-';
  };

  const columns: ColumnDef<Product>[] = [
    {
      id: 'select',
      header: ({ table }) => (
        <Checkbox
          checked={table.getIsAllPageRowsSelected()}
          onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
          aria-label="Select all"
        />
      ),
      cell: ({ row }) => (
        <Checkbox
          checked={row.getIsSelected()}
          onCheckedChange={(value) => row.toggleSelected(!!value)}
          aria-label="Select row"
        />
      ),
      enableSorting: false,
      enableHiding: false,
    },
    {
      accessorKey: 'image_url',
      header: 'Image',
      cell: ({ row }) => {
        const imageUrl = row.original.image_url;
        if (imageUrl) {
          return (
            <img 
              src={imageUrl} 
              alt={row.original.model_name}
              className="h-12 w-12 object-cover rounded"
            />
          );
        }
        return (
          <div className="h-12 w-12 bg-muted rounded flex items-center justify-center">
            <Package className="h-6 w-6 text-muted-foreground" />
          </div>
        );
      },
    },
    {
      accessorKey: 'category',
      header: 'Category',
      cell: ({ row }) => (
        <Badge variant="secondary">{row.original.category}</Badge>
      ),
    },
    {
      accessorKey: 'model_name',
      header: 'Model Name',
      cell: ({ row }) => (
        <div className="font-medium">{row.original.model_name}</div>
      ),
    },
    {
      accessorKey: 'brand',
      header: 'Brand',
    },
    {
      accessorKey: 'price_euro',
      header: 'Price',
      cell: ({ row }) => formatPrice(row.original.price_euro),
    },
    {
      id: 'actions',
      header: 'Actions',
      cell: ({ row }) => (
        <div className="flex gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => {
              setEditingProduct(row.original);
              setShowEditDialog(true);
            }}
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setDeleteProduct(row.original)}
          >
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      ),
    },
  ];

  const filteredProducts = products.filter(product => {
    if (categoryFilter !== 'all' && product.category !== categoryFilter) {
      return false;
    }
    if (globalFilter) {
      const searchLower = globalFilter.toLowerCase();
      return (
        product.model_name?.toLowerCase().includes(searchLower) ||
        product.brand?.toLowerCase().includes(searchLower) ||
        product.category?.toLowerCase().includes(searchLower)
      );
    }
    return true;
  });

  const table = useReactTable({
    data: filteredProducts,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onRowSelectionChange: (updater) => {
      const newSelection = typeof updater === 'function' 
        ? updater(table.getState().rowSelection) 
        : updater;
      const selected = Object.keys(newSelection)
        .filter(key => newSelection[key])
        .map(key => filteredProducts[parseInt(key)]);
      setSelectedProducts(selected);
    },
    initialState: {
      pagination: {
        pageSize: 20,
      },
    },
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="mb-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-500 to-teal-600 shadow-lg">
              <Package className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Product Management</h1>
              <p className="text-muted-foreground">
                Create, edit, and manage your product catalog
              </p>
            </div>
          </div>
        </div>

        {/* Toolbar */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex flex-wrap gap-2">
                <Button onClick={() => setShowCreateDialog(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  New Product
                </Button>
                <Button variant="outline" onClick={() => setShowBulkImportDialog(true)}>
                  <Upload className="mr-2 h-4 w-4" />
                  Bulk Import
                </Button>
                {selectedProducts.length > 0 && (
                  <Button 
                    variant="destructive" 
                    onClick={() => setShowBulkDeleteDialog(true)}
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete ({selectedProducts.length})
                  </Button>
                )}
              </div>
              
              <div className="flex flex-wrap gap-2">
                <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                  <SelectTrigger className="w-[180px]">
                    <Filter className="mr-2 h-4 w-4" />
                    <SelectValue placeholder="Category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    {categories.map(cat => (
                      <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    value={globalFilter}
                    onChange={(e) => setGlobalFilter(e.target.value)}
                    placeholder="Search products..."
                    className="pl-9 w-64"
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Table */}
        <Card>
          <CardContent className="p-6">
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  {table.getHeaderGroups().map((headerGroup) => (
                    <TableRow key={headerGroup.id}>
                      {headerGroup.headers.map((header) => (
                        <TableHead key={header.id}>
                          {header.isPlaceholder
                            ? null
                            : flexRender(
                                header.column.columnDef.header,
                                header.getContext()
                              )}
                        </TableHead>
                      ))}
                    </TableRow>
                  ))}
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={columns.length} className="h-24 text-center">
                        Loading...
                      </TableCell>
                    </TableRow>
                  ) : table.getRowModel().rows?.length ? (
                    table.getRowModel().rows.map((row) => (
                      <TableRow key={row.id} data-state={row.getIsSelected() && "selected"}>
                        {row.getVisibleCells().map((cell) => (
                          <TableCell key={cell.id}>
                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                          </TableCell>
                        ))}
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={columns.length} className="h-24 text-center">
                        No products found
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-muted-foreground">
                {table.getFilteredRowModel().rows.length > 0
                  ? `Showing ${table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1} to ${Math.min((table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize, table.getFilteredRowModel().rows.length)} of ${table.getFilteredRowModel().rows.length} products`
                  : 'No products'}
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => table.previousPage()}
                  disabled={!table.getCanPreviousPage()}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => table.nextPage()}
                  disabled={!table.getCanNextPage()}
                >
                  Next
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Create Dialog */}
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create New Product</DialogTitle>
            </DialogHeader>
            <ProductForm
              categories={categories}
              onSubmit={handleCreateProduct}
              onCancel={() => setShowCreateDialog(false)}
            />
          </DialogContent>
        </Dialog>

        {/* Edit Dialog */}
        <Dialog open={showEditDialog} onOpenChange={(open) => {
          setShowEditDialog(open);
          if (!open) setEditingProduct(null);
        }}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Edit Product</DialogTitle>
            </DialogHeader>
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
          </DialogContent>
        </Dialog>

        {/* Bulk Import Dialog */}
        <Dialog open={showBulkImportDialog} onOpenChange={setShowBulkImportDialog}>
          <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Bulk Import Products</DialogTitle>
            </DialogHeader>
            <ProductBulkImport
              onImport={handleBulkImport}
              onCancel={() => setShowBulkImportDialog(false)}
            />
          </DialogContent>
        </Dialog>

        {/* Delete Confirmation */}
        <AlertDialog open={!!deleteProduct} onOpenChange={() => setDeleteProduct(null)}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Confirm Delete</AlertDialogTitle>
              <AlertDialogDescription>
                Are you sure you want to delete "{deleteProduct?.model_name}"? 
                This action cannot be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction onClick={handleDeleteProduct} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                Delete
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>

        {/* Bulk Delete Confirmation */}
        <AlertDialog open={showBulkDeleteDialog} onOpenChange={setShowBulkDeleteDialog}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Confirm Bulk Delete</AlertDialogTitle>
              <AlertDialogDescription>
                Are you sure you want to delete {selectedProducts.length} products? 
                This action cannot be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction onClick={handleBulkDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                Delete All
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
  );
};

export default ProductManagementModern;
