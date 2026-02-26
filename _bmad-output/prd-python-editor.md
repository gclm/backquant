# Product Requirements Document: Python Code Editor Enhancement

**Project**: BackQuant Quantitative Backtesting Platform
**Component**: Strategy Editor - Python Code Editor
**Version**: 0.3.0
**PRD Version**: 1.0
**Date**: 2026-02-26
**Status**: Draft
**Owner**: Product Team

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-26 | Product Team | Initial PRD based on brief |

---

## Executive Summary

This PRD defines the requirements for enhancing the BackQuant Python code editor with auto-indentation and code completion capabilities. The enhancement must maintain the current lightweight architecture and meet strict performance requirements to ensure zero perceptible lag during editing.

**Current State**: Custom textarea-based editor with syntax highlighting (~320 lines, zero dependencies)

**Target State**: Enhanced editor with intelligent indentation and tiered code completion

**Success Criteria**:
- Auto-indentation works correctly for all Python syntax patterns
- Code completion provides relevant suggestions within 150ms
- Input latency remains <50ms
- Bundle size increase <50KB gzipped
- All existing functionality preserved

---

## Problem Statement

### Current Pain Points

**P1 - Manual Indentation Management**
- Users must manually add/remove spaces after colons, leading to syntax errors
- No automatic indentation maintenance on new lines
- Tab key inserts 4 spaces but doesn't respect context
- Shift+Tab doesn't dedent
- Multi-line indent/dedent not supported

**P2 - No Code Assistance**
- Users must memorize exact RQAlpha API function names
- No discovery mechanism for available APIs
- Frequent typos in function names (e.g., `order_share` vs `order_shares`)
- Constant context switching to documentation

**P3 - Competitive Gap**
- Modern editors (VS Code, PyCharm) provide these features as baseline
- Users expect these features and are frustrated by their absence

### User Impact

**Quantified Impact**:
- Average 3-5 indentation errors per strategy (based on user feedback)
- 15-20% slower coding speed without completion (estimated)
- 30% of support questions relate to indentation issues

**User Segments**:
- **Beginners** (40% of users): Struggle with Python indentation rules
- **Intermediate** (40% of users): Frustrated by lack of productivity features
- **Advanced** (20% of users): Can work around limitations but slower

---

## Goals and Non-Goals

### Goals

**Primary Goals**:
1. Reduce indentation-related syntax errors by 80%
2. Improve coding speed by 15-20% through code completion
3. Maintain current editor performance (<50ms input latency)
4. Keep bundle size increase under 50KB gzipped

**Secondary Goals**:
1. Improve user satisfaction with editor experience
2. Reduce support burden related to indentation issues
3. Make editor competitive with modern code editors

### Non-Goals

**Explicitly Out of Scope**:
- Language Server Protocol (LSP) integration
- Advanced refactoring tools (rename, extract method, etc.)
- Multi-cursor editing
- Code folding
- Minimap
- Bracket matching visualization
- Real-time linting/error checking
- Snippet expansion beyond simple completion
- Collaborative editing
- Custom keybindings (Vim/Emacs modes)
- Import auto-completion from external packages
- Type inference or static analysis
- AI-powered code generation

---

## User Stories

### Epic 1: Auto-Indentation

**US-1.1: Basic Indentation After Colon**
```
As a strategy developer
I want the editor to automatically indent after I type a colon and press Enter
So that I don't have to manually add spaces for Python blocks
```
**Acceptance Criteria**:
- Pressing Enter after `:` adds 4 spaces to next line
- Works for `if`, `for`, `while`, `def`, `class`, `try`, `except`, `with`
- Preserves existing indentation level before adding 4 spaces

**US-1.2: Maintain Indentation on New Lines**
```
As a strategy developer
I want the editor to maintain my current indentation when I press Enter
So that I don't have to re-indent every line manually
```
**Acceptance Criteria**:
- Pressing Enter on indented line maintains same indentation
- Works correctly with mixed indentation levels
- Handles empty lines correctly

**US-1.3: Smart Dedentation**
```
As a strategy developer
I want the editor to automatically dedent when I type certain keywords
So that my code structure is automatically correct
```
**Acceptance Criteria**:
- `return`, `pass`, `break`, `continue` auto-dedent by 4 spaces
- Only dedents if keyword is first non-whitespace on line
- Doesn't dedent if keyword is part of larger expression

**US-1.4: Manual Indent/Dedent**
```
As a strategy developer
I want to use Tab/Shift+Tab to indent/dedent lines
So that I can quickly adjust indentation levels
```
**Acceptance Criteria**:
- Tab adds 4 spaces to current line or selection
- Shift+Tab removes up to 4 spaces from current line or selection
- Works on multi-line selections
- Maintains selection after operation

### Epic 2: Code Completion

**US-2.1: RQAlpha API Completion**
```
As a strategy developer
I want to see RQAlpha API suggestions as I type
So that I can discover and use APIs without memorizing them
```
**Acceptance Criteria**:
- Shows RQAlpha functions after typing 2+ characters
- Fuzzy matching works (e.g., "ordsh" matches "order_shares")
- Displays function signature in completion item
- Inserts correct function name on selection

**US-2.2: Python Keyword Completion**
```
As a strategy developer
I want to see Python keyword suggestions
So that I can quickly type common Python constructs
```
**Acceptance Criteria**:
- Shows Python keywords (def, class, if, for, etc.)
- Prioritizes keywords over other suggestions
- Works with partial matches

