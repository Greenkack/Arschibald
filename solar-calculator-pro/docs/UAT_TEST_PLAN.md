# User Acceptance Testing (UAT) Test Plan
# Solar Calculator Pro

## Document Information
- **Version**: 1.0
- **Date**: November 29, 2025
- **Author**: Development Team
- **Status**: Active

## 1. Introduction

### 1.1 Purpose
This document outlines the User Acceptance Testing (UAT) plan for the Solar Calculator Pro application. UAT ensures that the application meets business requirements and is ready for production deployment.

### 1.2 Scope
UAT covers all major user workflows including:
- Solar calculation workflows
- Heat pump calculation workflows
- CRM functionality
- PDF generation
- Admin panel features
- 3D visualization
- Reporting and analytics

### 1.3 Objectives
- Validate that all business requirements are met
- Ensure user workflows function correctly
- Verify data accuracy and integrity
- Confirm usability and user experience
- Identify any remaining issues before production

## 2. Test Environment

### 2.1 Hardware Requirements
- Windows 10/11, macOS 10.15+, or Linux
- Minimum 8GB RAM
- 500MB free disk space
- Display resolution: 1920x1080 or higher

### 2.2 Software Requirements
- Node.js 18+
- Python 3.10+
- Modern web browser (Chrome, Firefox, Edge)
- Electron application installed

### 2.3 Test Data
- Sample customer data
- Sample product database
- Test price matrices
- Sample PDF templates

## 3. Test Cases

### 3.1 Solar Calculator Workflows

#### UAT-001: Complete Solar Calculation
**Priority**: Critical
**Preconditions**: User is logged in

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to Solar Calculator | Calculator page loads |
| 2 | Enter customer data | Data is saved |
| 3 | Configure roof parameters | Parameters are validated |
| 4 | Select PV modules | Modules are displayed |
| 5 | Enter consumption data | Data is validated |
| 6 | Click Calculate | Results are displayed |
| 7 | Verify annual yield | Value matches expected range |
| 8 | Verify savings calculation | Savings are calculated correctly |

#### UAT-002: Quick Calculation
**Priority**: High
**Preconditions**: User is logged in

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to Quick Calculation | Quick calc page loads |
| 2 | Enter annual consumption | Value is accepted |
| 3 | Enter roof area | Value is accepted |
| 4 | Select location | Location is set |
| 5 | Click Estimate | Estimate is displayed |

#### UAT-003: Module Selection
**Priority**: High
**Preconditions**: Solar calculation in progress

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open module selector | Module list loads |
| 2 | Filter by manufacturer | List is filtered |
| 3 | Sort by power | List is sorted |
| 4 | Select module | Module is selected |
| 5 | Verify module details | Details are displayed |

### 3.2 Heat Pump Workflows

#### UAT-004: Heat Pump Calculation
**Priority**: High
**Preconditions**: User is logged in

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to Heat Pump Calculator | Calculator loads |
| 2 | Enter building data | Data is validated |
| 3 | Select building type | Type is set |
| 4 | Enter heating consumption | Value is accepted |
| 5 | Click Analyze | Analysis is displayed |
| 6 | Verify heat load | Value is calculated |

#### UAT-005: Heat Pump Model Selection
**Priority**: Medium
**Preconditions**: Building analysis complete

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | View recommended models | Models are displayed |
| 2 | Compare models | Comparison is shown |
| 3 | Select model | Model is selected |
| 4 | View specifications | Specs are displayed |

### 3.3 CRM Workflows

#### UAT-006: Customer Management
**Priority**: Critical
**Preconditions**: User is logged in

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to Customers | Customer list loads |
| 2 | Click Add Customer | Form opens |
| 3 | Enter customer data | Data is validated |
| 4 | Save customer | Customer is created |
| 5 | Search for customer | Customer is found |
| 6 | Edit customer | Changes are saved |
| 7 | Delete customer | Customer is removed |

#### UAT-007: Offer Tracking
**Priority**: High
**Preconditions**: Customer exists

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to Offers | Offer list loads |
| 2 | Create new offer | Offer form opens |
| 3 | Link to customer | Customer is linked |
| 4 | Add products | Products are added |
| 5 | Save offer | Offer is created |
| 6 | Update status | Status is changed |
| 7 | View offer history | History is displayed |

#### UAT-008: Task Management
**Priority**: Medium
**Preconditions**: User is logged in

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to Tasks | Task list loads |
| 2 | Create task | Task form opens |
| 3 | Set due date | Date is set |
| 4 | Assign priority | Priority is set |
| 5 | Save task | Task is created |
| 6 | Mark complete | Task is completed |

### 3.4 PDF Generation Workflows

#### UAT-009: Standard Offer PDF
**Priority**: Critical
**Preconditions**: Calculation complete

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click Generate PDF | PDF dialog opens |
| 2 | Select template | Template is selected |
| 3 | Configure options | Options are set |
| 4 | Click Generate | PDF is generated |
| 5 | Preview PDF | PDF is displayed |
| 6 | Download PDF | PDF is downloaded |

#### UAT-010: Extended Offer PDF
**Priority**: High
**Preconditions**: Calculation complete

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Select Extended template | Template is selected |
| 2 | Enable technical details | Option is enabled |
| 3 | Enable financial analysis | Option is enabled |
| 4 | Generate PDF | PDF is generated |
| 5 | Verify all sections | All sections present |

