/**
 * Modern Communication History Page with shadcn/ui
 * 
 * Manage all customer communications in one place
 */

import React, { useState } from 'react';
import { MessageSquare, Mail, Phone, Paperclip, Search, Users } from 'lucide-react';
import { Card, CardContent, CardDescription, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  CommunicationLog,
  EmailIntegration,
  CallLogging,
  DocumentAttachments,
  CommunicationSearch
} from '../components/crm';

interface Customer {
  id: number;
  first_name: string;
  last_name: string;
  email?: string;
  phone_mobile?: string;
}

export const CommunicationHistoryModern: React.FC = () => {
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [activeTab, setActiveTab] = useState('all');

  React.useEffect(() => {
    const mockCustomers: Customer[] = [
      { id: 1, first_name: 'Max', last_name: 'Mustermann', email: 'max@example.com', phone_mobile: '+49 123 456789' },
      { id: 2, first_name: 'Anna', last_name: 'Schmidt', email: 'anna@example.com', phone_mobile: '+49 987 654321' }
    ];
    setCustomers(mockCustomers);
    if (mockCustomers.length > 0) {
      setSelectedCustomer(mockCustomers[0]);
    }
  }, []);

  const handleCustomerChange = (customerId: string) => {
    const customer = customers.find(c => c.id === parseInt(customerId));
    if (customer) {
      setSelectedCustomer(customer);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 shadow-lg">
              <MessageSquare className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Communication History</h1>
              <p className="text-muted-foreground">
                Manage all customer communications in one place
              </p>
            </div>
          </div>
        </div>

        {/* Customer Selector */}
        <Card className="mb-6">
          <CardContent className="flex items-center gap-4 p-6">
            <div className="flex-1">
              <label className="text-sm font-medium mb-2 block">Select Customer:</label>
              <Select
                value={selectedCustomer?.id.toString()}
                onValueChange={handleCustomerChange}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select a customer" />
                </SelectTrigger>
                <SelectContent>
                  {customers.map((customer) => (
                    <SelectItem key={customer.id} value={customer.id.toString()}>
                      {customer.first_name} {customer.last_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            {selectedCustomer && (
              <div className="flex gap-4 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <Mail className="h-4 w-4" />
                  {selectedCustomer.email || 'No email'}
                </div>
                <div className="flex items-center gap-2">
                  <Phone className="h-4 w-4" />
                  {selectedCustomer.phone_mobile || 'No phone'}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Main Content */}
        {selectedCustomer ? (
          <Card>
            <CardContent className="p-6">
              <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
                <TabsList className="grid w-full grid-cols-5">
                  <TabsTrigger value="all" className="gap-2">
                    <MessageSquare className="h-4 w-4" />
                    All Communications
                  </TabsTrigger>
                  <TabsTrigger value="emails" className="gap-2">
                    <Mail className="h-4 w-4" />
                    Emails
                  </TabsTrigger>
                  <TabsTrigger value="calls" className="gap-2">
                    <Phone className="h-4 w-4" />
                    Calls
                  </TabsTrigger>
                  <TabsTrigger value="documents" className="gap-2">
                    <Paperclip className="h-4 w-4" />
                    Documents
                  </TabsTrigger>
                  <TabsTrigger value="search" className="gap-2">
                    <Search className="h-4 w-4" />
                    Search
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="all" className="space-y-4">
                  <CommunicationLog customerId={selectedCustomer.id} />
                </TabsContent>

                <TabsContent value="emails" className="space-y-4">
                  <EmailIntegration 
                    customerId={selectedCustomer.id}
                    customerEmail={selectedCustomer.email}
                  />
                </TabsContent>

                <TabsContent value="calls" className="space-y-4">
                  <CallLogging 
                    customerId={selectedCustomer.id}
                    customerPhone={selectedCustomer.phone_mobile}
                  />
                </TabsContent>

                <TabsContent value="documents" className="space-y-4">
                  <DocumentAttachments customerId={selectedCustomer.id} />
                </TabsContent>

                <TabsContent value="search" className="space-y-4">
                  <CommunicationSearch customerId={selectedCustomer.id} />
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="flex min-h-[400px] items-center justify-center">
              <div className="text-center">
                <Users className="mx-auto h-12 w-12 text-muted-foreground" />
                <CardTitle className="mt-4">No Customer Selected</CardTitle>
                <CardDescription className="mt-2">
                  Please select a customer to view their communication history
                </CardDescription>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default CommunicationHistoryModern;
