<template>
  <div class="kline-panel">
    <div class="chart-row">
      <!-- K线卡片 -->
      <div class="chart-card">
        <div class="card-header">
          <div class="header-content">
            <h3>📈 {{ name }} {{ code }}｜{{ perfInfo }}</h3>
            <div class="timeframe-info">
              {{ getTimeframeInfo() }}
            </div>
          </div>
        </div>
        <div class="card-content">
          <div class="detail-info">
            <div class="detail-item">
              <span class="detail-label">时间:</span>
              <span class="detail-value">{{ selectedData ? formatTimestamp(selectedData.timestamp) : '--' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">开盘:</span>
              <span class="detail-value">{{ selectedData ? selectedData.open : '--' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">收盘:</span>
              <span class="detail-value">{{ selectedData ? selectedData.close : '--' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">涨幅:</span>
              <span class="detail-value" :class="getChangeClass(selectedData)">
                {{ selectedData ? getChangePercent(selectedData) : '--' }}
              </span>
            </div>
          </div>
          <div class="chart-wrapper">
            <div ref="chartRef" class="chart"></div>
          </div>
        </div>
      </div>

      <!-- 交易信号卡片 -->
      <div class="signal-card">
        <div class="card-header">
          <h3>📶 交易信号</h3>
        </div>
        <div class="card-content">
          <div class="signal-table-wrapper">
            <table class="signal-table">
              <thead>
                <tr>
                  <th>信号</th>
                  <th>日期</th>
                  <th>时间</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="signal in topSignals" :key="signal.timestamp" :class="getSignalRowClass(signal.trend)">
                  <td class="signal-cell">
                    <span class="signal-badge" :class="getSignalClass(signal.trend)">{{ signal.trend === 'up' ? '买' : (signal.trend === 'down' ? '卖' : '跳过') }}</span>
                  </td>
                  <td class="date-cell">{{ formatDateFromTimestamp(signal.timestamp) }}</td>
                  <td class="time-cell">{{ formatTimeFromTimestamp(signal.timestamp) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: 'KlinePanel',
  props: {
    code: { type: String, required: true },
    name: { type: String, required: true },
    perfInfo: { type: String, default: '' },
    kline: { type: Array, default: () => [] },
    signals: { type: Array, default: () => [] },
    isDarkMode: { type: Boolean, default: false }
  },
  data() {
    return {
      chart: null,
      selectedData: null,
      resizeHandler: null,
      updateTimer: null
    };
  },
  computed: {
    topSignals() {
      return (this.signals || [])
        .filter(s => s && s.code === this.code)
        .sort((a, b) => b.timestamp.localeCompare(a.timestamp))
        .slice(0, 8);
    }
  },
  mounted() {
    this.$nextTick(() => this.safeInit());
  },
  beforeUnmount() {
    this.cleanup();
  },
  watch: {
    code() {
      // 代码切换：完全重建
      this.cleanup();
      this.$nextTick(() => this.safeInit());
    },
    kline: {
      handler() {
        // 防抖更新，避免频繁切换时的残影
        if (this.updateTimer) {
          clearTimeout(this.updateTimer);
        }
        this.updateTimer = setTimeout(() => {
          this.$nextTick(() => this.updateChart());
        }, 50);
      },
      deep: true
    },
    signals: {
      handler() {
        // 防抖更新，避免频繁切换时的残影
        if (this.updateTimer) {
          clearTimeout(this.updateTimer);
        }
        this.updateTimer = setTimeout(() => {
          this.$nextTick(() => this.updateChart());
        }, 50);
      },
      deep: true
    },
    isDarkMode() {
      this.$nextTick(() => this.updateChart());
    }
  },
  methods: {
    safeInit(retry = 0) {
      const el = this.$refs.chartRef;
      if (!el) return;
      const { offsetWidth: w, offsetHeight: h } = el;
      if (w > 0 && h > 0) {
        this.initChart();
      } else if (retry < 10) {
        setTimeout(() => this.safeInit(retry + 1), 80);
      }
    },
    initChart() {
      const el = this.$refs.chartRef;
      if (!el) return;
      // 容器高度
      const isMobile = window.innerWidth <= 768;
      el.style.height = isMobile ? '300px' : '350px';
      this.chart = echarts.init(el);
      this.bindResize();
      this.updateChart();
    },
    bindResize() {
      this.resizeHandler = () => {
        if (this.chart) {
          const el = this.$refs.chartRef;
          if (el) {
            const isMobile = window.innerWidth <= 768;
            el.style.height = isMobile ? '300px' : '350px';
          }
          this.chart.resize();
          // 调整为移动端时，自动滚动到最右侧，默认显示最近K线
          if (window.innerWidth <= 768) {
            this.$nextTick(() => {
              const wrapper = this.$el.querySelector('.chart-wrapper');
              if (wrapper && wrapper.scrollWidth > wrapper.clientWidth) {
                wrapper.scrollLeft = wrapper.scrollWidth;
              }
            });
          }
        }
      };
      window.addEventListener('resize', this.resizeHandler);
    },
    cleanup() {
      if (this.chart) {
        this.chart.dispose();
        this.chart = null;
      }
      if (this.resizeHandler) {
        window.removeEventListener('resize', this.resizeHandler);
        this.resizeHandler = null;
      }
      if (this.updateTimer) {
        clearTimeout(this.updateTimer);
        this.updateTimer = null;
      }
    },
    updateChart() {
      if (!this.chart || !this.kline || this.kline.length === 0) return;

      // 清除之前的图表内容，减少残影
      this.chart.clear();

      const valid = this.kline
        .filter(i => i && i.timestamp)
        .map(i => ({
          t: this.formatTimestamp(i.timestamp),
          o: Number(i.open), c: Number(i.close), l: Number(i.low), h: Number(i.high)
        }))
        .filter(i => ![i.o, i.c, i.l, i.h].some(v => isNaN(v) || v <= 0) && i.l <= Math.min(i.o, i.c) && i.h >= Math.max(i.o, i.c));
      if (!valid.length) return;

      const timeData = valid.map(i => i.t);
      const klineData = valid.map(i => [i.o, i.c, i.l, i.h]);
      // 默认选中最后一条
      this.selectedData = this.kline[this.kline.length - 1] || null;

      // 信号使用类别名作为x
      const buySignals = [];
      const sellSignals = [];
      (this.signals || []).forEach(s => {
        if (s.code !== this.code) return;
        const t = this.formatTimestamp(s.timestamp);
        const idx = timeData.indexOf(t);
        if (idx === -1) return;
        const ref = valid[idx];
        if (!ref) return;
        if (s.trend === 'up') buySignals.push([t, ref.h * 1.002]);
        else if (s.trend === 'down') sellSignals.push([t, ref.l * 0.998]);
      });

      const option = {
        animation: true,
        animationDuration: 200,
        animationEasing: 'cubicOut',
        animationThreshold: 2000,
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross',
            lineStyle: {
              color: this.isDarkMode ? '#b0b3b8' : '#999',
              width: 1,
              type: 'dashed'
            }
          },
          formatter: (p) => {
            const list = Array.isArray(p) ? p : [p];
            const k = list.find(x => x.seriesType === 'candlestick') || list[0];
            if (!k) return '';
            const data = k.data;
            const time = timeData[k.dataIndex];
            // 确保数据完整性
            const open = data[0] !== undefined ? data[0].toFixed(4) : '--';
            const close = data[1] !== undefined ? data[1].toFixed(4) : '--';
            const low = data[2] !== undefined ? data[2].toFixed(4) : '--';
            const high = data[3] !== undefined ? data[3].toFixed(4) : '--';
            return `<div style="padding:8px;">
              <div style="margin-bottom:8px;font-weight:bold;">${time}</div>
              <div style="margin:4px 0;">开盘: ${open}</div>
              <div style="margin:4px 0;">收盘: ${close}</div>
              <div style="margin:4px 0;">最低: ${low}</div>
              <div style="margin:4px 0;">最高: ${high}</div>
            </div>`;
          }
        },
        legend: {
          data: ['B', 'S'],
          top: 25,
          textStyle: { color: this.isDarkMode ? '#b0b3b8' : '#666', fontSize: 10 },
          selectedMode: false
        },
        grid: { left: '6%', right: '1%', top: '12%', bottom: '6%', containLabel: true },
        xAxis: {
          type: 'category',
          data: timeData,
          boundaryGap: true,
          axisTick: { alignWithLabel: true },
          axisLabel: {
            rotate: 0,
            color: this.isDarkMode ? '#b0b3b8' : '#666', fontSize: 10,
            formatter: (val) => {
              if (!val) return '';
              // 显示日期和时间，格式：MM-DD HH:mm
              const date = val.slice(5, 10); // MM-DD
              const time = val.slice(11, 16); // HH:mm
              return `${date}\n${time}`;
            }
          }
        },
        yAxis: {
          scale: true,
          splitArea: { show: true, areaStyle: { color: this.isDarkMode ? ['rgba(255,255,255,0.02)', 'rgba(255,255,255,0.05)'] : ['rgba(250,250,250,0.3)', 'rgba(200,200,200,0.1)'] } },
          axisLabel: { color: this.isDarkMode ? '#b0b3b8' : '#666', fontSize: 10 },
          splitLine: { lineStyle: { color: this.isDarkMode ? 'rgba(255, 255, 255, 0.1)' : '#eee' } }
        },
        series: [
          {
            name: 'K线', type: 'candlestick', data: klineData,
            itemStyle: { color: '#FD1050', color0: '#00A854', borderColor: '#FD1050', borderColor0: '#00A854' }
          },
          { name: 'B', type: 'scatter', data: buySignals, symbol: 'circle', symbolSize: 12,
            itemStyle: { color: '#FF4444' }, label: { show: true, formatter: 'B', color: '#fff', fontSize: 10, fontWeight: 'bold', position: 'inside' } },
          { name: 'S', type: 'scatter', data: sellSignals, symbol: 'circle', symbolSize: 12,
            itemStyle: { color: '#00CC00' }, label: { show: true, formatter: 'S', color: '#fff', fontSize: 10, fontWeight: 'bold', position: 'inside' } }
        ]
      };

      // 使用更平滑的更新方式，减少残影
      this.chart.setOption(option, false, false);

      // 事件联动：鼠标移动时实时更新顶部明细
      this.chart.off('mousemove');
      this.chart.off('click');
      this.chart.off('axisareaselected');

      // 监听鼠标移动事件，确保在图表区域内移动时更新数据
      this.chart.on('mousemove', (params) => {
        if (params && typeof params.dataIndex === 'number') {
          const idx = params.dataIndex;
          const raw = this.kline[idx];
          if (raw) this.selectedData = raw;
        }
      });

      // 监听坐标轴区域选择事件，这是十字光标线移动时触发的事件
      this.chart.on('axisareaselected', (params) => {
        if (params && typeof params.dataIndex === 'number') {
          const idx = params.dataIndex;
          const raw = this.kline[idx];
          if (raw) this.selectedData = raw;
        }
      });

      this.chart.on('click', (params) => {
        if (params && typeof params.dataIndex === 'number' && params.seriesType === 'candlestick') {
          const idx = params.dataIndex;
          const raw = this.kline[idx];
          if (raw) this.selectedData = raw;
        }
      });

      // 移动端：如果图表横向宽于视口，默认滚动到最右侧以显示最近K线
      if (window.innerWidth <= 768) {
        this.$nextTick(() => {
          const wrapper = this.$el.querySelector('.chart-wrapper');
          if (wrapper && wrapper.scrollWidth > wrapper.clientWidth) {
            wrapper.scrollLeft = wrapper.scrollWidth;
          }
        });
      }
    },
    formatTimestamp(ts) {
      if (ts && ts.length === 12) {
        const y = ts.substring(0, 4);
        const m = ts.substring(4, 6);
        const d = ts.substring(6, 8);
        const hh = ts.substring(8, 10);
        const mm = ts.substring(10, 12);
        return `${y}-${m}-${d} ${hh}:${mm}`;
      }
      return ts;
    },
    formatDate(date) {
      if (!date) return '--';
      if (date.length === 8) return `${date.substring(4, 6)}-${date.substring(6, 8)}`;
      return date;
    },
    formatTime(timestamp) {
      if (!timestamp) return '--';
      if (timestamp.length === 12) return `${timestamp.substring(8, 10)}:${timestamp.substring(10, 12)}`;
      return timestamp;
    },
    getChangePercent(data) {
      if (!data || data.open === 0) return '0.00%';
      const change = ((data.close - data.open) / data.open * 100).toFixed(2);
      return `${change}%`;
    },
    getChangeClass(data) {
      if (!data) return '';
      const change = data.close - data.open;
      return change > 0 ? 'positive-change' : change < 0 ? 'negative-change' : '';
    },
    getSignalClass(trend) {
      return trend === 'down' ? 'sell-signal' : 'buy-signal';
    },
    getSignalRowClass(trend) {
      return trend === 'down' ? 'sell-row' : 'buy-row';
    },

    getTimeframeInfo() {
      // 创业板ETF使用15分钟分时，其他ETF使用5分钟分时
      if (this.code === 'sz159915') {
        return '15分钟分时';
      }
      return '15分钟分时';
    },

    formatDateFromTimestamp(timestamp) {
      if (!timestamp || timestamp.length < 8) return '--';
      // 从timestamp中提取日期部分 (YYYYMMDDHHMM)
      const datePart = timestamp.substring(0, 8);
      return `${datePart.substring(4, 6)}-${datePart.substring(6, 8)}`;
    },

    formatTimeFromTimestamp(timestamp) {
      if (!timestamp || timestamp.length < 12) return '--';
      // 从timestamp中提取时间部分 (YYYYMMDDHHMM)
      const timePart = timestamp.substring(8, 12);
      return `${timePart.substring(0, 2)}:${timePart.substring(2, 4)}`;
    }
  }
};
</script>

<style scoped>
.kline-panel {
  width: 100%;
}
.chart-row { display: flex; gap: 20px; flex-wrap: wrap; }
.chart-card { flex: 2; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden; min-width: 400px; }
.signal-card { flex: 1; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden; min-width: 250px; }
.card-header { background: #f8f9fa; padding: 12px 16px; border-bottom: 1px solid #e9ecef; }
.card-header h3 { margin: 0; font-size: 14px; font-weight: 600; color: #333; }
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.timeframe-info {
  font-size: 12px;
  color: #FF4444;
  font-weight: bold;
  margin-left: auto;
}
.card-content { padding: 0; }
.detail-info { display: flex; justify-content: space-around; align-items: center; padding: 8px 16px; background: #f5f5f5; border-bottom: 1px solid #e0e0e0; flex-wrap: wrap; gap: 10px; min-height: 40px; }
.detail-item { display: flex; align-items: center; gap: 4px; }
.detail-label { font-size: 11px; color: #555; font-weight: 500; margin-right: 2px; }
.detail-value { font-size: 12px; font-weight: 600; color: #333; min-width: 40px; text-align: right; }
.positive-change { color: #FD1050; }
.negative-change { color: #00A854; }
.chart-wrapper { padding: 12px; }
.chart { width: 100%; height: 330px; }
.signal-table-wrapper { padding: 16px; max-height: 300px; overflow-y: auto; }
.signal-table { width: 100%; border-collapse: collapse; font-size: 12px; border-radius: 6px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.signal-table th { background: #f8f9fa; padding: 7px 5px; text-align: center; font-weight: 600; color: #333; border-bottom: 1px solid #e9ecef; font-size: 11px; }
.signal-table td { padding: 4px 4px; border-bottom: 1px solid #eee; transition: background-color 0.2s ease; }
.signal-cell { text-align: center; width: 50px; }
.date-cell { text-align: center; font-weight: 500; color: #666; font-size: 11px; }
.time-cell { text-align: center; font-weight: 500; color: #666; }
.signal-badge { display: inline-block; padding: 3px 7px; border-radius: 4px; font-size: 11px; font-weight: bold; min-width: 20px; text-align: center; background: transparent; color: inherit; border: 1px solid currentColor; }
.buy-signal { color: #FF4444; }
.sell-signal { color: #00CC00; }
.buy-row { background: rgba(253, 16, 80, 0.05); }
.sell-row { background: rgba(0, 168, 84, 0.05); }
.buy-row:hover { background: rgba(253, 16, 80, 0.1); }
.sell-row:hover { background: rgba(0, 168, 84, 0.1); }

@media (max-width: 768px) {
  .chart-row {
    flex-direction: column;
    gap: 15px;
  }

  .chart-card,
  .signal-card {
    min-width: auto;
    width: 100%;
  }

  .chart {
    height: 280px;
    min-width: 600px; /* 确保图表内容完整显示 */
  }

  .chart-wrapper {
    padding: 10px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .timeframe-info {
    margin-left: 0;
  }

  .detail-info {
    padding: 6px 12px;
    gap: 8px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }

  .detail-info::-webkit-scrollbar {
    display: none;
  }

  .detail-item {
    gap: 3px;
    flex-shrink: 0;
    min-width: fit-content;
  }

  .detail-label {
    font-size: 10px;
  }

  .detail-value {
    font-size: 11px;
  }
}

/* 超小屏幕优化 */
@media (max-width: 480px) {
  .chart {
    height: 250px;
    min-width: 500px;
  }

  .detail-info {
    padding: 5px 10px;
    gap: 6px;
  }

  .detail-label {
    font-size: 9px;
  }

  .detail-value {
    font-size: 10px;
  }

  .chart-wrapper {
    padding: 8px;
  }
}
</style>
