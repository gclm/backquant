# Story 02: Static Code Completion (Tier 1)

**Story ID**: PYEDIT-002
**Priority**: P0 - Critical
**Estimated Effort**: 3 days
**Sprint**: Week 1-2, Days 3-5
**Dependencies**: Story 01 (Auto-Indentation)

---

## User Story

**As a** strategy developer
**I want** code completion for RQAlpha APIs, Python keywords, and built-ins
**So that** I can write code faster and avoid typos in API names

---

## User Value

- **Reduces API lookup time by 60%** (no need to check documentation)
- **Improves coding speed by 20-25%** (faster API discovery)
- **Reduces typos by 70%** (autocomplete prevents misspellings)
- **Lowers learning curve** (discover APIs through suggestions)

---

## Functional Acceptance Criteria

### AC-2.1: Completion Trigger on Typing
```
GIVEN: User typing in editor
WHEN: User types 2+ consecutive alphanumeric characters
THEN: Show completion popup after 150ms debounce

Examples:
✅ Type "or" → No popup (< 2 chars)
✅ Type "ord" → Popup shows after 150ms
✅ Type "order_" → Popup updates with matching items
✅ Type rapidly → Debounce resets, popup shows after last keystroke + 150ms
```

### AC-2.2: Completion Trigger After Dot
```
GIVEN: User types dot (.) after identifier
WHEN: Dot is typed
THEN: Show completion popup immediately (no debounce)

Examples:
✅ "context." → Popup shows immediately
✅ "portfolio." → Popup shows immediately
✅ "bar_dict." → Popup shows immediately
```

### AC-2.3: RQAlpha API Completion
```
GIVEN: Completion popup is shown
WHEN: User types partial API name
THEN: Show matching RQAlpha functions with fuzzy match

Examples:
✅ "order" → Shows: order_shares, order_lots, order_value, order_percent, order_target_value, order_target_percent
✅ "get_p" → Shows: get_position, get_positions, get_price
✅ "hist" → Shows: history_bars
✅ "ordsh" → Shows: order_shares (fuzzy match)
```

### AC-2.4: Python Keywords Completion
```
GIVEN: Completion popup is shown
WHEN: User types partial keyword
THEN: Show matching Python keywords

Examples:
✅ "def" → Shows: def
✅ "im" → Shows: import, if
✅ "ret" → Shows: return
✅ "fo" → Shows: for
```

### AC-2.5: Python Built-ins Completion
```
GIVEN: Completion popup is shown
WHEN: User types partial built-in name
THEN: Show matching Python built-in functions

Examples:
✅ "len" → Shows: len
✅ "pri" → Shows: print
✅ "ran" → Shows: range
✅ "str" → Shows: str, isinstance, hasattr
```

### AC-2.6: Fuzzy Matching Algorithm
```
GIVEN: User types partial text
WHEN: Matching suggestions
THEN: Score and rank by fuzzy match quality

Scoring Rules:
- Exact prefix match: Score 100
- Consecutive character match: Score 80
- Non-consecutive match: Score 50
- Case-insensitive bonus: +10

Examples:
✅ "ordsh" matches "order_shares" (score: 50)
✅ "ord" matches "order_shares" (score: 100, prefix)
✅ "os" matches "order_shares" (score: 50, non-consecutive)
✅ Sort by score descending
```

### AC-2.7: Keyboard Navigation
```
GIVEN: Completion popup is shown
WHEN: User presses arrow keys
THEN: Navigate through suggestions

Examples:
✅ ↓ Arrow → Select next item
✅ ↑ Arrow → Select previous item
✅ Enter → Insert selected item
✅ Tab → Insert selected item (alternative)
✅ Esc → Close popup
✅ Wrap around: Last item + ↓ → First item
```

### AC-2.8: Mouse Selection
```
GIVEN: Completion popup is shown
WHEN: User clicks suggestion
THEN: Insert clicked suggestion

Examples:
✅ Click "order_shares" → Insert "order_shares"
✅ Hover highlights item
✅ Click outside → Close popup
```