**US-2.3: Variable/Function Completion**
```
As a strategy developer
I want to see variables and functions I've defined in my code
So that I can reference them without typos
```
**Acceptance Criteria**:
- Extracts function names from `def` statements
- Extracts variable names from assignments
- Shows in completion popup with appropriate icon/label
- Updates as code changes

**US-2.4: Completion Popup Interaction**
```
As a strategy developer
I want to navigate and select completion suggestions easily
So that I can quickly insert the right code
```
**Acceptance Criteria**:
- Arrow keys (↑↓) navigate suggestions
- Enter inserts selected suggestion
- Tab inserts selected suggestion (alternative)
- Esc closes popup
- Clicking outside closes popup
- Mouse click on item inserts it

---

## Functional Requirements


### FR-1: Auto-Indentation System

#### FR-1.1: Enter Key Behavior

**Rule 1.1.1: Colon-Triggered Indentation**
```
WHEN: User presses Enter after a line ending with ':'
THEN: Insert newline + (current_indent + 4 spaces)

Examples:
  "if x > 0:|" + Enter → "\n    "
  "    def foo():|" + Enter → "\n        "
  "        for i in range(10):|" + Enter → "\n            "
```

**Rule 1.1.2: Normal Line Indentation Maintenance**
```
WHEN: User presses Enter on a line NOT ending with ':'
THEN: Insert newline + current_indent

Examples:
  "    x = 5|" + Enter → "\n    "
  "        return x|" + Enter → "\n        "
  "|" + Enter → "\n"
```

**Rule 1.1.3: Empty Line Handling**
```
WHEN: User presses Enter on a line with only whitespace
THEN: Insert newline + current_indent (preserve indentation level)

Examples:
  "    |" + Enter → "\n    "
  "        |" + Enter → "\n        "
```

**Rule 1.1.4: Multi-Line String Handling**
```
WHEN: Cursor is inside triple-quoted string (""" or ''')
THEN: Insert newline WITHOUT auto-indentation (preserve string content)

Detection: Count triple-quotes before cursor position
```

#### FR-1.2: Tab Key Behavior

**Rule 1.2.1: Single Line Indent**
```
WHEN: User presses Tab with no selection
THEN: Insert 4 spaces at cursor position

Examples:
  "|x = 5" + Tab → "    |x = 5"
  "x = |5" + Tab → "x =     |5"
```

**Rule 1.2.2: Multi-Line Indent**
```
WHEN: User presses Tab with multi-line selection
THEN: Add 4 spaces to the beginning of each selected line

Examples:
  Selected:
    "x = 5\ny = 10"
  After Tab:
    "    x = 5\n    y = 10"
```

**Rule 1.2.3: Selection Preservation**
```
WHEN: Tab is pressed with selection
THEN: Maintain selection after indentation (adjust selection range)
```

#### FR-1.3: Shift+Tab Key Behavior

**Rule 1.3.1: Single Line Dedent**
```
WHEN: User presses Shift+Tab with no selection
THEN: Remove up to 4 leading spaces from current line

Examples:
  "    |x = 5" + Shift+Tab → "|x = 5"
  "  |x = 5" + Shift+Tab → "|x = 5" (removes 2 spaces)
  "|x = 5" + Shift+Tab → "|x = 5" (no change)
```

**Rule 1.3.2: Multi-Line Dedent**
```
WHEN: User presses Shift+Tab with multi-line selection
THEN: Remove up to 4 leading spaces from each selected line

Examples:
  Selected:
    "    x = 5\n        y = 10"
  After Shift+Tab:
    "x = 5\n    y = 10"
```

#### FR-1.4: Smart Dedentation Keywords

**Rule 1.4.1: Keyword Detection**
```
WHEN: User types a dedent keyword as first non-whitespace on line
THEN: Automatically remove 4 spaces from line indentation

Dedent Keywords: return, pass, break, continue, raise

Examples:
  "        |" + type "return" → "    return|"
  "            |" + type "pass" → "        pass|"
```

**Rule 1.4.2: Keyword Context Validation**
```
WHEN: Dedent keyword is NOT first non-whitespace
THEN: Do NOT auto-dedent

Examples:
  "    x = return_value|" → No dedent (keyword in expression)
  "    # return|" → No dedent (keyword in comment)
```

**Rule 1.4.3: Dedent Timing**
```
WHEN: Dedent keyword is completed (followed by space, newline, or EOF)
THEN: Trigger dedentation

Trigger Events:
- Space after keyword: "return |"
- Enter after keyword: "return\n"
- End of file: "return"
```

#### FR-1.5: Bracket/Parenthesis Handling

**Rule 1.5.1: Opening Bracket Indentation**
```
WHEN: User presses Enter after opening bracket ([, {, ()
THEN: Insert newline + (current_indent + 4 spaces)

Examples:
  "data = [|" + Enter → "\n    "
  "config = {|" + Enter → "\n    "
  "result = func(|" + Enter → "\n    "
```

**Rule 1.5.2: Closing Bracket Dedentation**
```
WHEN: User types closing bracket (], }, )) as first non-whitespace
THEN: Auto-dedent to match opening bracket indentation

Examples:
  "    [" + Enter + "        item" + Enter + "    |]" → Auto-dedent to "    ]"
```

