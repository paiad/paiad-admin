<template>
  <div class="data-screen-container">
    <header class="screen-header">
      <h1 class="header-title">数据大屏</h1>
      <div class="header-extra">
        <span class="current-time">{{ currentTime }}</span>
      </div>
    </header>

    <div class="screen-body">
      <section class="kpi-area">
        <div class="kpi-card">
          <div class="kpi-icon">📈</div>
          <div class="kpi-content">
            <span class="kpi-value">{{ kpiData.totalSales.toLocaleString() }}</span>
            <span class="kpi-label">总销售额 (元)</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon">📄</div>
          <div class="kpi-content">
            <span class="kpi-value">{{ kpiData.totalOrders.toLocaleString() }}</span>
            <span class="kpi-label">总订单数</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon">📦</div>
          <div class="kpi-content">
            <span class="kpi-value">{{ kpiData.skuCount }}</span>
            <span class="kpi-label">商品SKU数</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon warning-icon">⚠️</div>
          <div class="kpi-content">
            <span class="kpi-value">{{ kpiData.lowStockWarning }}</span>
            <span class="kpi-label">低库存预警</span>
          </div>
        </div>
      </section>

      <main class="main-content">
        <div class="chart-card sales-rank">
          <h2 class="card-title">商品销售排行</h2>
          <div class="chart-container" ref="rankingChartDom"></div>
        </div>
        <div class="chart-card inventory-status">
          <h2 class="card-title">库存状态分布</h2>
          <div class="chart-container" ref="inventoryChartDom"></div>
        </div>
        <div class="chart-card order-map">
          <h2 class="card-title">订单地理分布</h2>
          <div class="chart-container" ref="mapChartDom"></div>
        </div>
        <div class="chart-card sales-trend">
          <h2 class="card-title">近30日销售趋势</h2>
          <div class="chart-container" ref="trendChartDom"></div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, nextTick } from 'vue';
import * as echarts from 'echarts';
import { chinaGeoJson } from './china-geojson';

// --- 响应式状态定义 ---
const currentTime = ref('');
let timerId: number | null = null;
let kpiUpdateTimer: number | null = null;

// ECharts 实例
let rankingChart: echarts.ECharts | null = null;
let inventoryChart: echarts.ECharts | null = null;
let mapChart: echarts.ECharts | null = null;
let trendChart: echarts.ECharts | null = null;

// DOM 引用
const rankingChartDom = ref<HTMLElement>();
const inventoryChartDom = ref<HTMLElement>();
const mapChartDom = ref<HTMLElement>();
const trendChartDom = ref<HTMLElement>();

// 模拟的业务数据
const kpiData = reactive({
  totalSales: 7895432,
  totalOrders: 13589,
  skuCount: 128,
  lowStockWarning: 15,
});

// --- ECharts 浅色主题颜色配置 ---
const themeColors = {
  primary: '#337ecc',
  text: '#333333',
  axisLine: '#cccccc',
  splitLine: '#eeeeee',
  tooltipBg: 'rgba(255, 255, 255, 0.9)',
  tooltipBorder: '#cccccc',
};


// --- ECharts 配置项 ---

// 销售排行条形图
const getRankingChartOption = computed(() => {
  const data = [
    { value: 18203, name: '智能降噪耳机' },
    { value: 23489, name: '机械键盘' },
    { value: 29034, name: '4K显示器' },
    { value: 30497, name: '人体工学椅' },
    { value: 33231, name: '便携咖啡机' }
  ].sort((a,b) => a.value - b.value);

  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '25%', right: '10%', top: '10%', bottom: '10%' },
    xAxis: {
      type: 'value',
      axisLabel: { color: themeColors.text },
      splitLine: { lineStyle: { color: themeColors.splitLine } }
    },
    yAxis: {
      type: 'category',
      data: data.map(item => item.name),
      axisLabel: { color: themeColors.text },
      axisLine: { lineStyle: { color: themeColors.axisLine } }
    },
    series: [{
      name: '销量', type: 'bar',
      data: data.map(item => item.value),
      itemStyle: { color: themeColors.primary }
    }]
  };
});

