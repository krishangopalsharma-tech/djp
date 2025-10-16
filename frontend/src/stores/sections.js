import { defineStore } from 'pinia';

export const useSectionsStore = defineStore('sections', {
  state: () => ({
    sections: [{ id: 1, name: 'North Section', depot: 1, depot_name: 'Main Depot', subsection_count: 2 }],
    sectionSubsections: [],
    loading: false,
  }),
  actions: {
    async fetchSections() { this.loading = false; },
    // Add other placeholder actions if needed
  },
});