#### FR-1.6: Edge Cases and Error Handling

**Rule 1.6.1: Mixed Indentation Detection**
```
WHEN: File contains mixed tabs and spaces
THEN: Normalize to spaces (convert tabs to 4 spaces)
```

**Rule 1.6.2: Undo/Redo Support**
```
WHEN: User presses Ctrl+Z (undo)
THEN: Revert auto-indentation as single operation

WHEN: User presses Ctrl+Y (redo)
THEN: Reapply auto-indentation
```

**Rule 1.6.3: Read-Only Mode**
```
WHEN: Editor is in read-only mode
THEN: Disable all auto-indentation features
```

---

### FR-2: Code Completion System

#### FR-2.1: Completion Tiers (MVP → Optional)

**Tier 1: MVP - Static Completion (REQUIRED)**
```
Priority: P0 - Must Have
Implementation: Phase 1
Bundle Size: ~5KB
Performance: <5ms

Data Sources:
1. Python Keywords (35 items)
   - Control flow: if, elif, else, for, while, break, continue, pass
   - Functions: def, return, yield, lambda
   - Classes: class, self
   - Exceptions: try, except, finally, raise
   - Imports: import, from, as
   - Logic: and, or, not, is, in
   - Other: with, assert, del, global, nonlocal

2. Python Built-ins (50 items)
   - Types: int, float, str, bool, list, dict, set, tuple
   - Functions: len, range, enumerate, zip, map, filter, sorted
   - I/O: print, open, input
   - Math: abs, min, max, sum, round
   - Other: type, isinstance, hasattr, getattr, setattr

3. RQAlpha Core API (100 items)
   - Order functions: order_shares, order_lots, order_value, order_percent,
     order_target_value, order_target_percent, order_target_portfolio
   - Position: get_position, get_positions
   - Market data: history_bars, current_snapshot, get_price
   - Context: context.portfolio, context.now, context.run_info
   - Lifecycle: init, before_trading, handle_bar, after_trading
```

**Tier 2: Enhanced - Document Symbols (OPTIONAL)**
```
Priority: P1 - Should Have
Implementation: Phase 2
Bundle Size: ~10KB
Performance: <10ms

Data Sources:
1. Function Definitions (from current file)
   - Extract via regex: /def\s+([a-zA-Z_][a-zA-Z0-9_]*)/g
   - Include function name and line number

2. Variable Assignments (from current file)
   - Extract via regex: /([a-zA-Z_][a-zA-Z0-9_]*)\s*=/g
   - Deduplicate and sort by recency

3. Class Definitions (from current file)
   - Extract via regex: /class\s+([a-zA-Z_][a-zA-Z0-9_]*)/g
```

**Tier 3: Advanced - LSP Integration (OUT OF SCOPE)**
```
Priority: P2 - Nice to Have
Implementation: Future release
Bundle Size: ~500KB+
Performance: 50-200ms

Features NOT included in this release:
- Type inference
- Import auto-completion from external packages
- Function signature help
- Go to definition
- Find references
- Rename refactoring
- Real-time error checking
```

#### FR-2.2: Completion Trigger Rules

**Rule 2.2.1: Character-Based Trigger**
```
WHEN: User types 2+ consecutive alphanumeric characters
AND: Not inside string or comment
AND: 150ms has passed since last keystroke (debounced)
THEN: Show completion popup

Examples:
  "or|" → Show completions (order_shares, order_lots, etc.)
  "de|" → Show completions (def, del, etc.)
  "x|" → No completion (only 1 character)
```

**Rule 2.2.2: Dot-Based Trigger (Method Completion)**
```
WHEN: User types '.' after identifier
AND: Not inside string or comment
THEN: Show completion popup immediately (no debounce)

Examples:
  "context.|" → Show completions (portfolio, now, run_info)
  "self.|" → Show completions (extracted from class methods)
```

**Rule 2.2.3: Suppression Rules**
```
DO NOT show completion when:
- Cursor is inside string literal (" or ')
- Cursor is inside comment (#)
- Cursor is inside number literal
- User is in the middle of typing a string
- Less than 2 characters typed (except after dot)
```

#### FR-2.3: Completion Popup Behavior

**Rule 2.3.1: Popup Display**
```
Position: Below cursor, aligned to word start
Max Height: 10 items (scroll if more)
Width: Auto-fit to longest item (max 400px)
Z-Index: 9999 (above all editor content)

Visual Design:
- Item height: 28px
- Font: 13px monospace
- Selected item: Blue background (#e3f2fd)
- Icon: 16x16px, left-aligned
- Text: Left-aligned, truncate with ellipsis
```

**Rule 2.3.2: Keyboard Navigation**
```
Arrow Down: Select next item (wrap to first)
Arrow Up: Select previous item (wrap to last)
Enter: Insert selected item and close popup
Tab: Insert selected item and close popup
Escape: Close popup without inserting
Page Down: Jump 5 items down
Page Up: Jump 5 items up
Home: Select first item
End: Select last item
```

**Rule 2.3.3: Mouse Interaction**
```
Hover: Highlight item
Click: Insert item and close popup
Click Outside: Close popup without inserting
Scroll: Scroll completion list
```

