# Story 04: Completion Popup UI Component

**Story ID**: PYEDIT-004
**Priority**: P0 - Critical
**Estimated Effort**: 2 days
**Sprint**: Week 2, Days 3-4
**Dependencies**: Story 02 (Static Code Completion), Story 03 (Document Symbol Completion)

---

## User Story

**As a** strategy developer
**I want** a polished, responsive completion popup interface
**So that** I can easily navigate and select code suggestions without disrupting my workflow

---

## User Value

- **Improves selection speed by 50%** (clear visual hierarchy, easy navigation)
- **Reduces selection errors by 80%** (clear highlighting, visual feedback)
- **Better user experience** (smooth animations, intuitive interactions)
- **Professional appearance** (matches modern editor standards)

---

## Functional Acceptance Criteria

### AC-4.1: Popup Positioning
```
GIVEN: Completion is triggered
WHEN: Popup is displayed
THEN: Position popup optimally relative to cursor

Examples:
✅ Default: Below cursor, left-aligned with typed text
✅ Near bottom edge: Above cursor instead
✅ Near right edge: Right-aligned to stay in viewport
✅ Minimum 10px margin from viewport edges
✅ Follows cursor when typing continues
```

### AC-4.2: Visual Design
```
GIVEN: Popup is displayed
WHEN: User views popup
THEN: Display with professional styling

Requirements:
✅ Max width: 400px
✅ Max height: 300px (10 items × 30px)
✅ Border: 1px solid with theme color
✅ Border radius: 4px
✅ Box shadow: 0 2px 8px rgba(0,0,0,0.15)
✅ Background: Theme-appropriate (light/dark)
✅ Font: Monospace, 14px
✅ Scrollbar: Custom styled, theme-appropriate
```

### AC-4.3: Item Display
```
GIVEN: Completion items in popup
WHEN: User views items
THEN: Display each item with clear information

Item Structure:
✅ Icon: Type indicator (function, variable, class, keyword)
✅ Name: Primary text, bold
✅ Type: Secondary text, muted color
✅ Source: Badge (RQAlpha, Python, Document)
✅ Height: 30px per item
✅ Padding: 8px horizontal, 6px vertical
```

### AC-4.4: Selection Highlighting
```
GIVEN: User navigating popup
WHEN: Item is selected (keyboard or mouse)
THEN: Highlight selected item clearly

Examples:
✅ Selected item: Background color change (theme-appropriate)
✅ Hover: Lighter highlight than selection
✅ Smooth transition: 100ms ease
✅ Selected item always visible (auto-scroll)
✅ First item selected by default
```

### AC-4.5: Keyboard Navigation
```
GIVEN: Popup is displayed
WHEN: User presses navigation keys
THEN: Navigate through items smoothly

Examples:
✅ ↓ Arrow: Select next item, scroll if needed
✅ ↑ Arrow: Select previous item, scroll if needed
✅ Page Down: Jump 5 items down
✅ Page Up: Jump 5 items up
✅ Home: Select first item
✅ End: Select last item
✅ Enter: Insert selected item, close popup
✅ Tab: Insert selected item, close popup
✅ Esc: Close popup without inserting
```

### AC-4.6: Mouse Interaction
```
GIVEN: Popup is displayed
WHEN: User interacts with mouse
THEN: Respond to mouse events

Examples:
✅ Hover: Highlight item
✅ Click: Insert item, close popup
✅ Scroll: Navigate through items
✅ Click outside: Close popup without inserting
✅ Cursor changes to pointer on hover
```

### AC-4.7: Scrolling Behavior
```
GIVEN: More than 10 items in popup
WHEN: User navigates
THEN: Scroll smoothly to keep selection visible

Examples:
✅ Selected item always visible
✅ Scroll with 1-item buffer (show next/prev item)
✅ Smooth scroll animation (100ms)
✅ Mouse wheel scrolling works
✅ Scrollbar visible when needed
```

### AC-4.8: Dark Mode Support
```
GIVEN: User has dark mode enabled
WHEN: Popup is displayed
THEN: Use dark mode colors

Dark Mode Colors:
✅ Background: #1e1e1e
✅ Border: #3e3e3e
✅ Text: #d4d4d4
✅ Selected background: #2a2d2e
✅ Hover background: #252526
✅ Muted text: #858585
✅ Scrollbar: #424242
```

