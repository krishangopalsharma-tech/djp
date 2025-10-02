<!--
This file is a new Vue component for managing archived failures.
1. It uses the `useFailureStore` to fetch and display `archivedFailures` in a table.
2. The table shows 'Fail ID', 'Archived At', 'Archived Reason', 'Circuit', and 'Station'.
3. It includes a "Permanent Delete" button for each row that opens a confirmation modal.
4. On confirmation, it calls the `permanentlyDeleteFailure` action from the store.
-->
<script setup>
import { onMounted, computed, ref } from 'vue';
import { useFailureStore } from '@/stores/failures';
import { Trash2 } from 'lucide-vue-next';
import Spinner from '@/components/ui/Spinner.vue';

const failureStore = useFailureStore();
const archivedFailures = computed(() => failureStore.archivedFailures);

const isDeleteModalOpen = ref(false);
const failureToDelete = ref(null);

onMounted(() => {
  failureStore.fetchArchivedFailures();
});

function openDeleteModal(failure) {
  failureToDelete.value = failure;
  isDeleteModalOpen.value = true;
}

async function confirmDelete() {
  if (!failureToDelete.value) return;
  await failureStore.permanentlyDeleteFailure(failureToDelete.value.id);
  isDeleteModalOpen.value = false;
  failureToDelete.value = null;
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleString();
};
</script>

<template>
  <div class="space-y-4">
    <p class="text-app/80 text-sm">
      Review and permanently delete archived failure logs. This action cannot be undone.
    </p>

    <div class="rounded-2xl border-app bg-card text-app overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left border-b border-app/40">
              <th class="py-2.5 px-3">Event ID</th>
              <th class="py-2.5 px-3">Circuit</th>
              <th class="py-2.5 px-3">Station</th>
              <th class="py-2.5 px-3">Archived At</th>
              <th class="py-2.5 px-3">Reason</th>
              <th class="py-2.5 px-3 w-40 text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="failureStore.loading && archivedFailures.length === 0">
              <td colspan="6" class="py-6 px-3 text-center text-muted"><Spinner /></td>
            </tr>
            <tr v-else-if="failureStore.error && archivedFailures.length === 0">
              <td colspan="6" class="py-6 px-3 text-center text-red-500">{{ failureStore.error }}</td>
            </tr>
            <tr v-else-if="archivedFailures.length === 0">
              <td colspan="6" class="py-6 px-3 text-center text-app/60">No archived failures found.</td>
            </tr>
            <tr v-for="failure in archivedFailures" :key="failure.id" class="border-t border-app/30">
              <td class="py-2 px-3 align-middle">{{ failure.fail_id }}</td>
              <td class="py-2 px-3 align-middle">{{ failure.circuit?.name || 'N/A' }}</td>
              <td class="py-2 px-3 align-middle">{{ failure.station?.name || 'N/A' }}</td>
              <td class="py-2 px-3 align-middle">{{ formatDate(failure.archived_at) }}</td>
              <td class="py-2 px-3 align-middle">{{ failure.archived_reason || 'No reason provided' }}</td>
              <td class="py-2 px-3 align-middle text-center">
                <button @click="openDeleteModal(failure)" class="btn btn-sm btn-danger inline-flex items-center justify-center h-9 w-9 rounded-md" title="Permanently Delete">
                  <Trash2 class="w-4 h-4" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="isDeleteModalOpen" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div class="bg-card rounded-2xl p-6 w-full max-w-md space-y-4">
        <h3 class="text-lg font-semibold">Confirm Permanent Deletion</h3>
        <p>Are you sure you want to permanently delete event "<strong>{{ failureToDelete?.fail_id }}</strong>"? This action cannot be undone.</p>
        <div class="flex justify-end gap-3 pt-4">
          <button @click="isDeleteModalOpen = false" class="btn btn-outline">Cancel</button>
          <button @click="confirmDelete" class="btn btn-danger" :disabled="failureStore.loading">
            {{ failureStore.loading ? 'Deleting...' : 'Delete Permanently' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>