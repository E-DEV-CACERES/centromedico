<template>
  <el-config-provider :locale="locale">
    <router-view />
  </el-config-provider>
</template>

<script setup lang="ts">
import { ElConfigProvider } from 'element-plus'
import es from 'element-plus/dist/locale/es.mjs'

const locale = es
</script>
