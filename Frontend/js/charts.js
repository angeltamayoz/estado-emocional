
// charts.js - helper utilities for creating and destroying Chart.js charts
window.createChart = function(ctx, config) {
  // if ctx is an id string, get element
  try {
    if (typeof ctx === 'string') {
      const el = document.getElementById(ctx);
      if (!el) throw new Error('Canvas element not found: ' + ctx);
      ctx = el.getContext('2d');
    }
    return new Chart(ctx, config);
  } catch (err) {
    console.error('createChart error', err);
    return null;
  }
};

window.safeDestroyChart = function(chart) {
  if (chart && typeof chart.destroy === 'function') {
    try { chart.destroy(); } catch (e) { console.warn('destroy failed', e); }
  }
};

window.updateOrCreateChart = function(windowName, canvasId, config) {
  // destroy previous chart safely, then create new and attach to window
  if (window[windowName]) safeDestroyChart(window[windowName]);
  const c = createChart(canvasId, config);
  window[windowName] = c;
  return c;
};
