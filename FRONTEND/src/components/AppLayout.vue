<template>
  <el-container class="min-h-screen">
    <el-aside width="250px" class="bg-gray-800 text-white">
      <div class="p-4 text-xl font-bold border-b border-gray-700">
        Centro Médico
      </div>
      <el-menu
        :default-active="activeMenu"
        class="border-0 bg-gray-800 text-white"
        router
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <span>Inicio</span>
        </el-menu-item>
        <el-menu-item index="/pacientes">
          <el-icon><User /></el-icon>
          <span>Pacientes</span>
        </el-menu-item>
        <el-menu-item index="/doctores">
          <el-icon><Avatar /></el-icon>
          <span>Doctores</span>
        </el-menu-item>
        <el-menu-item index="/citas">
          <el-icon><Calendar /></el-icon>
          <span>Citas</span>
        </el-menu-item>
        <el-menu-item index="/consultas">
          <el-icon><Document /></el-icon>
          <span>Consultas</span>
        </el-menu-item>
        <el-menu-item index="/facturacion">
          <el-icon><Money /></el-icon>
          <span>Facturación</span>
        </el-menu-item>
        <el-menu-item index="/recetas">
          <el-icon><Notebook /></el-icon>
          <span>Recetas</span>
        </el-menu-item>
        <el-menu-item index="/historial">
          <el-icon><Files /></el-icon>
          <span>Historial</span>
        </el-menu-item>
        <el-menu-item index="/examenes">
          <el-icon><Search /></el-icon>
          <span>Exámenes</span>
        </el-menu-item>
        <el-menu-item index="/usuarios">
          <el-icon><UserFilled /></el-icon>
          <span>Usuarios</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="bg-white shadow-sm border-b">
        <div class="flex items-center justify-between h-full">
          <h1 class="text-2xl font-semibold text-gray-800">
            {{ pageTitle }}
          </h1>
          <div class="flex items-center gap-4">
            <el-dropdown v-if="authStore.usuario" @command="handleCommand">
              <span class="flex items-center gap-2 cursor-pointer">
                <el-icon><UserFilled /></el-icon>
                <span class="text-sm">{{ authStore.usuario.Usuario }}</span>
                <span class="text-xs text-gray-500">({{ authStore.usuario.Rol }})</span>
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="logout">
                    <el-icon><SwitchButton /></el-icon>
                    Cerrar Sesión
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      <el-main class="bg-gray-50">
        <slot />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import {
  House,
  User,
  Avatar,
  Calendar,
  Document,
  Money,
  Notebook,
  Files,
  Search,
  UserFilled,
  ArrowDown,
  SwitchButton
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)
const pageTitle = computed(() => route.meta.title || 'Sistema')

async function handleCommand(command: string) {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm(
        '¿Está seguro que desea cerrar sesión?',
        'Confirmar',
        {
          confirmButtonText: 'Cerrar Sesión',
          cancelButtonText: 'Cancelar',
          type: 'warning'
        }
      )
      await authStore.logout()
      router.push('/login')
    } catch {
      // Usuario canceló
    }
  }
}
</script>

<style scoped>
.el-menu {
  border-right: none;
}

.el-menu-item {
  color: #e5e7eb;
}

.el-menu-item:hover {
  background-color: #374151;
  color: #fff;
}

.el-menu-item.is-active {
  background-color: #3b82f6;
  color: #fff;
}
</style>
