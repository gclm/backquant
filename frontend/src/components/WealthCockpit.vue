<template>
  <div class="w-full mx-auto max-w-7xl space-y-6">
    <!-- 加载 / 错误 状态 -->
    <div v-if="loading" class="etf-cockpit-loading">
      加载中...
    </div>
    <div v-else-if="error" class="etf-cockpit-error">
      {{ error }}
    </div>

    <!-- 页面标题和清算日期 -->
    <div v-else class="space-y-6">
      <div class="flex flex-col items-center gap-3">
        <!-- 标题居中 -->
        <h1 class="text-2xl md:text-3xl font-bold text-slate-800 tracking-tight">
          财富驾驶舱
        </h1>
        <!-- 清算日期和曲线切换按钮 - 移动端垂直堆叠,桌面端水平排列 -->
        <div class="w-full flex flex-col md:flex-row items-center justify-between gap-3 px-4 md:px-0">
          <div class="hidden md:block flex-1"></div>
          <div class="inline-flex items-center gap-2 px-4 py-2 bg-gray-50 border border-gray-200 rounded-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span class="text-sm font-medium text-gray-800">
              清算日期:{{ formattedClearDate || '—' }}
            </span>
          </div>
          <div class="hidden md:block flex-1"></div>
        </div>
      </div>

      <!-- 顶部统计总览 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- 第一个卡片：当日总资产 -->
        <div class="rounded-xl border border-slate-200 bg-white shadow-sm p-4 md:p-5 flex flex-col justify-between hover:-translate-y-1 hover:shadow-md hover:border-emerald-400 transition-transform transition-shadow duration-200">
          <div class="flex items-center justify-between mb-3">
            <div>
              <div class="text-xs font-medium text-slate-500 tracking-wide">当日总资产</div>
              <div class="mt-2 font-mono font-semibold text-3xl md:text-4xl text-slate-900">
                <template v-if="isEmptyPosition">
                  <span class="text-slate-500 text-2xl font-medium">暂未持仓</span>
                </template>
                <template v-else>
                  {{ formatNumber(dailyStatData.assets) }}
                </template>
              </div>
            </div>
            <div class="inline-flex items-center justify-center rounded-full bg-emerald-50 text-emerald-600 w-9 h-9">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 7h16a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2Z" />
                <path d="M16 3H5a2 2 0 0 0-2 2v2" />
                <path d="M16 11h2" />
              </svg>
            </div>
          </div>
          <div class="flex items-center justify-between mt-3">
             <div class="text-xs text-slate-500">
              可用金额：<span class="font-mono font-semibold">{{ formatNumber(dailyStatData.avaliable) }}</span>
            </div>
             <div class="text-xs text-slate-500">
              现金：<span class="font-mono font-semibold">{{ formatNumber(dailyStatData.cash) }}</span>
            </div>
          </div>
        </div>

        <!-- 第二个卡片：当日总市值 -->
        <div class="rounded-xl border border-slate-200 bg-white shadow-sm p-4 md:p-5 flex flex-col justify-between hover:-translate-y-1 hover:shadow-md hover:border-emerald-400 transition-transform transition-shadow duration-200">
          <div class="flex items-center justify-between mb-3">
            <div>
              <div class="text-xs font-medium text-slate-500 tracking-wide">当日总市值</div>
              <div class="mt-2 font-mono font-semibold text-3xl md:text-4xl text-slate-900">
                <template v-if="isEmptyPosition">
                  <span class="text-slate-500 text-2xl font-medium">暂未持仓</span>
                </template>
                <template v-else>
                  {{ formatNumber(summary.totalMarketValue) }}
                </template>
              </div>
            </div>
            <div class="inline-flex items-center justify-center rounded-full bg-emerald-50 text-emerald-600 w-9 h-9">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 7h16a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2Z" />
                <path d="M16 3H5a2 2 0 0 0-2 2v2" />
                <path d="M16 11h2" />
              </svg>
            </div>
          </div>
          <div class="flex items-center justify-between mt-3">
             <div class="text-xs text-slate-500">
              清算日期：<span class="font-medium">{{ formattedClearDate || '—' }}</span>
            </div>
             <div class="text-xs text-slate-500">
              持仓成本：<span class="font-mono font-semibold">{{ formatNumber(summary.totalCost) }}</span>
            </div>
          </div>
        </div>

        <!-- 第三个卡片：浮动总盈亏 -->
        <div class="rounded-xl border border-slate-200 bg-white shadow-sm p-4 md:p-5 flex flex-col justify-between hover:-translate-y-1 hover:shadow-md transition-transform transition-shadow duration-200">
          <div class="flex items-center justify-between mb-3">
            <div>
              <div class="text-xs font-medium text-slate-500 tracking-wide">浮动总盈亏</div>
              <div class="mt-2 flex items-baseline gap-3">
                <template v-if="isEmptyPosition">
                  <div class="font-mono font-medium text-2xl md:text-3xl text-slate-500">暂未持仓</div>
                </template>
                <template v-else>
                  <div :class="['font-mono font-semibold text-2xl md:text-3xl', profitTextClass(summary.floatingProfit)]">
                    {{ formatSignedNumber(summary.floatingProfit) }}
                  </div>
                  <div class="text-xs font-mono font-semibold" :class="profitTextClass(floatingProfitPercent)">
                    {{ formatPercent(floatingProfitPercent) }}
                  </div>
                </template>
              </div>
            </div>
            <div :class="['inline-flex items-center justify-center rounded-full w-9 h-9', profitBgClass(summary.floatingProfit)]">
              <svg v-if="(summary.floatingProfit || 0) >= 0" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 17L9 11L13 15L21 7" />
                <path d="M14 7H21V14" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 7L9 13L13 9L21 17" />
                <path d="M14 17H21V10" />
              </svg>
            </div>
          </div>
          <div class="text-xs text-slate-500 flex items-center gap-2">
            <span>实现总盈亏：</span>
            <span :class="['font-mono font-semibold', profitTextClass(summary.totalRealizedProfit)]">{{ formatSignedNumber(summary.totalRealizedProfit) }}</span>
            <span v-if="!isEmptyPosition" :class="['font-mono font-semibold text-[10px]', profitTextClass(realizedProfitPercent)]">{{ formatPercent(realizedProfitPercent) }}</span>
          </div>
        </div>
      </div>

      <!-- 策略持仓概览 - 横向长条卡片 -->
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-medium text-slate-700">策略持仓概览</h3>
        </div>

        <div v-if="processedStrategies.length === 0" class="text-xs text-slate-400">
          暂无持仓数据
        </div>

        <!-- 单列堆叠的横向长条卡片 -->
        <div class="space-y-3">
          <div
            v-for="(strategy, index) in visibleStrategies"
            :key="index"
            class="strategy-row-card"
          >
            <!-- 主卡片 -->
            <div 
              class="strategy-row bg-white rounded-lg border border-slate-200 shadow-sm hover:-translate-y-1 hover:shadow-lg transition-all duration-200 overflow-hidden"
              :style="{ borderLeftColor: getStrategyColor(strategy.name), borderLeftWidth: '4px' }"
            >
              <!-- Grid 容器: 移动端为Flex垂直布局，桌面端为Grid水平布局 -->
              <div class="flex flex-col md:grid md:grid-cols-[140px_260px_160px_1fr_80px] gap-4 p-4">
                
                <!-- 移动端第一行：策略名称 + 操作按钮 -->
                <div class="flex md:hidden items-center justify-between w-full">
                   <div class="flex items-center">
                    <span class="strategy-badge" :class="getStrategyBadgeClass(strategy.name)">
                      {{ strategy.name }}
                    </span>
                  </div>
                  <!-- 移动端操作按钮 -->
                  <div class="flex items-center gap-2">
                     <button
                        v-if="strategy.hasCurveData"
                        @click.stop="openChartModal(strategy)"
                        class="p-1.5 rounded hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
                        title="查看深度分析"
                      >
                       <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                    </button>
                    <button
                      v-if="strategy.securities.length > 0"
                      @click.stop="toggleExpand(visibleStrategies.indexOf(strategy))"
                      class="p-1.5 rounded hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
                      :title="expandedStrategies[visibleStrategies.indexOf(strategy)] ? '收起明细' : '展开明细'"
                    >
                      <svg 
                        xmlns="http://www.w3.org/2000/svg" 
                        class="h-5 w-5 transition-transform duration-200"
                        :class="{ 'rotate-180': expandedStrategies[visibleStrategies.indexOf(strategy)] }"
                        fill="none" 
                        viewBox="0 0 24 24" 
                        stroke="currentColor"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                  </div>
                </div>

                <!-- 桌面端 列1: 策略识别区 (Fixed 140px) -->
                <div class="hidden md:flex items-center">
                  <span class="strategy-badge" :class="getStrategyBadgeClass(strategy.name)">
                    {{ strategy.name }}
                  </span>
                </div>

                <!-- 列2: 核心数据区 (移动端铺满，桌面端Fixed 260px) -->
                <div class="flex items-center justify-between md:justify-start gap-1 w-full md:w-auto">
                  <!-- 左侧: 数据指标 -->
                  <div class="flex flex-col md:justify-center gap-1.5 flex-shrink-0 min-w-[120px]">
                    <!-- 上方: 当日市值 -->
                    <div class="flex items-baseline gap-2">
                      <span class="text-xs text-slate-400">市值</span>
                      <span class="text-base font-bold text-slate-800 font-mono">
                        {{ formatNumberWithComma(strategy.marketValue) }}
                      </span>
                    </div>

                    <!-- 中间: 盈亏数据 -->
                    <div class="flex items-center gap-3">
                      <div class="flex flex-col">
                        <span class="text-[10px] text-slate-400">浮盈</span>
                        <span :class="['text-xs font-semibold font-mono', profitTextClass(strategy.floatingProfit)]">
                          {{ formatSignedNumberWithComma(strategy.floatingProfit) }}
                        </span>
                      </div>
                      <div class="flex flex-col">
                        <span class="text-[10px] text-slate-400">总实盈</span>
                        <span :class="['text-xs font-semibold font-mono', profitTextClass(strategy.realizedProfit)]">
                          {{ formatSignedNumberWithComma(strategy.realizedProfit) }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- 右侧: Sparkline (紧跟数据) -->
                  <div v-if="strategy.hasCurveData && strategy.sparklineData.length > 0" class="flex-shrink-0">
                    <svg width="120" height="30" class="sparkline opacity-80">
                      <polyline
                        :points="generateSparklinePoints(strategy.sparklineData, 120, 30)"
                        :stroke="getSparklineColor(strategy.sparklineData)"
                        stroke-width="1.5"
                        fill="none"
                      />
                    </svg>
                  </div>
                </div>

                <!-- 列3: 容量仪表区 (移动端铺满，桌面端Fixed 160px) -->
                <div class="flex flex-col gap-1.5 justify-center w-full md:w-auto">
                  <!-- 进度条区域 -->
                  <div class="flex items-center gap-2">
                    <div class="flex-grow h-1.5 bg-slate-100 rounded-full overflow-hidden border border-slate-100">
                      <div 
                        class="h-full rounded-full transition-all duration-500"
                        :class="getProgressBarColorClass(strategy)"
                        :style="{ width: getUsagePercent(strategy) + '%' }"
                      ></div>
                    </div>
                    <!-- 占比文字 -->
                    <div :class="['text-xs font-bold whitespace-nowrap w-10 text-right', getUsageColorClass(strategy)]">
                      {{ getUsagePercent(strategy) }}%
                    </div>
                  </div>
                  <!-- 数值对比 -->
                  <div class="text-[10px] text-slate-400 font-mono flex justify-end gap-1">
                    <span>容量占比：<span class="font-bold text-slate-700">{{ formatNumberWithComma(strategy.marketValue) }}</span>/{{ formatNumberWithComma(strategy.capacity) }}</span>
                  </div>
                </div>

                <!-- 列4: 证券持仓区 (Flex 1fr) -->
                <div class="flex items-start justify-start gap-3 h-auto md:h-full overflow-x-auto md:overflow-hidden w-full md:w-auto pb-2 md:pb-0 hide-scrollbar">
                  <div 
                    v-for="(sec, idx) in getTopHoldings(strategy.securities)" 
                    :key="idx"
                    class="bg-slate-50 border border-slate-200 rounded-lg p-2 w-[calc(50%-6px)] md:w-44 h-[72px] flex flex-col justify-between flex-shrink-0 group hover:border-slate-300 transition-colors"
                  >
                    <!-- 上部分: 名称和代码 -->
                    <div>
                      <div class="flex items-center justify-between gap-2">
                        <div class="text-xs font-semibold text-slate-700 truncate" :title="sec.name">{{ sec.name }}</div>
                        <div class="text-[10px] text-slate-400 font-mono">{{ sec.code }}</div>
                      </div>
                    </div>
                    
                    <!-- 下部分: 数据 -->
                    <div class="flex items-end justify-between mt-1">
                      <div class="flex flex-col">
                        <span class="text-[10px] text-slate-400">持仓数量</span>
                        <span class="text-xs font-mono font-medium text-slate-600">{{ formatNumberWithComma(sec.holdQty) }}</span>
                      </div>
                      <div class="flex flex-col items-end">
                        <span class="text-[10px] text-slate-400">浮盈</span>
                        <span :class="['text-xs font-mono font-semibold', profitTextClass(sec.floatingProfit)]">
                          {{ formatSignedNumberWithComma(sec.floatingProfit) }}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 更多提示 -->
                  <div v-if="strategy.securities.length > 2" class="flex flex-col justify-center h-[72px] pl-1 flex-shrink-0">
                    <span class="text-xs font-bold text-slate-400">+{{ strategy.securities.length - 2 }}</span>
                  </div>
                </div>
                
                <!-- 列5: 操作区 (Fixed 80px) - 只在桌面端显示 -->
                <div class="hidden md:flex flex-col items-center justify-center gap-2 border-l border-slate-100 h-10 pl-4 flex-shrink-0">
                  <div class="flex items-center gap-1">
                    <!-- 深度分析按钮 -->
                    <button
                      v-if="strategy.hasCurveData"
                      @click="openChartModal(strategy)"
                      class="p-1.5 rounded hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
                      title="查看深度分析"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    </button>
                    
                    <!-- 展开/折叠按钮 -->
                    <button
                      v-if="strategy.securities.length > 0"
                      @click="toggleExpand(visibleStrategies.indexOf(strategy))"
                      class="p-1.5 rounded hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
                      :title="expandedStrategies[visibleStrategies.indexOf(strategy)] ? '收起明细' : '展开明细'"
                    >
                      <svg 
                        xmlns="http://www.w3.org/2000/svg" 
                        class="h-4 w-4 transition-transform duration-200"
                        :class="{ 'rotate-180': expandedStrategies[visibleStrategies.indexOf(strategy)] }"
                        fill="none" 
                        viewBox="0 0 24 24" 
                        stroke="currentColor"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                  </div>
                  
                  <!-- 持仓数 -->
                  <div class="text-[10px] text-slate-400 font-medium">
                    {{ strategy.securities.length }}只持仓
                  </div>
                </div>
              </div>
            </div>

            <!-- 持仓明细微表格 (折叠区域) -->
            <transition name="slide-down">
              <div v-if="expandedStrategies[visibleStrategies.indexOf(strategy)]" class="mt-3 bg-gradient-to-br from-slate-50/80 to-slate-100/50 rounded-2xl overflow-hidden shadow-inner overflow-x-auto relative">
                <table class="w-full text-sm">
                  <thead>
                    <tr class="text-xs uppercase tracking-wide text-slate-600 bg-slate-100/50">
                      <th class="text-center py-3 px-2 font-semibold sticky-col sticky-col-1">证券名称</th>
                      <th class="text-center py-3 px-2 font-semibold sticky-col sticky-col-2">证券代码</th>
                      <th class="text-center py-3 px-2 font-semibold">持仓数量</th>
                      <th class="text-center py-3 px-2 font-semibold">当前市值</th>
                      <th class="text-center py-3 px-2 font-semibold">浮动盈亏</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr 
                      v-for="(sec, idx) in getSortedSecurities(strategy.securities)" 
                      :key="idx"
                      class="border-t border-slate-200/40 hover:bg-white/60 transition-all duration-150"
                    >
                      <td class="py-3 px-2 text-slate-700 font-medium text-center sticky-col sticky-col-1 bg-inherit">{{ sec.name }}</td>
                      <td class="py-3 px-2 text-slate-500 font-mono text-center sticky-col sticky-col-2 bg-inherit">{{ sec.code }}</td>
                      <td class="py-3 px-2 text-center text-slate-700 font-bold font-mono">{{ formatNumberWithComma(sec.holdQty) }}</td>
                      <td class="py-3 px-2 text-center text-slate-700 font-bold font-mono">{{ formatNumberWithComma(sec.marketValue) }}</td>
                      <td class="py-3 px-2 text-center font-bold font-mono" :class="profitTextClass(sec.floatingProfit)">
                        {{ formatSignedNumberWithComma(sec.floatingProfit) }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </transition>
          </div>
        </div>

        <!-- 展开更多按钮 -->
        <div v-if="hasEmptyStrategies" class="flex justify-center pt-2">
          <button
            @click="showEmptyStrategies = !showEmptyStrategies"
            class="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg transition-colors flex items-center gap-2"
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              class="h-4 w-4 transition-transform duration-200"
              :class="{ 'rotate-180': showEmptyStrategies }"
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
            <span>{{ showEmptyStrategies ? '收起空仓策略' : '展开更多策略' }}</span>
          </button>
        </div>
      </div>

      <!-- 深度分析模态框 -->
      <transition name="modal-fade">
        <div 
          v-if="showChartModal" 
          class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4"
          @click.self="closeChartModal"
        >
          <div class="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
            <!-- 模态框头部 -->
            <div class="flex items-center justify-between p-4 border-b border-slate-200">
              <h3 class="text-lg font-semibold text-slate-800">
                {{ selectedStrategy?.name }} - 实现盈亏曲线
              </h3>
              <button 
                @click="closeChartModal"
                class="p-2 rounded-lg hover:bg-slate-100 transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <!-- 模态框内容 -->
            <div class="p-6">
              <div class="h-96 w-full" ref="modalChart"></div>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import axios from '@/utils/axios';
import { API_ENDPOINTS } from '@/config/api';
import * as echarts from 'echarts';

export default {
  name: 'WealthCockpit',
  data() {
    return {
      loading: false,
      error: null,
      apiData: null,
      dailyStatData: {
        assets: 0,
        avaliable: 0,
        cash: 0,
        busi_date: '',
        market_value: 0
      },
      processedStrategies: [],
      userName: '',
      dailyClearDate: '',
      chartInstances: [],
      showCharts: false, // 默认折叠曲线
      expandedStrategies: [], // 记录每个策略的展开状态
      showChartModal: false, // 深度分析模态框显示状态
      selectedStrategy: null, // 当前选中的策略
      modalChartInstance: null, // 模态框中的图表实例
      showEmptyStrategies: false // 控制空仓策略显示
    };
  },
  computed: {
    isEmptyPosition() {
      // If we have no strategies with holdings, consider it empty position (or check raw data)
      return !this.processedStrategies || this.processedStrategies.length === 0;
    },
    visibleStrategies() {
      if (this.showEmptyStrategies) {
        return this.processedStrategies;
      }
      return this.processedStrategies.filter(s => s.isActive);
    },
    hasEmptyStrategies() {
      return this.processedStrategies.some(s => !s.isActive);
    },
    summary() {
      if (!this.apiData) {
         return {
            totalCost: 0,
            totalMarketValue: 0,
            totalRealizedProfit: 0,
            floatingProfit: 0
         };
      }

      const { latest_daily_clear, now_realize_info } = this.apiData;
      
      let totalCost = 0;
      let totalMarketValue = 0;
      
      // Sum from latest_daily_clear
      if (latest_daily_clear) {
          latest_daily_clear.forEach(item => {
             totalCost += Number(item.total_cost || 0);
             totalMarketValue += Number(item.market_value || 0);
          });
      }

      // Sum realized profit from now_realize_info
      let totalRealizedProfit = 0;
      if (now_realize_info) {
          Object.values(now_realize_info).forEach(val => {
              totalRealizedProfit += Number(val || 0);
          });
      }

      return {
          totalCost,
          totalMarketValue,
          totalRealizedProfit,
          floatingProfit: totalMarketValue - totalCost
      };
    },
    floatingProfitPercent() {
      // Use Daily Total Assets as denominator
      if (!this.dailyStatData || !this.dailyStatData.assets) return 0;
      return (this.summary.floatingProfit / this.dailyStatData.assets) * 100;
    },
    realizedProfitPercent(){
       // Use Daily Total Assets as denominator
       if (!this.dailyStatData || !this.dailyStatData.assets) return 0;
       return (this.summary.totalRealizedProfit / this.dailyStatData.assets) * 100;
    },
    formattedClearDate() {
       if (this.dailyClearDate && this.dailyClearDate.length === 8) {
           return `${this.dailyClearDate.substring(0, 4)}-${this.dailyClearDate.substring(4, 6)}-${this.dailyClearDate.substring(6, 8)}`;
       }
       return this.dailyClearDate;
    }
  },
  methods: {
    async fetchData() {
      this.loading = true;
      this.error = null;
      try {
        // 并行请求两个接口
        const [cockpitResponse, dailyStatResponse] = await Promise.all([
          axios.get(API_ENDPOINTS.GET_COCKPIT),
          axios.get(API_ENDPOINTS.GET_DAILY_STAT)
        ]);
        
        // 处理驾驶舱数据
        if (cockpitResponse.data.code === 200 && cockpitResponse.data.data) {
           this.apiData = cockpitResponse.data.data;
           this.userName = this.apiData.user; 
           this.processData();
        } else {
           this.error = cockpitResponse.data.msg || '获取驾驶舱数据失败';
        }
        
        // 处理每日统计数据
        if (dailyStatResponse.data.code === 0 && dailyStatResponse.data.infos && dailyStatResponse.data.infos.length > 0) {
           const info = dailyStatResponse.data.infos[0];
           this.dailyStatData = {
             assets: Number(info.assets || 0),
             avaliable: Number(info.avaliable || 0),
             cash: Number(info.cash || 0),
             busi_date: info.busi_date || '',
             market_value: Number(info.market_value || 0)
           };
        }
      } catch (err) {
         console.error('获取财富驾驶舱数据失败:', err);
         if (!(err.response && err.response.status === 401)) {
            this.error = '网络请求失败，请稍后重试';
         }
      } finally {
         this.loading = false;
         // After DOM update, init charts
         this.$nextTick(() => {
             this.initCharts();
         });
      }
    },
    processData() {
        if (!this.apiData) return;
        const { latest_daily_clear, history_curve_data } = this.apiData;
        const strategiesMap = {};

        // 1. Group latest_daily_clear by strategy_name
        if (latest_daily_clear) {
           this.dailyClearDate = latest_daily_clear.length > 0 ? latest_daily_clear[0].clear_date : '';
           latest_daily_clear.forEach(item => {
               if (!strategiesMap[item.strategy_name]) {
                   strategiesMap[item.strategy_name] = {
                       name: item.strategy_name,
                       capacity: Number(item.all_money || 0), // Assuming same for all items in strategy
                       marketValue: 0,
                       totalCost: 0,
                       securities: [],
                       curveData: [],
                       isActive: false // Flag to track if strategy has active holdings
                   };
               }
               
               // Only process if security_code is valid
               if (item.security_code) {
                   const marketValue = Number(item.market_value || 0);
                   const totalCost = Number(item.total_cost || 0);
                   
                   strategiesMap[item.strategy_name].marketValue += marketValue;
                   strategiesMap[item.strategy_name].totalCost += totalCost;
                   strategiesMap[item.strategy_name].securities.push({
                       code: item.security_code,
                       name: item.security_name,
                       marketValue: marketValue,
                       holdQty: Number(item.hold_qty || 0),
                       floatingProfit: marketValue - totalCost
                   });
                   strategiesMap[item.strategy_name].isActive = true;
               }
           });
        }
        
        // 2. Attach history_curve_data
        if (history_curve_data) {
            history_curve_data.forEach(point => {
                if (strategiesMap[point.strategy_name]) {
                    strategiesMap[point.strategy_name].curveData.push({
                        date: point.clear_date,
                        value: Number(point.realized_profit || 0)
                    });
                }
            });
        }

        // 3. Extract realized profit from now_realize_info
        const { now_realize_info } = this.apiData;
        
        // 4. Compute derived stats and flatten
        const strategiesList = Object.values(strategiesMap).map(strat => {
             // Capacity ratio
             let capacityRatio = 0;
             if (strat.capacity > 0) {
                 capacityRatio = (strat.marketValue / strat.capacity) * 100;
             }
             
             // Sort curve data by date
             strat.curveData.sort((a, b) => a.date.localeCompare(b.date));
             
             // Get last 10 days for sparkline
             const sparklineData = strat.curveData.slice(-10).map(d => d.value);
             
             // Get realized profit for this strategy from now_realize_info
             let realizedProfit = 0;
             if (now_realize_info && now_realize_info[strat.name]) {
                 realizedProfit = Number(now_realize_info[strat.name] || 0);
             }
             
             return {
                 ...strat,
                 floatingProfit: strat.marketValue - strat.totalCost,
                 capacityRatio,
                 realizedProfit,
                 hasCurveData: strat.curveData.length > 0,
                 sparklineData // 最后10天的数据
             };
        });

        // 5. Sort strategies: Active first (by market value desc), then empty positions (by realized profit)
        strategiesList.sort((a, b) => {
             // Active strategies first
             if (a.isActive && !b.isActive) return -1;
             if (!a.isActive && b.isActive) return 1;
             
             // For active strategies, sort by market value descending
             if (a.isActive && b.isActive) {
                 return b.marketValue - a.marketValue;
             }
             
             // For empty positions, sort by realized profit (non-zero first, then by absolute value)
             if (!a.isActive && !b.isActive) {
                 const aHasProfit = Math.abs(a.realizedProfit) > 0;
                 const bHasProfit = Math.abs(b.realizedProfit) > 0;
                 
                 if (aHasProfit && !bHasProfit) return -1;
                 if (!aHasProfit && bHasProfit) return 1;
                 
                 // Both have profit or both don't, sort by absolute value descending
                 return Math.abs(b.realizedProfit) - Math.abs(a.realizedProfit);
             }
             
             return 0;
        });

        this.processedStrategies = strategiesList;
        // Initialize expanded states
        this.expandedStrategies = new Array(strategiesList.length).fill(false);
    },
    initCharts() {
        // Dispose old charts
        this.chartInstances.forEach(inst => inst.dispose());
        this.chartInstances = [];

        this.$nextTick(() => {
            this.processedStrategies.forEach((strat, index) => {
                if (!strat.hasCurveData) {
                    return;
                }
                
                const refName = 'chart-' + index;
                const el = this.$refs[refName];
                const container = Array.isArray(el) ? el[0] : el;
                
                if (container) {
                    // Initialize chart even if dimensions are 0 initially
                    const chart = echarts.init(container);
                    const dates = strat.curveData.map(d => d.date.substring(4)); // MMDD
                    const values = strat.curveData.map(d => d.value);
                    
                    const isPositive = values.length > 0 ? values[values.length - 1] >= 0 : true;
                    const lineColor = isPositive ? '#ef4444' : '#10b981';
                    const areaColor = isPositive ? 'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)';

                    const option = {
                        grid: {
                            top: 20,
                            bottom: 30,
                            left: 45,
                            right: 15,
                            containLabel: false
                        },
                        tooltip: {
                            trigger: 'axis',
                            axisPointer: { type: 'line' },
                            formatter: function(params) {
                                const date = params[0].name;
                                const value = params[0].value;
                                return `${date}: ${value.toFixed(2)}`;
                            }
                        },
                        xAxis: {
                            type: 'category',
                            data: dates,
                            axisLine: {
                                lineStyle: { color: '#d1d5db' }
                            },
                            axisLabel: {
                                color: '#6b7280',
                                fontSize: 10,
                                interval: Math.floor(dates.length / 4) // Show ~5 labels
                            },
                            axisTick: {
                                show: false
                            }
                        },
                        yAxis: {
                            type: 'value',
                            axisLine: {
                                show: true,
                                lineStyle: { color: '#d1d5db' }
                            },
                            axisLabel: {
                                color: '#6b7280',
                                fontSize: 10,
                                formatter: (value) => value.toFixed(0)
                            },
                            splitLine: {
                                lineStyle: {
                                    color: '#e5e7eb',
                                    type: 'dashed'
                                }
                            },
                            scale: true,
                            min: (value) => value.min < 0 ? value.min : 0, 
                            max: (value) => value.max > 0 ? value.max : 100
                        },
                        series: [{
                            data: values,
                            type: 'line',
                            sampling: false,
                            smooth: true,
                            showSymbol: false,
                            lineStyle: { width: 2, color: lineColor },
                            areaStyle: { color: areaColor }
                        }]
                    };
                    
                    chart.setOption(option);
                    this.chartInstances.push(chart);
                    
                    // Force resize after a short delay
                    setTimeout(() => {
                        chart.resize();
                    }, 100);
                }
            });
        });
        
        // Handle resize
        window.addEventListener('resize', this.handleResize);
    },
    handleResize() {
        this.chartInstances.forEach(chart => chart.resize());
    },
    // Formatting Helpers
    formatNumber(val) {
      if (val === null || val === undefined || isNaN(Number(val))) return '—';
      return Number(val).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    },
    formatInteger(val) {
      if (val === null || val === undefined || isNaN(Number(val))) return '—';
      return Math.floor(Number(val)).toString();
    },
    formatSignedNumber(val) {
      if (val === null || val === undefined || isNaN(Number(val))) return '—';
      const num = Number(val);
      const sign = num > 0 ? '+' : '';
      return sign + num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    },
    formatSignedInteger(val) {
      if (val === null || val === undefined || isNaN(Number(val))) return '—';
      const num = Math.floor(Number(val));
      const sign = num > 0 ? '+' : '';
      return sign + num.toString();
    },
    formatPercent(val) {
      if (val === null || val === undefined || isNaN(Number(val))) return '—';
      return Number(val).toFixed(2) + '%';
    },
    profitTextClass(val) {
      const num = Number(val || 0);
      if (num > 0) return 'text-red-500';
      if (num < 0) return 'text-emerald-500';
      return 'text-slate-600';
    },
    profitBgClass(val) {
      const num = Number(val || 0);
      if (num > 0) return 'bg-red-50 text-red-600';
      if (num < 0) return 'bg-emerald-50 text-emerald-600';
      return 'bg-slate-50 text-slate-500';
    },
    getUsagePercent(strategy) {
      if (!strategy.capacity || strategy.capacity === 0) return 0;
      const percent = (strategy.marketValue / strategy.capacity) * 100;
      return Math.min(percent, 100).toFixed(1);
    },
    getProgressBarClass(strategy) {
      const percent = parseFloat(this.getUsagePercent(strategy));
      return percent > 90 ? 'bg-orange-400' : 'bg-blue-400';
    },
    getUsageTextClass(strategy) {
      const percent = parseFloat(this.getUsagePercent(strategy));
      return percent > 90 ? 'text-orange-500' : 'text-slate-500';
    },
    getStrategyBadgeClass(strategyName) {
      if (!strategyName) return '';
      // Use processedStrategies to get a deterministic list of currently displayed strategies
      // This ensures that active strategies get distinct colors relative to each other on this page
      const uniqueStrategies = [...new Set(this.processedStrategies.map(s => s.name))].sort();
      const index = uniqueStrategies.indexOf(strategyName);
      
      if (index === -1) return 'badge-color-1';
      
      // Cycle through 10 distinct colors
      const colorIndex = (index % 10) + 1;
      return `badge-color-${colorIndex}`;
    },
    // 新增：获取策略颜色(用于左侧边框)
    getStrategyColor(strategyName) {
      const colorMap = {
        1: '#0369a1', // Sky
        2: '#0e7490', // Cyan
        3: '#065f46', // Emerald
        4: '#c2410c', // Orange
        5: '#be185d', // Pink
        6: '#b91c1c', // Red
        7: '#a16207', // Yellow
        8: '#0f766e', // Teal
        9: '#3f6212', // Lime
        10: '#334155'  // Slate
      };
      
      const uniqueStrategies = [...new Set(this.processedStrategies.map(s => s.name))].sort();
      const index = uniqueStrategies.indexOf(strategyName);
      const colorIndex = index === -1 ? 1 : (index % 10) + 1;
      
      return colorMap[colorIndex] || colorMap[1];
    },
    // 新增:格式化数字(带千分位)
    formatNumberWithComma(val) {
      if (val === null || val === undefined || isNaN(Number(val))) return '—';
      return Math.floor(Number(val)).toLocaleString('zh-CN');
    },
    // 新增:格式化带符号数字(带千分位)
    formatSignedNumberWithComma(val) {
      if (val === null || val === undefined || isNaN(Number(val))) return '—';
      const num = Math.floor(Number(val));
      const sign = num > 0 ? '+' : '';
      return sign + num.toLocaleString('zh-CN');
    },
    // 新增：格式化数字(无千分位)
    formatNumberNoComma(val) {
      if (val === null || val === undefined || isNaN(Number(val))) return '—';
      return Math.floor(Number(val)).toString();
    },
    // 新增:格式化带符号数字(无千分位)
    formatSignedNumberNoComma(val) {
      if (val === null || val === undefined || isNaN(Number(val))) return '—';
      const num = Math.floor(Number(val));
      const sign = num > 0 ? '+' : '';
      return sign + num.toString();
    },
    // 获取容量利用率颜色类
    // 获取容量利用率颜色类
    getUsageColorClass(strategy) {
      const percent = parseFloat(this.getUsagePercent(strategy));
      if (percent >= 80) return 'text-orange-500';
      return 'text-blue-400';
    },
    // 新增:获取利用率光晕效果类
    getUsageGlowClass(strategy) {
      const percent = parseFloat(this.getUsagePercent(strategy));
      return percent > 95 ? 'usage-critical' : '';
    },
    // 获取进度条颜色类
    getProgressBarColorClass(strategy) {
      const percent = parseFloat(this.getUsagePercent(strategy));
      if (percent >= 80) return 'bg-orange-500';
      return 'bg-blue-300';
    },
    // 新增:获取进度条光晕效果类
    getProgressGlowClass(strategy) {
      const percent = parseFloat(this.getUsagePercent(strategy));
      return percent > 95 ? 'progress-critical' : '';
    },
    // 生成Sparkline的SVG points
    generateSparklinePoints(data, width = 40, height = 16) {
      if (!data || data.length === 0) return '';
      
      const padding = 2;
      
      const min = Math.min(...data);
      const max = Math.max(...data);
      const range = max - min || 1; // Avoid division by zero
      
      const points = data.map((value, index) => {
        const x = (index / (data.length - 1)) * (width - 2 * padding) + padding;
        const y = height - padding - ((value - min) / range) * (height - 2 * padding);
        return `${x},${y}`;
      });
      
      return points.join(' ');
    },
    // 新增：获取Sparkline颜色
    getSparklineColor(data) {
      if (!data || data.length === 0) return '#94a3b8';
      const lastValue = data[data.length - 1];
      return lastValue >= 0 ? '#ef4444' : '#10b981'; // 红色为正,绿色为负
    },
    // 切换展开/折叠
    toggleExpand(index) {
      // Vue 3 不需要 $set,直接修改数组元素
      this.expandedStrategies[index] = !this.expandedStrategies[index];
    },
    // 打开深度分析模态框
    openChartModal(strategy) {
      this.selectedStrategy = strategy;
      this.showChartModal = true;
      
      // 使用 setTimeout 确保 DOM 更新后再渲染图表
      setTimeout(() => {
        this.renderModalChart();
      }, 50);
    },
    // 新增：关闭模态框
    closeChartModal() {
      this.showChartModal = false;
      this.selectedStrategy = null;
      
      if (this.modalChartInstance) {
        this.modalChartInstance.dispose();
        this.modalChartInstance = null;
      }
    },
    // 新增：渲染模态框中的图表
    renderModalChart() {
      if (!this.selectedStrategy || !this.$refs.modalChart) return;
      
      // Dispose existing chart
      if (this.modalChartInstance) {
        this.modalChartInstance.dispose();
      }
      
      const chart = echarts.init(this.$refs.modalChart);
      const dates = this.selectedStrategy.curveData.map(d => {
        // Format date as MM-DD
        const dateStr = d.date.toString();
        return `${dateStr.substring(4, 6)}-${dateStr.substring(6, 8)}`;
      });
      const values = this.selectedStrategy.curveData.map(d => d.value);
      
      const isPositive = values.length > 0 ? values[values.length - 1] >= 0 : true;
      const lineColor = isPositive ? '#ef4444' : '#10b981';
      const areaColor = isPositive ? 'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)';
      
      const option = {
        grid: {
          top: 40,
          bottom: 60,
          left: 80,
          right: 40,
          containLabel: false
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'line' },
          formatter: function(params) {
            const date = params[0].name;
            const value = params[0].value;
            return `${date}<br/>实现盈亏: ${value.toFixed(2)}`;
          }
        },
        xAxis: {
          type: 'category',
          data: dates,
          axisLine: {
            lineStyle: { color: '#d1d5db' }
          },
          axisLabel: {
            color: '#6b7280',
            fontSize: 12,
            rotate: 45
          },
          axisTick: {
            show: false
          }
        },
        yAxis: {
          type: 'value',
          axisLine: {
            show: true,
            lineStyle: { color: '#d1d5db' }
          },
          axisLabel: {
            color: '#6b7280',
            fontSize: 12,
            formatter: (value) => value.toFixed(0)
          },
          splitLine: {
            lineStyle: {
              color: '#e5e7eb',
              type: 'dashed'
            }
          },
          scale: true
        },
        series: [{
          data: values,
          type: 'line',
          sampling: false,
          smooth: true,
          showSymbol: true,
          symbolSize: 6,
          lineStyle: { width: 3, color: lineColor },
          areaStyle: { color: areaColor },
          itemStyle: { color: lineColor }
        }]
      };
      
      chart.setOption(option);
      this.modalChartInstance = chart;
      
      // Handle resize
      window.addEventListener('resize', () => {
        if (this.modalChartInstance) {
          this.modalChartInstance.resize();
        }
      });
    },
    // 获取核心持仓(市值最高的2个)
    getTopHoldings(securities) {
      if (!securities || securities.length === 0) return [];
      return securities
        .slice()
        .sort((a, b) => b.marketValue - a.marketValue)
        .slice(0, 2);
    },
    // 获取排序后的证券列表(按市值降序)
    getSortedSecurities(securities) {
      if (!securities || securities.length === 0) return [];
      return securities
        .slice()
        .sort((a, b) => b.marketValue - a.marketValue);
    }
  },
  watch: {
    showCharts(newVal) {
      if (newVal) {
        // When charts are shown, reinitialize them after DOM update
        this.$nextTick(() => {
          this.initCharts();
        });
      }
    }
  },
  mounted() {
    this.fetchData();
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize);
    this.chartInstances.forEach(inst => inst.dispose());
    if (this.modalChartInstance) {
      this.modalChartInstance.dispose();
    }
  }
};
</script>

