/**
 * Code Completion Composable
 * Provides static code completion for RQAlpha API, Python keywords, and built-ins
 * Lazy-loaded only when feature is enabled
 */

// RQAlpha API functions
const RQALPHA_API = [
  'order_shares', 'order_lots', 'order_value', 'order_percent',
  'order_target_value', 'order_target_percent',
  'get_position', 'get_positions', 'update_universe',
  'history_bars', 'current_snapshot', 'get_price',
  'init', 'before_trading', 'handle_bar', 'after_trading'
];

// Python keywords
const PYTHON_KEYWORDS = [
  'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
  'break', 'class', 'continue', 'def', 'del', 'elif', 'else',
  'except', 'finally', 'for', 'from', 'global', 'if', 'import',
  'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise',
  'return', 'try', 'while', 'with', 'yield'
];

// Python built-ins
const PYTHON_BUILTINS = [
  'abs', 'all', 'any', 'bool', 'dict', 'enumerate', 'filter',
  'float', 'int', 'len', 'list', 'map', 'max', 'min', 'open',
  'print', 'range', 'set', 'sorted', 'str', 'sum', 'tuple', 'zip',
  'isinstance', 'hasattr', 'getattr', 'setattr'
];

// Combine all static completion items
const STATIC_ITEMS = [
  ...RQALPHA_API.map(name => ({ name, type: 'rqalpha', source: 'RQAlpha' })),
  ...PYTHON_KEYWORDS.map(name => ({ name, type: 'keyword', source: 'Python' })),
  ...PYTHON_BUILTINS.map(name => ({ name, type: 'builtin', source: 'Python' }))
];

export function useCodeCompletion() {
  let debounceTimer = null;

  function fuzzyMatch(query, items, maxResults = 10) {
    if (!query || query.length < 2) {
      return [];
    }

    const lowerQuery = query.toLowerCase();
    const results = [];

    for (const item of items) {
      const lowerName = item.name.toLowerCase();
      let score = 0;

      // Exact prefix match (highest score)
      if (lowerName.startsWith(lowerQuery)) {
        score = 100;
      } else {
        // Non-consecutive character matching
        let queryIndex = 0;
        let consecutive = 0;

        for (let i = 0; i < lowerName.length && queryIndex < lowerQuery.length; i++) {
          if (lowerName[i] === lowerQuery[queryIndex]) {
            score += consecutive > 0 ? 80 : 50;
            consecutive++;
            queryIndex++;
          } else {
            consecutive = 0;
          }
        }

        // Must match all query characters
        if (queryIndex < lowerQuery.length) {
          score = 0;
        }
      }

      if (score > 0) {
        results.push({ ...item, score });
      }
    }

    // Sort by score descending, then alphabetically
    results.sort((a, b) => {
      if (b.score !== a.score) {
        return b.score - a.score;
      }
      return a.name.localeCompare(b.name);
    });

    return results.slice(0, maxResults);
  }

  function getWordAtCursor(text, cursorPos) {
    // Find word boundaries
    let start = cursorPos;
    let end = cursorPos;

    // Move start backwards to find word start
    while (start > 0 && /[a-zA-Z0-9_]/.test(text[start - 1])) {
      start--;
    }

    // Move end forwards to find word end
    while (end < text.length && /[a-zA-Z0-9_]/.test(text[end])) {
      end++;
    }

    return {
      word: text.substring(start, end),
      start,
      end
    };
  }

  function shouldTriggerCompletion(text, cursorPos) {
    const { word } = getWordAtCursor(text, cursorPos);

    // Trigger if word is 2+ characters
    if (word.length >= 2) {
      return true;
    }

    // Trigger immediately after dot
    if (cursorPos > 0 && text[cursorPos - 1] === '.') {
      return true;
    }

    return false;
  }

  function getCompletions(text, cursorPos) {
    const { word } = getWordAtCursor(text, cursorPos);

    if (word.length < 2) {
      return [];
    }

    return fuzzyMatch(word, STATIC_ITEMS);
  }

  function triggerCompletion(text, cursorPos, callback, debounceMs = 150) {
    clearTimeout(debounceTimer);

    if (!shouldTriggerCompletion(text, cursorPos)) {
      callback([]);
      return;
    }

    debounceTimer = setTimeout(() => {
      const completions = getCompletions(text, cursorPos);
      callback(completions);
    }, debounceMs);
  }

  function cancelCompletion() {
    clearTimeout(debounceTimer);
  }

  function insertCompletion(text, cursorPos, completion) {
    const { start, end } = getWordAtCursor(text, cursorPos);
    const newText = text.substring(0, start) + completion.name + text.substring(end);
    const newCursorPos = start + completion.name.length;

    return {
      text: newText,
      cursorPos: newCursorPos
    };
  }

  return {
    getCompletions,
    triggerCompletion,
    cancelCompletion,
    insertCompletion,
    shouldTriggerCompletion,
    getWordAtCursor
  };
}