### AC-4.9: Light Mode Support
```
GIVEN: User has light mode enabled
WHEN: Popup is displayed
THEN: Use light mode colors

Light Mode Colors:
✅ Background: #ffffff
✅ Border: #e0e0e0
✅ Text: #333333
✅ Selected background: #e8f4fd
✅ Hover background: #f3f3f3
✅ Muted text: #999999
✅ Scrollbar: #d0d0d0
```

### AC-4.10: Animation and Transitions
```
GIVEN: Popup state changes
WHEN: Showing, hiding, or updating
THEN: Animate smoothly

Examples:
✅ Show: Fade in + slide down (150ms)
✅ Hide: Fade out (100ms)
✅ Item highlight: Transition background (100ms)
✅ Scroll: Smooth scroll (100ms)
✅ No animation jank or flicker
```

### AC-4.11: Accessibility
```
GIVEN: User with accessibility needs
WHEN: Using popup
THEN: Support accessibility features

Requirements:
✅ ARIA role="listbox"
✅ ARIA aria-activedescendant for selected item
✅ ARIA aria-label="Code completion suggestions"
✅ Each item has role="option"
✅ Keyboard navigation fully functional
✅ High contrast mode support
✅ Screen reader announces selected item
```

### AC-4.12: Empty State
```
GIVEN: No matching completions
WHEN: User types
THEN: Don't show popup or show "No suggestions"

Examples:
✅ No matches: Popup hidden
✅ OR: Show "No suggestions" message (optional)
✅ Don't show empty popup
```

---

## Performance Acceptance Criteria

### PAC-4.1: Popup Render Time
```
Metric: Time from show command to visible on screen
Target: <10ms
Critical Threshold: 20ms (must not exceed)

Test Method:
1. Open Chrome DevTools > Performance
2. Start recording
3. Trigger completion 100 times
4. Measure time from showPopup() to paint event

Pass Criteria:
- p50 render time: <5ms
- p95 render time: <10ms
- p99 render time: <20ms
- No render exceeds 20ms
```

### PAC-4.2: Scroll Performance
```
Metric: Frame rate during scrolling
Target: 60 FPS
Critical Threshold: 55 FPS (must not exceed)

Test Method:
1. Open Chrome DevTools > Performance
2. Load popup with 50 items
3. Scroll rapidly with mouse wheel
4. Measure frame rate

Pass Criteria:
- Average FPS: ≥60
- Minimum FPS: ≥55
- No dropped frames during scroll
```

### PAC-4.3: Keyboard Navigation Latency
```
Metric: Time from keypress to selection update
Target: <5ms
Critical Threshold: 10ms (must not exceed)

Test Method:
1. Open popup with 50 items
2. Press ↓ arrow 50 times rapidly
3. Measure time from keydown to selection change
4. Calculate p95

Pass Criteria:
- p50 latency: <3ms
- p95 latency: <5ms
- p99 latency: <10ms
- No lag perceptible to user
```

### PAC-4.4: Bundle Size Increase
```
Metric: Gzipped JavaScript + CSS size increase
Target: <8KB
Critical Threshold: 12KB (must not exceed)

Test Method:
1. Build before: npm run build
2. Record baseline bundle size
3. Implement feature
4. Build after: npm run build
5. Calculate diff (JS + CSS)

Pass Criteria:
- Bundle increase: <8KB gzipped
- Component JS: ~4KB
- Component CSS: ~2KB
- Icons/assets: ~2KB
- Total route chunk: <223KB gzipped
```

### PAC-4.5: Memory Usage
```
Metric: Heap memory for popup component
Target: <500KB
Critical Threshold: 1MB (must not exceed)

Test Method:
1. Open Chrome DevTools > Memory
2. Take heap snapshot (baseline)
3. Show/hide popup 100 times
4. Take heap snapshot (after)
5. Compare retained size

Pass Criteria:
- Memory increase: <500KB
- No memory leaks (GC cleans up)
- DOM nodes released on hide
```

