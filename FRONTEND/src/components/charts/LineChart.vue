<template>
  <div class="line-chart">
    <svg :width="width" :height="height" viewBox="0 0 600 300">
      <!-- Ejes -->
      <line x1="50" y1="250" x2="550" y2="250" stroke="#ddd" stroke-width="2" />
      <line x1="50" y1="250" x2="50" y2="20" stroke="#ddd" stroke-width="2" />
      
      <!-- Líneas de cuadrícula -->
      <template v-for="(tick, index) in yTicks" :key="index">
        <line
          :x1="50"
          :y1="tick.y"
          :x2="550"
          :y2="tick.y"
          stroke="#eee"
          stroke-width="1"
          stroke-dasharray="2,2"
        />
        <text :x="45" :y="tick.y + 5" text-anchor="end" font-size="11" fill="#666">
          {{ tick.value }}
        </text>
      </template>
      
      <!-- Línea del gráfico -->
      <polyline
        :points="linePoints"
        :fill="'none'"
        :stroke="props.data.color || '#409EFF'"
        stroke-width="3"
        class="line"
      />
      
      <!-- Puntos de datos -->
      <template v-for="(point, index) in dataPoints" :key="index">
        <circle
          :cx="point.x"
          :cy="point.y"
          r="5"
          :fill="props.data.color || '#409EFF'"
          class="point"
        />
        <text
          :x="point.x"
          :y="point.y - 10"
          text-anchor="middle"
          font-size="10"
          font-weight="bold"
          fill="#333"
        >
          {{ props.data.values[index] }}
        </text>
      </template>
      
      <!-- Etiquetas del eje X -->
      <template v-for="(label, index) in props.data.labels" :key="index">
        <text
          :x="getX(index)"
          :y="270"
          text-anchor="middle"
          font-size="10"
          fill="#666"
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
    color?: string
  }
}

const props = defineProps<Props>()

const width = 600
const height = 300
const padding = { top: 20, right: 50, bottom: 50, left: 50 }
const chartWidth = width - padding.left - padding.right
const chartHeight = height - padding.top - padding.bottom

const maxValue = computed(() => Math.max(...props.data.values, 1))

const yTicks = computed(() => {
  const ticks = 5
  const step = maxValue.value / ticks
  return Array.from({ length: ticks + 1 }, (_, i) => ({
    value: Math.round(step * (ticks - i)),
    y: padding.top + (chartHeight / ticks) * i
  }))
})

const dataPoints = computed(() => {
  return props.data.values.map((value, index) => ({
    x: getX(index),
    y: getY(value)
  }))
})

const linePoints = computed(() => {
  return dataPoints.value.map(p => `${p.x},${p.y}`).join(' ')
})

function getX(index: number): number {
  if (props.data.labels.length === 1) {
    return padding.left + chartWidth / 2
  }
  return padding.left + (index / (props.data.labels.length - 1)) * chartWidth
}

function getY(value: number): number {
  return padding.top + chartHeight - (value / maxValue.value) * chartHeight
}
</script>

<style scoped>
.line-chart {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.line {
  transition: all 0.3s ease;
}

.point {
  cursor: pointer;
  transition: all 0.3s ease;
}

.point:hover {
  r: 7;
  opacity: 0.8;
}
</style>
