# User Acceptance Testing (UAT) Plan

## Task 242: User Acceptance Testing Preparation

## 1. Overview

This document outlines the User Acceptance Testing plan for the Streamlit to Electron migration project.

### 1.1 Objectives
- Verify all functionality from Streamlit app is preserved
- Ensure user experience meets expectations
- Validate performance improvements
- Confirm German formatting works correctly
- Test all critical workflows

### 1.2 Scope
- Solar Calculator functionality
- Heat Pump Calculator functionality
- Price Matrix operations
- PDF Generation
- 3D Visualization
- CRM System
- Product Management
- Admin Panel

## 2. UAT Environment

### 2.1 Hardware Requirements
- Windows 10/11 PC
- Minimum 8GB RAM
- 500MB free disk space
- 1920x1080 display resolution

### 2.2 Software Requirements
- Electron application (latest build)
- Test database with sample data
- PDF viewer
- 3D model viewer (optional)

### 2.3 Test Data
- 10 sample customers
- 5 sample solar projects
- 3 sample heat pump projects
- 2 price matrices
- Sample product catalog

## 3. Test Scenarios

### 3.1 Solar Calculator Workflow

| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|
| SC-01 | Create new solar project | 1. Open Solar Calculator<br>2. Enter roof parameters<br>3. Select modules<br>4. Calculate | System displays calculation results |
| SC-02 | View 3D visualization | 1. Complete calculation<br>2. Click 3D view | 3D model renders with modules |
| SC-03 | Generate PDF offer | 1. Complete calculation<br>2. Click Generate PDF<br>3. Select template | PDF downloads successfully |
| SC-04 | Save project | 1. Complete calculation<br>2. Click Save<br>3. Enter project name | Project saved and appears in list |

### 3.2 Heat Pump Calculator Workflow

| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|
| HP-01 | Calculate heat pump sizing | 1. Open Heat Pump Calculator<br>2. Enter building data<br>3. Calculate | Sizing recommendations displayed |
| HP-02 | Compare heat pump models | 1. Complete calculation<br>2. View comparison | Model comparison table shown |
| HP-03 | Combined solar + heat pump | 1. Create solar project<br>2. Add heat pump<br>3. Calculate combined | Combined savings displayed |

### 3.3 Price Matrix Workflow

| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|
| PM-01 | Upload price matrix | 1. Open Admin Panel<br>2. Upload Excel file<br>3. Validate | Matrix uploaded successfully |
| PM-02 | Price lookup | 1. Select module count<br>2. Select storage<br>3. View price | Correct price displayed |
| PM-03 | German number formatting | 1. Enter price values<br>2. View display | Numbers show German format (1.234,56 €) |

### 3.4 CRM Workflow

| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|
| CRM-01 | Create customer | 1. Open CRM<br>2. Click New Customer<br>3. Enter details<br>4. Save | Customer created |
| CRM-02 | Create offer | 1. Select customer<br>2. Create offer<br>3. Add products | Offer created with correct pricing |
| CRM-03 | Track offer status | 1. Open offer<br>2. Change status | Status updated, history logged |

### 3.5 Admin Workflow

| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|
| ADM-01 | User management | 1. Open Admin<br>2. Create user<br>3. Assign role | User created with correct permissions |
| ADM-02 | System settings | 1. Open Settings<br>2. Change company info<br>3. Save | Settings saved and applied |
| ADM-03 | Database backup | 1. Open Database<br>2. Create backup | Backup file created |

## 4. Test Cases

### 4.1 Functional Test Cases

#### TC-001: Login Authentication
- **Precondition:** Application is running
- **Steps:**
  1. Enter valid email
  2. Enter valid password
  3. Click Login
- **Expected:** User logged in, dashboard displayed
- **Priority:** Critical

#### TC-002: Solar Calculation Accuracy
- **Precondition:** User logged in
- **Steps:**
  1. Enter roof area: 50 m²
  2. Enter roof angle: 30°
  3. Select orientation: South
  4. Enter consumption: 4000 kWh
  5. Click Calculate
