# Phase 1 - Task 2.2: Visual Inspection Guide

## Overview

This guide provides step-by-step instructions for visually inspecting the 3D PV module placement on all roof types to verify that the critical bugfix is working correctly.

**Date:** January 3, 2026  
**Status:** Ready for Testing  
**Priority:** CRITICAL

## What to Verify

The visual inspection should confirm that:
1. ✅ Modules on **flat roofs** are elevated at 0.30m (Aufständerung)
2. ✅ Modules on **pitched roofs** follow the roof surface geometry
3. ✅ Modules do NOT float above or sink below the roof surface
4. ✅ Z-position varies correctly based on Y-position for pitched roofs

## Test Scenarios

### Scenario 1: Flachdach (Flat Roof)

**Expected Behavior:**
- All modules at constant height (0.30m above roof base)
- Modules tilted at 30° for optimal solar exposure
- Modules appear "elevated" on mounting frames

**Test Steps:**
1. Open the 3D visualization in the app
2. Select **Flachdach** as roof type
3. Set roof dimensions: Length=12m, Width=10m
4. Place 20 modules automatically
5. Rotate the 3D view to see from the side

**Visual Checks:**
- [ ] All modules are at the same height
- [ ] Modules are elevated above the flat roof surface
- [ ] Gap between roof and modules is consistent (~30cm)
- [ ] Modules are tilted at 30° angle
- [ ] No modules touching the roof surface

**Screenshot Location:** `tests/visual_inspection/flachdach_side_view.png`

---

### Scenario 2: Satteldach (Gable Roof) - 35° Pitch

**Expected Behavior:**
- Modules follow the angled roof surface
- Z-position increases from eave (bottom) to ridge (top)
- Modules appear to "sit" on the roof, not float

**Test Steps:**
1. Select **Satteldach** as roof type
2. Set roof pitch: **35°**
3. Set roof dimensions: Length=12m, Width=10m
4. Place 20 modules automatically
5. Rotate view to see from the side (perpendicular to ridge)

**Visual Checks:**
- [ ] Modules follow the roof slope (not horizontal)
- [ ] Lower modules (near eave) are at lower Z-position
- [ ] Upper modules (near ridge) are at higher Z-position
- [ ] Modules are ON the blue angled roof surface (not on red base)
- [ ] No gaps between modules and roof surface
- [ ] No modules floating above roof
- [ ] No modules sinking below roof

**Critical View:** Side view showing the roof slope and module placement

**Screenshot Location:** `tests/visual_inspection/satteldach_35deg_side_view.png`

---

### Scenario 3: Pultdach (Shed Roof) - 25° Pitch

**Expected Behavior:**
- Modules follow single-slope roof surface
- Z-position increases linearly from front to back
- Smooth linear progression of module heights

**Test Steps:**
1. Select **Pultdach** as roof type
2. Set roof pitch: **25°**
3. Set roof dimensions: Length=12m, Width=10m
4. Place 20 modules automatically
5. Rotate view to see from the side

**Visual Checks:**
- [ ] Modules follow the single slope
- [ ] Z-position increases linearly from front to back
- [ ] Modules are ON the angled roof surface
- [ ] Linear progression (no sudden jumps in height)
- [ ] No modules floating or sinking

**Screenshot Location:** `tests/visual_inspection/pultdach_25deg_side_view.png`

---

### Scenario 4: Walmdach (Hip Roof) - 30° Pitch

**Expected Behavior:**
- Similar to Satteldach
- Modules follow roof slope on all four sides
- Z-position increases from eaves to ridge

**Test Steps:**
1. Select **Walmdach** as roof type
2. Set roof pitch: **30°**
3. Set roof dimensions: Length=12m, Width=10m
4. Place 20 modules automatically
5. Rotate view to see from multiple angles

**Visual Checks:**
- [ ] Modules follow roof slope
- [ ] Z-position increases toward center/ridge
- [ ] Modules on all roof faces follow their respective slopes
- [ ] No floating or sinking modules

**Screenshot Location:** `tests/visual_inspection/walmdach_30deg_side_view.png`

---

### Scenario 5: Zeltdach (Pyramid Roof) - 30° Pitch

**Expected Behavior:**
- Modules follow pyramidal roof surface
- Z-position increases from edges to center
- Symmetrical placement

**Test Steps:**
1. Select **Zeltdach** as roof type
2. Set roof pitch: **30°**
3. Set roof dimensions: Length=10m, Width=10m (square)
4. Place 16 modules automatically
5. Rotate view to see from corner angle