### PAC-4.6: Animation Performance
```
Metric: Frame rate during show/hide animations
Target: 60 FPS
Critical Threshold: 55 FPS (must not exceed)

Test Method:
1. Open Chrome DevTools > Performance
2. Record show/hide animation 50 times
3. Measure frame rate during animation
4. Calculate average

Pass Criteria:
- Average FPS: ≥60
- Minimum FPS: ≥55
- No animation jank
- Smooth transitions
```

---

## Performance Testing Script

```javascript
// test/performance/completion-popup-perf.spec.js
describe('Completion Popup UI Performance', () => {
  let popup, items;

  beforeEach(() => {
    items = generateCompletionItems(50);
    popup = mount(CompletionPopup, {
      props: { items, visible: false }
    });
  });

  test('Popup render time <10ms (p95)', async () => {
    const times = [];

    for (let i = 0; i < 100; i++) {
      const start = performance.now();

      await popup.setProps({ visible: true });
      await nextTick();

      const end = performance.now();
      times.push(end - start);

      await popup.setProps({ visible: false });
    }

    const p95 = times.sort((a, b) => a - b)[Math.floor(times.length * 0.95)];
    expect(p95).toBeLessThan(10);
  });

  test('Scroll performance ≥55 FPS', async () => {
    await popup.setProps({ visible: true });
    const scrollContainer = popup.find('.completion-list').element;

    const frames = [];
    let lastTime = performance.now();

    // Simulate rapid scrolling
    for (let i = 0; i < 100; i++) {
      scrollContainer.scrollTop = i * 30;
      await nextTick();

      const now = performance.now();
      const fps = 1000 / (now - lastTime);
      frames.push(fps);
      lastTime = now;
    }

    const avgFps = frames.reduce((a, b) => a + b) / frames.length;
    const minFps = Math.min(...frames);

    expect(avgFps).toBeGreaterThanOrEqual(60);
    expect(minFps).toBeGreaterThanOrEqual(55);
  });

  test('Keyboard navigation <5ms (p95)', async () => {
    await popup.setProps({ visible: true });
    const times = [];

    for (let i = 0; i < 50; i++) {
      const start = performance.now();

      await popup.vm.selectNext();
      await nextTick();

      const end = performance.now();
      times.push(end - start);
    }

    const p95 = times.sort((a, b) => a - b)[Math.floor(times.length * 0.95)];
    expect(p95).toBeLessThan(5);
  });

  test('Bundle size increase <8KB', () => {
    const stats = require('../../../dist/stats.json');
    const routeChunk = stats.assets.find(a => a.name.includes('route-strategies'));
    const increase = routeChunk.size - BASELINE_SIZE;
    expect(increase).toBeLessThan(8 * 1024); // 8KB
  });

  test('Memory usage <500KB', async () => {
    const before = performance.memory.usedJSHeapSize;

    // Show/hide 100 times
    for (let i = 0; i < 100; i++) {
      await popup.setProps({ visible: true });
      await popup.setProps({ visible: false });
    }

    const after = performance.memory.usedJSHeapSize;
    const increase = after - before;
    expect(increase).toBeLessThan(500 * 1024); // 500KB
  });

  test('Animation performance ≥55 FPS', async () => {
    const frames = [];
    let lastTime = performance.now();

    // Measure show animation
    for (let i = 0; i < 50; i++) {
      await popup.setProps({ visible: true });

      const now = performance.now();
      const fps = 1000 / (now - lastTime);
      frames.push(fps);
      lastTime = now;

      await popup.setProps({ visible: false });
    }

    const avgFps = frames.reduce((a, b) => a + b) / frames.length;
    const minFps = Math.min(...frames);

    expect(avgFps).toBeGreaterThanOrEqual(60);
    expect(minFps).toBeGreaterThanOrEqual(55);
  });
});
```

---
## Rollback/Disable Strategy

### Automatic Rollback Triggers

**Trigger 1: Render Performance Degradation**
```
IF: p95 popup render time > 20ms for 10 consecutive operations
THEN:
  1. Log warning to console
  2. Show notification: "Completion popup disabled due to performance"
  3. Set featureFlags.completionPopup = false
  4. Fallback to inline completion (no popup)
```