### AC-2.9: Completion Insertion
```
GIVEN: User selects suggestion
WHEN: Enter or Tab pressed
THEN: Replace typed text with full suggestion

Examples:
✅ Type "ord" + select "order_shares" → "order_shares"
✅ Type "get_p" + select "get_position" → "get_position"
✅ Cursor positioned after inserted text
✅ Undo reverts to typed text
```

### AC-2.10: Popup Positioning
```
GIVEN: Completion popup is shown
WHEN: Cursor position changes
THEN: Position popup below cursor

Examples:
✅ Popup appears directly below cursor
✅ If near bottom edge → Show above cursor
✅ If near right edge → Align right
✅ Max 10 visible items, scroll if more
```

### AC-2.11: Popup Dismissal
```
GIVEN: Completion popup is shown
WHEN: User performs dismissal action
THEN: Hide popup

Dismissal Actions:
✅ Press Esc
✅ Click outside popup
✅ Move cursor away from word
✅ Select suggestion
✅ Type space or punctuation (except .)
```

### AC-2.12: Read-Only Mode
```
GIVEN: Editor in read-only mode
WHEN: User types
THEN: No completion popup appears
```

---

## Performance Acceptance Criteria

### PAC-2.1: Completion Trigger Latency
```
Metric: Time from keystroke to popup display
Target: <10ms (p95)
Critical Threshold: 20ms (must not exceed)

Test Method:
1. Open Chrome DevTools > Performance
2. Start recording
3. Type "order" 100 times
4. Measure time from keydown to popup render

Pass Criteria:
- p50 latency: <5ms
- p95 latency: <10ms
- p99 latency: <20ms
- No operation exceeds 20ms
```

### PAC-2.2: Fuzzy Matching Performance
```
Metric: Time to filter and rank 185 items (100 API + 35 keywords + 50 built-ins)
Target: <5ms per keystroke
Critical Threshold: 10ms (must not exceed)

Test Method:
1. Benchmark fuzzy match function
2. Test with 185 static items
3. Measure 1000 iterations
4. Calculate average time

Pass Criteria:
- Average time: <3ms
- p95 time: <5ms
- p99 time: <10ms
```

### PAC-2.3: Bundle Size Increase
```
Metric: Gzipped JavaScript size increase
Target: <10KB
Critical Threshold: 15KB (must not exceed)

Test Method:
1. Build before: npm run build
2. Record baseline bundle size
3. Implement feature
4. Build after: npm run build
5. Calculate diff

Pass Criteria:
- Bundle increase: <10KB gzipped
- Static data (185 items): ~5KB
- Fuzzy match + UI: ~5KB
- Total route chunk: <210KB gzipped
```

### PAC-2.4: Memory Usage
```
Metric: Heap memory increase
Target: <2MB
Critical Threshold: 5MB (must not exceed)

Test Method:
1. Open Chrome DevTools > Memory
2. Take heap snapshot (baseline)
3. Open editor, trigger completion 500 times
4. Take heap snapshot (after)
5. Compare retained size

Pass Criteria:
- Memory increase: <2MB
- Static data retained: ~500KB
- No memory leaks (GC cleans up)
```

### PAC-2.5: Popup Render Performance
```
Metric: Time to render popup with 10 items
Target: <10ms
Critical Threshold: 20ms (must not exceed)

Test Method:
1. Measure time from popup show to paint
2. Test with 10 visible items
3. Repeat 100 times
4. Calculate p95

Pass Criteria:
- p50 render time: <5ms
- p95 render time: <10ms
- p99 render time: <20ms
```

---

## Performance Testing Script

