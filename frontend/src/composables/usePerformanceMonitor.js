/**
 * Performance Monitoring System
 * Tracks editor performance metrics and enforces budgets
 */

const PERFORMANCE_BUDGETS = {
  inputLatency: 50,        // ms - p95
  completionTrigger: 20,   // ms - p95
  memoryUsage: 10485760,   // bytes - 10MB
  renderTime: 20           // ms - p95
};

export function usePerformanceMonitor() {
  const metrics = {
    inputLatency: [],
    completionTrigger: [],
    renderTime: [],
    memoryUsage: 0
  };

  const violations = [];
  let isMonitoring = true;

  function recordMetric(name, value) {
    if (!isMonitoring) return;

    if (metrics[name] && Array.isArray(metrics[name])) {
      metrics[name].push(value);

      // Keep only last 100 measurements
      if (metrics[name].length > 100) {
        metrics[name].shift();
      }
    } else if (name === 'memoryUsage') {
      metrics.memoryUsage = value;
    }
  }

  function getPercentile(arr, percentile) {
    if (arr.length === 0) return 0;
    const sorted = [...arr].sort((a, b) => a - b);
    const index = Math.floor(sorted.length * percentile);
    return sorted[index];
  }

  function getMetrics() {
    return {
      inputLatency: {
        p50: getPercentile(metrics.inputLatency, 0.5),
        p95: getPercentile(metrics.inputLatency, 0.95),
        p99: getPercentile(metrics.inputLatency, 0.99)
      },
      completionTrigger: {
        p50: getPercentile(metrics.completionTrigger, 0.5),
        p95: getPercentile(metrics.completionTrigger, 0.95),
        p99: getPercentile(metrics.completionTrigger, 0.99)
      },
      renderTime: {
        p50: getPercentile(metrics.renderTime, 0.5),
        p95: getPercentile(metrics.renderTime, 0.95),
        p99: getPercentile(metrics.renderTime, 0.99)
      },
      memoryUsage: metrics.memoryUsage
    };
  }

  function checkBudgets() {
    const current = getMetrics();
    const newViolations = [];

    if (current.inputLatency.p95 > PERFORMANCE_BUDGETS.inputLatency) {
      newViolations.push({
        metric: 'inputLatency',
        value: current.inputLatency.p95,
        budget: PERFORMANCE_BUDGETS.inputLatency,
        action: 'enablePerformanceMode'
      });
    }

    if (current.completionTrigger.p95 > PERFORMANCE_BUDGETS.completionTrigger) {
      newViolations.push({
        metric: 'completionTrigger',
        value: current.completionTrigger.p95,
        budget: PERFORMANCE_BUDGETS.completionTrigger,
        action: 'increaseDebounce'
      });
    }

    if (current.memoryUsage > PERFORMANCE_BUDGETS.memoryUsage) {
      newViolations.push({
        metric: 'memoryUsage',
        value: current.memoryUsage,
        budget: PERFORMANCE_BUDGETS.memoryUsage,
        action: 'disableDocumentSymbols'
      });
    }

    violations.push(...newViolations);
    return newViolations;
  }

  function clearMetrics() {
    metrics.inputLatency = [];
    metrics.completionTrigger = [];
    metrics.renderTime = [];
    metrics.memoryUsage = 0;
    violations.length = 0;
  }

  function disable() {
    isMonitoring = false;
  }

  function enable() {
    isMonitoring = true;
  }

  return {
    recordMetric,
    getMetrics,
    checkBudgets,
    clearMetrics,
    disable,
    enable,
    isMonitoring: () => isMonitoring
  };
}