**Trigger 2: Animation Performance Degradation**
```
IF: Animation FPS < 55 for 5 consecutive animations
THEN:
  1. Log warning to console
  2. Disable animations (instant show/hide)
  3. Show notification: "Animations disabled for better performance"
  4. Continue with static popup
```

**Trigger 3: Memory Leak Detected**
```
IF: Memory increase > 1MB after 100 show/hide cycles
THEN:
  1. Log error to console
  2. Show notification: "Completion popup disabled due to memory issue"
  3. Set featureFlags.completionPopup = false
  4. Reload editor component
```

**Trigger 4: Bundle Size Exceeded**
```
IF: Bundle size increase > 12KB in CI/CD
THEN:
  1. Fail build
  2. Block merge to main
  3. Alert team via Slack/email
  4. Require manual review and approval
```

### Manual Disable Options

**Option 1: Feature Toggle**
```
Settings UI:
☐ Completion Popup UI

User can disable via:
- Settings panel
- localStorage: { completionPopup: false }
- URL parameter: ?completionPopup=false
```

**Option 2: Performance Mode**
```
When Performance Mode enabled:
- Disable animations (instant show/hide)
- Reduce max items to 5
- Simplify styling (no shadows, gradients)
- Still functional but faster
```

**Option 3: Accessibility Mode**
```
When Accessibility Mode enabled:
- High contrast colors
- Larger text (16px)
- No animations
- Enhanced keyboard navigation
```

**Option 4: Emergency Disable**
```
Console command:
> window.__disableCompletionPopup = true

Immediately disables feature without page reload
```

### Rollback Procedure

**Step 1: Detect Issue**
```
- Automated performance tests fail
- User reports UI lag or jank
- Monitoring alerts trigger
- High error rate in logs
```

**Step 2: Immediate Mitigation**
```
1. Deploy feature flag: completionPopup: false
2. Push to production (no code change needed)
3. Notify users via banner: "Completion popup temporarily disabled"
4. Completion still works (inline fallback)
```

**Step 3: Investigation**
```
1. Review performance metrics
2. Analyze error logs
3. Reproduce issue locally
4. Identify root cause (render? animation? positioning?)
```

**Step 4: Fix or Revert**
```
Option A: Quick Fix
- Optimize render logic
- Disable animations only
- Deploy patch
- Re-enable feature flag

Option B: Partial Rollback
- Disable animations
- Keep static popup
- Deploy degraded version

Option C: Full Revert
- Revert commit
- Remove feature code
- Deploy rollback
- Plan re-implementation
```

---

## Technical Implementation Notes

### File Changes
```
frontend/src/components/CompletionPopup.vue (NEW, ~250 lines)
├── Template: Popup structure with items list
├── Script: Navigation, selection, positioning logic
├── Style: Light/dark mode, animations, scrollbar
└── Accessibility: ARIA attributes, keyboard support

frontend/src/composables/useCompletionPopup.js (NEW, ~150 lines)
├── showPopup(items, position)
├── hidePopup()
├── selectNext()
├── selectPrevious()
├── selectItem(index)
├── handleKeyboard(event)
└── calculatePosition(cursorPos)

frontend/src/components/PythonCodeEditor.vue (MODIFY, +40 lines)
├── Import CompletionPopup component
├── Import useCompletionPopup composable
├── Add popup positioning logic
└── Integrate with completion data
```

### Key Algorithms

**Popup Positioning**:
```javascript
function calculatePosition(cursorPos, viewportSize, popupSize) {
  let top = cursorPos.top + cursorPos.height + 4; // 4px gap
  let left = cursorPos.left;

  // Check if popup would overflow bottom
  if (top + popupSize.height > viewportSize.height - 10) {
    top = cursorPos.top - popupSize.height - 4; // Show above
  }

  // Check if popup would overflow right
  if (left + popupSize.width > viewportSize.width - 10) {
    left = viewportSize.width - popupSize.width - 10; // Align right
  }

  // Ensure minimum margins
  top = Math.max(10, top);
  left = Math.max(10, left);

  return { top, left };
}
```

