import React, { useState, useRef } from 'react';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { Divider } from 'primereact/divider';
import {
  FormInput,
  DataTable,
  Modal,
  SimpleModal,
  LoadingSpinner,
  InlineSpinner,
  SkeletonLoader,
  CardSkeleton,
  TableSkeleton,
  FormSkeleton,
  ListSkeleton,
  ToastNotification,
  useToast,
  ConfirmDialog,
  useConfirmDialog,
  StandaloneConfirmDialog,
} from '../components/common';
import type { DataTableColumn } from '../components/common';

export const CommonComponentsDemo: React.FC = () => {
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    age: 0,
    country: '',
    interests: [],
    bio: '',
    birthdate: null,
    newsletter: false,
    gender: '',
  });

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [showSimpleModal, setShowSimpleModal] = useState(false);

  // Loading state
  const [loading, setLoading] = useState(false);
  const [showSkeleton, setShowSkeleton] = useState(false);

  // Standalone confirm dialog state
  const [showStandaloneConfirm, setShowStandaloneConfirm] = useState(false);

  // Toast and Confirm hooks
  const { toast, showSuccess, showError, showWarn, showInfo } = useToast();
  const { confirmDialog, confirm, confirmDelete, confirmSave, confirmDiscard } = useConfirmDialog();

  // Sample data for table
  const [tableData] = useState([
    { id: 1, name: 'John Doe', email: 'john@example.com', role: 'Admin', status: 'Active' },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'User', status: 'Active' },
    { id: 3, name: 'Bob Johnson', email: 'bob@example.com', role: 'User', status: 'Inactive' },
    { id: 4, name: 'Alice Brown', email: 'alice@example.com', role: 'Manager', status: 'Active' },
    { id: 5, name: 'Charlie Wilson', email: 'charlie@example.com', role: 'User', status: 'Active' },
  ]);

  const columns: DataTableColumn[] = [
    { field: 'id', header: 'ID', sortable: true, filterable: true },
    { field: 'name', header: 'Name', sortable: true, filterable: true },
    { field: 'email', header: 'Email', sortable: true, filterable: true },
    { field: 'role', header: 'Role', sortable: true, filterable: true },
    {
      field: 'status',
      header: 'Status',
      sortable: true,
      filterable: true,
      body: (rowData) => (
        <span
          className={`px-2 py-1 rounded ${
            rowData.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
          }`}
        >
          {rowData.status}
        </span>
      ),
    },
  ];

  const countryOptions = [
    { label: 'Germany', value: 'de' },
    { label: 'Austria', value: 'at' },
    { label: 'Switzerland', value: 'ch' },
    { label: 'United States', value: 'us' },
  ];

  const interestOptions = [
    { label: 'Solar Energy', value: 'solar' },
    { label: 'Heat Pumps', value: 'heatpump' },
    { label: 'Energy Storage', value: 'storage' },
    { label: 'Smart Home', value: 'smarthome' },
  ];

  const handleFormChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const simulateLoading = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      showSuccess('Success!', 'Operation completed successfully');
    }, 2000);
  };

  const toggleSkeleton = () => {
    setShowSkeleton(!showSkeleton);
  };

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-4">Common UI Components Demo</h1>

      {/* Toast Notification */}
      <ToastNotification ref={toast} />

      {/* Confirm Dialog */}
      <ConfirmDialog ref={confirmDialog} />

      {/* Standalone Confirm Dialog */}
      <StandaloneConfirmDialog
        visible={showStandaloneConfirm}
        onHide={() => setShowStandaloneConfirm(false)}
        message="This is a standalone confirmation dialog. Do you want to proceed?"
        header="Standalone Confirmation"
        onConfirm={() => showSuccess('Confirmed!', 'You clicked confirm')}
        onCancel={() => showInfo('Cancelled', 'You clicked cancel')}
      />

      {/* Form Inputs Section */}
      <Card title="Form Input Components" className="mb-4">
        <div className="grid">
          <div className="col-12 md:col-6">
            <FormInput
              name="name"
              label="Name"
              type="text"
              value={formData.name}
              onChange={(value) => handleFormChange('name', value)}
              placeholder="Enter your name"
              required
            />
          </div>

          <div className="col-12 md:col-6">
            <FormInput
              name="email"
              label="Email"
              type="email"
              value={formData.email}
              onChange={(value) => handleFormChange('email', value)}
              placeholder="Enter your email"
              required
            />
          </div>

          <div className="col-12 md:col-6">
            <FormInput
              name="age"
              label="Age"
              type="number"
              value={formData.age}
              onChange={(value) => handleFormChange('age', value)}
              min={0}
              max={120}
            />
          </div>

          <div className="col-12 md:col-6">
            <FormInput
              name="country"
              label="Country"
              type="select"
              value={formData.country}
              onChange={(value) => handleFormChange('country', value)}
              options={countryOptions}
              placeholder="Select a country"
            />
          </div>

          <div className="col-12">
            <FormInput
              name="interests"
              label="Interests"
              type="multiselect"
              value={formData.interests}
              onChange={(value) => handleFormChange('interests', value)}
              options={interestOptions}
              placeholder="Select your interests"
            />
          </div>

          <div className="col-12">
            <FormInput
              name="bio"
              label="Bio"
              type="textarea"
              value={formData.bio}
              onChange={(value) => handleFormChange('bio', value)}
              placeholder="Tell us about yourself"
              rows={4}
            />
          </div>

          <div className="col-12 md:col-6">
            <FormInput
              name="birthdate"
              label="Birth Date"
              type="date"
              value={formData.birthdate}
              onChange={(value) => handleFormChange('birthdate', value)}
            />
          </div>

          <div className="col-12 md:col-6">
            <FormInput
              name="newsletter"
              label="Subscribe to newsletter"
              type="checkbox"
              value={formData.newsletter}
              onChange={(value) => handleFormChange('newsletter', value)}
            />
          </div>

          <div className="col-12">
            <FormInput
              name="gender"
              label="Gender"
              type="radio"
              value={formData.gender}
              onChange={(value) => handleFormChange('gender', value)}
              options={[
                { label: 'Male', value: 'male' },
                { label: 'Female', value: 'female' },
                { label: 'Other', value: 'other' },
              ]}
            />
          </div>
        </div>
      </Card>

      {/* Data Table Section */}
      <Card title="Data Table Component" className="mb-4">
        <DataTable
          data={tableData}
          columns={columns}
          paginator
          rows={5}
          globalFilterFields={['name', 'email', 'role']}
          stripedRows
        />
      </Card>

      {/* Modal Section */}
      <Card title="Modal Components" className="mb-4">
        <div className="flex gap-2 flex-wrap">
          <Button label="Open Modal" icon="pi pi-external-link" onClick={() => setShowModal(true)} />
          <Button
            label="Open Simple Modal"
            icon="pi pi-external-link"
            onClick={() => setShowSimpleModal(true)}
            severity="secondary"
          />
        </div>

        <Modal visible={showModal} onHide={() => setShowModal(false)} title="Custom Modal" width="600px">
          <p>This is a custom modal with full control over content and footer.</p>
          <p>You can add any content here.</p>
        </Modal>

        <SimpleModal
          visible={showSimpleModal}
          onHide={() => setShowSimpleModal(false)}
          title="Simple Modal"
          onConfirm={() => {
            showSuccess('Confirmed!', 'You clicked OK');
            setShowSimpleModal(false);
          }}
          confirmLabel="OK"
          cancelLabel="Cancel"
        >
          <p>This is a simple modal with predefined OK/Cancel buttons.</p>
        </SimpleModal>
      </Card>

      {/* Loading Section */}
      <Card title="Loading Components" className="mb-4">
        <div className="flex gap-2 flex-wrap mb-4">
          <Button label="Simulate Loading" icon="pi pi-spin pi-spinner" onClick={simulateLoading} />
          <Button
            label={showSkeleton ? 'Hide Skeleton' : 'Show Skeleton'}
            icon="pi pi-eye"
            onClick={toggleSkeleton}
            severity="secondary"
          />
        </div>

        {loading && <LoadingSpinner message="Loading data..." />}

        <Divider />

        <h3>Inline Spinner</h3>
        <Button label="Loading" icon={<InlineSpinner />} disabled />

        <Divider />

        <h3>Skeleton Loaders</h3>
        {showSkeleton ? (
          <div className="grid">
            <div className="col-12 md:col-6">
              <h4>Card Skeleton</h4>
              <CardSkeleton />
            </div>
            <div className="col-12 md:col-6">
              <h4>Form Skeleton</h4>
              <FormSkeleton fields={3} />
            </div>
            <div className="col-12">
              <h4>Table Skeleton</h4>
              <TableSkeleton rows={3} columns={4} />
            </div>
            <div className="col-12">
              <h4>List Skeleton</h4>
              <ListSkeleton items={3} />
            </div>
          </div>
        ) : (
          <p className="text-500">Click "Show Skeleton" to see skeleton loaders</p>
        )}
      </Card>

      {/* Toast Notifications Section */}
      <Card title="Toast Notifications" className="mb-4">
        <div className="flex gap-2 flex-wrap">
          <Button
            label="Success"
            icon="pi pi-check"
            severity="success"
            onClick={() => showSuccess('Success!', 'Operation completed successfully')}
          />
          <Button
            label="Info"
            icon="pi pi-info-circle"
            severity="info"
            onClick={() => showInfo('Information', 'This is an informational message')}
          />
          <Button
            label="Warning"
            icon="pi pi-exclamation-triangle"
            severity="warning"
            onClick={() => showWarn('Warning!', 'Please be careful')}
          />
          <Button
            label="Error"
            icon="pi pi-times-circle"
            severity="danger"
            onClick={() => showError('Error!', 'Something went wrong')}
          />
        </div>
      </Card>

      {/* Confirmation Dialogs Section */}
      <Card title="Confirmation Dialogs" className="mb-4">
        <div className="flex gap-2 flex-wrap">
          <Button
            label="Custom Confirm"
            icon="pi pi-question-circle"
            onClick={() =>
              confirm({
                message: 'Are you sure you want to proceed?',
                header: 'Confirmation',
                onAccept: () => showSuccess('Accepted!', 'You clicked Yes'),
                onReject: () => showInfo('Rejected', 'You clicked No'),
              })
            }
          />
          <Button
            label="Confirm Delete"
            icon="pi pi-trash"
            severity="danger"
            onClick={() =>
              confirmDelete('Test Item', () => showSuccess('Deleted!', 'Item has been deleted'))
            }
          />
          <Button
            label="Confirm Save"
            icon="pi pi-save"
            severity="success"
            onClick={() =>
              confirmSave(
                () => showSuccess('Saved!', 'Changes have been saved'),
                () => showInfo('Cancelled', 'Save cancelled')
              )
            }
          />
          <Button
            label="Confirm Discard"
            icon="pi pi-times"
            severity="warning"
            onClick={() =>
              confirmDiscard(
                () => showWarn('Discarded!', 'Changes have been discarded'),
                () => showInfo('Kept', 'Continuing to edit')
              )
            }
          />
          <Button
            label="Standalone Confirm"
            icon="pi pi-external-link"
            severity="secondary"
            onClick={() => setShowStandaloneConfirm(true)}
          />
        </div>
      </Card>
    </div>
  );
};
