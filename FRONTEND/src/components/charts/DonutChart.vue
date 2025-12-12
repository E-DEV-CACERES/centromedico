<template>
  <div class="donut-chart">
    <svg :width="size" :height="size" viewBox="0 0 300 300">
      <g transform="translate(150, 150)">
        <template v-for="(value, index) in props.data.values" :key="index">
          <path
            :d="getArcPath(index)"
            :fill="props.data.colors[index] || defaultColors[index] || '#409EFF'"
            class="segment"
            :style="{ transition: 'all 0.3s ease' }"
          />
        </template>
        
        <!-- Centro con información -->
        <circle cx="0" cy="0" r="80" fill="white" />
        <text x="0" y="-10" text-anchor="middle" font-size="24" font-weight="bold" fill="#333">
          {{ total }}
        </text>
        <text x="0" y="15" text-anchor="middle" font-size="14" fill="#666">
          Total
        </text>
      </g>
    </svg>
    
    <!-- Leyenda -->
    <div class="legend">
      <div
        v-for="(label, index) in props.data.labels"
        :key="index"
        class="legend-item"
      >
        <div
          class="legend-color"
          :style="{ backgroundColor: props.data.colors[index] || defaultColors[index] || '#409EFF' }"
        />
        <span class="legend-label">{{ label }}</span>
        <span class="legend-value">({{ props.data.values[index] }})</span>
      </div>
    </div>
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

const size = 300
const radius = 100
const innerRadius = 80
const defaultColors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']

const total = computed(() => props.data.values.reduce((sum, val) => sum + val, 0))

function getArcPath(index: number): string {
  const startAngle = props.data.values
    .slice(0, index)
    .reduce((sum, val) => sum + (val / total.value) * 360, 0)
  
  const endAngle = startAngle + (props.data.values[index] / total.value) * 360
  
  const startAngleRad = ((startAngle - 90) * Math.PI) / 180
  const endAngleRad = ((endAngle - 90) * Math.PI) / 180
  
  const x1 = radius * Math.cos(startAngleRad)
  const y1 = radius * Math.sin(startAngleRad)
  const x2 = radius * Math.cos(endAngleRad)
  const y2 = radius * Math.sin(endAngleRad)
  
  const x3 = innerRadius * Math.cos(endAngleRad)
  const y3 = innerRadius * Math.sin(endAngleRad)
  const x4 = innerRadius * Math.cos(startAngleRad)
  const y4 = innerRadius * Math.sin(startAngleRad)
  
  const largeArc = endAngle - startAngle > 180 ? 1 : 0
  
  return `
    M ${x1} ${y1}
    A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2}
    L ${x3} ${y3}
    A ${innerRadius} ${innerRadius} 0 ${largeArc} 0 ${x4} ${y4}
    Z
  `
}
</script>

<style scoped>
.donut-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.segment {
  cursor: pointer;
}

.segment:hover {
  opacity: 0.8;
}

.legend {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
}

.legend-label {
  color: #333;
  min-width: 100px;
}

.legend-value {
  color: #666;
  font-weight: bold;
}
</style>