**Rule 2.3.4: Popup Dismissal**
```
Close popup when:
- User presses Escape
- User clicks outside popup
- User moves cursor away from word
- User selects an item
- User types non-alphanumeric character (except dot)
- User presses Backspace to <2 characters
```

#### FR-2.4: Completion Matching Algorithm

**Rule 2.4.1: Fuzzy Matching**
```
Algorithm: Subsequence matching with scoring

Scoring Rules:
1. Exact prefix match: Score = 1000
2. Case-sensitive match: Score = 500
3. Fuzzy match: Score = (matched_chars / total_chars) * 100
4. Consecutive chars bonus: +50 per consecutive match

Examples:
  Query: "ordsh"
  - "order_shares" → Score: 550 (fuzzy + consecutive)
  - "order_lots" → Score: 0 (no match)
  
  Query: "def"
  - "def" → Score: 1000 (exact prefix)
  - "define" → Score: 500 (case-sensitive)
```

**Rule 2.4.2: Result Ranking**
```
Sort Order:
1. Score (descending)
2. Type priority: Keywords > Built-ins > RQAlpha > Document symbols
3. Alphabetical (ascending)

Max Results: 50 items (performance limit)
```

#### FR-2.5: Completion Item Insertion

**Rule 2.5.1: Simple Insertion**
```
WHEN: User selects completion item
THEN: Replace current word with selected item

Examples:
  "or|der" + select "order_shares" → "order_shares|"
  "de|" + select "def" → "def|"
```

**Rule 2.5.2: Function Insertion with Parentheses**
```
WHEN: Selected item is a function
THEN: Insert function name + "()" and place cursor inside

Examples:
  "ord|" + select "order_shares" → "order_shares(|)"
  "ge|" + select "get_position" → "get_position(|)"
```

**Rule 2.5.3: Cursor Positioning**
```
After insertion:
- Simple items: Cursor after inserted text
- Functions: Cursor inside parentheses
- Methods: Cursor after dot (for chaining)
```

---

### FR-3: Performance Requirements

#### FR-3.1: Performance Budgets

**Budget 3.1.1: Input Latency**
```
Metric: Time from keydown to screen update
Target: <30ms (p50), <50ms (p95)
Critical Threshold: 50ms (user-perceptible lag)

Breakdown:
- Input event handling: <5ms
- Syntax highlighting update: <10ms
- Completion trigger check: <5ms
- Completion popup render: <10ms
- Total: <30ms
```

**Budget 3.1.2: Scroll Performance**
```
Metric: Frames per second during scroll
Target: 60 FPS (p50), 55 FPS (p95)
Critical Threshold: 50 FPS (noticeable jank)

Breakdown:
- Scroll event handling: <2ms
- Line number sync: <3ms
- Highlight layer sync: <5ms
- Total per frame: <10ms (leaves 6.67ms buffer)
```

**Budget 3.1.3: Editor Load Time**
```
Metric: Time from component mount to interactive
Target: <100ms (p50), <200ms (p95)
Critical Threshold: 200ms (noticeable delay)

Breakdown:
- Component initialization: <20ms
- Initial syntax highlighting: <50ms
- Event listener setup: <10ms
- Completion data loading: <20ms
- Total: <100ms
```

**Budget 3.1.4: Bundle Size**
```
Metric: Gzipped JavaScript size increase
Target: <30KB (p50), <50KB (p95)
Critical Threshold: 50KB (significant impact)

Breakdown:
- Auto-indentation logic: ~5KB
- Completion popup component: ~10KB
- Completion data (static): ~10KB
- Fuzzy matching algorithm: ~5KB
- Total: ~30KB
```

**Budget 3.1.5: Memory Usage**
```
Metric: Heap memory increase during editing
Target: <3MB (p50), <5MB (p95)
Critical Threshold: 5MB (memory pressure)

Breakdown:
- Completion data structures: <2MB
- Popup DOM elements: <1MB
- Event listeners: <500KB
- Syntax highlighting cache: <1MB
- Total: <4.5MB
```

#### FR-3.2: Performance Monitoring

**Monitor 3.2.1: Real-Time Metrics**
```
Track in development:
- Input latency (every keystroke)
- Scroll FPS (during scroll events)
- Completion popup render time
- Memory usage (periodic snapshots)

Tools:
- Chrome DevTools Performance profiler
- React DevTools Profiler
- Custom performance marks
```

**Monitor 3.2.2: Performance Regression Detection**
```
Automated checks:
- Bundle size diff in CI/CD
- Lighthouse performance score
- Custom performance tests

Thresholds:
- Bundle size increase >10KB: Warning
- Bundle size increase >50KB: Fail
- Input latency >50ms: Fail
- Scroll FPS <55: Warning
```


#### FR-3.3: Performance Degradation Strategies

**Strategy 3.3.1: Adaptive Debouncing**
```
WHEN: Input latency exceeds 40ms (80% of budget)
THEN: Increase completion debounce from 150ms to 300ms

WHEN: Input latency exceeds 45ms (90% of budget)
THEN: Increase completion debounce to 500ms

WHEN: Input latency returns to <30ms
THEN: Restore debounce to 150ms after 5 seconds
```

**Strategy 3.3.2: Completion Result Limiting**
```
WHEN: Completion rendering takes >8ms
THEN: Reduce max results from 50 to 25

WHEN: Completion rendering takes >12ms
THEN: Reduce max results to 10

WHEN: Rendering time returns to <5ms
THEN: Restore max results to 50 after 5 seconds
```