### 3.5 Admin Workflows

#### UAT-011: Product Management
**Priority**: High
**Preconditions**: Admin user logged in

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to Products | Product list loads |
| 2 | Add product | Product form opens |
| 3 | Enter product data | Data is validated |
| 4 | Upload image | Image is uploaded |
| 5 | Save product | Product is created |
| 6 | Edit product | Changes are saved |
| 7 | Delete product | Product is removed |

#### UAT-012: Price Matrix Management
**Priority**: High
**Preconditions**: Admin user logged in

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to Price Matrix | Matrix list loads |
| 2 | Upload new matrix | Upload dialog opens |
| 3 | Select Excel file | File is selected |
| 4 | Validate matrix | Validation runs |
| 5 | Activate matrix | Matrix is active |
| 6 | Test price lookup | Prices are correct |

#### UAT-013: User Management
**Priority**: Medium
**Preconditions**: Admin user logged in

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to Users | User list loads |
| 2 | Add user | User form opens |
| 3 | Set role | Role is assigned |
| 4 | Save user | User is created |
| 5 | Edit permissions | Permissions updated |
| 6 | Deactivate user | User is deactivated |

### 3.6 3D Visualization Workflows

#### UAT-014: 3D Roof Visualization
**Priority**: High
**Preconditions**: Roof data entered

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open 3D view | 3D viewer loads |
| 2 | Rotate view | View rotates |
| 3 | Zoom in/out | Zoom works |
| 4 | Pan view | Pan works |
| 5 | Reset view | View resets |

#### UAT-015: Module Placement
**Priority**: Medium
**Preconditions**: 3D view open

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Enable module placement | Mode is enabled |
| 2 | Place modules | Modules appear |
| 3 | Adjust placement | Modules move |
| 4 | Check collision | Collision detected |
| 5 | Export view | View is exported |

### 3.7 Reporting Workflows

#### UAT-016: Results Dashboard
**Priority**: High
**Preconditions**: Calculation complete

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | View dashboard | Dashboard loads |
| 2 | Check key metrics | Metrics displayed |
| 3 | View charts | Charts render |
| 4 | Export data | Data is exported |

#### UAT-017: Financial Charts
**Priority**: High
**Preconditions**: Calculation complete

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | View break-even chart | Chart displays |
| 2 | View cashflow chart | Chart displays |
| 3 | Adjust parameters | Charts update |
| 4 | Export chart | Chart is exported |

### 3.8 Integration Workflows

#### UAT-018: Combined PV + Heat Pump
**Priority**: Medium
**Preconditions**: Both calculations complete

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Enable combined mode | Mode is enabled |
| 2 | View synergy analysis | Analysis displays |
| 3 | Compare scenarios | Comparison shown |
| 4 | Generate combined PDF | PDF is generated |

#### UAT-019: Scenario Comparison
**Priority**: Medium
**Preconditions**: Multiple scenarios created

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Select scenarios | Scenarios selected |
| 2 | View comparison | Comparison displays |
| 3 | Highlight differences | Differences shown |
| 4 | Export comparison | Export works |

## 4. Test Execution

### 4.1 Test Schedule
| Phase | Duration | Activities |
|-------|----------|------------|
| Preparation | 2 days | Environment setup, data preparation |
| Execution | 5 days | Test case execution |
| Defect Resolution | 3 days | Bug fixes and retesting |
| Sign-off | 1 day | Final review and approval |

### 4.2 Test Team
| Role | Responsibility |
|------|----------------|
| UAT Lead | Overall coordination |
| Business Analyst | Requirements validation |
| End Users | Test execution |
| Developer | Defect resolution |

### 4.3 Entry Criteria
- All development complete
- Unit and integration tests passed
- Test environment ready
- Test data prepared
- UAT team trained

### 4.4 Exit Criteria
- All critical test cases passed
- No critical or high severity defects open
- Business stakeholder sign-off obtained
- Documentation complete

## 5. Defect Management

### 5.1 Severity Levels
| Level | Description | Resolution Time |
|-------|-------------|-----------------|
| Critical | System unusable | Immediate |
| High | Major feature broken | 24 hours |
| Medium | Feature partially working | 3 days |
| Low | Minor issue | Next release |

### 5.2 Defect Workflow
1. Defect identified during testing
2. Defect logged with details
3. Developer assigned
4. Fix implemented
5. Retest performed
6. Defect closed

## 6. Sign-off

### 6.1 Approval Criteria
- All critical and high priority test cases passed
- No open critical or high severity defects
- Performance meets requirements
- Security requirements met

### 6.2 Sign-off Form

| Role | Name | Signature | Date |
|------|------|-----------|------|
| UAT Lead | | | |
| Business Owner | | | |
| IT Manager | | | |
| Quality Assurance | | | |

## 7. Appendices

### A. Test Data Requirements
- 50 sample customers
- 100 sample products
- 5 price matrices
- 10 PDF templates

### B. Environment Configuration
- API URL: http://localhost:8000
- Frontend URL: http://localhost:3000
- Database: SQLite/PostgreSQL

### C. Contact Information
- UAT Lead: [Contact]
- Technical Support: [Contact]
- Business Owner: [Contact]
