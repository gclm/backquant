if (!window.ResizeObserver) {
  window.ResizeObserver = class ResizeObserver {
    observe() {
      // noop
    }
    unobserve() {
      // noop
    }
    disconnect() {
      // noop
    }
  };
}
