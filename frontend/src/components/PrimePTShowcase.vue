<script setup>
import { ref } from 'vue'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import Checkbox from 'primevue/checkbox'
import RadioButton from 'primevue/radiobutton'
import Dialog from 'primevue/dialog'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'

const toast = useToast()

const name = ref('')
const city = ref(null)
const cities = [
  { label: 'Bandra', value: 'BND' },
  { label: 'Andheri', value: 'ADH' },
  { label: 'Dadar', value: 'DDR' }
]
const agree = ref(false)
const priority = ref('M')
const showDlg = ref(false)

function showToast() {
  toast.add({ severity: 'success', summary: 'Saved', detail: 'Token-styled PrimeVue works!', life: 2000 })
}
</script>

<template>
  <div class="card mx-auto my-token-6 max-w-3xl">
    <div class="card-body stack-md">
      <div class="text-h3">PrimeVue PT Showcase</div>

      <div class="row-md">
        <PButton label="Primary" icon="pi pi-check" @click="showToast" />
        <PButton label="Secondary" severity="secondary" icon="pi pi-minus-circle" />
        <PButton label="Success" severity="success" icon="pi pi-check-circle" />
        <PButton label="Warning" severity="warning" icon="pi pi-exclamation-triangle" />
        <PButton label="Danger" severity="danger" icon="pi pi-times" />
        <PButton label="Open Dialog" icon="pi pi-window-maximize" @click="showDlg = true" />
      </div>

      <div class="row-md">
        <div class="w-64">
          <label class="text-muted text-token-sm mb-token-2 block">Your Name</label>
          <InputText v-model="name" placeholder="Type here…" />
        </div>
        <div class="w-64">
          <label class="text-muted text-token-sm mb-token-2 block">Station</label>
           <Select v-model="city" :options="cities" optionLabel="label" optionValue="value" placeholder="Select…" />
        </div>
      </div>

      <div class="row-md">
        <label class="inline-flex items-center gap-token-2">
          <Checkbox v-model="agree" binary />
          <span class="text-body">Agree</span>
        </label>

        <label class="inline-flex items-center gap-token-2">
          <RadioButton name="prio" value="H" v-model="priority" />
          <span>High</span>
        </label>
        <label class="inline-flex items-center gap-token-2">
          <RadioButton name="prio" value="M" v-model="priority" />
          <span>Medium</span>
        </label>
        <label class="inline-flex items-center gap-token-2">
          <RadioButton name="prio" value="L" v-model="priority" />
          <span>Low</span>
        </label>
      </div>

      <Toast position="top-right" />
      <Dialog v-model:visible="showDlg" modal :draggable="false">
        <template #header>Tokenized Dialog</template>
        <p class="text-body text-muted">
          This dialog surface, borders, spacing and buttons all come from your tokens.
        </p>
        <template #footer>
          <PButton label="Close" severity="secondary" @click="showDlg = false" />
          <PButton label="Confirm" icon="pi pi-check" @click="showDlg = false" />
        </template>
      </Dialog>
    </div>
  </div>
</template>
