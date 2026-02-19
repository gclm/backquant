<template>
  <div class="theme-toggle-wrapper">
    <div class="theme-toggle-btn" :class="{ 'is-inline': inline, 'dark': isDarkMode }" @click="toggleTheme" title="网站主题切换">
      <!-- Sun Icon (Show when in Dark Mode -> Switch to Light) -->
      <svg v-if="isDarkMode" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon sun-icon" style="color: #ffffff;"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
      
      <!-- Moon Icon (Show when in Light Mode -> Switch to Dark) -->
      <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon moon-icon" style="color: #ffffff;"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
    </div>
    
    <!-- 悬浮文字提示 -->
    <div class="theme-label" :class="{ 'dark': isDarkMode }">
      {{ isDarkMode ? '切换到亮色' : '切换到暗黑' }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'ThemeToggleButton',
  props: {
    isDarkMode: {
      type: Boolean,
      required: true
    },
    inline: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    toggleTheme() {
      this.$emit('toggle');
    }
  }
}
</script>

<style scoped>
.theme-toggle-wrapper {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 移动端调整位置到底部中央，避免遮挡导航栏 */
@media (max-width: 768px) {
  .theme-toggle-wrapper {
    bottom: 20px;
    right: 50%;
    transform: translateX(50%);
    z-index: 999; /* 降低层级，让导航栏在上面 */
  }
}

.theme-toggle-btn {
  /* 移除fixed定位，由wrapper控制 */
  position: relative;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* 紫色渐变 */
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  user-select: none;
  border: none;
}

.theme-toggle-btn.is-inline {
  position: static;
  box-shadow: none;
  z-index: auto;
  margin-left: 10px;
  width: 36px;
  height: 36px;
  background-color: transparent;
  border: 1px solid transparent;
}
.theme-toggle-btn.is-inline .icon {
  font-size: 20px;
}
.theme-toggle-btn.is-inline:hover {
  background-color: rgba(0,0,0,0.05);
  transform: none;
  box-shadow: none;
}


.theme-toggle-btn:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.theme-toggle-btn:active {
  transform: translateY(0) scale(0.95);
}

.icon {
  font-size: 24px;
  line-height: 1;
}

/* Dark mode styles - direct class binding */
.theme-toggle-btn.dark {
  background-color: #2d2d2d;
  border-color: #4c4d4f;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}

.theme-toggle-btn.dark:hover {
  background-color: #383838;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.5);
}

/* Inline dark mode overrides */
.theme-toggle-btn.is-inline.dark {
  background-color: transparent;
  border-color: transparent;
  box-shadow: none;
}
.theme-toggle-btn.is-inline.dark:hover {
  background-color: rgba(255,255,255,0.1);
  box-shadow: none;
}

/* 悬浮文字标签样式 */
.theme-label {
  position: absolute;
  right: 60px; /* 按钮右侧 */
  background-color: #ffffff;
  color: #333;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  opacity: 0;
  transform: translateX(10px);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  pointer-events: none;
  border: 1px solid #e0e0e0;
}

.theme-label.dark {
  background-color: #2d2d2d;
  color: #e0e0e0;
  border-color: #4c4d4f;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}

/* 悬停时显示标签 */
.theme-toggle-wrapper:hover .theme-label {
  opacity: 1;
  transform: translateX(0);
}

/* 移动端隐藏文字标签 */
@media (max-width: 768px) {
  .theme-label {
    display: none;
  }
}
</style>
