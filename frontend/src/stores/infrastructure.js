// Path: frontend/src/stores/infrastructure.js

import { defineStore } from 'pinia'
import { http } from '@/lib/http'

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
      try {
        // Send the new depot data to the backend
        await http.post('/infrastructure/depots/', payload);
        // After success, refresh the list to show the new depot
        await this.fetchDepots();
      } catch (err) {
        this.error = 'Failed to add depot.';
        console.error(err);
      } finally {
        this.loading.depots = false;
      }
    },

    async removeDepot(depotId) {
      this.loading.depots = true;
      this.error = null;
      try {
        // Send a delete request for the specific depot ID
        await http.delete(`/infrastructure/depots/${depotId}/`);
        // After success, refresh the list
        await this.fetchDepots();
      } catch (err) {
        this.error = 'Failed to remove depot.';
        console.error(err);
      } finally {
        this.loading.depots = false;
      }
    },
    async addStation(payload) {
      this.loading.stations = true;
      this.error = null;
      try {
        // Payload will be { name: '...', code: '...', depot: depotId }
        await http.post('/infrastructure/stations/', payload);
        await this.fetchStations(); // Refresh the list
      } catch (err) {
        this.error = 'Failed to add station.';
        console.error(err);
      } finally {
        this.loading.stations = false;
      }
    },

    async removeStation(stationId) {
      this.loading.stations = true;
      this.error = null;
      try {
        await http.delete(`/infrastructure/stations/${stationId}/`);
        await this.fetchStations(); // Refresh the list
      } catch (err) {
        this.error = 'Failed to remove station.';
        console.error(err);
      } finally {
        this.loading.stations = false;
      }
    },
  },
})