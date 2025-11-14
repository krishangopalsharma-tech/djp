// Path: frontend/src/stores/stations.js
import { defineStore } from 'pinia';
import { http } from '@/lib/http';
import { useUIStore } from './ui';

export const useStationsStore = defineStore('stations', {
  state: () => ({
    stations: [],
    loading: { stations: false, equipment: false }, // Separate loading states
    error: null,
  }),
  actions: {
    // --- Station Actions ---
    async fetchStations() {
      this.loading.stations = true; this.error = null;
      try {
        const response = await http.get('/stations/');
        const results = response.data.results || response.data;
        this.stations = Array.isArray(results) ? results : [];
      } catch (err) {
        this.error = 'Failed to fetch stations.'; this.stations = [];
        useUIStore().pushToast({ type: 'error', title: 'Error', message: this.error });
      } finally { this.loading.stations = false; }
    },
    async addStation(payload) {
      this.loading.stations = true; const uiStore = useUIStore();
      try {
        await http.post('/stations/', payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Station added.' });
        await this.fetchStations();
      } catch (err) {
        const errorDetail = err.response?.data ? JSON.stringify(err.response.data) : 'Failed to add station.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: errorDetail });
      } finally { this.loading.stations = false; }
    },
    async updateStation(id, payload) {
      this.loading.stations = true; const uiStore = useUIStore();
      try {
        // Prepare payload, don't send nested read-only fields back
        const updateData = { depot: payload.depot, name: payload.name, code: payload.code, category: payload.category };
        await http.patch(`/stations/${id}/`, updateData);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Station updated.' });
        await this.fetchStations();
      } catch (err) {
        const errorDetail = err.response?.data ? JSON.stringify(err.response.data) : 'Failed to update station.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: errorDetail });
      } finally { this.loading.stations = false; }
    },
    async removeStation(id) {
      this.loading.stations = true; const uiStore = useUIStore();
      try {
        await http.delete(`/stations/${id}/`);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Station removed.' });
        await this.fetchStations();
      } catch (err) {
        this.error = 'Failed to remove station.'; uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
      } finally { this.loading.stations = false; }
    },
    async uploadStationsFile(file) {
      this.loading.stations = true; const uiStore = useUIStore(); const formData = new FormData(); formData.append('file', file);
      try {
        const response = await http.post('/stations/import_stations_file/', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
        uiStore.pushToast({ type: 'success', title: 'Import Complete', message: response.data.message });
        await this.fetchStations(); // Refresh stations
        // Consider refreshing depots if the import could create them implicitly (depends on backend logic)
        // await useDepotsStore().fetchDepots();
      } catch (err) {
        const message = err.response?.data?.error || err.response?.data?.message || 'File upload failed.';
        const errors = err.response?.data?.errors;
        if (errors && Array.isArray(errors)) { uiStore.pushToast({ type: 'warning', title: 'Import Issues', message: `${message} First few errors: ${errors.slice(0, 3).join(', ')}`, duration: 10000 }); }
        else { uiStore.pushToast({ type: 'error', title: 'Import Failed', message }); }
      } finally { this.loading.stations = false; }
    },
     async exportStationsToExcel() {
        this.loading.stations = true; const uiStore = useUIStore();
        try {
            const response = await http.get('/stations/export_to_excel/', { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([response.data])); const link = document.createElement('a'); link.href = url;
            link.setAttribute('download', 'stations_equipment_export.xlsx'); document.body.appendChild(link); link.click(); link.remove(); window.URL.revokeObjectURL(url);
            uiStore.pushToast({ type: 'success', title: 'Success', message: 'Station data export started.' });
        } catch (err) {
            this.error = 'Failed to export station data.'; uiStore.pushToast({ type: 'error', title: 'Export Error', message: this.error });
        } finally { this.loading.stations = false; }
    },

    // --- Station Equipment Actions ---
    // Note: The station object fetched initially might contain equipment, but for editing,
    // it's often cleaner to fetch/manage equipment via its dedicated endpoint.
    // The current component logic uses temp arrays, let's connect those save operations.
    async addStationEquipment(payload) {
      this.loading.equipment = true; const uiStore = useUIStore();
      try {
        await http.post('/station-equipments/', payload);
        // Don't toast for every single item during bulk save
      } catch (err) {
        const errorDetail = err.response?.data ? JSON.stringify(err.response.data) : 'Could not add station equipment.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: errorDetail });
      } finally { this.loading.equipment = false; }
    },
    async updateStationEquipment(id, payload) {
      this.loading.equipment = true; const uiStore = useUIStore();
      try {
        await http.patch(`/station-equipments/${id}/`, payload);
      } catch (err) {
        const errorDetail = err.response?.data ? JSON.stringify(err.response.data) : 'Could not update station equipment.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: errorDetail });
      } finally { this.loading.equipment = false; }
    },
    async removeStationEquipment(id) {
      this.loading.equipment = true; const uiStore = useUIStore();
      try {
        await http.delete(`/station-equipments/${id}/`);
      } catch (err) {
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not remove station equipment.' });
      } finally { this.loading.equipment = false; }
    },
  },
});