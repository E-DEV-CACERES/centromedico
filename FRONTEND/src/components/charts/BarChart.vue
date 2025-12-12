<template>
  <div class="bar-chart">
    <svg :width="width" :height="height" viewBox="0 0 600 300">
      <!-- Ejes -->
      <line x1="50" y1="250" x2="550" y2="250" stroke="#ddd" stroke-width="2" />
      <line x1="50" y1="250" x2="50" y2="20" stroke="#ddd" stroke-width="2" />
      
      <!-- Etiquetas del eje Y -->
      <template v-for="(tick, index) in yTicks" :key="index">
        <line :x1="45" :y1="tick.y" :x2="50" :y2="tick.y" stroke="#ddd" stroke-width="1" />
        <text :x="40" :y="tick.y + 5" text-anchor="end" font-size="12" fill="#666">
          {{ tick.value }}
        </text>
      </template>
      
      <!-- Barras -->
      <template v-for="(value, index) in props.data.values" :key="index">
        <g>
          <rect
            :x="getBarX(index)"
            :y="getBarY(value)"
            :width="barWidth"
            :height="getBarHeight(value)"
            :fill="props.data.colors?.[index] || '#409EFF'"
            class="bar"
            :style="{ transition: 'all 0.3s ease' }"
          />
          <text
            :x="getBarX(index) + barWidth / 2"
            :y="getBarY(value) - 5"
            text-anchor="middle"
            font-size="11"
            font-weight="bold"
            fill="#333"
          >
            {{ value }}
          </text>
        </g>
      </template>
      
      <!-- Etiquetas del eje X -->
      <template v-for="(label, index) in props.data.labels" :key="index">
        <text
          :x="getBarX(index) + barWidth / 2"
          :y="270"
          text-anchor="middle"
          font-size="10"
          fill="#666"
          :transform="getTransform(index)"
        >
          {{ label }}
        </text>
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
const padding = { top: 20, right: 50, bottom: 50, left: 50 }
const chartWidth = width - padding.left - padding.right
const chartHeight = height - padding.top - padding.bottom

const maxValue = computed(() => Math.max(...props.data.values, 1))
const barWidth = computed(() => (chartWidth / props.data.values.length) * 0.7)
const barSpacing = computed(() => chartWidth / props.data.values.length)

const yTicks = computed(() => {
  const ticks = 5
  const step = maxValue.value / ticks
  return Array.from({ length: ticks + 1 }, (_, i) => ({
    value: Math.round(step * (ticks - i)),
    y: padding.top + (chartHeight / ticks) * i
  }))
})

function getBarX(index: number): number {
  return padding.left + (index * barSpacing.value) + (barSpacing.value - barWidth.value) / 2
}

function getBarY(value: number): number {
  return padding.top + chartHeight - (value / maxValue.value) * chartHeight
}

function getBarHeight(value: number): number {
  return (value / maxValue.value) * chartHeight
}

function getTransform(index: number): string {
  const x = getBarX(index) + barWidth.value / 2
  return `rotate(-45, ${x}, 270)`
}
</script>

<style scoped>
.bar-chart {
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
