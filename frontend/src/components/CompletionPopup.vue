<template>
  <div
    v-if="visible && items.length > 0"
    ref="popup"
    class="completion-popup"
    :style="popupStyle"
    role="listbox"
    aria-label="Code completion suggestions"
  >
    <div
      v-for="(item, index) in items"
      :key="item.name"
      class="completion-item"
      :class="{ 'is-selected': index === selectedIndex }"
      role="option"
      :aria-selected="index === selectedIndex"
      @click="selectItem(index)"
      @mouseenter="selectedIndex = index"
    >
      <span class="item-icon" :class="`icon-${item.type}`">{{ getIcon(item.type) }}</span>
      <span class="item-name">{{ item.name }}</span>
      <span class="item-source">{{ item.source }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CompletionPopup',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    items: {
      type: Array,
      default: () => []
    },
    position: {
      type: Object,
      default: () => ({ top: 0, left: 0 })
    }
  },
  emits: ['select', 'close'],
  data() {
    return {
      selectedIndex: 0
    };
  },
  computed: {
    popupStyle() {
      return {
        top: `${this.position.top}px`,
        left: `${this.position.left}px`
      };
    }
  },
  watch: {
    visible(newVal) {
      if (newVal) {
        this.selectedIndex = 0;
        this.$nextTick(() => {
          document.addEventListener('keydown', this.handleKeydown);
          document.addEventListener('click', this.handleClickOutside);
        });
      } else {
        document.removeEventListener('keydown', this.handleKeydown);
        document.removeEventListener('click', this.handleClickOutside);
      }
    },
    items() {
      this.selectedIndex = 0;
    }
  },
  beforeUnmount() {
    document.removeEventListener('keydown', this.handleKeydown);
    document.removeEventListener('click', this.handleClickOutside);
  },
  methods: {
    getIcon(type) {
      const icons = {
        rqalpha: '📦',
        keyword: '🔑',
        builtin: '⚙️'
      };
      return icons[type] || '•';
    },
    selectItem(index) {
      this.$emit('select', this.items[index]);
    },
    handleKeydown(event) {
      if (!this.visible) return;

      switch (event.key) {
        case 'ArrowDown':
          event.preventDefault();
          this.selectedIndex = Math.min(this.selectedIndex + 1, this.items.length - 1);
          this.scrollToSelected();
          break;
        case 'ArrowUp':
          event.preventDefault();
          this.selectedIndex = Math.max(this.selectedIndex - 1, 0);
          this.scrollToSelected();
          break;
        case 'Enter':
        case 'Tab':
          event.preventDefault();
          this.selectItem(this.selectedIndex);
          break;
        case 'Escape':
          event.preventDefault();
          this.$emit('close');
          break;
      }
    },
    handleClickOutside(event) {
      if (this.$refs.popup && !this.$refs.popup.contains(event.target)) {
        this.$emit('close');
      }
    },
    scrollToSelected() {
      this.$nextTick(() => {
        const popup = this.$refs.popup;
        if (!popup) return;

        const items = popup.querySelectorAll('.completion-item');
        const selectedItem = items[this.selectedIndex];
        if (!selectedItem) return;

        const popupRect = popup.getBoundingClientRect();
        const itemRect = selectedItem.getBoundingClientRect();

        if (itemRect.bottom > popupRect.bottom) {
          selectedItem.scrollIntoView({ block: 'nearest' });
        } else if (itemRect.top < popupRect.top) {
          selectedItem.scrollIntoView({ block: 'nearest' });
        }
      });
    }
  }
};
</script>

<style scoped>
.completion-popup {
  position: fixed;
  z-index: 9999;
  background: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  max-width: 400px;
  max-height: 300px;
  overflow-y: auto;
  font-family: SFMono-Regular, Menlo, Monaco, Consolas, 'Courier New', monospace;
  font-size: 13px;
}

.completion-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  cursor: pointer;
  transition: background-color 0.1s ease;
}

.completion-item:hover {
  background: #f3f3f3;
}

.completion-item.is-selected {
  background: #e8f4fd;
}

.item-icon {
  flex-shrink: 0;
  width: 20px;
  text-align: center;
  font-size: 14px;
}

.item-name {
  flex: 1;
  font-weight: 500;
  color: #333333;
}

.item-source {
  flex-shrink: 0;
  font-size: 11px;
  color: #999999;
  padding: 2px 6px;
  background: #f5f5f5;
  border-radius: 3px;
}

/* Dark mode */
body.dark-mode .completion-popup {
  background: #1e1e1e;
  border-color: #3e3e3e;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
}

body.dark-mode .completion-item:hover {
  background: #252526;
}

body.dark-mode .completion-item.is-selected {
  background: #2a2d2e;
}

body.dark-mode .item-name {
  color: #d4d4d4;
}

body.dark-mode .item-source {
  color: #858585;
  background: #2a2a2a;
}

/* Scrollbar styling */
.completion-popup::-webkit-scrollbar {
  width: 8px;
}

.completion-popup::-webkit-scrollbar-track {
  background: transparent;
}

.completion-popup::-webkit-scrollbar-thumb {
  background: #d0d0d0;
  border-radius: 4px;
}

.completion-popup::-webkit-scrollbar-thumb:hover {
  background: #b0b0b0;
}

body.dark-mode .completion-popup::-webkit-scrollbar-thumb {
  background: #424242;
}

body.dark-mode .completion-popup::-webkit-scrollbar-thumb:hover {
  background: #525252;
}
</style>