- **Expected:** Results match Streamlit version (±1%)
- **Priority:** Critical

#### TC-003: German Number Input
- **Precondition:** User logged in
- **Steps:**
  1. Open any number input field
  2. Enter "1234,56"
  3. Tab out of field
- **Expected:** Value displayed as "1.234,56"
- **Priority:** High

#### TC-004: PDF Generation
- **Precondition:** Solar calculation completed
- **Steps:**
  1. Click Generate PDF
  2. Select Standard template
  3. Click Generate
- **Expected:** PDF downloads with correct data
- **Priority:** Critical

#### TC-005: 3D Model Export
- **Precondition:** 3D visualization displayed
- **Steps:**
  1. Click Export
  2. Select STL format
  3. Click Download
- **Expected:** STL file downloads
- **Priority:** Medium

## 5. UAT Feedback Form

### Test Session Information
- **Tester Name:** _______________
- **Date:** _______________
- **Build Version:** _______________

### Test Results

| Test ID | Pass/Fail | Comments |
|---------|-----------|----------|
| SC-01 | | |
| SC-02 | | |
| SC-03 | | |
| SC-04 | | |
| HP-01 | | |
| HP-02 | | |
| HP-03 | | |
| PM-01 | | |
| PM-02 | | |
| PM-03 | | |
| CRM-01 | | |
| CRM-02 | | |
| CRM-03 | | |
| ADM-01 | | |
| ADM-02 | | |
| ADM-03 | | |

### Overall Assessment
- [ ] All critical features work correctly
- [ ] Performance is acceptable
- [ ] UI is intuitive and user-friendly
- [ ] German formatting is correct throughout
- [ ] No critical bugs found

### Issues Found

| Issue # | Severity | Description | Steps to Reproduce |
|---------|----------|-------------|-------------------|
| | | | |
| | | | |
| | | | |

### Suggestions for Improvement
_____________________________________
_____________________________________
_____________________________________

### Sign-off
- **Tester Signature:** _______________
- **Date:** _______________

## 6. UAT Training Materials

### 6.1 Quick Start Guide
1. Launch the application
2. Login with provided credentials
3. Navigate using the sidebar menu
4. Use keyboard shortcuts for efficiency

### 6.2 Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| Ctrl+N | New Project |
| Ctrl+S | Save |
| Ctrl+P | Generate PDF |
| Ctrl+Z | Undo |
| F1 | Help |

### 6.3 Common Tasks
- Creating a solar project
- Generating an offer PDF
- Managing customers
- Uploading price matrices

## 7. Issue Tracking

### 7.1 Severity Levels
- **Critical:** Application crash, data loss, security issue
- **High:** Major feature not working
- **Medium:** Feature works but with issues
- **Low:** Minor UI issues, cosmetic problems

### 7.2 Issue Template
```
Issue ID: UAT-XXX
Severity: [Critical/High/Medium/Low]
Summary: [Brief description]
Steps to Reproduce:
1. 
2. 
3. 
Expected Result: 
Actual Result: 
Screenshots: [Attach if applicable]
```

## 8. Success Criteria

UAT is considered successful when:
- [ ] All critical test cases pass
- [ ] No critical or high severity issues remain open
- [ ] Performance meets targets (startup <3s, navigation <100ms)
- [ ] At least 80% of testers approve the application
- [ ] All German formatting displays correctly

## 9. Schedule

| Phase | Duration | Activities |
|-------|----------|------------|
| Preparation | 2 days | Environment setup, test data |
| Training | 1 day | Tester training session |
| Execution | 5 days | Test execution |
| Bug Fixes | 3 days | Fix identified issues |
| Retest | 2 days | Verify fixes |
| Sign-off | 1 day | Final approval |

## 10. Contacts

| Role | Name | Email |
|------|------|-------|
| UAT Lead | TBD | |
| Development Lead | TBD | |
| Support | TBD | |