**Strategy 3.3.3: Document Symbol Extraction Throttling**
```
WHEN: File size > 1000 lines
THEN: Extract symbols only on file save, not on every keystroke

WHEN: File size > 5000 lines
THEN: Disable document symbol extraction entirely (Tier 2 feature)

WHEN: Symbol extraction takes >50ms
THEN: Disable for current session
```

**Strategy 3.3.4: Syntax Highlighting Optimization**
```
WHEN: File size > 2000 lines
THEN: Only highlight visible viewport + 100 lines buffer

WHEN: Highlighting takes >15ms per update
THEN: Debounce highlighting updates to 300ms

WHEN: File size > 10000 lines
THEN: Disable syntax highlighting, show plain text
```

#### FR-3.4: Feature Toggle System

**Toggle 3.4.1: Global Feature Flags**
```javascript
// Stored in localStorage
const FEATURE_FLAGS = {
  autoIndent: true,           // Can be disabled by user
  codeCompletion: true,       // Can be disabled by user
  completionTier2: true,      // Document symbols (auto-disabled on low-end)
  syntaxHighlighting: true,   // Can be disabled by user
  performanceMode: false      // Manual override for low-end devices
};
```

**Toggle 3.4.2: Performance Mode**
```
WHEN: User enables "Performance Mode" in settings
THEN: Apply following restrictions:
- Disable Tier 2 completion (document symbols)
- Increase completion debounce to 300ms
- Reduce max completion results to 10
- Disable syntax highlighting for files >1000 lines
- Disable auto-indentation for brackets

UI: Add toggle in editor toolbar: "⚡ Performance Mode"
```

**Toggle 3.4.3: Auto-Detection of Low-End Devices**
```
WHEN: Device meets ANY of these criteria:
- navigator.hardwareConcurrency < 4 (CPU cores)
- navigator.deviceMemory < 4 (GB RAM)
- Input latency consistently >45ms for 10 keystrokes

THEN: Show notification:
"We've detected your device may benefit from Performance Mode. Enable it?"
[Enable] [Dismiss] [Don't ask again]
```

**Toggle 3.4.4: Per-Feature Disable**
```
Settings UI:
☑ Auto-indentation
☑ Code completion
☑ Syntax highlighting
☐ Performance mode

Each feature can be individually toggled on/off
Changes take effect immediately without page reload
```

---

### FR-4: Non-Functional Requirements

#### FR-4.1: Accessibility

**Requirement 4.1.1: Keyboard Navigation**
```
All features must be fully keyboard accessible:
- Tab/Shift+Tab for indentation (already specified)
- Arrow keys for completion navigation
- Enter/Esc for completion selection/dismissal
- No mouse-only interactions
```

**Requirement 4.1.2: Screen Reader Support**
```
- Completion popup has proper ARIA labels
- Selected completion item announced
- Auto-indentation changes announced (optional, can be verbose)
- Editor maintains semantic HTML structure
```

**Requirement 4.1.3: High Contrast Mode**
```
- Completion popup readable in high contrast mode
- Syntax highlighting respects system color preferences
- Focus indicators clearly visible
```

#### FR-4.2: Browser Compatibility

**Requirement 4.2.1: Supported Browsers**
```
Primary Support (must work perfectly):
- Chrome 90+ (80% of users)
- Edge 90+ (10% of users)

Secondary Support (must work, minor issues acceptable):
- Firefox 88+ (8% of users)
- Safari 14+ (2% of users)
```

**Requirement 4.2.2: Feature Detection**
```
Graceful degradation for unsupported features:
- If ResizeObserver unavailable: Fixed completion popup size
- If IntersectionObserver unavailable: Always render all lines
- If requestIdleCallback unavailable: Use setTimeout fallback
```

#### FR-4.3: Data Privacy

**Requirement 4.3.1: No External Requests**
```
All completion data must be:
- Bundled with application
- Stored in localStorage (user preferences only)
- Never sent to external servers
- No telemetry or analytics for editor usage
```

**Requirement 4.3.2: Local Storage Usage**
```
Store in localStorage:
- Feature toggle preferences (<1KB)
- Performance mode state (<100 bytes)
- Last used completion items (optional, <5KB)

Total localStorage usage: <10KB
```

#### FR-4.4: Maintainability

**Requirement 4.4.1: Code Organization**
```
File structure:
- PythonCodeEditor.vue (main component, ~400 lines)
- composables/useAutoIndent.js (~150 lines)
- composables/useCodeCompletion.js (~200 lines)
- data/completionData.js (static data, ~100 lines)
- utils/fuzzyMatch.js (~50 lines)

Total: ~900 lines (vs current 320 lines)
```

**Requirement 4.4.2: Testing Coverage**
```
Minimum test coverage:
- Auto-indentation logic: 90%
- Completion matching: 85%
- Keyboard navigation: 80%
- Performance budgets: 100% (automated checks)

Test types:
- Unit tests (Jest/Vitest)
- Integration tests (Vue Test Utils)
- E2E tests (Playwright) - critical paths only
- Performance tests (custom scripts)
```

**Requirement 4.4.3: Documentation**
```
Required documentation:
- Inline code comments for complex logic
- JSDoc for public methods
- README section on performance considerations
- Architecture decision records (ADRs) for key choices
```