**Auto-scroll to Selected Item**:
```javascript
function scrollToSelected(selectedIndex, itemHeight, containerHeight) {
  const selectedTop = selectedIndex * itemHeight;
  const selectedBottom = selectedTop + itemHeight;
  const scrollTop = container.scrollTop;
  const scrollBottom = scrollTop + containerHeight;

  // Scroll down if selected item is below visible area
  if (selectedBottom > scrollBottom) {
    container.scrollTop = selectedBottom - containerHeight + itemHeight;
  }

  // Scroll up if selected item is above visible area
  if (selectedTop < scrollTop) {
    container.scrollTop = selectedTop - itemHeight;
  }
}
```

**Keyboard Navigation**:
```javascript
function handleKeyboard(event) {
  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault();
      selectNext();
      break;
    case 'ArrowUp':
      event.preventDefault();
      selectPrevious();
      break;
    case 'PageDown':
      event.preventDefault();
      selectIndex(Math.min(selectedIndex + 5, items.length - 1));
      break;
    case 'PageUp':
      event.preventDefault();
      selectIndex(Math.max(selectedIndex - 5, 0));
      break;
    case 'Home':
      event.preventDefault();
      selectIndex(0);
      break;
    case 'End':
      event.preventDefault();
      selectIndex(items.length - 1);
      break;
    case 'Enter':
    case 'Tab':
      event.preventDefault();
      insertSelected();
      hidePopup();
      break;
    case 'Escape':
      event.preventDefault();
      hidePopup();
      break;
  }
}
```

---

## Testing Checklist

### Unit Tests (90% coverage required)
- [ ] Popup positions below cursor by default
- [ ] Popup positions above cursor near bottom edge
- [ ] Popup aligns right near right edge
- [ ] Popup maintains minimum margins
- [ ] Items display with correct structure (icon, name, type, source)
- [ ] Selection highlighting works
- [ ] Hover highlighting works
- [ ] Keyboard navigation works (all keys)
- [ ] Mouse click selection works
- [ ] Mouse hover works
- [ ] Scrolling works (keyboard and mouse)
- [ ] Auto-scroll to selected item works
- [ ] Dark mode colors applied correctly
- [ ] Light mode colors applied correctly
- [ ] Animations work smoothly
- [ ] ARIA attributes present
- [ ] Empty state handled correctly

### Integration Tests
- [ ] Works with static completion (Story 02)
- [ ] Works with document symbols (Story 03)
- [ ] Works with auto-indentation (Story 01)
- [ ] Popup shows when completion triggered
- [ ] Popup hides when Esc pressed
- [ ] Popup hides when clicking outside
- [ ] Selected item inserted correctly
- [ ] Cursor positioned after insertion
- [ ] Undo reverts insertion
- [ ] Popup follows cursor when typing

### Performance Tests
- [ ] Popup render time <10ms (p95)
- [ ] Scroll performance ≥55 FPS
- [ ] Keyboard navigation <5ms (p95)
- [ ] Bundle size <8KB increase
- [ ] Memory usage <500KB
- [ ] Animation performance ≥55 FPS

### Accessibility Tests
- [ ] ARIA attributes correct
- [ ] Keyboard navigation fully functional
- [ ] Screen reader announces selected item
- [ ] High contrast mode works
- [ ] Focus management correct
- [ ] Tab order logical

### Browser Compatibility Tests
- [ ] Chrome 90+
- [ ] Firefox 88+
- [ ] Safari 14+
- [ ] Edge 90+

---

## Definition of Done

- [ ] All functional acceptance criteria met
- [ ] All performance acceptance criteria met
- [ ] Unit test coverage ≥90%
- [ ] Integration tests passing
- [ ] Performance tests passing
- [ ] Accessibility tests passing
- [ ] Browser compatibility verified
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] Feature flag implemented
- [ ] Rollback strategy tested
- [ ] Dark mode styling complete
- [ ] Light mode styling complete
- [ ] Animations polished
- [ ] Keyboard navigation tested
- [ ] Mouse interaction tested
- [ ] Positioning logic tested (all edge cases)
- [ ] ARIA attributes validated
- [ ] Screen reader tested
- [ ] Deployed to staging
- [ ] User acceptance testing passed
- [ ] Deployed to production
- [ ] Monitoring alerts configured

---

**Story Status**: Ready for Development
**Last Updated**: 2026-02-26
**Approved By**: _____________

