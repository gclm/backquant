# Product Brief: Python Code Editor Enhancement

**Project**: BackQuant Quantitative Backtesting Platform
**Component**: Strategy Editor - Python Code Editor
**Version**: 0.3.0
**Date**: 2026-02-26
**Status**: Draft

---

## Executive Summary

Enhance the existing Python code editor in the strategy editing interface with auto-indentation and code completion capabilities while maintaining the current lightweight, performant architecture. The enhancement must not introduce any perceptible lag in typing, scrolling, or editor initialization.

**Current State**: Custom-built textarea-based editor with syntax highlighting (~320 lines, zero external editor dependencies)

**Target State**: Enhanced editor with intelligent indentation and context-aware code completion, maintaining sub-50ms input latency

---

## Problem Statement

### Current Pain Points

1. **Manual Indentation Management**: Users must manually manage Python indentation after colons, leading to:
   - Frequent syntax errors from incorrect indentation
   - Slower coding workflow
   - Cognitive overhead tracking indentation levels

2. **No Code Assistance**: Users must remember exact RQAlpha API names and signatures:
   - Slows down strategy development
   - Increases likelihood of typos
   - Requires constant reference to documentation

3. **Competitive Gap**: Modern code editors provide these features as baseline expectations

### User Impact

- **Beginner Users**: Struggle with Python indentation rules, make frequent errors
- **Experienced Users**: Frustrated by lack of productivity features they expect from modern editors
- **All Users**: Slower strategy development cycle, more time debugging indentation issues

---

## User Needs

### Primary Needs

1. **Auto-Indentation** (P0 - Critical)
   - Automatic indentation after colons (`:`)
   - Maintain indentation on new lines
   - Smart dedentation for `return`, `break`, `continue`, `pass`
   - Tab/Shift+Tab for indent/dedent selected lines

2. **Code Completion** (P0 - Critical)
   - RQAlpha API completion (`order_`, `get_`, `update_`, etc.)
   - Python built-ins and keywords
   - Variable/function names from current file
   - Triggered by typing (no manual shortcut required)

### Secondary Needs

1. **Performance** (P0 - Critical Constraint)
   - Zero perceptible lag during typing
   - Smooth scrolling at 60 FPS
   - Fast editor initialization (<200ms)

2. **Lightweight** (P0 - Critical Constraint)
   - Minimal bundle size increase (<50KB gzipped)
   - No heavy external dependencies
   - Maintain current memory footprint

---

## Proposed Solution

### Technical Approach

**Philosophy**: Extend existing custom editor rather than replace with heavy library

#### 1. Auto-Indentation Implementation

**Approach**: Event-driven indentation logic in Vue component

```javascript
// On Enter key:
- Detect if previous line ends with ':'
- Copy previous line's indentation
- Add 4 spaces if colon detected
- Handle dedent keywords (return, pass, etc.)

// On Tab/Shift+Tab:
- Indent/dedent selected lines or current line
- Maintain selection after operation
```

**Estimated Complexity**: Low (50-80 lines of code)
**Performance Impact**: <1ms per keystroke

#### 2. Code Completion Implementation

**Approach**: Lightweight autocomplete dropdown with fuzzy matching

**Data Sources**:
1. **Static RQAlpha API** (~100 functions): Pre-defined list
2. **Python Keywords** (~35 keywords): Pre-defined list
3. **Document Symbols** (dynamic): Extract from current code via regex

**UI Component**:
- Floating dropdown below cursor
- Keyboard navigation (↑↓ arrows, Enter, Esc)
- Mouse selection support
- Max 10 visible suggestions
- Fuzzy match scoring

**Trigger Logic**:
```javascript
// Show completion when:
- User types 2+ characters
- After dot (.) for method completion
- Debounced 150ms to avoid flicker

// Hide completion when:
- User presses Esc
- Clicks outside
- Moves cursor away
- Selects suggestion
```

**Estimated Complexity**: Medium (200-300 lines of code)
**Performance Impact**: <5ms per keystroke (debounced)

### Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Extend custom editor vs. adopt Monaco/CodeMirror | Maintain lightweight architecture, avoid 500KB+ bundle increase |
| Client-side completion only | No network latency, works offline, simpler implementation |
| Static API list vs. dynamic analysis | Predictable performance, sufficient for RQAlpha use case |
| Debounced completion (150ms) | Balance responsiveness with performance |
| Fuzzy matching vs. prefix-only | Better UX, minimal performance cost with small dataset |

---

## Success Metrics

### Performance Acceptance Criteria (HARD REQUIREMENTS)

| Metric | Current Baseline | Maximum Acceptable | Measurement Method |
|--------|------------------|-------------------|-------------------|
| **Input Latency** | <10ms | <50ms | Time from keydown to screen update |
| **Scroll FPS** | 60 FPS | ≥55 FPS | Chrome DevTools Performance profiler |
| **Editor Load Time** | ~50ms | <200ms | Time from mount to interactive |
| **Bundle Size Increase** | 0 KB | <50 KB (gzipped) | webpack-bundle-analyzer |
| **Memory Usage** | ~2 MB | <5 MB | Chrome DevTools Memory profiler |
| **Completion Popup Delay** | N/A | <150ms | Time from trigger to display |

### Functional Acceptance Criteria

#### Auto-Indentation
- [ ] Pressing Enter after `:` adds 4 spaces to next line
- [ ] Pressing Enter on normal line maintains current indentation
- [ ] `return`, `pass`, `break`, `continue` auto-dedent by 4 spaces
- [ ] Tab indents current line or selection by 4 spaces
- [ ] Shift+Tab dedents current line or selection by 4 spaces
- [ ] Multi-line selection indent/dedent works correctly
- [ ] Undo/redo works correctly with auto-indentation

#### Code Completion
- [ ] Completion popup appears after typing 2+ characters
- [ ] Completion popup appears after typing `.` (method completion)
- [ ] Shows RQAlpha API functions (order_shares, get_position, etc.)
- [ ] Shows Python keywords (def, class, if, for, etc.)
- [ ] Shows variables/functions from current file
- [ ] Fuzzy matching works (typing "ordsh" matches "order_shares")
- [ ] Arrow keys navigate suggestions
- [ ] Enter key inserts selected suggestion
- [ ] Esc key closes popup
- [ ] Clicking outside closes popup
- [ ] Tab key inserts selected suggestion (alternative to Enter)

### User Experience Criteria

- [ ] No perceptible lag when typing rapidly (>100 WPM)
- [ ] Smooth scrolling through 1000+ line files
- [ ] Editor opens instantly when navigating to strategy
- [ ] Completion suggestions are relevant and helpful
- [ ] Auto-indentation feels natural and predictable

---

## Technical Constraints

### Must Maintain

1. **Zero External Editor Dependencies**: No Monaco, CodeMirror, Ace, or similar
2. **Current Architecture**: Textarea overlay with syntax highlighting
3. **Vue 3 Compatibility**: Must work with existing Vue 3 setup
4. **Dark Mode Support**: Must work in both light and dark themes
5. **Read-Only Mode**: Must respect existing `readOnly` prop

### Performance Budgets

```javascript
// Per-keystroke operations budget
const PERFORMANCE_BUDGET = {
  inputHandler: 5,        // ms - handle input event
  syntaxHighlight: 10,    // ms - update highlighting
  completionTrigger: 5,   // ms - check if should show completion
  completionRender: 10,   // ms - render completion popup
  total: 30               // ms - total per keystroke (leaves 20ms buffer)
};
```

### Browser Support

- Chrome 90+ (primary target)
- Firefox 88+
- Safari 14+
- Edge 90+

---

## Out of Scope

The following features are explicitly **NOT** included in this enhancement:

