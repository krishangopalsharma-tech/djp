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
    <div class="w-full max-w-sm rounded-2xl border bg-white p-6">
      <div>
        <h2 class="text-xl font-semibold">Sign in</h2>
        <p class="text-sm text-gray-500">Demo auth — will connect to Django later.</p>
      </div>
      <form class="space-y-4 mt-4" @submit.prevent="submit">
        <div class="space-y-3">
          <InputText label="Username" v-model="form.username" :error="errors.username" placeholder="e.g. admin" />
          <InputText label="Password" v-model="form.password" :error="errors.password" type="password" placeholder="••••••••" autocomplete="current-password" />
        </div>
        <button type="submit" class="btn w-full">Sign in</button>
      </form>
    </div>
  </div>
</template>
