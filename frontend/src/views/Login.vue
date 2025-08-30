<script setup>
import { reactive } from 'vue'
import InputText from '@/components/form/InputText.vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const ui = useUIStore()

const form = reactive({ username: '', password: '' })
const errors = reactive({ username: '', password: '' })

function validate() {
  errors.username = form.username ? '' : 'Required'
  errors.password = form.password ? '' : 'Required'
  return !errors.username && !errors.password
}

async function submit() {
  if (!validate()) return ui.pushToast({ type: 'error', title: 'Missing fields', message: 'Enter username & password.' })
  try {
    await auth.login(form) // mock for now
    ui.pushToast({ type: 'success', title: 'Welcome', message: `Logged in as ${auth.user.username}` })
    const next = (route.query.next && String(route.query.next)) || '/dashboard'
    router.push(next)
  } catch (e) {
    ui.pushToast({ type: 'error', title: 'Login failed', message: e?.message || 'Try again.' })
  }
}
</script>

<template>
  <div class="min-h-[60vh] flex items-center justify-center p-6">
    <div class="w-full max-w-sm rounded-2xl border bg-white p-6 space-y-4">
      <div>
        <h2 class="text-xl font-semibold">Sign in</h2>
        <p class="text-sm text-gray-500">Demo auth — will connect to Django later.</p>
      </div>
      <div class="space-y-3">
        <InputText label="Username" v-model="form.username" :error="errors.username" placeholder="e.g. admin" />
        <InputText label="Password" v-model="form.password" :error="errors.password" type="password" placeholder="••••••••" />
      </div>
      <button @click="submit" class="h-10 w-full rounded-lg bg-gray-900 text-white text-sm">Sign in</button>
    </div>
  </div>
</template>