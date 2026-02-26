# Story 01: Auto-Indentation for Python Code Editor

**Story ID**: PYEDIT-001
**Priority**: P0 - Critical
**Estimated Effort**: 2 days
**Sprint**: Week 1, Days 1-2
**Dependencies**: None

---

## User Story

**As a** strategy developer
**I want** automatic indentation when writing Python code
**So that** I don't have to manually manage spaces and can avoid indentation errors

---

## User Value

- **Reduces indentation errors by 80%** (primary pain point)
- **Improves coding speed by 10-15%** (less manual space management)
- **Lowers cognitive load** (focus on logic, not formatting)
- **Matches modern editor expectations** (VS Code, PyCharm behavior)

---

## Functional Acceptance Criteria

### AC-1.1: Enter Key After Colon
```
GIVEN: Cursor at end of line ending with ':'
WHEN: User presses Enter
THEN: New line starts with current indent + 4 spaces

Examples:
✅ "if x > 0:|" + Enter → "\n    "
✅ "    def foo():|" + Enter → "\n        "
✅ "        for i in range(10):|" + Enter → "\n            "
```

### AC-1.2: Enter Key on Normal Line
```
GIVEN: Cursor at end of line NOT ending with ':'
WHEN: User presses Enter
THEN: New line maintains current indentation level

Examples:
✅ "    x = 5|" + Enter → "\n    "
✅ "        return x|" + Enter → "\n        "
✅ "|" + Enter → "\n"
```

### AC-1.3: Tab Key Indentation
```
GIVEN: Cursor on a line (no selection)
WHEN: User presses Tab
THEN: Insert 4 spaces at cursor position

Examples:
✅ "|x = 5" + Tab → "    |x = 5"
✅ "x = |5" + Tab → "x =     |5"
```

### AC-1.4: Tab Key Multi-Line Indentation
```
GIVEN: Multiple lines selected
WHEN: User presses Tab
THEN: Add 4 spaces to beginning of each selected line

Examples:
✅ Selected "x = 5\ny = 10" + Tab → "    x = 5\n    y = 10"
✅ Selection preserved after indentation
```

### AC-1.5: Shift+Tab Dedentation
```
GIVEN: Cursor on indented line (no selection)
WHEN: User presses Shift+Tab
THEN: Remove up to 4 leading spaces

Examples:
✅ "    |x = 5" + Shift+Tab → "|x = 5"
✅ "  |x = 5" + Shift+Tab → "|x = 5" (removes 2 spaces)
✅ "|x = 5" + Shift+Tab → "|x = 5" (no change)
```

### AC-1.6: Smart Dedentation Keywords
```
GIVEN: User types dedent keyword as first non-whitespace
WHEN: Keyword is completed (followed by space/newline)
THEN: Automatically remove 4 spaces from line

Dedent Keywords: return, pass, break, continue, raise

Examples:
✅ "        |" + type "return " → "    return |"
✅ "            |" + type "pass\n" → "        pass\n"
❌ "    x = return_value|" → No dedent (keyword in expression)
```

### AC-1.7: Bracket Indentation
```
GIVEN: Cursor after opening bracket ([, {, ()
WHEN: User presses Enter
THEN: New line indented by 4 spaces

Examples:
✅ "data = [|" + Enter → "\n    "
✅ "config = {|" + Enter → "\n    "
✅ "result = func(|" + Enter → "\n    "
```

### AC-1.8: Undo/Redo Support
```
GIVEN: Auto-indentation just occurred
WHEN: User presses Ctrl+Z
THEN: Auto-indentation reverted as single operation

WHEN: User presses Ctrl+Y
THEN: Auto-indentation reapplied
```

### AC-1.9: Read-Only Mode
```
GIVEN: Editor in read-only mode
WHEN: User attempts any indentation operation
THEN: No changes occur (all features disabled)
```

---

## Performance Acceptance Criteria