```javascript
// test/performance/static-completion-perf.spec.js
describe('Static Code Completion Performance', () => {
  let completionData, fuzzyMatcher;

  beforeEach(() => {
    // Load 185 static items
    completionData = [
      ...RQALPHA_API,      // 100 items
      ...PYTHON_KEYWORDS,  // 35 items
      ...PYTHON_BUILTINS   // 50 items
    ];
    fuzzyMatcher = new FuzzyMatcher(completionData);
  });

  test('Completion trigger latency <10ms (p95)', async () => {
    const latencies = [];
    const editor = mount(PythonCodeEditor);

    for (let i = 0; i < 100; i++) {
      const start = performance.now();

      // Simulate typing "order"
      await editor.vm.handleInput('order');
      await nextTick();

      const end = performance.now();
      latencies.push(end - start);
    }

    const p95 = latencies.sort((a, b) => a - b)[Math.floor(latencies.length * 0.95)];
    expect(p95).toBeLessThan(10);
  });

  test('Fuzzy matching <5ms (p95)', () => {
    const times = [];

    for (let i = 0; i < 1000; i++) {
      const start = performance.now();

      const results = fuzzyMatcher.match('order');

      const end = performance.now();
      times.push(end - start);
    }

    const p95 = times.sort((a, b) => a - b)[Math.floor(times.length * 0.95)];
    expect(p95).toBeLessThan(5);
    expect(results.length).toBeGreaterThan(0);
  });

  test('Bundle size increase <10KB', () => {
    const stats = require('../../../dist/stats.json');
    const routeChunk = stats.assets.find(a => a.name.includes('route-strategies'));
    const increase = routeChunk.size - BASELINE_SIZE;
    expect(increase).toBeLessThan(10 * 1024); // 10KB
  });

  test('Memory usage <2MB', async () => {
    const before = performance.memory.usedJSHeapSize;
    const editor = mount(PythonCodeEditor);

    // Trigger completion 500 times
    for (let i = 0; i < 500; i++) {
      await editor.vm.showCompletion('order');
      await editor.vm.hideCompletion();
    }

    const after = performance.memory.usedJSHeapSize;
    const increase = after - before;
    expect(increase).toBeLessThan(2 * 1024 * 1024); // 2MB
  });

  test('Popup render <10ms (p95)', async () => {
    const times = [];
    const editor = mount(PythonCodeEditor);

    for (let i = 0; i < 100; i++) {
      const start = performance.now();

      await editor.vm.showCompletion('order');
      await nextTick();

      const end = performance.now();
      times.push(end - start);

      await editor.vm.hideCompletion();
    }

    const p95 = times.sort((a, b) => a - b)[Math.floor(times.length * 0.95)];
    expect(p95).toBeLessThan(10);
  });
});
```

---
## Rollback/Disable Strategy

### Automatic Rollback Triggers

**Trigger 1: Completion Latency Degradation**
```
IF: p95 completion trigger latency > 20ms for 10 consecutive operations
THEN:
  1. Log warning to console
  2. Show notification: "Code completion disabled due to performance"
  3. Set featureFlags.codeCompletion = false
  4. Revert to no completion
```

**Trigger 2: Bundle Size Exceeded**
```
IF: Bundle size increase > 15KB in CI/CD
THEN:
  1. Fail build
  2. Block merge to main
  3. Alert team via Slack/email
  4. Require manual review and approval
```

**Trigger 3: Memory Leak Detected**
```
IF: Memory increase > 5MB after 500 operations
THEN:
  1. Log error to console
  2. Show notification: "Code completion disabled due to memory issue"
  3. Set featureFlags.codeCompletion = false
  4. Reload editor component
```

**Trigger 4: Fuzzy Match Performance Degradation**
```
IF: Fuzzy matching takes > 10ms for 5 consecutive operations
THEN:
  1. Log warning to console
  2. Disable fuzzy matching, use prefix-only matching
  3. Show notification: "Fuzzy matching disabled, using prefix matching"
  4. Continue with degraded completion
```

### Manual Disable Options

**Option 1: Feature Toggle**
```
Settings UI:
☐ Code Completion

User can disable via:
- Settings panel
- localStorage: { codeCompletion: false }
- URL parameter: ?codeCompletion=false
```

**Option 2: Performance Mode**
```
When Performance Mode enabled:
- Increase debounce to 300ms
- Limit results to 5 items
- Disable fuzzy matching (prefix-only)
- Still functional but faster
```

**Option 3: Emergency Disable**
```
Console command:
> window.__disableCodeCompletion = true

Immediately disables feature without page reload
```

### Rollback Procedure

**Step 1: Detect Issue**
```
- Automated performance tests fail
- User reports lag/slowness
- Monitoring alerts trigger
- High error rate in logs
```

**Step 2: Immediate Mitigation**
```
1. Deploy feature flag: codeCompletion: false
2. Push to production (no code change needed)
3. Notify users via banner: "Code completion temporarily disabled"
```

