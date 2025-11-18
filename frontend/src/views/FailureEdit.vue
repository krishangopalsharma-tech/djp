<script setup>
import { useRoute } from 'vue-router';
const route = useRoute();
const failureId = route.params.id;
</script>

<template>
  <div class="space-y-4 max-w-4xl mx-auto">
    <div class="text-center">
      <h2 class="text-2xl font-semibold leading-tight">
        Edit Failure Log #{{ failureId }}
      </h2>
      <p class="text-sm text-app/70">
        (WIP: The form will be populated with data in the next step.)
      </p>
    </div>
    <div class="card min-h-[400px]">
      </div>
  </div>
</template>