### PAC-1.1: Input Latency
```
Metric: Time from keydown to screen update
Target: <5ms per operation (p95)
Critical Threshold: 10ms (must not exceed)

Test Method:
1. Open Chrome DevTools > Performance
2. Start recording
3. Press Enter after colon 100 times
4. Stop recording
5. Measure time for each keydown → paint event

Pass Criteria:
- p50 latency: <3ms
- p95 latency: <5ms
- p99 latency: <10ms
- No operation exceeds 10ms
```

### PAC-1.2: Bundle Size Increase
```
Metric: Gzipped JavaScript size increase
Target: <5KB
Critical Threshold: 10KB (must not exceed)

Test Method:
1. Build before: npm run build
2. Record baseline: ls -lh dist/js/route-strategies.*.js | gzip -c | wc -c
3. Implement feature
4. Build after: npm run build
5. Calculate diff

Pass Criteria:
- Bundle increase: <5KB gzipped
- Total route chunk: <200KB gzipped
```

### PAC-1.3: Memory Usage
```
Metric: Heap memory increase
Target: <500KB
Critical Threshold: 1MB (must not exceed)

Test Method:
1. Open Chrome DevTools > Memory
2. Take heap snapshot (baseline)
3. Open editor, type 500 lines with auto-indent
4. Take heap snapshot (after)
5. Compare retained size

Pass Criteria:
- Memory increase: <500KB
- No memory leaks (GC cleans up)
```

### PAC-1.4: Large File Performance
```
Metric: Performance with 1000+ line files
Target: Same latency as small files
Critical Threshold: <10ms per operation

Test Method:
1. Load 1000-line Python file
2. Measure Enter key latency at line 500
3. Measure Tab key latency with 50 lines selected

Pass Criteria:
- Enter latency: <5ms
- Tab (single line): <5ms
- Tab (50 lines): <50ms (1ms per line)
```

---

## Performance Testing Script

```javascript
// test/performance/auto-indent-perf.spec.js
describe('Auto-Indentation Performance', () => {
  let editor, latencies = [];

  beforeEach(() => {
    editor = mount(PythonCodeEditor, {
      props: { modelValue: 'def foo():\n    pass' }
    });
  });

  test('Enter key latency <5ms (p95)', async () => {
    const textarea = editor.find('textarea').element;

    for (let i = 0; i < 100; i++) {
      const start = performance.now();

      // Simulate Enter after colon
      textarea.value = 'if x > 0:';
      textarea.selectionStart = textarea.selectionEnd = 10;
      await textarea.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));
      await nextTick();

      const end = performance.now();
      latencies.push(end - start);
    }

    const p95 = latencies.sort((a, b) => a - b)[Math.floor(latencies.length * 0.95)];
    expect(p95).toBeLessThan(5);
  });

  test('Bundle size increase <5KB', () => {
    const stats = require('../../../dist/stats.json');
    const routeChunk = stats.assets.find(a => a.name.includes('route-strategies'));
    const increase = routeChunk.size - BASELINE_SIZE;
    expect(increase).toBeLessThan(5 * 1024); // 5KB
  });

  test('Memory usage <500KB', async () => {
    const before = performance.memory.usedJSHeapSize;

    // Type 500 lines with auto-indent
    for (let i = 0; i < 500; i++) {
      await editor.vm.handleEnterKey();
    }

    const after = performance.memory.usedJSHeapSize;
    const increase = after - before;
    expect(increase).toBeLessThan(500 * 1024); // 500KB
  });
});
```

---

## Rollback/Disable Strategy

### Automatic Rollback Triggers

**Trigger 1: Performance Degradation**
```
IF: p95 input latency > 10ms for 10 consecutive operations
THEN:
  1. Log warning to console
  2. Show notification: "Auto-indent disabled due to performance"
  3. Set featureFlags.autoIndent = false
  4. Revert to manual indentation
```

**Trigger 2: Bundle Size Exceeded**
```
IF: Bundle size increase > 10KB in CI/CD
THEN:
  1. Fail build
  2. Block merge to main
  3. Alert team via Slack/email
  4. Require manual review and approval
```