**Visual Checks:**
- [ ] Modules follow pyramidal slope
- [ ] Center modules are highest
- [ ] Edge modules are lowest
- [ ] Symmetrical around center
- [ ] No floating or sinking modules

**Screenshot Location:** `tests/visual_inspection/zeltdach_30deg_corner_view.png`

---

## Edge Case Testing

### Test 6: Extreme Pitch Angles

**Test 6a: Very Steep Roof (60°)**
1. Select Satteldach with 60° pitch
2. Place modules
3. Verify modules still follow roof surface (no floating)

**Test 6b: Very Shallow Roof (5°)**
1. Select Satteldach with 5° pitch
2. Place modules
3. Verify slight Z-variation (not completely flat)

### Test 7: Manual Module Placement

**Test Steps:**
1. Select Satteldach with 35° pitch
2. Manually add a module at position (0, -4)
3. Manually add a module at position (0, 0)
4. Manually add a module at position (0, 4)
5. Verify Z-positions increase correctly

**Visual Checks:**
- [ ] Manually placed modules follow roof surface
- [ ] Z-position calculated correctly based on Y-position
- [ ] No collision with automatically placed modules

### Test 8: Module Movement

**Test Steps:**
1. Place modules automatically on Satteldach
2. Select a module near the eave (low Z)
3. Move it toward the ridge (higher Y)
4. Verify Z-position updates correctly

**Visual Checks:**
- [ ] Module Z-position updates when moved
- [ ] Module stays on roof surface after move
- [ ] No floating after movement

---

## Common Issues to Look For

### ❌ INCORRECT (Before Fix)
- Modules on pitched roofs appear at constant height (like flat roof)
- Modules float above the angled roof surface
- Modules are on the red flat base instead of blue angled surface
- Gap between modules and roof surface varies

### ✅ CORRECT (After Fix)
- Modules follow the roof surface geometry
- Modules are ON the blue angled roof surface
- Z-position varies based on Y-position
- No gaps between modules and roof

---

## Inspection Checklist

### Pre-Inspection Setup
- [ ] App is running without errors
- [ ] 3D visualization loads correctly
- [ ] All roof types are available in dropdown
- [ ] Module placement controls are functional

### Flachdach Inspection
- [ ] Constant height verified
- [ ] Aufständerung (0.30m) visible
- [ ] 30° tilt angle correct
- [ ] Screenshot captured

### Satteldach Inspection
- [ ] Modules follow roof slope
- [ ] Z increases from eave to ridge
- [ ] No floating modules
- [ ] Screenshot captured

### Pultdach Inspection
- [ ] Linear Z progression
- [ ] Modules on angled surface
- [ ] Screenshot captured

### Walmdach Inspection
- [ ] Modules follow slope
- [ ] All roof faces correct
- [ ] Screenshot captured

### Zeltdach Inspection
- [ ] Pyramidal placement
- [ ] Center highest
- [ ] Screenshot captured

### Edge Cases
- [ ] Extreme pitches tested
- [ ] Manual placement tested
- [ ] Module movement tested

### Final Verification
- [ ] No regressions in existing features
- [ ] Performance acceptable (no lag)
- [ ] No console errors
- [ ] All screenshots documented

---

## Reporting Issues

If you find any issues during visual inspection, document them as follows:

**Issue Template:**
```
### Issue: [Brief Description]

**Roof Type:** [e.g., Satteldach]
**Roof Pitch:** [e.g., 35°]
**Roof Dimensions:** [e.g., 12m x 10m]

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Screenshot:**
[Path to screenshot]

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Severity:** [Critical / High / Medium / Low]
```

---

## Success Criteria

Visual inspection is considered **PASSED** when:

✅ All 5 roof types display modules correctly  
✅ Modules on pitched roofs follow roof surface geometry  
✅ No floating or sinking modules detected  
✅ Manual placement works correctly  
✅ Module movement updates Z-position correctly  
✅ No regressions in existing features  
✅ All screenshots captured and documented  

---

## Next Steps

After completing visual inspection:

1. ✅ Document all findings in `PHASE_1_TASK_2_VISUAL_INSPECTION_RESULTS.md`
2. ⏭️ Proceed to **Task 2.3: Kollisions-Tests**
3. ⏭️ Complete **Phase 1 Checkpoint** before moving to Phase 2

---

**Inspection Time Estimate:** 30-45 minutes  
**Required Tools:** Running Streamlit app, screenshot tool  
**Recommended:** Test with multiple roof dimensions and module counts

