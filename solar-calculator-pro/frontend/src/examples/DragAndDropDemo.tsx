/**
 * Drag and Drop Demo
 * Demonstrates all drag and drop functionality
 */

import React, { useState } from 'react';
import {
  FileDropZone,
  DraggableList,
  DraggableCard,
  DropZone,
  DashboardCustomizer,
  DashboardWidget,
  DashboardLayout,
} from '../components/dragdrop';
import { Card } from 'primereact/card';
import { TabView, TabPanel } from 'primereact/tabview';
import { Message } from 'primereact/message';
import './DragAndDropDemo.css';

// Sample widgets for dashboard customization
const SampleWidget: React.FC<{ title: string }> = ({ title }) => (
  <div className="sample-widget">
    <p>This is a sample widget: {title}</p>
  </div>
);

const availableWidgets: DashboardWidget[] = [
  {
    id: 'widget-1',
    type: 'widget',
    title: 'Statistics',
    component: SampleWidget,
    props: { title: 'Statistics' },
    size: 'medium',
  },
  {
    id: 'widget-2',
    type: 'widget',
    title: 'Recent Projects',
    component: SampleWidget,
    props: { title: 'Recent Projects' },
    size: 'large',
  },
  {
    id: 'widget-3',
    type: 'widget',
    title: 'Quick Actions',
    component: SampleWidget,
    props: { title: 'Quick Actions' },
    size: 'small',
  },
  {
    id: 'widget-4',
    type: 'widget',
    title: 'Activity Feed',
    component: SampleWidget,
    props: { title: 'Activity Feed' },
    size: 'medium',
  },
];

const initialDashboardLayout: DashboardLayout = {
  zones: {
    main: [availableWidgets[0], availableWidgets[1]],
    sidebar: [availableWidgets[2]],
  },
};

export const DragAndDropDemo: React.FC = () => {
  // File drop state
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);

  // List reorder state
  const [listItems, setListItems] = useState([
    { id: '1', name: 'Item 1', description: 'First item' },
    { id: '2', name: 'Item 2', description: 'Second item' },
    { id: '3', name: 'Item 3', description: 'Third item' },
    { id: '4', name: 'Item 4', description: 'Fourth item' },
  ]);

  // Card drag state
  const [zone1Items, setZone1Items] = useState([
    { id: 'card-1', title: 'Card 1', content: 'Content 1' },
    { id: 'card-2', title: 'Card 2', content: 'Content 2' },
  ]);
  const [zone2Items, setZone2Items] = useState([
    { id: 'card-3', title: 'Card 3', content: 'Content 3' },
  ]);

  // Dashboard layout state
  const [dashboardLayout, setDashboardLayout] = useState(initialDashboardLayout);

  const handleFileDrop = (files: File[]) => {
    setUploadedFiles((prev) => [...prev, ...files]);
  };

  const handleListReorder = (items: typeof listItems) => {
    setListItems(items);
  };

  const handleCardDrop = (zoneId: string) => (item: any) => {
    if (zoneId === 'zone1') {
      // Remove from zone2
      setZone2Items((prev) => prev.filter((i) => i.id !== item.id));
      // Add to zone1 if not already there
      if (!zone1Items.find((i) => i.id === item.id)) {
        setZone1Items((prev) => [...prev, item.data]);
      }
    } else {
      // Remove from zone1
      setZone1Items((prev) => prev.filter((i) => i.id !== item.id));
      // Add to zone2 if not already there
      if (!zone2Items.find((i) => i.id === item.id)) {
        setZone2Items((prev) => [...prev, item.data]);
      }
    }
  };

  return (
    <div className="drag-drop-demo">
      <h1>Drag and Drop Demo</h1>
      <Message
        severity="info"
        text="This demo showcases all drag and drop functionality including file uploads, list reordering, component dragging, and dashboard customization."
      />

      <TabView>
        <TabPanel header="File Upload">
          <Card title="File Drag and Drop">
            <FileDropZone
              onFileDrop={handleFileDrop}
              accept={['.pdf', '.jpg', '.png', 'image/*']}
              maxSize={5 * 1024 * 1024} // 5MB
              maxFiles={5}
            />

            {uploadedFiles.length > 0 && (
              <div className="uploaded-files">
                <h3>Uploaded Files:</h3>
                <ul>
                  {uploadedFiles.map((file, index) => (
                    <li key={index}>
                      {file.name} ({(file.size / 1024).toFixed(2)} KB)
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </Card>
        </TabPanel>

        <TabPanel header="List Reordering">
          <Card title="Draggable List">
            <p>Drag items to reorder the list:</p>
            <DraggableList
              items={listItems}
              onReorder={handleListReorder}
              getId={(item) => item.id}
              renderItem={(item) => (
                <div>
                  <strong>{item.name}</strong>
                  <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem' }}>
                    {item.description}
                  </p>
                </div>
              )}
            />
          </Card>
        </TabPanel>

        <TabPanel header="Component Dragging">
          <Card title="Drag Cards Between Zones">
            <div className="card-zones">
              <div className="card-zone">
                <h3>Zone 1</h3>
                <DropZone
                  id="zone1"
                  accepts={['card']}
                  onDrop={handleCardDrop('zone1')}
                >
                  <div className="card-grid">
                    {zone1Items.map((item) => (
                      <DraggableCard
                        key={item.id}
                        id={item.id}
                        type="card"
                        data={item}
                      >
                        <Card title={item.title}>
                          <p>{item.content}</p>
                        </Card>
                      </DraggableCard>
                    ))}
                  </div>
                </DropZone>
              </div>

              <div className="card-zone">
                <h3>Zone 2</h3>
                <DropZone
                  id="zone2"
                  accepts={['card']}
                  onDrop={handleCardDrop('zone2')}
                >
                  <div className="card-grid">
                    {zone2Items.map((item) => (
                      <DraggableCard
                        key={item.id}
                        id={item.id}
                        type="card"
                        data={item}
                      >
                        <Card title={item.title}>
                          <p>{item.content}</p>
                        </Card>
                      </DraggableCard>
                    ))}
                  </div>
                </DropZone>
              </div>
            </div>
          </Card>
        </TabPanel>

        <TabPanel header="Dashboard Customization">
          <DashboardCustomizer
            availableWidgets={availableWidgets}
            initialLayout={initialDashboardLayout}
            onLayoutChange={setDashboardLayout}
            zones={['main', 'sidebar']}
          />
        </TabPanel>
      </TabView>
    </div>
  );
};
