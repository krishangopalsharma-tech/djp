// Path: frontend/src/stores/infrastructure.js

import { defineStore } from 'pinia'
import { http } from '@/lib/http'
import { useUIStore } from './ui'

export const useInfrastructureStore = defineStore('infrastructure', {
  state: () => ({
    depots: [],
    stations: [],
    sections: [],
    circuits: [],
    supervisors: [],
    subSections: [],
    loading: {
      depots: false,
      stations: false,
      sections: false,
      circuits: false,
      supervisors: false,
    },
    error: null,
  }),
  actions: {
    async fetchDepots() {
      this.loading.depots = true
      this.error = null
      try {
        const response = await http.get('/infrastructure/depots/')
        this.depots = response.data.results || response.data
      } catch (err) {
        this.error = 'Failed to fetch depots.'
        console.error(err)
      } finally {
        this.loading.depots = false
      }
    },
    async fetchStations() {
      this.loading.stations = true
      this.error = null
      try {
        const response = await http.get('/infrastructure/stations/')
        this.stations = response.data.results || response.data
      } catch (err) {
        this.error = 'Failed to fetch stations.'
        console.error(err)
      } finally {
        this.loading.stations = false
      }
    },
    async fetchSupervisors() {
      this.loading.supervisors = true
      this.error = null
      try {
        const response = await http.get('/infrastructure/supervisors/')
        this.supervisors = response.data.results || response.data
      } catch (err) {
        this.error = 'Failed to fetch supervisors.'
        console.error(err)
      } finally {
        this.loading.supervisors = false
      }
    },
    async fetchSections() {
      this.loading.sections = true
      this.error = null
      try {
        const response = await http.get('/infrastructure/sections/')
        this.sections = response.data.results || response.data
      } catch (err) {
        this.error = 'Failed to fetch sections.'
        console.error(err)
      } finally {
        this.loading.sections = false
      }
    },
    async fetchSubSections() {
      this.loading.sections = true; // Can share loading state with sections
      this.error = null;
      try {
        const response = await http.get('/infrastructure/subsections/');
        this.subSections = response.data.results || response.data;
      } catch (err) {
        this.error = 'Failed to fetch sub-sections.';
        console.error(err);
      } finally {
        this.loading.sections = false;
      }
    },
    async fetchCircuits() {
      this.loading.circuits = true
      this.error = null
      try {
        const response = await http.get('/infrastructure/circuits/')
        this.circuits = response.data.results || response.data
      } catch (err) {
        this.error = 'Failed to fetch circuits.'
        console.error(err)
      } finally {
        this.loading.circuits = false
      }
    },
    async addDepot(payload) {
      this.loading.depots = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        await http.post('/infrastructure/depots/', payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Depot added.' });
        await this.fetchDepots();
      } catch (err) {
        this.error = 'Failed to add depot.';
         uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
        console.error(err);
      } finally {
        this.loading.depots = false;
      }
    },
    async removeDepot(depotId) {
      this.loading.depots = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        await http.delete(`/infrastructure/depots/${depotId}/`);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Depot removed.' });
        await this.fetchDepots();
      } catch (err) {
        this.error = 'Failed to remove depot.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
        console.error(err);
      } finally {
        this.loading.depots = false;
      }
    },
     async uploadDepotsFile(file) {
      this.loading.depots = true;
      this.error = null;
      const uiStore = useUIStore();

      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await http.post('/infrastructure/depots/import/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });

        const { depots_processed, equipment_created, errors } = response.data;
        let message = `Import successful! Depots: ${depots_processed}, Equipment: ${equipment_created}.`;
        if (errors && errors.length) {
            message += ` Errors: ${errors.length}.`;
        }
        uiStore.pushToast({ type: 'success', title: 'Import Complete', message });

        await this.fetchDepots();
      } catch (err) {
        const message = err.response?.data?.error || 'File upload failed.';
        this.error = message;
        uiStore.pushToast({ type: 'error', title: 'Import Failed', message });
        console.error(err);
      } finally {
        this.loading.depots = false;
      }
    },
    async addEquipment(payload) {
      const uiStore = useUIStore();
      try {
        await http.post('/infrastructure/equipments/', payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Equipment added.' });
      } catch (err) {
         uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not add equipment.' });
        console.error(err);
      }
    },
    async updateEquipment(equipmentId, payload) {
      const uiStore = useUIStore();
      try {
        await http.patch(`/infrastructure/equipments/${equipmentId}/`, payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Equipment updated.' });
      } catch (err) {
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not update equipment.' });
        console.error(err);
      }
    },
    async removeEquipment(equipmentId) {
      const uiStore = useUIStore();
      try {
        await http.delete(`/infrastructure/equipments/${equipmentId}/`);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Equipment removed.' });
      } catch (err) {
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not remove equipment.' });
        console.error(err);
      }
    },
    async addSection(payload) {
      this.loading.sections = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        await http.post('/infrastructure/sections/', payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Section added.' });
        await this.fetchSections(); // Refresh the list
      } catch (err) {
        this.error = 'Failed to add section.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
        console.error(err);
      } finally {
        this.loading.sections = false;
      }
    },
    async removeSection(sectionId) {
      this.loading.sections = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        await http.delete(`/infrastructure/sections/${sectionId}/`);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Section removed.' });
        await this.fetchSections(); // Refresh the list
      } catch (err) {
        this.error = 'Failed to remove section.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
        console.error(err);
      } finally {
        this.loading.sections = false;
      }
    },
    async uploadSectionsFile(file) {
      this.loading.sections = true;
      this.error = null;
      const uiStore = useUIStore();

      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await http.post('/infrastructure/sections/import/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        uiStore.pushToast({ type: 'success', title: 'Import Complete', message: response.data.message });
        await this.fetchSections();
      } catch (err) {
        const message = err.response?.data?.error || 'File upload failed.';
        this.error = message;
        uiStore.pushToast({ type: 'error', title: 'Import Failed', message });
        console.error(err);
      } finally {
        this.loading.sections = false;
      }
    },
    async addStation(payload) {
      this.loading.stations = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        await http.post('/infrastructure/stations/', payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Station added.' });
        await this.fetchStations(); 
      } catch (err) {
        this.error = 'Failed to add station.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
        console.error(err);
      } finally {
        this.loading.stations = false;
      }
    },
    async removeStation(stationId) {
      this.loading.stations = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        await http.delete(`/infrastructure/stations/${stationId}/`);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Station removed.' });
        await this.fetchStations();
      } catch (err) {
        this.error = 'Failed to remove station.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
        console.error(err);
      } finally {
        this.loading.stations = false;
      }
    },
    async uploadStationsFile(file) {
      this.loading.stations = true;
      this.error = null;
      const uiStore = useUIStore();

      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await http.post('/infrastructure/stations/import/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });

        const { stations_processed, equipment_created } = response.data;
        let message = `Import successful! Stations: ${stations_processed}, Equipment: ${equipment_created}.`;
        
        uiStore.pushToast({ type: 'success', title: 'Import Complete', message });
        await this.fetchStations();
      } catch (err) {
        const message = err.response?.data?.error || 'File upload failed.';
        this.error = message;
        uiStore.pushToast({ type: 'error', title: 'Import Failed', message });
        console.error(err);
      } finally {
        this.loading.stations = false;
      }
    },
     async addStationEquipment(payload) {
      const uiStore = useUIStore();
      try {
        await http.post('/infrastructure/station-equipments/', payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Equipment added.' });
      } catch (err) {
        console.error("Failed to add station equipment:", err);
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not add equipment.' });
      }
    },
    async updateStationEquipment(equipmentId, payload) {
       const uiStore = useUIStore();
      try {
        await http.patch(`/infrastructure/station-equipments/${equipmentId}/`, payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Equipment updated.' });
      } catch (err) {
        console.error("Failed to update station equipment:", err);
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not update equipment.' });
      }
    },
    async removeStationEquipment(equipmentId) {
       const uiStore = useUIStore();
      try {
        await http.delete(`/infrastructure/station-equipments/${equipmentId}/`);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Equipment removed.' });
      } catch (err) {
        console.error("Failed to remove station equipment:", err);
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not remove equipment.' });
      }
    },
    async addSupervisor(payload) {
      this.loading.supervisors = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        await http.post('/infrastructure/supervisors/', payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Supervisor added.' });
        await this.fetchSupervisors();
      } catch (err) {
        this.error = 'Failed to add supervisor.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
        console.error(err);
      } finally {
        this.loading.supervisors = false;
      }
    },
    async removeSupervisor(supervisorId) {
      this.loading.supervisors = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        await http.delete(`/infrastructure/supervisors/${supervisorId}/`);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Supervisor removed.' });
        await this.fetchSupervisors();
      } catch (err) {
        this.error = 'Failed to remove supervisor.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
        console.error(err);
      } finally {
        this.loading.supervisors = false;
      }
    },
    async updateSupervisor(supervisorId, payload) {
      this.loading.supervisors = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        await http.patch(`/infrastructure/supervisors/${supervisorId}/`, payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Supervisor updated.' });
        await this.fetchSupervisors();
      } catch (err) {
        this.error = 'Failed to update supervisor.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
        console.error(err);
      } finally {
        this.loading.supervisors = false;
      }
    },
  },
})