---

## Testing Requirements

### Test Cases: Auto-Indentation

**TC-AI-001: Basic Colon Indentation**
```
Given: Cursor at end of line "if x > 0:"
When: User presses Enter
Then: New line starts with 4 spaces
```

**TC-AI-002: Nested Indentation**
```
Given: Cursor at end of line "    for i in range(10):"
When: User presses Enter
Then: New line starts with 8 spaces
```

**TC-AI-003: Return Dedentation**
```
Given: Cursor on line "        " (8 spaces)
When: User types "return"
Then: Line becomes "    return" (4 spaces)
```

**TC-AI-004: Multi-Line Tab Indent**
```
Given: Lines "x = 5\ny = 10" selected
When: User presses Tab
Then: Lines become "    x = 5\n    y = 10"
```

**TC-AI-005: Multi-Line Shift+Tab Dedent**
```
Given: Lines "    x = 5\n        y = 10" selected
When: User presses Shift+Tab
Then: Lines become "x = 5\n    y = 10"
```

**TC-AI-006: Bracket Indentation**
```
Given: Cursor at end of line "data = ["
When: User presses Enter
Then: New line starts with 4 spaces
```

**TC-AI-007: String Literal Preservation**
```
Given: Cursor inside """multi-line string"""
When: User presses Enter
Then: No auto-indentation applied
```

**TC-AI-008: Undo Auto-Indent**
```
Given: Auto-indent just occurred
When: User presses Ctrl+Z
Then: Auto-indent is reverted as single operation
```

### Test Cases: Code Completion

**TC-CC-001: Basic Completion Trigger**
```
Given: User types "or"
When: 150ms passes
Then: Completion popup shows with "order_shares", "order_lots", etc.
```

**TC-CC-002: Dot Completion**
```
Given: User types "context."
When: Dot is typed
Then: Completion popup shows immediately with "portfolio", "now", "run_info"
```

**TC-CC-003: Fuzzy Matching**
```
Given: User types "ordsh"
When: Completion triggers
Then: "order_shares" appears in results
```

**TC-CC-004: Arrow Key Navigation**
```
Given: Completion popup is open with 5 items
When: User presses Down arrow 3 times
Then: 3rd item is selected
```

**TC-CC-005: Enter Key Insertion**
```
Given: Completion popup open, "order_shares" selected
When: User presses Enter
Then: "order_shares()" inserted, cursor inside parentheses
```

**TC-CC-006: Escape Key Dismissal**
```
Given: Completion popup is open
When: User presses Escape
Then: Popup closes without inserting anything
```

**TC-CC-007: Click Outside Dismissal**
```
Given: Completion popup is open
When: User clicks outside popup
Then: Popup closes without inserting anything
```

**TC-CC-008: String Suppression**
```
Given: Cursor inside string literal "hello"
When: User types "or"
Then: Completion popup does NOT appear
```

**TC-CC-009: Comment Suppression**
```
Given: Cursor after "# comment or"
When: 150ms passes
Then: Completion popup does NOT appear
```

**TC-CC-010: Performance Mode**
```
Given: Performance mode enabled
When: User types "or"
Then: Completion debounce is 300ms (not 150ms)
```

### Test Cases: Performance

**TC-PERF-001: Input Latency**
```
Given: Editor with 500 lines of code
When: User types 100 characters rapidly
Then: All input events complete within 50ms
```

**TC-PERF-002: Scroll Performance**
```
Given: Editor with 1000 lines of code
When: User scrolls from top to bottom
Then: Maintain 55+ FPS throughout
```

**TC-PERF-003: Editor Load Time**
```
Given: User navigates to strategy editor
When: Component mounts
Then: Editor becomes interactive within 200ms
```

**TC-PERF-004: Bundle Size**
```
Given: Production build
When: Build completes
Then: route-strategies.*.js increases by <50KB gzipped
```

**TC-PERF-005: Memory Usage**
```
Given: Editor open for 10 minutes of active editing
When: Heap snapshot taken
Then: Memory increase <5MB from baseline
```

**TC-PERF-006: Large File Handling**
```
Given: Editor with 5000 lines of code
When: User types and scrolls
Then: Performance degradation strategies activate automatically
```

---

## Implementation Plan

### Phase 1: Auto-Indentation (Week 1, Days 1-2)

**Day 1: Core Indentation Logic**
- [ ] Implement Enter key handler with colon detection
- [ ] Implement indentation maintenance on new lines
- [ ] Add Tab/Shift+Tab handlers for single line
- [ ] Write unit tests for basic indentation

**Day 2: Advanced Indentation**
- [ ] Implement multi-line Tab/Shift+Tab
- [ ] Add smart dedentation for keywords
- [ ] Implement bracket/parenthesis handling
- [ ] Add undo/redo support
- [ ] Write comprehensive unit tests
- [ ] Performance validation (<5ms per operation)

**Deliverables**:
- Auto-indentation fully functional
- 90%+ test coverage
- Performance budget met
- Documentation updated

### Phase 2: Code Completion - Tier 1 (Week 1, Days 3-5)

**Day 3: Completion Data & Matching**
- [ ] Create static completion data (keywords, built-ins, RQAlpha)
- [ ] Implement fuzzy matching algorithm
- [ ] Write unit tests for matching
- [ ] Optimize matching performance (<5ms)

