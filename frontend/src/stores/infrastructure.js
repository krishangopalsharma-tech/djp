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

    // ADD THESE NEW STATE PROPERTIES
    depotEquipments: [],
    stationEquipments: [],
    sectionSubsections: [],
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
    async updateDepot(depotId, payload) {
      this.loading.depots = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        await http.patch(`/infrastructure/depots/${depotId}/`, payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Depot updated.' });
        await this.fetchDepots();
      } catch (err) {
        this.error = 'Failed to update depot.';
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
        console.error("Failed to add equipment:", err);
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not add equipment.' });
      }
    },
    async updateEquipment(equipmentId, payload) {
       const uiStore = useUIStore();
      try {
        await http.patch(`/infrastructure/equipments/${equipmentId}/`, payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Equipment updated.' });
      } catch (err) {
        console.error("Failed to update equipment:", err);
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not update equipment.' });
      }
    },
    async removeEquipment(equipmentId) {
       const uiStore = useUIStore();
      try {
        await http.delete(`/infrastructure/equipments/${equipmentId}/`);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Equipment removed.' });
      } catch (err) {
        console.error("Failed to remove equipment:", err);
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not remove equipment.' });
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
     async updateSection(sectionId, payload) {
      this.loading.sections = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        await http.patch(`/infrastructure/sections/${sectionId}/`, payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Section updated.' });
        await this.fetchSections();
      } catch (err) {
        this.error = 'Failed to update section.';
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
        const errorData = err.response?.data;
        let message = 'File upload failed.';
        if (errorData && errorData.error) {
            message = errorData.error;
        }
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
    async updateStation(stationId, payload) {
      this.loading.stations = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        await http.patch(`/infrastructure/stations/${stationId}/`, payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Station updated.' });
        await this.fetchStations();
      } catch (err) {
        this.error = 'Failed to update station.';
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
        uiStore.pushToast({ type: 'success', title: 'Import Complete', message: response.data.message });
        await this.fetchStations();
        await this.fetchDepots(); // Also refresh depots in case new ones were created
      } catch (err) {
        const errorData = err.response?.data;
        let message = 'File upload failed.';
        if (errorData) {
            if (errorData.error && errorData.details) {
                message = `${errorData.error} ${errorData.details.join('; ')}`;
            } else if (errorData.error) {
                message = errorData.error;
            } else if (errorData.errors) {
                message = `${errorData.message} ${errorData.errors.join('; ')}`;
            }
        }
        
        this.error = message;
        uiStore.pushToast({ type: 'error', title: 'Import Failed', message: message, duration: 10000 });
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
    async addSubSection(payload) {
      const uiStore = useUIStore();
      try {
        const response = await http.post('/infrastructure/subsections/', payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Sub-section added.' });
        return response.data;
      } catch (err) {
        console.error("Failed to add sub-section:", err);
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not add sub-section.' });
      }
    },
    async updateSubSection(subSectionId, payload) {
      const uiStore = useUIStore();
      try {
        await http.patch(`/infrastructure/subsections/${subSectionId}/`, payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Sub-section updated.' });
      } catch (err) {
        console.error("Failed to update sub-section:", err);
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not update sub-section.' });
      }
    },
    async removeSubSection(subSectionId) {
      const uiStore = useUIStore();
      try {
        await http.delete(`/infrastructure/subsections/${subSectionId}/`);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Sub-section removed.' });
      } catch (err) {
        console.error("Failed to remove sub-section:", err);
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not remove sub-section.' });
      }
    },
    async addAsset(payload) {
      const uiStore = useUIStore();
      try {
        await http.post('/infrastructure/assets/', payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Asset added.' });
      } catch (err) {
        console.error("Failed to add asset:", err);
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not add asset.' });
      }
    },
    async updateAsset(assetId, payload) {
      const uiStore = useUIStore();
      try {
        await http.patch(`/infrastructure/assets/${assetId}/`, payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Asset updated.' });
      } catch (err) {
        console.error("Failed to update asset:", err);
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not update asset.' });
      }
    },
    async removeAsset(assetId) {
      const uiStore = useUIStore();
      try {
        await http.delete(`/infrastructure/assets/${assetId}/`);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Asset removed.' });
      } catch (err) {
        console.error("Failed to remove asset:", err);
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not remove asset.' });
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
    // --- Circuit Actions ---
    async addCircuit(payload) {
      this.loading.circuits = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        await http.post('/infrastructure/circuits/', payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Circuit added.' });
        await this.fetchCircuits();
      } catch (err) {
        this.error = 'Failed to add circuit.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Failed to add circuit.' });
        console.error(err);
      } finally {
        this.loading.circuits = false;
      }
    },
    async updateCircuit(circuitId, payload) {
      this.loading.circuits = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        await http.patch(`/infrastructure/circuits/${circuitId}/`, payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Circuit updated.' });
        await this.fetchCircuits();
      } catch (err) {
        this.error = 'Failed to update circuit.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Failed to update circuit.' });
        console.error(err);
      } finally {
        this.loading.circuits = false;
      }
    },
    async uploadCircuitsFile(file) {
      this.loading.circuits = true;
      this.error = null;
      const uiStore = useUIStore();
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await http.post('/infrastructure/circuits/import/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        const { created, updated, errors } = response.data;
        let message = `Import successful! Created: ${created}, Updated: ${updated}.`;
        if (errors.length) {
            message += ` Errors: ${errors.length}.`;
        }
        uiStore.pushToast({ type: 'success', title: 'Import Complete', message });
        await this.fetchCircuits();
      } catch (err) {
        const message = err.response?.data?.error || 'File upload failed.';
        this.error = message;
        uiStore.pushToast({ type: 'error', title: 'Import Failed', message });
        console.error(err);
      } finally {
        this.loading.circuits = false;
      }
    },
    async removeCircuit(circuitId) {
      this.loading.circuits = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        await http.delete(`/infrastructure/circuits/${circuitId}/`);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Circuit removed.' });
        await this.fetchCircuits();
      } catch (err) {
        this.error = 'Failed to remove circuit.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Failed to remove circuit.' });
        console.error(err);
      } finally {
        this.loading.circuits = false;
      }
    },
    // ADD THESE THREE NEW ACTIONS AT THE END OF THE 'actions' OBJECT
    async fetchEquipmentsForDepot(depotId) {
      this.loading.depots = true;
      try {
        const response = await http.get(`/infrastructure/equipments/?depot=${depotId}`);
        this.depotEquipments = response.data.results || response.data;
      } catch (err) {
        console.error(`Failed to fetch equipment for depot ${depotId}`, err);
      } finally {
        this.loading.depots = false;
      }
    },

    async fetchEquipmentsForStation(stationId) {
      this.loading.stations = true;
      try {
        const response = await http.get(`/infrastructure/station-equipments/?station=${stationId}`);
        this.stationEquipments = response.data.results || response.data;
      } catch (err) {
        console.error(`Failed to fetch equipment for station ${stationId}`, err);
      } finally {
        this.loading.stations = false;
      }
    },

    async fetchSubsectionsForSection(sectionId) {
      this.loading.sections = true;
      try {
        const response = await http.get(`/infrastructure/subsections/?section=${sectionId}`);
        this.sectionSubsections = response.data.results || response.data;
      } catch (err) {
        console.error(`Failed to fetch subsections for section ${sectionId}`, err);
      } finally {
        this.loading.sections = false;
      }
    },
  },
})