// 库存状态环形图
const getInventoryChartOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: {
    bottom: '5%', left: 'center',
    textStyle: { color: themeColors.text }
  },
  series: [{
    name: '库存状态', type: 'pie',
    radius: ['50%', '70%'],
    avoidLabelOverlap: false,
    label: { show: false, position: 'center' },
    emphasis: { label: { show: true, fontSize: 20, fontWeight: 'bold' } },
    labelLine: { show: false },
    data: [
      { value: 83, name: '库存健康' },
      { value: 15, name: '低库存' },
      { value: 5, name: '缺货' }
    ],
    color: ['#67C23A', '#E6A23C', '#F56C6C']
  }]
}));

// 地图配置
const getMapChartOption = computed(() => {
  echarts.registerMap('china', chinaGeoJson as any);
  return {
    tooltip: { trigger: 'item', formatter: '{b}<br/>订单数: {c}' },
    visualMap: {
      min: 80, max: 5000,
      text: ['高', '低'],
      realtime: false, calculable: true,
      inRange: { color: ['#50a3ba', '#eac736', '#d94e5d'].reverse() }, // 调整颜色以适应浅色主题
      textStyle: { color: themeColors.text }
    },
    series: [{
      name: '订单分布', type: 'map', map: 'china',
      roam: true,
      label: { show: false },
      emphasis: { label: { show: true, color: '#333' }, itemStyle: { areaColor: '#ffc107' } },
      data: [
        { name: '北京', value: 2800 }, { name: '天津', value: 1200 },
        { name: '上海', value: 4500 }, { name: '重庆', value: 2200 },
        { name: '河北', value: 1800 }, { name: '河南', value: 1900 },
        { name: '云南', value: 900 },  { name: '辽宁', value: 1100 },
        { name: '湖南', value: 1500 }, { name: '安徽', value: 1600 },
        { name: '山东', value: 2500 }, { name: '新疆', value: 300 },
        { name: '江苏', value: 3800 }, { name: '浙江', value: 4200 },
        { name: '江西', value: 1300 }, { name: '湖北', value: 1700 },
        { name: '广西', value: 1100 }, { name: '甘肃', value: 400 },
        { name: '山西', value: 900 },  { name: '陕西', value: 1000 },
        { name: '吉林', value: 800 },  { name: '福建', value: 2100 },
        { name: '贵州', value: 850 },  { name: '广东', value: 4800 },
        { name: '青海', value: 200 },  { name: '西藏', value: 100 },
        { name: '四川', value: 2600 }, { name: '宁夏', value: 350 },
        { name: '海南', value: 700 },  { name: '台湾', value: 600 },
        { name: '香港', value: 1300 }, { name: '澳门', value: 400 }
      ]
    }]
  };
});

// 销售趋势折线图
const getTrendChartOption = computed(() => {
  const date = [...Array(30)].map((_, i) => {
    const d = new Date();
    d.setDate(d.getDate() - 29 + i);
    return `${d.getMonth() + 1}-${d.getDate()}`;
  });
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: '10%', right: '5%', top: '15%', bottom: '15%' },
    xAxis: { type: 'category', boundaryGap: false, data: date,
      axisLine: { lineStyle: { color: themeColors.axisLine } },
      axisLabel: { color: themeColors.text },
    },
    yAxis: { type: 'value',
      axisLine: { show: true, lineStyle: { color: themeColors.axisLine } },
      axisLabel: { color: themeColors.text },
      splitLine: { lineStyle: { color: themeColors.splitLine } }
    },
    series: [{
      name: '销售额', type: 'line', smooth: true,
      data: [...Array(30)].map(() => Math.floor(Math.random() * (30000 - 10000 + 1)) + 10000),
      itemStyle: { color: themeColors.primary },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: themeColors.primary },
          { offset: 1, color: 'rgba(51, 126, 204, 0)' }
        ])
      }
    }]
  };
});


// --- 方法 ---
const updateTime = () => {
  const now = new Date();
  currentTime.value = now.toLocaleString('de-DE', { timeZone: 'Europe/Berlin' });
};

const initCharts = () => {
  rankingChart = echarts.init(rankingChartDom.value);
  inventoryChart = echarts.init(inventoryChartDom.value);
  mapChart = echarts.init(mapChartDom.value);
  trendChart = echarts.init(trendChartDom.value);

  rankingChart.setOption(getRankingChartOption.value);
  inventoryChart.setOption(getInventoryChartOption.value);
  mapChart.setOption(getMapChartOption.value);
  trendChart.setOption(getTrendChartOption.value);
};

