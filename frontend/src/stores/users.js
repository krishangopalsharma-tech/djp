import { defineStore } from 'pinia';
import { http } from '@/lib/http';
import { useUIStore } from './ui';

export const useUserStore = defineStore('users', {
  state: () => ({
    users: [],
    loading: false,
    error: null,
  }),
  actions: {
    /**
     * Fetches the list of all users from the backend API.
     */
    async fetchUsers() {
      this.loading = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        const response = await http.get('/users/');
        this.users = response.data.results || response.data;
      } catch (err) {
        this.error = 'Failed to fetch users.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
        console.error('Error fetching users:', err);
      } finally {
        this.loading = false;
      }
    },

    /**
     * Adds a new user via the backend API.
     * @param {object} userData - The new user's data.
     */
    async addUser(userData) {
      this.loading = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        await http.post('/users/', userData);
        uiStore.pushToast({
          type: 'success',
          title: 'User Added',
          message: `User "${userData.username}" has been created.`,
        });
        await this.fetchUsers(); // Refresh the user list
      } catch (err) {
        this.error = 'Failed to add user.';
        const errorMessage = err.response?.data ? JSON.stringify(err.response.data) : this.error;
        uiStore.pushToast({ type: 'error', title: 'Error', message: errorMessage });
        console.error('Error adding user:', err);
      } finally {
        this.loading = false;
      }
    },

    /**
     * Updates an existing user via the backend API.
     * @param {number} userId - The ID of the user to update.
     * @param {object} userData - The updated user data.
     */
    async updateUser(userId, userData) {
      this.loading = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        // Remove password from payload if it's empty
        const payload = { ...userData };
        if (!payload.password) {
          delete payload.password;
        }
          
        await http.patch(`/users/${userId}/`, payload);
        uiStore.pushToast({
          type: 'success',
          title: 'User Updated',
          message: `User "${userData.username}" has been updated.`,
        });
        await this.fetchUsers(); // Refresh the user list
      } catch (err) {
        this.error = 'Failed to update user.';
        const errorMessage = err.response?.data ? JSON.stringify(err.response.data) : this.error;
        uiStore.pushToast({ type: 'error', title: 'Error', message: errorMessage });
        console.error('Error updating user:', err);
      } finally {
        this.loading = false;
      }
    },

    /**
     * Deletes a user via the backend API.
     * @param {number} userId - The ID of the user to delete.
     */
    async deleteUser(userId) {
      this.loading = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        await http.delete(`/users/${userId}/`);
        uiStore.pushToast({
          type: 'success',
          title: 'User Deleted',
          message: `User with ID #${userId} has been deleted.`,
        });
        await this.fetchUsers(); // Refresh the user list
      } catch (err) {
        this.error = 'Failed to delete user.';
        const errorMessage = err.response?.data ? JSON.stringify(err.response.data) : this.error;
        uiStore.pushToast({ type: 'error', title: 'Error', message: errorMessage });
        console.error('Error deleting user:', err);
      } finally {
        this.loading = false;
      }
    },
  },
});