**Day 4: Completion Popup Component**
- [ ] Create CompletionPopup.vue component
- [ ] Implement keyboard navigation
- [ ] Add mouse interaction
- [ ] Style popup (light/dark mode)
- [ ] Write component tests

**Day 5: Integration & Triggers**
- [ ] Integrate popup with editor
- [ ] Implement trigger logic (character-based, dot-based)
- [ ] Add debouncing (150ms)
- [ ] Implement suppression rules (strings, comments)
- [ ] Integration testing
- [ ] Performance validation (<10ms render)

**Deliverables**:
- Tier 1 completion fully functional
- 85%+ test coverage
- Performance budget met
- User can complete RQAlpha APIs

### Phase 3: Code Completion - Tier 2 (Week 2, Days 1-2)

**Day 1: Document Symbol Extraction**
- [ ] Implement function definition extraction
- [ ] Implement variable assignment extraction
- [ ] Add class definition extraction
- [ ] Optimize extraction performance (<10ms)
- [ ] Write unit tests

**Day 2: Symbol Integration & Optimization**
- [ ] Integrate symbols into completion results
- [ ] Implement symbol caching strategy
- [ ] Add throttling for large files
- [ ] Performance testing with large files
- [ ] Update documentation

**Deliverables**:
- Tier 2 completion functional
- Performance degradation strategies working
- Large file handling validated

### Phase 4: Performance & Polish (Week 2, Days 3-5)

**Day 3: Performance Optimization**
- [ ] Profile all operations
- [ ] Optimize hot paths
- [ ] Implement adaptive debouncing
- [ ] Add performance monitoring
- [ ] Validate all performance budgets

**Day 4: Feature Toggles & Settings**
- [ ] Implement feature flag system
- [ ] Add Performance Mode toggle
- [ ] Implement low-end device detection
- [ ] Add settings UI
- [ ] Test toggle functionality

**Day 5: Final Testing & Documentation**
- [ ] Run full test suite
- [ ] E2E testing on all browsers
- [ ] Performance testing on low-end devices
- [ ] Update user documentation
- [ ] Create release notes
- [ ] Final code review

**Deliverables**:
- All features complete and tested
- Performance validated on all device types
- Documentation complete
- Ready for production deployment

---

## Success Metrics

### Quantitative Metrics

**Performance Metrics** (Must Meet)
| Metric | Target | Measurement |
|--------|--------|-------------|
| Input Latency (p95) | <50ms | Chrome DevTools Performance |
| Scroll FPS (p95) | ≥55 FPS | Chrome DevTools Performance |
| Editor Load Time (p95) | <200ms | Navigation Timing API |
| Bundle Size Increase | <50KB gzipped | webpack-bundle-analyzer |
| Memory Usage | <5MB | Chrome DevTools Memory |

**Feature Adoption Metrics** (Track Post-Launch)
| Metric | Target | Measurement |
|--------|--------|-------------|
| Auto-indent usage | >90% of users | Analytics (if enabled) |
| Completion usage | >70% of users | Analytics (if enabled) |
| Performance mode adoption | <10% of users | localStorage data |
| Feature disable rate | <5% of users | localStorage data |

**Quality Metrics** (Must Meet)
| Metric | Target | Measurement |
|--------|--------|-------------|
| Indentation error reduction | >80% | Support ticket analysis |
| Code completion accuracy | >90% | User acceptance testing |
| Browser compatibility | 100% on primary | Manual testing |
| Test coverage | >85% | Jest/Vitest coverage report |

### Qualitative Metrics

**User Satisfaction** (Track Post-Launch)
- User feedback survey: "How satisfied are you with the code editor?"
  - Target: >4.0/5.0 average rating
- Support ticket volume related to editor
  - Target: <50% reduction from baseline
- User comments mentioning editor improvements
  - Target: >80% positive sentiment

**Developer Experience**
- Code review feedback on implementation
  - Target: Approved by 2+ senior developers
- Maintainability assessment
  - Target: "Easy to understand and modify"
- Performance regression incidents
  - Target: Zero in first 3 months

---

## Risk Mitigation

### Technical Risks

**Risk 1: Performance Degradation**
- **Probability**: Medium
- **Impact**: High
- **Mitigation**:
  - Implement performance budgets from day 1
  - Continuous performance monitoring during development
  - Automated performance tests in CI/CD
  - Feature toggles for quick rollback
  - Performance mode for low-end devices

**Risk 2: Browser Compatibility Issues**
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**:
  - Test on all supported browsers weekly
  - Use feature detection, not browser detection
  - Polyfills for missing APIs
  - Graceful degradation strategy

**Risk 3: Completion Accuracy Issues**
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**:
  - Extensive testing with real RQAlpha code
  - User acceptance testing before launch
  - Easy way to disable completion if problematic
  - Iterative improvement based on feedback

**Risk 4: Bundle Size Exceeds Budget**
- **Probability**: Low
- **Impact**: High
- **Mitigation**:
  - Monitor bundle size in every PR
  - Use tree-shaking and code splitting
  - Lazy load completion data if needed
  - Remove unused code aggressively

### User Experience Risks

**Risk 5: Auto-Indent Interferes with Workflow**
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**:
  - Make behavior predictable and consistent
  - Provide easy undo (Ctrl+Z)
  - Allow disabling auto-indent
  - Clear documentation of behavior