const handleResize = () => {
  rankingChart?.resize();
  inventoryChart?.resize();
  mapChart?.resize();
  trendChart?.resize();
};

// --- 生命周期钩子 ---
onMounted(() => {
  updateTime();
  timerId = window.setInterval(updateTime, 1000);
  kpiUpdateTimer = window.setInterval(() => {
    kpiData.totalSales += Math.floor(Math.random() * 1000);
    kpiData.totalOrders += Math.floor(Math.random() * 20);
  }, 3000);

  nextTick(() => { initCharts() });
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  if (timerId) clearInterval(timerId);
  if (kpiUpdateTimer) clearInterval(kpiUpdateTimer);
  window.removeEventListener('resize', handleResize);
  rankingChart?.dispose();
  inventoryChart?.dispose();
  mapChart?.dispose();
  trendChart?.dispose();
});

</script>

<style lang="scss" scoped>
/* --- 浅色主题变量 --- */
.data-screen-container {
  --g-bg-color: #f0f2f5;
  --g-header-color: #303133;
  --g-text-color: #606266;
  --g-kpi-label-color: #909399;
  --g-card-bg: #ffffff;
  --g-card-border: #e4e7ed;
  --g-card-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  --g-card-title-color: #303133;
  --g-card-title-bar: #337ecc;
}

/* --- 基础与布局 --- */
.data-screen-container {
  width: 89vw;
  height: 100vh;
  padding: 20px;
  background-color: var(--g-bg-color);
  color: var(--g-text-color);
  font-family: 'Inter', 'MiSans', 'PingFang SC', sans-serif;
  box-sizing: border-box;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.screen-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 20px;
}

/* --- Header --- */
.screen-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}
.header-title {
  font-size: 28px;
  font-weight: bold;
  color: var(--g-header-color);
}
.header-extra {
  display: flex;
  align-items: center;
  gap: 20px;
}
.current-time {
  font-size: 16px;
  letter-spacing: 1px;
  background-color: var(--g-card-bg);
  padding: 8px 16px;
  border-radius: 4px;
  box-shadow: var(--g-card-shadow);
}

/* --- KPI 区域 --- */
.kpi-area {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}
.kpi-card {
  background-color: var(--g-card-bg);
  border: 1px solid var(--g-card-border);
  border-radius: 8px;
  padding: 15px 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s ease;
  box-shadow: var(--g-card-shadow);
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
  }
}
.kpi-icon {
  font-size: 40px;
  &.warning-icon { color: #F56C6C; }
}
.kpi-content {
  display: flex;
  flex-direction: column;
}
.kpi-value {
  font-size: 26px;
  font-weight: bold;
  color: var(--g-header-color);
}
.kpi-label {
  font-size: 14px;
  color: var(--g-kpi-label-color);
}

/* --- 主图表区域 Grid 布局 --- */
.main-content {
  flex: 1;
  display: grid;
  gap: 20px;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(2, 1fr);
  grid-template-areas:
    "rank map map trend"
    "inventory map map trend";
  min-height: 0; // 防止flex item溢出
}
.sales-rank { grid-area: rank; }
.inventory-status { grid-area: inventory; }
.order-map { grid-area: map; }
.sales-trend { grid-area: trend; }

/* --- 图表卡片通用样式 --- */
.chart-card {
  background-color: var(--g-card-bg);
  border: 1px solid var(--g-card-border);
  border-radius: 8px;
  padding: 16px;
  box-shadow: var(--g-card-shadow);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
  }
}

.card-title {
  font-size: 18px;
  color: var(--g-card-title-color);
  font-weight: 600;
  margin-bottom: 10px;
  flex-shrink: 0;
  &::before {
    content: ''; display: inline-block;
    width: 4px; height: 18px;
    background-color: var(--g-card-title-bar);
    margin-right: 8px; vertical-align: middle;
  }
}
.chart-container {
  width: 100%;
  height: 100%;
  flex: 1;
  min-height: 0; // 防止flex item溢出
}
</style>