<style scoped>
.etf-cockpit-loading,
.etf-cockpit-error {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  font-size: 14px;
  color: #64748b;
}

.w-full.mx-auto.max-w-6xl {
  padding: 24px;
  min-height: calc(100vh - 64px);
}

/* 横向长条卡片样式 */
.strategy-row-card {
  position: relative;
}

.strategy-row {
  cursor: pointer;
}

/* Sparkline 样式 */
.sparkline {
  display: block;
}

/* 折叠动画 */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
  max-height: 500px;
  overflow: hidden;
}

.slide-down-enter-from,
.slide-down-leave-to {
  max-height: 0;
  opacity: 0;
}

/* 模态框动画 */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

/* Chart container styles */
.chart-container {
  width: 100%;
  height: 160px; /* h-40 = 10rem = 160px */
  min-height: 160px;
  position: relative;
}

/* Dark Mode Adaptation */
body.dark-mode .w-full.mx-auto.max-w-6xl {
  background-color: #1a1a1a !important;
}

body.dark-mode .w-full.mx-auto.max-w-6xl .text-slate-800,
body.dark-mode .w-full.mx-auto.max-w-6xl .text-slate-900 {
  color: #e0e0e0 !important;
}

body.dark-mode .w-full.mx-auto.max-w-6xl .text-slate-500,
body.dark-mode .w-full.mx-auto.max-w-6xl .text-slate-600,
body.dark-mode .w-full.mx-auto.max-w-6xl .text-slate-700 {
  color: #cbd5e1 !important; /* Lighter slate for better visibility */
}

