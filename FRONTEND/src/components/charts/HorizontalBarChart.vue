<template>
  <div class="horizontal-bar-chart">
    <svg :width="width" :height="height" viewBox="0 0 600 300">
      <!-- Ejes -->
      <line x1="150" y1="20" x2="150" y2="280" stroke="#ddd" stroke-width="2" />
      <line x1="150" y1="280" x2="550" y2="280" stroke="#ddd" stroke-width="2" />
      
      <!-- Etiquetas del eje X -->
      <template v-for="(tick, index) in xTicks" :key="index">
        <line
          :x1="tick.x"
          :y1="275"
          :x2="tick.x"
          :y2="280"
          stroke="#ddd"
          stroke-width="1"
        />
        <text :x="tick.x" :y="295" text-anchor="middle" font-size="11" fill="#666">
          {{ tick.value }}
        </text>
      </template>
      
      <!-- Barras horizontales -->
      <template v-for="(value, index) in props.data.values" :key="index">
        <g>
          <rect
            :x="150"
            :y="getBarY(index)"
            :width="getBarWidth(value)"
            :height="barHeight"
            :fill="props.data.colors[index] || defaultColors[index] || '#409EFF'"
            class="bar"
            :style="{ transition: 'all 0.3s ease' }"
          />
          <text
            :x="getBarWidth(value) + 155"
            :y="getBarY(index) + barHeight / 2 + 4"
            font-size="11"
            font-weight="bold"
            fill="#333"
          >
            {{ value }}
          </text>
          <text
            x="145"
            :y="getBarY(index) + barHeight / 2 + 4"
            text-anchor="end"
            font-size="11"
            fill="#666"
          >
            {{ props.data.labels[index] }}
          </text>
        </g>
      </template>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  data: {
    labels: string[]
    values: number[]
    colors?: string[]
  }
}

const props = defineProps<Props>()

const width = 600
const height = 300
const padding = { top: 20, right: 50, bottom: 50, left: 150 }
const chartWidth = width - padding.left - padding.right
const chartHeight = height - padding.top - padding.bottom

const maxValue = computed(() => Math.max(...props.data.values, 1))
const barHeight = computed(() => (chartHeight / props.data.values.length) * 0.7)
const barSpacing = computed(() => chartHeight / props.data.values.length)
const defaultColors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']

const xTicks = computed(() => {
  const ticks = 5
  const step = maxValue.value / ticks
  return Array.from({ length: ticks + 1 }, (_, i) => ({
    value: Math.round(step * i),
    x: padding.left + (i / ticks) * chartWidth
  }))
})

function getBarY(index: number): number {
  return padding.top + (index * barSpacing.value) + (barSpacing.value - barHeight.value) / 2
}

function getBarWidth(value: number): number {
  return (value / maxValue.value) * chartWidth
}
</script>

<style scoped>
.horizontal-bar-chart {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bar {
  cursor: pointer;
}

.bar:hover {
  opacity: 0.8;
}
</style>