**Trigger 3: Memory Leak Detected**
```
IF: Memory increase > 1MB after 1000 operations
THEN:
  1. Log error to console
  2. Show notification: "Auto-indent disabled due to memory issue"
  3. Set featureFlags.autoIndent = false
  4. Reload editor component
```

### Manual Disable Options

**Option 1: Feature Toggle**
```
Settings UI:
☐ Auto-indentation

User can disable via:
- Settings panel
- localStorage: { autoIndent: false }
- URL parameter: ?autoIndent=false
```

**Option 2: Performance Mode**
```
When Performance Mode enabled:
- Auto-indent remains enabled (low overhead)
- But can be individually disabled if needed
```

**Option 3: Emergency Disable**
```
Console command:
> window.__disableAutoIndent = true

Immediately disables feature without page reload
```

### Rollback Procedure

**Step 1: Detect Issue**
```
- Automated performance tests fail
- User reports lag/issues
- Monitoring alerts trigger
```

**Step 2: Immediate Mitigation**
```
1. Deploy feature flag: autoIndent: false
2. Push to production (no code change needed)
3. Notify users via banner: "Auto-indent temporarily disabled"
```

**Step 3: Investigation**
```
1. Review performance metrics
2. Analyze error logs
3. Reproduce issue locally
4. Identify root cause
```

**Step 4: Fix or Revert**
```
Option A: Quick Fix
- Fix bug in code
- Deploy patch
- Re-enable feature flag

Option B: Full Revert
- Revert commit
- Remove feature code
- Deploy rollback
- Plan re-implementation
```

---

## Technical Implementation Notes

### File Changes
```
frontend/src/composables/useAutoIndent.js (NEW, ~150 lines)
├── handleEnterKey()
├── handleTabKey()
├── handleShiftTabKey()
├── detectDedentKeyword()
├── calculateIndentation()
└── isInsideString()

frontend/src/components/PythonCodeEditor.vue (MODIFY, +50 lines)
├── Import useAutoIndent composable
├── Add keydown event handlers
└── Integrate indentation logic
```

### Key Algorithms

**Indentation Calculation**:
```javascript
function calculateIndentation(line) {
  const match = line.match(/^(\s*)/);
  const currentIndent = match ? match[1] : '';
  const endsWithColon = line.trim().endsWith(':');
  return endsWithColon ? currentIndent + '    ' : currentIndent;
}
```

**Dedent Detection**:
```javascript
function shouldDedent(line, keyword) {
  const trimmed = line.trim();
  const isFirstWord = trimmed.startsWith(keyword);
  const isComplete = trimmed === keyword || trimmed.startsWith(keyword + ' ');
  return isFirstWord && isComplete;
}
```

---

## Testing Checklist

### Unit Tests (90% coverage required)
- [ ] Enter after colon adds 4 spaces
- [ ] Enter on normal line maintains indent
- [ ] Tab adds 4 spaces
- [ ] Shift+Tab removes up to 4 spaces
- [ ] Multi-line Tab/Shift+Tab works
- [ ] Dedent keywords trigger correctly
- [ ] Dedent keywords don't trigger in expressions
- [ ] Bracket indentation works
- [ ] Undo/redo works correctly
- [ ] Read-only mode disables features

### Integration Tests
- [ ] Works with syntax highlighting
- [ ] Works with code completion (when added)
- [ ] Doesn't interfere with copy/paste
- [ ] Doesn't interfere with find/replace

### Performance Tests
- [ ] Input latency <5ms (p95)
- [ ] Bundle size <5KB increase
- [ ] Memory usage <500KB increase
- [ ] Large file performance acceptable

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
- [ ] Deployed to staging
- [ ] User acceptance testing passed
- [ ] Deployed to production
- [ ] Monitoring alerts configured

---

**Story Status**: Ready for Development
**Last Updated**: 2026-02-26
**Approved By**: _____________
