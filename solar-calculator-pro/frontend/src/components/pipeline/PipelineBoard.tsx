/**
 * Pipeline Board Component
 * Drag-and-drop Kanban-style pipeline visualization
 */

import React, { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable, DropResult } from 'react-beautiful-dnd';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { Tag } from 'primereact/tag';
import { Dialog } from 'primereact/dialog';
import { Toast } from 'primereact/toast';
import api from '../../services/api';
import { OpportunityDialog } from './OpportunityDialog';
import './PipelineBoard.css';

interface PipelineStage {
  id: number;
  name: string;
  stage_type: string;
  order_index: number;
  probability: number;
  color: string;
  icon?: string;
  opportunity_count: number;
  total_value: number;
}

interface Opportunity {
  id: number;
  name: string;
  estimated_value: number;
  currency: string;
  probability: number;
  weighted_value: number;
  stage_id: number;
  owner_name?: string;
  contact_name?: string;
  expected_close_date?: string;
  days_in_stage?: number;
}

export const PipelineBoard: React.FC = () => {
  const [stages, setStages] = useState<PipelineStage[]>([]);
  const [opportunities, setOpportunities] = useState<Record<number, Opportunity[]>>({});
  const [loading, setLoading] = useState(true);
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);
  const [showDialog, setShowDialog] = useState(false);
  const [showNewDialog, setShowNewDialog] = useState(false);
  const toast = React.useRef<Toast>(null);

  useEffect(() => {
    loadPipelineData();
  }, []);

  const loadPipelineData = async () => {
    try {
      setLoading(true);
      
      // Load stages
      const stagesResponse = await api.get('/api/v1/pipeline/stages');
      const stagesData = stagesResponse.data.stages;
      setStages(stagesData);
      
      // Load opportunities for each stage
      const oppsData: Record<number, Opportunity[]> = {};
      for (const stage of stagesData) {
        const oppsResponse = await api.get('/api/v1/pipeline/opportunities', {
          params: { stage_id: stage.id, status: 'active' }
        });
        oppsData[stage.id] = oppsResponse.data.opportunities;
      }
      setOpportunities(oppsData);
      
    } catch (error) {
      console.error('Error loading pipeline data:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load pipeline data'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDragEnd = async (result: DropResult) => {
    const { source, destination, draggableId } = result;

    // Dropped outside the list
    if (!destination) {
      return;
    }

    // No movement
    if (source.droppableId === destination.droppableId && source.index === destination.index) {
      return;
    }

    const sourceStageId = parseInt(source.droppableId);
    const destStageId = parseInt(destination.droppableId);
    const opportunityId = parseInt(draggableId);

    // Update local state optimistically
    const sourceOpps = Array.from(opportunities[sourceStageId] || []);
    const destOpps = sourceStageId === destStageId 
      ? sourceOpps 
      : Array.from(opportunities[destStageId] || []);

    const [movedOpp] = sourceOpps.splice(source.index, 1);
    
    if (sourceStageId === destStageId) {
      sourceOpps.splice(destination.index, 0, movedOpp);
      setOpportunities({
        ...opportunities,
        [sourceStageId]: sourceOpps
      });
    } else {
      movedOpp.stage_id = destStageId;
      destOpps.splice(destination.index, 0, movedOpp);
      setOpportunities({
        ...opportunities,
        [sourceStageId]: sourceOpps,
        [destStageId]: destOpps
      });
    }

    // Update on server
    try {
      await api.post(`/api/v1/pipeline/opportunities/${opportunityId}/change-stage`, {
        stage_id: destStageId,
        reason: 'Moved via drag and drop'
      });
      
      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: 'Opportunity moved successfully'
      });
      
      // Reload to get updated data
      loadPipelineData();
      
    } catch (error) {
      console.error('Error moving opportunity:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to move opportunity'
      });
      // Revert optimistic update
      loadPipelineData();
    }
  };

  const formatCurrency = (value: number, currency: string = 'EUR') => {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: currency
    }).format(value);
  };

  const getStageColor = (stageType: string) => {
    const colors: Record<string, string> = {
      lead: 'info',
      qualified: 'primary',
      proposal: 'warning',
      negotiation: 'help',
      closed_won: 'success',
      closed_lost: 'danger'
    };
    return colors[stageType] || 'info';
  };

  const handleOpportunityClick = (opportunity: Opportunity) => {
    setSelectedOpportunity(opportunity);
    setShowDialog(true);
  };

  const handleOpportunitySaved = () => {
    setShowDialog(false);
    setShowNewDialog(false);
    loadPipelineData();
  };

  if (loading) {
    return <div className="pipeline-loading">Loading pipeline...</div>;
  }

  return (
    <div className="pipeline-board">
      <Toast ref={toast} />
      
      <div className="pipeline-header">
        <h2>Sales Pipeline</h2>
        <Button
          label="New Opportunity"
          icon="pi pi-plus"
          onClick={() => setShowNewDialog(true)}
        />
      </div>

      <DragDropContext onDragEnd={handleDragEnd}>
        <div className="pipeline-stages">
          {stages.map((stage) => (
            <div key={stage.id} className="pipeline-stage">
              <div className="stage-header" style={{ borderTopColor: stage.color }}>
                <div className="stage-title">
                  {stage.icon && <i className={stage.icon} />}
                  <span>{stage.name}</span>
                  <Tag value={opportunities[stage.id]?.length || 0} />
                </div>
                <div className="stage-stats">
                  <span className="stage-value">
                    {formatCurrency(stage.total_value)}
                  </span>
                  <span className="stage-probability">
                    {stage.probability}% win rate
                  </span>
                </div>
              </div>

              <Droppable droppableId={stage.id.toString()}>
                {(provided, snapshot) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    className={`stage-opportunities ${snapshot.isDraggingOver ? 'dragging-over' : ''}`}
                  >
                    {(opportunities[stage.id] || []).map((opp, index) => (
                      <Draggable
                        key={opp.id}
                        draggableId={opp.id.toString()}
                        index={index}
                      >
                        {(provided, snapshot) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            className={`opportunity-card ${snapshot.isDragging ? 'dragging' : ''}`}
                            onClick={() => handleOpportunityClick(opp)}
                          >
                            <div className="opp-header">
                              <h4>{opp.name}</h4>
                              <Tag
                                value={`${opp.probability}%`}
                                severity={getStageColor(stage.stage_type)}
                              />
                            </div>
                            
                            <div className="opp-value">
                              {formatCurrency(opp.estimated_value, opp.currency)}
                            </div>
                            
                            {opp.contact_name && (
                              <div className="opp-contact">
                                <i className="pi pi-user" />
                                <span>{opp.contact_name}</span>
                              </div>
                            )}
                            
                            {opp.owner_name && (
                              <div className="opp-owner">
                                <i className="pi pi-briefcase" />
                                <span>{opp.owner_name}</span>
                              </div>
                            )}
                            
                            {opp.expected_close_date && (
                              <div className="opp-date">
                                <i className="pi pi-calendar" />
                                <span>
                                  {new Date(opp.expected_close_date).toLocaleDateString('de-DE')}
                                </span>
                              </div>
                            )}
                            
                            {opp.days_in_stage !== undefined && (
                              <div className="opp-days">
                                <i className="pi pi-clock" />
                                <span>{opp.days_in_stage} days in stage</span>
                              </div>
                            )}
                          </div>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                    
                    {(opportunities[stage.id] || []).length === 0 && (
                      <div className="stage-empty">
                        No opportunities in this stage
                      </div>
                    )}
                  </div>
                )}
              </Droppable>
            </div>
          ))}
        </div>
      </DragDropContext>

      {/* Opportunity Detail Dialog */}
      {selectedOpportunity && (
        <OpportunityDialog
          visible={showDialog}
          opportunity={selectedOpportunity}
          onHide={() => setShowDialog(false)}
          onSave={handleOpportunitySaved}
        />
      )}

      {/* New Opportunity Dialog */}
      <OpportunityDialog
        visible={showNewDialog}
        onHide={() => setShowNewDialog(false)}
        onSave={handleOpportunitySaved}
      />
    </div>
  );
};
