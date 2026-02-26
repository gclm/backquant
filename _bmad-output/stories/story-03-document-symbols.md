# Story 03: Document Symbol Completion (Tier 2)

**Story ID**: PYEDIT-003
**Priority**: P1 - High
**Estimated Effort**: 2 days
**Sprint**: Week 2, Days 1-2
**Dependencies**: Story 02 (Static Code Completion)

---

## User Story

**As a** strategy developer
**I want** code completion for variables and functions I've defined in my current file
**So that** I can quickly reference my own code without scrolling or remembering exact names

---

## User Value

- **Reduces scrolling by 40%** (no need to scroll up to check variable names)
- **Improves coding speed by 15%** (faster access to own symbols)
- **Reduces typos in variable names by 80%** (autocomplete prevents misspellings)
- **Better code navigation** (discover what's available in current file)

---

## Functional Acceptance Criteria

### AC-3.1: Function Definition Extraction
```
GIVEN: Python code with function definitions
WHEN: Document symbols are extracted
THEN: All function names are available in completion

Examples:
✅ "def calculate_rsi(prices):" → Extract "calculate_rsi"
✅ "def init(context):" → Extract "init"
✅ "def handle_bar(context, bar_dict):" → Extract "handle_bar"
✅ Nested functions extracted
✅ Class methods extracted
```

### AC-3.2: Variable Assignment Extraction
```
GIVEN: Python code with variable assignments
WHEN: Document symbols are extracted
THEN: All variable names are available in completion

Examples:
✅ "portfolio = context.portfolio" → Extract "portfolio"
✅ "rsi_period = 14" → Extract "rsi_period"
✅ "buy_threshold, sell_threshold = 30, 70" → Extract "buy_threshold", "sell_threshold"
✅ "data = []" → Extract "data"
```

### AC-3.3: Class Definition Extraction
```
GIVEN: Python code with class definitions
WHEN: Document symbols are extracted
THEN: All class names are available in completion

Examples:
✅ "class Strategy:" → Extract "Strategy"
✅ "class RsiStrategy(BaseStrategy):" → Extract "RsiStrategy"
✅ Nested classes extracted
```

### AC-3.4: Import Statement Extraction
```
GIVEN: Python code with import statements
WHEN: Document symbols are extracted
THEN: Imported names are available in completion

Examples:
✅ "import numpy" → Extract "numpy"
✅ "import pandas as pd" → Extract "pd"
✅ "from datetime import datetime" → Extract "datetime"
✅ "from rqalpha.api import *" → Skip (wildcard imports)
```

### AC-3.5: Real-Time Symbol Updates
```
GIVEN: User is typing code
WHEN: New symbols are defined
THEN: Completion list updates within 500ms

Examples:
✅ Type "new_var = 10" → "new_var" appears in completion
✅ Type "def new_func():" → "new_func" appears in completion
✅ Delete function → Symbol removed from completion
✅ Rename variable → Old name removed, new name added
```

### AC-3.6: Symbol Deduplication
```
GIVEN: Multiple symbol sources (static + document)
WHEN: Showing completion
THEN: Deduplicate symbols, prioritize document symbols

Examples:
✅ Document has "range" variable → Show document "range" first
✅ Document has "order_shares" function → Show document version first
✅ No duplicates in completion list
```

### AC-3.7: Symbol Scope Awareness
```
GIVEN: Symbols defined in different scopes
WHEN: Extracting symbols
THEN: Extract all symbols regardless of scope

Examples:
✅ Global variables extracted
✅ Function parameters extracted
✅ Local variables in functions extracted
✅ Class attributes extracted (self.attribute)
```

### AC-3.8: Incremental Extraction
```
GIVEN: Large file (500+ lines)
WHEN: User types
THEN: Extract symbols incrementally without blocking

Examples:
✅ Extract on file load (background)
✅ Re-extract on significant changes (debounced 500ms)
✅ Don't re-extract on every keystroke
✅ No UI lag during extraction
```

### AC-3.9: Extraction Error Handling
```
GIVEN: Invalid Python syntax in file
WHEN: Extracting symbols
THEN: Extract what's possible, skip invalid sections

Examples:
✅ Syntax error on line 50 → Extract lines 1-49
✅ Incomplete function definition → Skip that function
✅ No errors shown to user
✅ Extraction doesn't crash
```

---

## Performance Acceptance Criteria

### PAC-3.1: Symbol Extraction Time
```
Metric: Time to extract symbols from 500-line file
Target: <50ms
Critical Threshold: 100ms (must not exceed)

Test Method:
1. Create 500-line Python file with 50 functions, 100 variables
2. Measure extraction time
3. Repeat 100 times
4. Calculate p95

Pass Criteria:
- p50 extraction time: <30ms
- p95 extraction time: <50ms
- p99 extraction time: <100ms
- No extraction exceeds 100ms
```

### PAC-3.2: Incremental Update Performance
```
Metric: Time to re-extract after code change
Target: <20ms
Critical Threshold: 50ms (must not exceed)

Test Method:
1. Load 500-line file
2. Add new function definition
3. Measure re-extraction time
4. Repeat 100 times

Pass Criteria:
- p50 update time: <10ms
- p95 update time: <20ms
- p99 update time: <50ms
- Debounced to avoid excessive re-extraction
```

### PAC-3.3: Bundle Size Increase
```
Metric: Gzipped JavaScript size increase
Target: <5KB
Critical Threshold: 10KB (must not exceed)

Test Method:
1. Build before: npm run build
2. Record baseline bundle size
3. Implement feature
4. Build after: npm run build
5. Calculate diff

Pass Criteria:
- Bundle increase: <5KB gzipped
- Regex patterns: ~1KB
- Extraction logic: ~4KB
- Total route chunk: <215KB gzipped
```

### PAC-3.4: Memory Usage
```
Metric: Heap memory for storing extracted symbols
Target: <1MB per file
Critical Threshold: 2MB (must not exceed)

Test Method:
1. Open Chrome DevTools > Memory
2. Take heap snapshot (baseline)
3. Load 500-line file with 150 symbols
4. Take heap snapshot (after)
5. Compare retained size

Pass Criteria:
- Memory per file: <1MB
- Symbol storage: ~500KB
- No memory leaks on file change
```

### PAC-3.5: Completion Performance with Document Symbols
```
Metric: Time to filter combined static + document symbols
Target: <10ms
Critical Threshold: 20ms (must not exceed)

Test Method:
1. Load file with 150 document symbols
2. Combine with 185 static symbols (335 total)
3. Measure fuzzy match time
4. Repeat 1000 times

Pass Criteria:
- p50 match time: <5ms
- p95 match time: <10ms
- p99 match time: <20ms
- No perceptible lag when typing
```

---

## Performance Testing Script

```javascript
// test/performance/document-symbols-perf.spec.js
describe('Document Symbol Completion Performance', () => {
  let symbolExtractor, testCode;

  beforeEach(() => {
    symbolExtractor = new DocumentSymbolExtractor();

    // Generate 500-line test file
    testCode = generateTestCode({
      functions: 50,
      variables: 100,
      classes: 10,
      lines: 500
    });
  });

  test('Symbol extraction <50ms (p95)', () => {
    const times = [];

    for (let i = 0; i < 100; i++) {
      const start = performance.now();

      const symbols = symbolExtractor.extract(testCode);

      const end = performance.now();
      times.push(end - start);
    }

    const p95 = times.sort((a, b) => a - b)[Math.floor(times.length * 0.95)];
    expect(p95).toBeLessThan(50);
    expect(symbols.length).toBeGreaterThan(0);
  });

  test('Incremental update <20ms (p95)', () => {
    const times = [];
    symbolExtractor.extract(testCode); // Initial extraction

    for (let i = 0; i < 100; i++) {
      const updatedCode = testCode + '\ndef new_function():\n    pass\n';

      const start = performance.now();

      const symbols = symbolExtractor.extract(updatedCode);

      const end = performance.now();
      times.push(end - start);
    }

    const p95 = times.sort((a, b) => a - b)[Math.floor(times.length * 0.95)];
    expect(p95).toBeLessThan(20);
  });

  test('Bundle size increase <5KB', () => {
    const stats = require('../../../dist/stats.json');
    const routeChunk = stats.assets.find(a => a.name.includes('route-strategies'));
    const increase = routeChunk.size - BASELINE_SIZE;
    expect(increase).toBeLessThan(5 * 1024); // 5KB
  });

  test('Memory usage <1MB per file', async () => {
    const before = performance.memory.usedJSHeapSize;

    const symbols = symbolExtractor.extract(testCode);

    const after = performance.memory.usedJSHeapSize;
    const increase = after - before;
    expect(increase).toBeLessThan(1 * 1024 * 1024); // 1MB
    expect(symbols.length).toBeGreaterThan(0);
  });

  test('Combined completion <10ms (p95)', () => {
    const times = [];
    const documentSymbols = symbolExtractor.extract(testCode); // 150 symbols
    const staticSymbols = [...RQALPHA_API, ...PYTHON_KEYWORDS, ...PYTHON_BUILTINS]; // 185 symbols
    const allSymbols = [...staticSymbols, ...documentSymbols]; // 335 total

    const fuzzyMatcher = new FuzzyMatcher(allSymbols);

    for (let i = 0; i < 1000; i++) {
      const start = performance.now();

      const results = fuzzyMatcher.match('calc');

      const end = performance.now();
      times.push(end - start);
    }

    const p95 = times.sort((a, b) => a - b)[Math.floor(times.length * 0.95)];
    expect(p95).toBeLessThan(10);
  });
});
```

---

## Rollback/Disable Strategy

### Automatic Rollback Triggers

**Trigger 1: Extraction Performance Degradation**
```
IF: p95 extraction time > 100ms for 5 consecutive operations
THEN:
  1. Log warning to console
  2. Show notification: "Document symbol completion disabled due to performance"
  3. Set featureFlags.documentSymbols = false
  4. Revert to static completion only
```

**Trigger 2: Memory Leak Detected**
```
IF: Memory increase > 2MB per file
THEN:
  1. Log error to console
  2. Show notification: "Document symbols disabled due to memory issue"
  3. Set featureFlags.documentSymbols = false
  4. Clear symbol cache
  5. Reload editor component
```

**Trigger 3: Extraction Errors**
```
IF: Extraction fails 10 consecutive times
THEN:
  1. Log error to console
  2. Disable document symbol extraction
  3. Continue with static completion only
  4. No user notification (silent fallback)
```

**Trigger 4: Bundle Size Exceeded**
```
IF: Bundle size increase > 10KB in CI/CD
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
☐ Document Symbol Completion

User can disable via:
- Settings panel
- localStorage: { documentSymbols: false }
- URL parameter: ?documentSymbols=false
```

**Option 2: Performance Mode**
```
When Performance Mode enabled:
- Disable document symbol extraction
- Use static completion only
- Faster but less context-aware
```

**Option 3: Emergency Disable**
```
Console command:
> window.__disableDocumentSymbols = true

Immediately disables feature without page reload
```

### Rollback Procedure

**Step 1: Detect Issue**
```
- Automated performance tests fail
- User reports lag when typing
- Monitoring alerts trigger
- High extraction error rate
```

**Step 2: Immediate Mitigation**
```
1. Deploy feature flag: documentSymbols: false
2. Push to production (no code change needed)
3. Notify users via banner: "Document symbols temporarily disabled"
4. Static completion continues working
```

**Step 3: Investigation**
```
1. Review performance metrics
2. Analyze error logs
3. Reproduce issue locally
4. Identify root cause (regex? large files? syntax errors?)
```

**Step 4: Fix or Revert**
```
Option A: Quick Fix
- Optimize regex patterns
- Add extraction timeout
- Deploy patch
- Re-enable feature flag

Option B: Partial Rollback
- Disable for large files (>1000 lines)
- Keep enabled for small files
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
frontend/src/composables/useDocumentSymbols.js (NEW, ~200 lines)
├── extractSymbols(code)
├── extractFunctions(code)
├── extractVariables(code)
├── extractClasses(code)
├── extractImports(code)
└── debounceExtraction()

frontend/src/composables/useCodeCompletion.js (MODIFY, +50 lines)
├── Integrate document symbols
├── Merge with static symbols
├── Deduplicate symbols
└── Prioritize document symbols

frontend/src/components/PythonCodeEditor.vue (MODIFY, +30 lines)
├── Import useDocumentSymbols composable
├── Trigger extraction on file load
├── Trigger re-extraction on change (debounced)
└── Pass document symbols to completion
```

### Key Algorithms

**Symbol Extraction (Regex-Based)**:
```javascript
function extractSymbols(code) {
  const symbols = [];

  // Extract function definitions
  const funcRegex = /def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(/g;
  let match;
  while ((match = funcRegex.exec(code)) !== null) {
    symbols.push({ name: match[1], type: 'function' });
  }

  // Extract variable assignments
  const varRegex = /^[ \t]*([a-zA-Z_][a-zA-Z0-9_]*)\s*=/gm;
  while ((match = varRegex.exec(code)) !== null) {
    symbols.push({ name: match[1], type: 'variable' });
  }

  // Extract class definitions
  const classRegex = /class\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
  while ((match = classRegex.exec(code)) !== null) {
    symbols.push({ name: match[1], type: 'class' });
  }

  // Extract imports
  const importRegex = /(?:import\s+([a-zA-Z_][a-zA-Z0-9_]*)|from\s+[\w.]+\s+import\s+([a-zA-Z_][a-zA-Z0-9_]*))/g;
  while ((match = importRegex.exec(code)) !== null) {
    const name = match[1] || match[2];
    if (name) symbols.push({ name, type: 'import' });
  }

  return symbols;
}
```

**Debounced Extraction**:
```javascript
let extractionTimer = null;
let lastCode = '';

function handleCodeChange(code) {
  // Skip if code hasn't changed significantly
  if (code === lastCode) return;

  clearTimeout(extractionTimer);

  extractionTimer = setTimeout(() => {
    const symbols = extractSymbols(code);
    updateCompletionData(symbols);
    lastCode = code;
  }, 500); // 500ms debounce
}
```

**Symbol Merging and Deduplication**:
```javascript
function mergeSymbols(staticSymbols, documentSymbols) {
  const symbolMap = new Map();

  // Add static symbols first
  staticSymbols.forEach(s => symbolMap.set(s.name, s));

  // Override with document symbols (higher priority)
  documentSymbols.forEach(s => symbolMap.set(s.name, s));

  return Array.from(symbolMap.values());
}
```

---
## Testing Checklist

### Unit Tests (90% coverage required)
- [ ] Function definitions extracted correctly
- [ ] Variable assignments extracted correctly
- [ ] Class definitions extracted correctly
- [ ] Import statements extracted correctly
- [ ] Multiple assignment extraction (a, b = 1, 2)
- [ ] Nested functions extracted
- [ ] Class methods extracted
- [ ] Function parameters extracted
- [ ] Symbols update in real-time (<500ms)
- [ ] Symbol deduplication works
- [ ] Document symbols prioritized over static
- [ ] Incremental extraction works (debounced 500ms)
- [ ] Extraction handles syntax errors gracefully
- [ ] Extraction doesn't crash on invalid code
- [ ] Symbol cache cleared on file change

### Integration Tests
- [ ] Works with static completion (Story 02)
- [ ] Works with auto-indentation (Story 01)
- [ ] Works with syntax highlighting
- [ ] Symbols appear in completion popup
- [ ] Document symbols ranked higher than static
- [ ] No duplicates in completion list
- [ ] Extraction doesn't block UI
- [ ] Re-extraction triggered on significant changes
- [ ] No re-extraction on every keystroke

### Performance Tests
- [ ] Symbol extraction <50ms (p95) for 500-line file
- [ ] Incremental update <20ms (p95)
- [ ] Bundle size <5KB increase
- [ ] Memory usage <1MB per file
- [ ] Combined completion <10ms (p95) with 335 symbols
- [ ] No lag when typing in large files

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
- [ ] Regex patterns optimized
- [ ] Extraction debouncing tested
- [ ] Symbol deduplication verified
- [ ] Error handling tested (invalid syntax)
- [ ] Memory leak testing passed
- [ ] Large file testing (1000+ lines)
- [ ] Deployed to staging
- [ ] User acceptance testing passed
- [ ] Deployed to production
- [ ] Monitoring alerts configured

---

**Story Status**: Ready for Development
**Last Updated**: 2026-02-26
**Approved By**: _____________