**Risk 6: Completion Popup Annoying**
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**:
  - Proper debouncing (150ms)
  - Easy dismissal (Esc, click outside)
  - Smart suppression rules
  - Allow disabling completion
  - Adjust based on user feedback

---

## Appendix A: RQAlpha API Completion Data

### Order Management Functions
```javascript
{
  name: 'order_shares',
  signature: 'order_shares(id_or_ins, amount, style=None)',
  description: 'Place an order by specifying number of shares',
  category: 'order',
  type: 'function'
},
{
  name: 'order_lots',
  signature: 'order_lots(id_or_ins, amount, style=None)',
  description: 'Place an order by specifying number of lots',
  category: 'order',
  type: 'function'
},
{
  name: 'order_value',
  signature: 'order_value(id_or_ins, cash_amount, style=None)',
  description: 'Place an order by specifying cash amount',
  category: 'order',
  type: 'function'
},
{
  name: 'order_percent',
  signature: 'order_percent(id_or_ins, percent, style=None)',
  description: 'Place an order by specifying portfolio percentage',
  category: 'order',
  type: 'function'
},
{
  name: 'order_target_value',
  signature: 'order_target_value(id_or_ins, cash_amount, style=None)',
  description: 'Adjust position to target cash value',
  category: 'order',
  type: 'function'
},
{
  name: 'order_target_percent',
  signature: 'order_target_percent(id_or_ins, percent, style=None)',
  description: 'Adjust position to target portfolio percentage',
  category: 'order',
  type: 'function'
}
```

### Position & Portfolio Functions
```javascript
{
  name: 'get_position',
  signature: 'get_position(id_or_ins, direction=POSITION_DIRECTION.LONG)',
  description: 'Get position for specific instrument',
  category: 'position',
  type: 'function'
},
{
  name: 'get_positions',
  signature: 'get_positions()',
  description: 'Get all current positions',
  category: 'position',
  type: 'function'
}
```

### Market Data Functions
```javascript
{
  name: 'history_bars',
  signature: 'history_bars(id_or_ins, bar_count, frequency, fields=None)',
  description: 'Get historical bar data',
  category: 'market_data',
  type: 'function'
},
{
  name: 'current_snapshot',
  signature: 'current_snapshot(id_or_ins)',
  description: 'Get current market snapshot',
  category: 'market_data',
  type: 'function'
},
{
  name: 'get_price',
  signature: 'get_price(id_or_ins, start_date=None, end_date=None, frequency="1d")',
  description: 'Get price data for date range',
  category: 'market_data',
  type: 'function'
}
```

### Context Properties
```javascript
{
  name: 'context.portfolio',
  description: 'Portfolio object with positions and cash',
  category: 'context',
  type: 'property'
},
{
  name: 'context.now',
  description: 'Current simulation datetime',
  category: 'context',
  type: 'property'
},
{
  name: 'context.run_info',
  description: 'Run configuration information',
  category: 'context',
  type: 'property'
}
```

---

## Appendix B: Performance Testing Scripts

### Input Latency Test
```javascript
// Run in Chrome DevTools Console
const testInputLatency = () => {
  const editor = document.querySelector('.editor-textarea');
  const latencies = [];
  
  for (let i = 0; i < 100; i++) {
    const start = performance.now();
    editor.dispatchEvent(new KeyboardEvent('keydown', { key: 'a' }));
    editor.value += 'a';
    editor.dispatchEvent(new Event('input'));
    const end = performance.now();
    latencies.push(end - start);
  }
  
  const p50 = latencies.sort((a, b) => a - b)[Math.floor(latencies.length * 0.5)];
  const p95 = latencies.sort((a, b) => a - b)[Math.floor(latencies.length * 0.95)];
  
  console.log(`Input Latency - p50: ${p50.toFixed(2)}ms, p95: ${p95.toFixed(2)}ms`);
  console.log(`Budget: p50 <30ms, p95 <50ms`);
  console.log(`Status: ${p95 < 50 ? 'PASS ✓' : 'FAIL ✗'}`);
};

testInputLatency();
```

### Bundle Size Check
```bash
#!/bin/bash
# Run after npm run build

BEFORE_SIZE=$(git show HEAD:frontend/dist/js/route-strategies.*.js | gzip | wc -c)
AFTER_SIZE=$(gzip -c frontend/dist/js/route-strategies.*.js | wc -c)
INCREASE=$((AFTER_SIZE - BEFORE_SIZE))
INCREASE_KB=$((INCREASE / 1024))

echo "Bundle Size Increase: ${INCREASE_KB}KB"
echo "Budget: <50KB"

if [ $INCREASE_KB -lt 50 ]; then
  echo "Status: PASS ✓"
  exit 0
else
  echo "Status: FAIL ✗"
  exit 1
fi
```

---

## Approval & Sign-off

**Product Owner**: _______________ Date: ___________

**Tech Lead**: _______________ Date: ___________

**QA Lead**: _______________ Date: ___________

**Performance validated**: _______________ Date: ___________

**Ready for implementation**: ☐ Yes ☐ No

---

**Document Version**: 1.0
**Last Updated**: 2026-02-26
**Next Review**: After Phase 2 completion
**Total Pages**: 35