**Step 3: Investigation**
```
1. Review performance metrics
2. Analyze error logs
3. Reproduce issue locally
4. Identify root cause (fuzzy match? popup render? data size?)
```

**Step 4: Fix or Revert**
```
Option A: Quick Fix
- Fix bug in code (e.g., optimize fuzzy match)
- Deploy patch
- Re-enable feature flag

Option B: Partial Rollback
- Disable fuzzy matching only
- Keep prefix matching
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
frontend/src/composables/useCodeCompletion.js (NEW, ~300 lines)
├── Static data: RQALPHA_API, PYTHON_KEYWORDS, PYTHON_BUILTINS
├── fuzzyMatch(query, items)
├── showCompletion(trigger)
├── hideCompletion()
├── selectSuggestion(item)
└── handleKeyboardNav(event)

frontend/src/components/CompletionPopup.vue (NEW, ~150 lines)
├── Popup UI component
├── Keyboard navigation
├── Mouse selection
└── Positioning logic

frontend/src/components/PythonCodeEditor.vue (MODIFY, +80 lines)
├── Import useCodeCompletion composable
├── Import CompletionPopup component
├── Add input event handlers
└── Integrate completion logic
```

### Key Algorithms

**Fuzzy Matching**:
```javascript
function fuzzyMatch(query, items) {
  const results = items.map(item => {
    let score = 0;
    let queryIndex = 0;
    let consecutive = 0;
    
    // Check if exact prefix match
    if (item.toLowerCase().startsWith(query.toLowerCase())) {
      score = 100;
    } else {
      // Non-consecutive character matching
      for (let i = 0; i < item.length && queryIndex < query.length; i++) {
        if (item[i].toLowerCase() === query[queryIndex].toLowerCase()) {
          score += consecutive > 0 ? 80 : 50;
          consecutive++;
          queryIndex++;
        } else {
          consecutive = 0;
        }
      }
    }
    
    return { item, score };
  });
  
  return results
    .filter(r => r.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 10)
    .map(r => r.item);
}
```

**Debounced Trigger**:
```javascript
let debounceTimer = null;

function handleInput(text) {
  clearTimeout(debounceTimer);
  
  if (text.length < 2) {
    hideCompletion();
    return;
  }
  
  debounceTimer = setTimeout(() => {
    const matches = fuzzyMatch(text, completionData);
    if (matches.length > 0) {
      showCompletion(matches);
    }
  }, 150);
}
```

---

## Testing Checklist

### Unit Tests (90% coverage required)
- [ ] Completion triggers after 2+ characters
- [ ] Completion triggers immediately after dot
- [ ] Debounce works correctly (150ms)
- [ ] RQAlpha API items appear in results
- [ ] Python keywords appear in results
- [ ] Python built-ins appear in results
- [ ] Fuzzy matching scores correctly
- [ ] Fuzzy matching ranks by score
- [ ] Keyboard navigation works (↑↓ Enter Tab Esc)
- [ ] Mouse selection works
- [ ] Popup positioning works
- [ ] Popup dismissal works (Esc, click outside, move cursor)
- [ ] Completion insertion replaces typed text
- [ ] Undo reverts completion
- [ ] Read-only mode disables completion

### Integration Tests
- [ ] Works with auto-indentation (Story 01)
- [ ] Works with syntax highlighting
- [ ] Doesn't interfere with copy/paste
- [ ] Doesn't interfere with find/replace
- [ ] Popup doesn't block editor interaction

### Performance Tests
- [ ] Completion trigger latency <10ms (p95)
- [ ] Fuzzy matching <5ms (p95)
- [ ] Bundle size <10KB increase
- [ ] Memory usage <2MB increase
- [ ] Popup render <10ms (p95)

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
- [ ] Browser compatibility verified
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] Feature flag implemented
- [ ] Rollback strategy tested
- [ ] Static data validated (185 items)
- [ ] Fuzzy matching algorithm optimized
- [ ] Popup UI polished (dark mode support)
- [ ] Keyboard navigation tested
- [ ] Mouse interaction tested
- [ ] Deployed to staging
- [ ] User acceptance testing passed
- [ ] Deployed to production
- [ ] Monitoring alerts configured

---

**Story Status**: Ready for Development
**Last Updated**: 2026-02-26
**Approved By**: _____________

