<template>
  <div class="python-editor" :style="editorStyle">
    <div class="editor-main">
      <div ref="lineNumbers" class="line-numbers" aria-hidden="true">
        <span v-for="line in lineCount" :key="`line-${line}`">{{ line }}</span>
      </div>

      <div class="editor-stack">
        <pre ref="highlight" class="highlight-layer" v-html="highlightedHtml"></pre>
        <textarea
          ref="textarea"
          :value="modelValue"
          class="editor-textarea"
          :class="{ 'is-readonly': readOnly }"
          :readonly="readOnly"
          spellcheck="false"
          @input="handleInput"
          @scroll="syncScroll"
          @keydown.tab.prevent="insertTab"
        ></textarea>
      </div>
    </div>
  </div>
</template>

<script>
const KEYWORDS = new Set([
  'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue',
  'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import',
  'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while',
  'with', 'yield'
]);

const BUILTINS = new Set([
  'abs', 'all', 'any', 'bool', 'dict', 'enumerate', 'filter', 'float', 'int', 'len', 'list',
  'map', 'max', 'min', 'open', 'print', 'range', 'set', 'sorted', 'str', 'sum', 'tuple', 'zip', 'self'
]);

const TOKEN_REGEX = /("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|#[^\n]*|\b[A-Za-z_][A-Za-z0-9_]*\b|\b\d+(?:\.\d+)?\b)/g;

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function classifyToken(token) {
  if (token.startsWith('#')) {
    return 'token-comment';
  }

  if (
    token.startsWith('"""') || token.startsWith("'''") ||
    token.startsWith('"') || token.startsWith("'")
  ) {
    return 'token-string';
  }

  if (/^\d/.test(token)) {
    return 'token-number';
  }

  if (KEYWORDS.has(token)) {
    return 'token-keyword';
  }

  if (BUILTINS.has(token)) {
    return 'token-builtin';
  }

  return '';
}

function renderHighlighted(code) {
  const source = code || '';
  TOKEN_REGEX.lastIndex = 0;
  let result = '';
  let lastIndex = 0;
  let match = TOKEN_REGEX.exec(source);

  while (match) {
    const token = match[0];
    const start = match.index;

    result += escapeHtml(source.slice(lastIndex, start));

    const tokenClass = classifyToken(token);
    if (tokenClass) {
      result += `<span class="${tokenClass}">${escapeHtml(token)}</span>`;
    } else {
      result += escapeHtml(token);
    }

    lastIndex = start + token.length;
    match = TOKEN_REGEX.exec(source);
  }

  result += escapeHtml(source.slice(lastIndex));

  TOKEN_REGEX.lastIndex = 0;
  return `${result}\n`;
}

export default {
  name: 'PythonCodeEditor',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    minHeight: {
      type: Number,
      default: 360
    },
    readOnly: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue'],
  computed: {
    lineCount() {
      return Math.max(1, (this.modelValue || '').split('\n').length);
    },
    highlightedHtml() {
      return renderHighlighted(this.modelValue);
    },
    editorStyle() {
      return {
        '--editor-min-height': `${this.minHeight}px`
      };
    }
  },
  methods: {
    handleInput(event) {
      if (this.readOnly) {
        return;
      }
      this.$emit('update:modelValue', event.target.value);
    },
    syncScroll(event) {
      if (this.$refs.highlight) {
        this.$refs.highlight.scrollTop = event.target.scrollTop;
        this.$refs.highlight.scrollLeft = event.target.scrollLeft;
      }
      if (this.$refs.lineNumbers) {
        this.$refs.lineNumbers.scrollTop = event.target.scrollTop;
      }
    },
    insertTab() {
      if (this.readOnly) {
        return;
      }
      const textarea = this.$refs.textarea;
      if (!textarea) {
        return;
      }

      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const original = this.modelValue || '';
      const nextValue = `${original.slice(0, start)}    ${original.slice(end)}`;

      this.$emit('update:modelValue', nextValue);

      this.$nextTick(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 4;
      });
    }
  }
};
</script>

<style scoped>
.python-editor {
  border: 1px solid #dcdfe6;
  border-radius: 10px;
  overflow: hidden;
  min-height: var(--editor-min-height);
  background: #fff;
}

.editor-main {
  display: flex;
  min-height: var(--editor-min-height);
  font-family: SFMono-Regular, Menlo, Monaco, Consolas, 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.line-numbers {
  width: 48px;
  background: #f8f9fa;
  border-right: 1px solid #ebeef5;
  padding: 12px 8px;
  overflow: hidden;
  text-align: right;
  color: #909399;
  user-select: none;
}

.line-numbers span {
  display: block;
  min-height: 20.8px;
}

.editor-stack {
  position: relative;
  flex: 1;
  min-height: var(--editor-min-height);
}

.highlight-layer,
.editor-textarea {
  margin: 0;
  padding: 12px;
  border: 0;
  width: 100%;
  height: 100%;
  min-height: var(--editor-min-height);
  font: inherit;
  line-height: inherit;
  letter-spacing: 0;
  tab-size: 4;
  white-space: pre;
  overflow: auto;
  box-sizing: border-box;
}

.highlight-layer {
  pointer-events: none;
  color: #1f2937;
  background: #fff;
}

.editor-textarea {
  position: absolute;
  inset: 0;
  resize: none;
  color: transparent;
  background: transparent;
  caret-color: #303133;
  z-index: 2;
  outline: none;
}

.editor-textarea.is-readonly {
  caret-color: transparent;
}

.editor-textarea::selection {
  background: rgba(64, 158, 255, 0.25);
}

:deep(.token-keyword) {
  color: #7c3aed;
  font-weight: 600;
}

:deep(.token-builtin) {
  color: #2563eb;
}

:deep(.token-string) {
  color: #059669;
}

:deep(.token-number) {
  color: #ea580c;
}

:deep(.token-comment) {
  color: #9ca3af;
  font-style: italic;
}

body.dark-mode .python-editor {
  border-color: #4c4d4f;
  background: #1f1f1f;
}

body.dark-mode .line-numbers {
  background: #2a2a2a;
  border-color: #4c4d4f;
  color: #8f9399;
}

body.dark-mode .highlight-layer {
  background: #1f1f1f;
  color: #e5e7eb;
}

body.dark-mode .editor-textarea {
  caret-color: #f5f7fa;
}

body.dark-mode :deep(.token-keyword) {
  color: #c084fc;
}

body.dark-mode :deep(.token-builtin) {
  color: #60a5fa;
}

body.dark-mode :deep(.token-string) {
  color: #34d399;
}

body.dark-mode :deep(.token-number) {
  color: #fb923c;
}

body.dark-mode :deep(.token-comment) {
  color: #9ca3af;
}
</style>
