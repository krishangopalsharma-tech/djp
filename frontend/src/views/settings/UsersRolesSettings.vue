<script setup>
import { onMounted, computed, ref, reactive } from 'vue';
import { useUserStore } from '@/stores/users';
import { useUIStore } from '@/stores/ui';
import { Trash2 } from 'lucide-vue-next';

// Initialize stores
const userStore = useUserStore();
const uiStore = useUIStore();

const users = computed(() => userStore.users);

// State for Add User modal
const isAddModalOpen = ref(false);
const initialNewUserState = {
  username: '', email: '', first_name: '', last_name: '', role: 'viewer', password: '',
};
const newUser = reactive({ ...initialNewUserState });

// State for Edit User modal
const isEditModalOpen = ref(false);
const currentUserToEdit = ref(null);

// State for Delete User modal
const isDeleteModalOpen = ref(false);
const userToDelete = ref(null);

const roleOptions = ['viewer', 'operator', 'supervisor', 'admin'];

onMounted(() => {
  userStore.fetchUsers();
});

// --- Add User Functions ---
function openAddModal() {
  Object.assign(newUser, initialNewUserState);
  isAddModalOpen.value = true;
}

async function saveNewUser() {
  if (!newUser.username || !newUser.password) {
    uiStore.pushToast({ type: 'error', title: 'Missing Fields', message: 'User ID (PF Number) and Password are required.' });
    return;
  }
  await userStore.addUser(newUser);
  if (!userStore.error) {
    isAddModalOpen.value = false;
  }
}

// --- Edit User Functions ---
function openEditModal(user) {
  currentUserToEdit.value = reactive({ ...user, password: '' });
  isEditModalOpen.value = true;
}

async function saveUserChanges() {
  if (!currentUserToEdit.value) return;
  await userStore.updateUser(currentUserToEdit.value.id, currentUserToEdit.value);
  if (!userStore.error) {
    isEditModalOpen.value = false;
    currentUserToEdit.value = null;
  }
}

// --- Delete User Functions ---
function openDeleteModal(user) {
  userToDelete.value = user;
  isDeleteModalOpen.value = true;
}

async function confirmDelete() {
  if (!userToDelete.value) return;
  await userStore.deleteUser(userToDelete.value.id);
  if (!userStore.error) {
    isDeleteModalOpen.value = false;
    userToDelete.value = null;
  }
}

// --- UI Helpers ---
function getRoleClass(role) {
  switch (role) {
    case 'admin': return 'bg-red-100 text-red-800 border-red-200';
    case 'supervisor': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    case 'operator': return 'bg-blue-100 text-blue-800 border-blue-200';
    case 'viewer': default: return 'bg-gray-100 text-gray-800 border-gray-200';
  }
}

