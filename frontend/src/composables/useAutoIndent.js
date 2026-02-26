/**
 * Auto-Indentation Composable
 * Handles automatic indentation for Python code
 * Lazy-loaded only when feature is enabled
 */

const DEDENT_KEYWORDS = new Set(['return', 'pass', 'break', 'continue', 'raise']);

export function useAutoIndent() {
  function getLineIndentation(line) {
    const match = line.match(/^(\s*)/);
    return match ? match[1] : '';
  }

  function handleEnterKey(textarea, value) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;

    // Get current line
    const beforeCursor = value.substring(0, start);
    const lines = beforeCursor.split('\n');
    const currentLine = lines[lines.length - 1];

    // Calculate indentation
    const currentIndent = getLineIndentation(currentLine);
    const trimmedLine = currentLine.trim();

    // Check if line ends with colon (function, class, if, for, etc.)
    const endsWithColon = trimmedLine.endsWith(':');

    // Calculate new indentation
    let newIndent = currentIndent;
    if (endsWithColon) {
      newIndent = currentIndent + '    '; // Add 4 spaces
    }

    // Insert newline with indentation
    const newValue = value.substring(0, start) + '\n' + newIndent + value.substring(end);
    const newCursorPos = start + 1 + newIndent.length;

    return {
      value: newValue,
      cursorPos: newCursorPos
    };
  }

  function handleTabKey(textarea, value, shiftKey = false) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;

    // Multi-line selection
    if (start !== end) {
      const beforeSelection = value.substring(0, start);
      const afterSelection = value.substring(end);

      // Find line boundaries
      const startLineBegin = beforeSelection.lastIndexOf('\n') + 1;
      const endLineEnd = afterSelection.indexOf('\n');
      const fullEnd = endLineEnd === -1 ? value.length : end + endLineEnd;

      const selectedText = value.substring(startLineBegin, fullEnd);
      const lines = selectedText.split('\n');

      let modifiedLines;
      if (shiftKey) {
        // Dedent: remove up to 4 spaces from each line
        modifiedLines = lines.map(line => {
          if (line.startsWith('    ')) {
            return line.substring(4);
          } else if (line.startsWith('   ')) {
            return line.substring(3);
          } else if (line.startsWith('  ')) {
            return line.substring(2);
          } else if (line.startsWith(' ')) {
            return line.substring(1);
          }
          return line;
        });
      } else {
        // Indent: add 4 spaces to each line
        modifiedLines = lines.map(line => '    ' + line);
      }

      const newValue = value.substring(0, startLineBegin) +
                      modifiedLines.join('\n') +
                      value.substring(fullEnd);

      return {
        value: newValue,
        selectionStart: startLineBegin,
        selectionEnd: startLineBegin + modifiedLines.join('\n').length
      };
    }

    // Single line
    if (shiftKey) {
      // Dedent: remove up to 4 spaces before cursor
      const beforeCursor = value.substring(0, start);
      const lineStart = beforeCursor.lastIndexOf('\n') + 1;
      const lineBeforeCursor = value.substring(lineStart, start);

      let spacesToRemove = 0;
      for (let i = lineBeforeCursor.length - 1; i >= 0 && spacesToRemove < 4; i--) {
        if (lineBeforeCursor[i] === ' ') {
          spacesToRemove++;
        } else {
          break;
        }
      }

      if (spacesToRemove > 0) {
        const newValue = value.substring(0, start - spacesToRemove) + value.substring(start);
        return {
          value: newValue,
          cursorPos: start - spacesToRemove
        };
      }

      return null; // No change
    } else {
      // Indent: insert 4 spaces at cursor
      const newValue = value.substring(0, start) + '    ' + value.substring(end);
      return {
        value: newValue,
        cursorPos: start + 4
      };
    }
  }

  function shouldDedent(line) {
    const trimmed = line.trim();
    for (const keyword of DEDENT_KEYWORDS) {
      if (trimmed === keyword || trimmed.startsWith(keyword + ' ')) {
        return true;
      }
    }
    return false;
  }

  function handleDedentKeyword(textarea, value) {
    const start = textarea.selectionStart;
    const beforeCursor = value.substring(0, start);
    const lines = beforeCursor.split('\n');
    const currentLine = lines[lines.length - 1];

    if (shouldDedent(currentLine)) {
      const indent = getLineIndentation(currentLine);
      if (indent.length >= 4) {
        // Remove 4 spaces from current line
        const lineStart = beforeCursor.lastIndexOf('\n') + 1;
        const newValue = value.substring(0, lineStart) +
                        currentLine.substring(4) +
                        value.substring(start);
        return {
          value: newValue,
          cursorPos: start - 4
        };
      }
    }

    return null;
  }

  return {
    handleEnterKey,
    handleTabKey,
    handleDedentKeyword
  };
}
