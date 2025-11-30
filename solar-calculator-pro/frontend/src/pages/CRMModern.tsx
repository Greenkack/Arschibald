/**
 * Modern CRM Page with shadcn/ui
 * 
 * Customer relationship management with customer list, creation, editing, and detail view
 */

import React, { useState } from 'react';
import { Users, Plus, FileText, CheckSquare, Calendar } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import CustomerList from '../components/crm/CustomerList';
import CustomerForm from '../components/crm/CustomerForm';
import CustomerDetail from '../components/crm/CustomerDetail';

interface Customer {
  id: number;
  first_name: string;
  last_name: string;
  company_name?: string;
  email?: string;
  phone_mobile?: string;
  phone_landline?: string;
  street?: string;
  city?: string;
  postal_code?: string;
  country?: string;
  notes?: string;
  created_at?: string;
}

const CRMModern: React.FC = () => {
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showDetailDialog, setShowDetailDialog] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Handle create customer
  const handleCreateClick = () => {
    setSelectedCustomer(null);
    setShowCreateDialog(true);
  };

  // Handle edit customer
  const handleEditCustomer = (customer: Customer) => {
    setSelectedCustomer(customer);
    setShowEditDialog(true);
  };

  // Handle view customer details
  const handleViewCustomer = (customer: Customer) => {
    setSelectedCustomer(customer);
    setShowDetailDialog(true);
  };

  // Handle save (create or update)
  const handleSave = () => {
    setShowCreateDialog(false);
    setShowEditDialog(false);
    setShowDetailDialog(false);
    setRefreshTrigger(prev => prev + 1);
  };

  // Handle cancel
  const handleCancel = () => {
    setShowCreateDialog(false);
    setShowEditDialog(false);
    setSelectedCustomer(null);
  };

  // Handle edit from detail view
  const handleEditFromDetail = () => {
    setShowDetailDialog(false);
    setShowEditDialog(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="mb-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg">
              <Users className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Customer Management</h1>
              <p className="text-muted-foreground">
                Verwalten Sie Ihre Kunden, Angebote und Aktivitäten
              </p>
            </div>
          </div>
          <Button onClick={handleCreateClick} size="lg">
            <Plus className="mr-2 h-5 w-5" />
            New Customer
          </Button>
        </div>

        {/* Main Content */}
        <Card>
          <CardContent className="p-6">
            <Tabs defaultValue="customers" className="space-y-6">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="customers" className="gap-2">
                  <Users className="h-4 w-4" />
                  Customers
                </TabsTrigger>
                <TabsTrigger value="offers" disabled className="gap-2">
                  <FileText className="h-4 w-4" />
                  Offers
                </TabsTrigger>
                <TabsTrigger value="tasks" disabled className="gap-2">
                  <CheckSquare className="h-4 w-4" />
                  Tasks
                </TabsTrigger>
                <TabsTrigger value="activities" disabled className="gap-2">
                  <Calendar className="h-4 w-4" />
                  Activities
                </TabsTrigger>
              </TabsList>

              <TabsContent value="customers" className="space-y-4">
                <CustomerList
                  onCustomerSelect={handleViewCustomer}
                  onCustomerEdit={handleEditCustomer}
                  refreshTrigger={refreshTrigger}
                />
              </TabsContent>

              <TabsContent value="offers" className="space-y-4">
                <div className="flex min-h-[400px] items-center justify-center rounded-lg border border-dashed">
                  <div className="text-center">
                    <FileText className="mx-auto h-12 w-12 text-muted-foreground" />
                    <h3 className="mt-4 text-lg font-semibold">Offer Management</h3>
                    <p className="mt-2 text-sm text-muted-foreground">
                      Coming soon...
                    </p>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="tasks" className="space-y-4">
                <div className="flex min-h-[400px] items-center justify-center rounded-lg border border-dashed">
                  <div className="text-center">
                    <CheckSquare className="mx-auto h-12 w-12 text-muted-foreground" />
                    <h3 className="mt-4 text-lg font-semibold">Task Management</h3>
                    <p className="mt-2 text-sm text-muted-foreground">
                      Coming soon...
                    </p>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="activities" className="space-y-4">
                <div className="flex min-h-[400px] items-center justify-center rounded-lg border border-dashed">
                  <div className="text-center">
                    <Calendar className="mx-auto h-12 w-12 text-muted-foreground" />
                    <h3 className="mt-4 text-lg font-semibold">Activity Tracking</h3>
                    <p className="mt-2 text-sm text-muted-foreground">
                      Coming soon...
                    </p>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Create Customer Dialog */}
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create New Customer</DialogTitle>
            </DialogHeader>
            <CustomerForm
              onSave={handleSave}
              onCancel={handleCancel}
            />
          </DialogContent>
        </Dialog>

        {/* Edit Customer Dialog */}
        <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
          <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Edit Customer</DialogTitle>
            </DialogHeader>
            <CustomerForm
              customer={selectedCustomer}
              onSave={handleSave}
              onCancel={handleCancel}
            />
          </DialogContent>
        </Dialog>

        {/* Customer Detail Dialog */}
        <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
          <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
            {selectedCustomer && (
              <CustomerDetail
                customer={selectedCustomer}
                onEdit={handleEditFromDetail}
                onClose={() => setShowDetailDialog(false)}
              />
            )}
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default CRMModern;