function getStatusClass(isActive) {
  return isActive ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800';
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex justify-between items-center">
      <p class="text-app/80 text-sm">Create users, assign roles, and manage permissions for the RFMS application.</p>
      <button class="btn btn-primary" @click="openAddModal">+ Add User</button>
    </div>

    <div class="rounded-2xl border-app bg-card text-app overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left border-b border-app/40">
              <th class="py-2.5 px-3 whitespace-nowrap">DB ID</th>
              <th class="py-2.5 px-3 whitespace-nowrap">User ID (PF Number)</th>
              <th class="py-2.5 px-3 whitespace-nowrap">Full Name</th>
              <th class="py-2.5 px-3 whitespace-nowrap">Email</th>
              <th class="py-2.5 px-3 whitespace-nowrap text-center">Role</th>
              <th class="py-2.5 px-3 whitespace-nowrap text-center">Status</th>
              <th class="py-2.5 px-3 w-40 text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="userStore.loading && users.length === 0">
              <td colspan="7" class="py-6 px-3 text-center text-muted">Loading users...</td>
            </tr>
            <tr v-else-if="userStore.error && users.length === 0">
              <td colspan="7" class="py-6 px-3 text-center text-red-500">{{ userStore.error }}</td>
            </tr>
            <tr v-else-if="users.length === 0">
              <td colspan="7" class="py-6 px-3 text-center text-app/60">No users found. Click "Add User" to begin.</td>
            </tr>
            <tr v-for="user in users" :key="user.id" class="border-t border-app/30">
              <td class="py-2 px-3 align-middle">{{ user.id }}</td>
              <td class="py-2 px-3 align-middle">{{ user.username }}</td>
              <td class="py-2 px-3 align-middle">{{ user.first_name }} {{ user.last_name }}</td>
              <td class="py-2 px-3 align-middle">{{ user.email }}</td>
              <td class="py-2 px-3 align-middle text-center">
                <span class="badge capitalize" :class="getRoleClass(user.role)">{{ user.role }}</span>
              </td>
              <td class="py-2 px-3 align-middle text-center">
                 <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium" :class="getStatusClass(user.is_active)">
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="py-2 px-3 align-middle text-center">
                <div class="flex items-center justify-center gap-2">
                  <button @click="openEditModal(user)" class="h-9 w-9 flex items-center justify-center rounded-lg bg-[var(--button-primary)] text-[var(--seasalt)] hover:bg-[var(--button-hover)] transition" title="Edit User">
                     <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                      <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
                    </svg>
                  </button>
                  <button @click="openDeleteModal(user)" class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app border border-app hover:bg-gray-100 transition" title="Remove User">
                    <Trash2 class="w-6 h-6" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="isAddModalOpen" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div class="bg-card rounded-2xl p-6 w-full max-w-2xl space-y-4">
        <h3 class="text-lg font-semibold">Add New User</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div><label class="block text-sm font-medium mb-1">User ID (PF Number)</label><input v-model="newUser.username" class="field" placeholder="e.g., 12345678" /></div>
          <div><label class="block text-sm font-medium mb-1">Email</label><input v-model="newUser.email" type="email" class="field" placeholder="e.g., j.doe@example.com" /></div>
          <div><label class="block text-sm font-medium mb-1">First Name</label><input v-model="newUser.first_name" class="field" placeholder="e.g., John" /></div>
          <div><label class="block text-sm font-medium mb-1">Last Name</label><input v-model="newUser.last_name" class="field" placeholder="e.g., Doe" /></div>
          <div>
            <label class="block text-sm font-medium mb-1">Role</label>
            <select v-model="newUser.role" class="field capitalize">
              <option v-for="role in roleOptions" :key="role" :value="role">{{ role }}</option>
            </select>
          </div>
          <div><label class="block text-sm font-medium mb-1">Password</label><input v-model="newUser.password" type="password" class="field" placeholder="Enter a temporary password" /></div>
        </div>
        <div class="flex justify-end gap-3 pt-4">
          <button @click="isAddModalOpen = false" class="btn btn-outline">Cancel</button>
          <button @click="saveNewUser" class="btn btn-primary" :disabled="userStore.loading">{{ userStore.loading ? 'Saving...' : 'Save User' }}</button>
        </div>
      </div>
    </div>

    <div v-if="isEditModalOpen && currentUserToEdit" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div class="bg-card rounded-2xl p-6 w-full max-w-2xl space-y-4">
        <h3 class="text-lg font-semibold">Edit User: {{ currentUserToEdit.username }}</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div><label class="block text-sm font-medium mb-1">User ID (PF Number)</label><input v-model="currentUserToEdit.username" class="field" /></div>
          <div><label class="block text-sm font-medium mb-1">Email</label><input v-model="currentUserToEdit.email" type="email" class="field" /></div>
          <div><label class="block text-sm font-medium mb-1">First Name</label><input v-model="currentUserToEdit.first_name" class="field" /></div>
          <div><label class="block text-sm font-medium mb-1">Last Name</label><input v-model="currentUserToEdit.last_name" class="field" /></div>
          <div>
            <label class="block text-sm font-medium mb-1">Role</label>
            <select v-model="currentUserToEdit.role" class="field capitalize">
              <option v-for="role in roleOptions" :key="role" :value="role">{{ role }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Status</label>
            <label class="flex items-center gap-2">
              <input type="checkbox" v-model="currentUserToEdit.is_active" class="h-4 w-4 rounded" />
              <span>Active</span>
            </label>
          </div>
          <div class="md:col-span-2"><label class="block text-sm font-medium mb-1">New Password</label><input v-model="currentUserToEdit.password" type="password" class="field" placeholder="Leave blank to keep unchanged" /></div>
        </div>
        <div class="flex justify-end gap-3 pt-4">
          <button @click="isEditModalOpen = false" class="btn btn-outline">Cancel</button>
          <button @click="saveUserChanges" class="btn btn-primary" :disabled="userStore.loading">{{ userStore.loading ? 'Saving...' : 'Save Changes' }}</button>
        </div>
      </div>
    </div>
      
    <div v-if="isDeleteModalOpen" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div class="bg-card rounded-2xl p-6 w-full max-w-md space-y-4">
        <h3 class="text-lg font-semibold">Confirm Deletion</h3>
        <p>Are you sure you want to delete the user "<strong>{{ userToDelete?.username }}</strong>"? This action cannot be undone.</p>
        <div class="flex justify-end gap-3 pt-4">
          <button @click="isDeleteModalOpen = false" class="btn btn-outline">Cancel</button>
          <button @click="confirmDelete" class="btn" style="background-color: #ef4444; color: white;" :disabled="userStore.loading">
            {{ userStore.loading ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>