- [ ] Language Server Protocol (LSP) integration
- [ ] Advanced refactoring tools
- [ ] Git integration in editor
- [ ] Multi-cursor editing
- [ ] Code folding
- [ ] Minimap
- [ ] Bracket matching visualization
- [ ] Linting/error checking (beyond syntax highlighting)
- [ ] Snippet expansion
- [ ] Collaborative editing
- [ ] Vim/Emacs keybindings
- [ ] Custom themes beyond light/dark
- [ ] Import auto-completion from external packages
- [ ] Type inference or static analysis

---

## Implementation Plan

### Phase 1: Auto-Indentation (Week 1)

**Effort**: 1-2 days
**Risk**: Low

1. Implement Enter key handler with colon detection
2. Implement Tab/Shift+Tab for indent/dedent
3. Add dedent keyword detection
4. Test with various Python code patterns
5. Performance validation

### Phase 2: Code Completion (Week 1-2)

**Effort**: 3-4 days
**Risk**: Medium

1. Create RQAlpha API completion data
2. Implement completion popup component
3. Add fuzzy matching algorithm
4. Implement keyboard navigation
5. Add document symbol extraction
6. Performance optimization and testing

### Phase 3: Integration & Polish (Week 2)

**Effort**: 1-2 days
**Risk**: Low

1. Integration testing with full editor
2. Dark mode styling
3. Edge case handling
4. Performance profiling and optimization
5. User acceptance testing

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Performance degradation | Medium | High | Implement with performance budgets, continuous profiling |
| Completion popup interferes with typing | Medium | Medium | Proper z-index, click-outside handling, Esc key |
| Auto-indent breaks existing workflows | Low | Medium | Make behavior predictable, add undo support |
| Bundle size exceeds budget | Low | High | Use tree-shaking, avoid heavy dependencies |
| Browser compatibility issues | Low | Medium | Test on all supported browsers |

---

## Success Validation

### Performance Testing Protocol

```bash
# 1. Bundle Size Check
npm run build
# Verify: dist/js/route-strategies.*.js increase <50KB gzipped

# 2. Input Latency Test
# Chrome DevTools > Performance
# Record typing 100 characters rapidly
# Verify: All input events complete within 50ms

# 3. Scroll Performance Test
# Chrome DevTools > Performance
# Record scrolling through 1000-line file
# Verify: Maintain 55+ FPS

# 4. Memory Profiling
# Chrome DevTools > Memory
# Take heap snapshot before/after editor use
# Verify: Memory increase <5MB

# 5. Load Time Test
# Chrome DevTools > Performance
# Record navigation to strategy editor
# Verify: Time to interactive <200ms
```

### User Acceptance Testing

- [ ] 5 users test auto-indentation with real strategies
- [ ] 5 users test code completion with RQAlpha APIs
- [ ] Collect feedback on perceived performance
- [ ] Verify no complaints about lag or slowness

---

## Appendix: RQAlpha API Reference

### Core APIs to Include in Completion

```python
# Order Management
order_shares(id_or_ins, amount, style=None)
order_lots(id_or_ins, amount, style=None)
order_value(id_or_ins, cash_amount, style=None)
order_percent(id_or_ins, percent, style=None)
order_target_value(id_or_ins, cash_amount, style=None)
order_target_percent(id_or_ins, percent, style=None)

# Position & Portfolio
get_position(id_or_ins, direction=POSITION_DIRECTION.LONG)
get_positions()
update_universe(id_or_ins_list)

# Market Data
history_bars(id_or_ins, bar_count, frequency, fields=None)
current_snapshot(id_or_ins)
get_price(id_or_ins, start_date=None, end_date=None, frequency='1d')

# Context
context.portfolio
context.now
context.run_info

# Lifecycle Hooks
init(context)
before_trading(context)
handle_bar(context, bar_dict)
after_trading(context)
```

---

## Approval & Sign-off

- [ ] Product Owner: _______________
- [ ] Tech Lead: _______________
- [ ] Performance validated: _______________
- [ ] Ready for implementation: _______________

---

**Document Version**: 1.0
**Last Updated**: 2026-02-26
**Next Review**: After Phase 1 completion
