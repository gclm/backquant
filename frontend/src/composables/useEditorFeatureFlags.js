/**
 * Editor Feature Flags System
 * Manages feature toggles with localStorage persistence
 */

const DEFAULT_FLAGS = {
  autoIndent: true,
  codeCompletion: true,
  performanceMonitoring: true
};

const STORAGE_KEY = 'pythonEditorFeatureFlags';

export function useEditorFeatureFlags() {
  const flags = loadFlags();

  function loadFlags() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        return { ...DEFAULT_FLAGS, ...JSON.parse(stored) };
      }
    } catch (error) {
      console.warn('Failed to load feature flags:', error);
    }
    return { ...DEFAULT_FLAGS };
  }

  function saveFlags(newFlags) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(newFlags));
    } catch (error) {
      console.warn('Failed to save feature flags:', error);
    }
  }

  function isEnabled(feature) {
    return flags[feature] !== false;
  }

  function toggle(feature) {
    flags[feature] = !flags[feature];
    saveFlags(flags);
    return flags[feature];
  }

  function enable(feature) {
    flags[feature] = true;
    saveFlags(flags);
  }

  function disable(feature) {
    flags[feature] = false;
    saveFlags(flags);
  }

  function reset() {
    Object.assign(flags, DEFAULT_FLAGS);
    saveFlags(flags);
  }

  return {
    flags,
    isEnabled,
    toggle,
    enable,
    disable,
    reset
  };
}
