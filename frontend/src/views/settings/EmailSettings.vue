<script setup>
import WidgetShell from '@/components/WidgetShell.vue'
import { reactive } from 'vue'
import { useEmailStore } from '@/stores/email'

const email = useEmailStore()

// Local inputs for adding recipients
const add = reactive({ to: '', cc: '', bcc: '' })

function onSave() {
  console.log('[EmailSettings] Saved SMTP + recipients', {
    smtp: { ...email.smtp, password: email.smtp.password ? '•••••' : '' },
    recipients: email.recipients,
  })
  alert('Email settings saved (mock).')
}

function onTest() {
  const msg = {
    smtp: { ...email.smtp, password: email.smtp.password ? '•••••' : '' },
    to: email.test.to || email.recipients.to[0] || '(none)',
  }
  console.log('[EmailSettings] TEST EMAIL payload', msg)
  alert(`Test email prepared for: ${msg.to}\n(Frontend mock — no email actually sent)`) 
}

function addRec(kind) {
  const v = (add[kind] || '').trim()
  if (!v) return
  email.addRecipient(kind, v)
  add[kind] = ''
}
</script>

<template>
  <div class="p-4 md:p-6 space-y-4">
    <h1 class="text-xl md:text-2xl font-semibold">Email Settings</h1>

    <WidgetShell :hideHeader="true">
      <div class="space-y-6">
        <!-- SMTP -->
        <section class="rounded-2xl border bg-white p-4 space-y-3">
          <h2 class="text-lg font-semibold">SMTP Server</h2>
          <div class="grid md:grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium mb-1">Host</label>
              <input class="w-full px-3 py-2 rounded-lg border border-[var(--surface-3)]"
                     v-model="email.smtp.host" placeholder="smtp.example.com" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Port</label>
              <input type="number" class="w-full px-3 py-2 rounded-lg border border-[var(--surface-3)]"
                     v-model.number="email.smtp.port" placeholder="587" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Encryption</label>
              <select class="chip w-full" v-model="email.smtp.encryption">
                <option value="STARTTLS">STARTTLS (587)</option>
                <option value="SSL/TLS">SSL/TLS (465)</option>
                <option value="None">None</option>
              </select>
            </div>
            <div></div>
            <div>
              <label class="block text-sm font-medium mb-1">Username</label>
              <input class="w-full px-3 py-2 rounded-lg border border-[var(--surface-3)]"
                     v-model="email.smtp.username" placeholder="user@example.com" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Password</label>
              <input type="password" class="w-full px-3 py-2 rounded-lg border border-[var(--surface-3)]"
                     v-model="email.smtp.password" autocomplete="new-password" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">From Name</label>
              <input class="w-full px-3 py-2 rounded-lg border border-[var(--surface-3)]"
                     v-model="email.smtp.fromName" placeholder="RFMS Notifications" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">From Address</label>
              <input class="w-full px-3 py-2 rounded-lg border border-[var(--surface-3)]"
                     v-model="email.smtp.fromAddress" placeholder="no-reply@example.com" />
            </div>
          </div>
        </section>

        <!-- Recipients -->
        <section class="rounded-2xl border bg-white p-4 space-y-3">
          <h2 class="text-lg font-semibold">Default Recipients (Automatic Emails)</h2>

          <!-- TO -->
          <div>
            <label class="block text-sm font-medium mb-1">To</label>
            <div class="flex gap-2 mb-2">
              <input class="flex-1 px-3 py-2 rounded-lg border border-[var(--surface-3)]"
                     v-model="add.to" placeholder="Add recipient email and press +"/>
              <button class="chip selected-primary" @click="addRec('to')">+</button>
            </div>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="r in email.recipients.to"
                :key="r"
                class="inline-flex items-center gap-2 px-2 py-1 rounded-lg border"
              >
                {{ r }}
                <button class="text-xs opacity-70 hover:opacity-100" @click="email.removeRecipient('to', r)">×</button>
              </span>
            </div>
          </div>

          <!-- CC -->
          <div>
            <label class="block text-sm font-medium mb-1">CC</label>
            <div class="flex gap-2 mb-2">
              <input class="flex-1 px-3 py-2 rounded-lg border border-[var(--surface-3)]"
                     v-model="add.cc" placeholder="Add CC email"/>
              <button class="chip" @click="addRec('cc')">+</button>
            </div>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="r in email.recipients.cc"
                :key="r"
                class="inline-flex items-center gap-2 px-2 py-1 rounded-lg border"
              >
                {{ r }}
                <button class="text-xs opacity-70 hover:opacity-100" @click="email.removeRecipient('cc', r)">×</button>
              </span>
            </div>
          </div>

          <!-- BCC -->
          <div>
            <label class="block text-sm font-medium mb-1">BCC</label>
            <div class="flex gap-2 mb-2">
              <input class="flex-1 px-3 py-2 rounded-lg border border-[var(--surface-3)]"
                     v-model="add.bcc" placeholder="Add BCC email"/>
              <button class="chip" @click="addRec('bcc')">+</button>
            </div>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="r in email.recipients.bcc"
                :key="r"
                class="inline-flex items-center gap-2 px-2 py-1 rounded-lg border"
              >
                {{ r }}
                <button class="text-xs opacity-70 hover:opacity-100" @click="email.removeRecipient('bcc', r)">×</button>
              </span>
            </div>
          </div>
        </section>

        <!-- Actions -->
        <div class="flex items-center justify-end gap-2">
          <input class="px-3 py-2 rounded-lg border border-[var(--surface-3)]"
                 v-model="email.test.to" placeholder="Test recipient (optional)"/>
          <button class="chip" @click="onTest">Send Test Email</button>
          <button class="chip selected-primary" @click="onSave">Save</button>
        </div>

        <p class="text-xs opacity-70">
          Frontend-only mock. Backend SMTP send will be wired later.
        </p>
      </div>
    </WidgetShell>
  </div>
  
</template>

<style scoped></style>