body.dark-mode .w-full.mx-auto.max-w-6xl .text-slate-400 {
  color: #94a3b8 !important; /* Lighter slate-400 */
}

/* Fix dark text visibility in dark mode */
body.dark-mode .text-gray-800 {
  color: #e2e8f0 !important;
}

body.dark-mode .text-gray-600 {
  color: #cbd5e1 !important;
}

body.dark-mode .rounded-xl,
body.dark-mode .rounded-lg {
  background-color: #2d2d2d !important;
  border-color: #4c4d4f !important;
}

body.dark-mode .strategy-row {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
}

body.dark-mode .bg-gray-50,
body.dark-mode .bg-slate-50 {
  background-color: #383838 !important;
  border-color: #4c4d4f !important;
}

body.dark-mode .bg-slate-100 {
  background-color: #3d3d3d !important;
}

body.dark-mode .hover\:bg-slate-100:hover {
  background-color: #3d3d3d !important;
}

/* Strategy Badge Styles - 10 Distinct Colors (No Purple) */
.strategy-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}

.badge-color-1 { background-color: #e0f2fe; color: #0369a1; } /* Sky */
.badge-color-2 { background-color: #cffafe; color: #0e7490; } /* Cyan */
.badge-color-3 { background-color: #d1fae5; color: #065f46; } /* Emerald */
.badge-color-4 { background-color: #fed7aa; color: #c2410c; } /* Orange */
.badge-color-5 { background-color: #fce7f3; color: #be185d; } /* Pink */
.badge-color-6 { background-color: #fee2e2; color: #b91c1c; } /* Red */
.badge-color-7 { background-color: #fef9c3; color: #a16207; } /* Yellow */
.badge-color-8 { background-color: #ccfbf1; color: #0f766e; } /* Teal */
.badge-color-9 { background-color: #ecfccb; color: #3f6212; } /* Lime */
.badge-color-10 { background-color: #f1f5f9; color: #334155; } /* Slate */

/* Dark Mode Badge Styles */
body.dark-mode .badge-color-1 { background-color: #1e3a8a; color: #93c5fd; }
body.dark-mode .badge-color-2 { background-color: #164e63; color: #67e8f9; }
body.dark-mode .badge-color-3 { background-color: #14532d; color: #86efac; }
body.dark-mode .badge-color-4 { background-color: #7c2d12; color: #fdba74; }
body.dark-mode .badge-color-5 { background-color: #831843; color: #f9a8d4; }
body.dark-mode .badge-color-6 { background-color: #7f1d1d; color: #fca5a5; }
body.dark-mode .badge-color-7 { background-color: #713f12; color: #fde047; }
body.dark-mode .badge-color-8 { background-color: #115e59; color: #5eead4; }
body.dark-mode .badge-color-9 { background-color: #365314; color: #bef264; }
body.dark-mode .badge-color-10 { background-color: #334155; color: #cbd5e1; }

/* Profit/Loss Colors */
body.dark-mode .text-emerald-600 { color: #10b981 !important; }
body.dark-mode .bg-emerald-50 { background-color: rgba(16, 185, 129, 0.1) !important; }
body.dark-mode .text-red-500 { color: #ef4444 !important; }
body.dark-mode .text-red-600 { color: #f87171 !important; }
body.dark-mode .bg-red-50 { background-color: rgba(239, 68, 68, 0.1) !important; }

/* Usage Rate Colors */
body.dark-mode .text-blue-500 { color: #3b82f6 !important; }
body.dark-mode .text-yellow-500 { color: #eab308 !important; }
body.dark-mode .text-orange-500 { color: #f97316 !important; }

body.dark-mode .border-slate-200,
body.dark-mode .border-slate-100 {
  border-color: #3d3d3d !important;
}

/* Modal Dark Mode */
body.dark-mode .fixed.inset-0 .bg-white {
  background-color: #2d2d2d !important;
}

body.dark-mode .fixed.inset-0 .border-slate-200 {
  border-color: #4c4d4f !important;
}

/* 利用率 > 95% 光晕效果 */
.usage-critical {
  text-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
}

.progress-critical {
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.6);
}

/* 深色模式下的光晕效果 */
body.dark-mode .usage-critical {
  text-shadow: 0 0 10px rgba(239, 68, 68, 0.7);
}

body.dark-mode .progress-critical {
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.8);
}

/* Mobile Sticky Columns */
@media (max-width: 768px) {
  .sticky-col {
    position: sticky;
    z-index: 10;
  }
  
  /* Security Name Column */
  .sticky-col-1 {
    left: 0;
    min-width: 90px;
    z-index: 20; /* Higher validation than col 2 */
  }
  
  /* Security Code Column */
  .sticky-col-2 {
    left: 90px; /* Offset by approx width of col 1 */
    min-width: 80px;
    z-index: 20;
    border-right: 1px solid rgba(226, 232, 240, 0.6); /* Slight separation using border-slate-200/60 */
  }

  /* Specific backgrounds for sticky cells to prevent transparency */
  .sticky-col-1, .sticky-col-2 {
      background-color: #f8fafc; /* bg-slate-50 */
  }
  
  tbody tr .sticky-col-1, tbody tr .sticky-col-2 {
      background-color: #f8fafc; /* Fallback */
  }
  
  /* Ensure hover effect doesn't break background of sticky cols too much, or force them to follow row bg */
  /* Actually, for sticky to work cleanly with row hovers, we need the cell to inherit bg or set it explicitly. */
  /* Since we have a gradient bg on the container and hover effects, solid color might look slightly off but it's checking constraints. */
  /* Let's try matching the container's base color roughly or white/slate-50 */
  
  /* Dark mode support for sticky columns */
  body.dark-mode table .sticky-col-1,
  body.dark-mode table .sticky-col-2,
  body.dark-mode .sticky-col-1,
  body.dark-mode .sticky-col-2 {
      background-color: #2d2d2d !important;
      border-right-color: #4c4d4f;
  }
}
</style>
