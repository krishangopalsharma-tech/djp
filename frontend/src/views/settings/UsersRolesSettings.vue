<script setup>
</script>
<template>
  <div class="space-y-4">
    <p class="text-app/80 text-sm">Create users, assign roles/permissions. (Frontend placeholder)</p>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium mb-1">New User Email</label>
        <input class="field" placeholder="user@example.com" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">Role</label>
        <select class="field">
          <option>Viewer</option>
          <option>Operator</option>
          <option>Supervisor</option>
          <option>Admin</option>
        </select>
      </div>
    </div>

    <div class="flex gap-2">
      <button class="btn btn-primary">Invite User</button>
      <button class="btn">Sync</button>
    </div>
  </div>
</template>
