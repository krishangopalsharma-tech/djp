// frontend/src/stores/catalog.js
import { defineStore } from 'pinia'

export const useCatalogStore = defineStore('catalog', {
  state: () => ({
    depots: [
      { id: 'ADI', name: 'Ahmedabad Depot' },
      { id: 'BRC', name: 'Vadodara Depot' },
    ],
    // Stations available per depot
    stationsByDepot: {
      ADI: [
        { id: 'ADI-AHMD', name: 'Ahmedabad' },
        { id: 'ADI-NADI', name: 'Nadiad' },
        { id: 'ADI-VIJL', name: 'Vijay Nagar' },
      ],
      BRC: [
        { id: 'BRC-BHAR', name: 'Bharuch' },
        { id: 'BRC-ANKL', name: 'Ankleshwar' },
      ],
    },
    // Sub-sections available per depot
    subSectionsByDepot: {
      ADI: [
        { id: 'SIG', name: 'Signal' },
        { id: 'TEL', name: 'Telecom' },
        { id: 'PWR', name: 'Power' },
      ],
      BRC: [
        { id: 'SIG', name: 'Signal' },
        { id: 'TEL', name: 'Telecom' },
      ],
    },
    /**
     * Assets keyed by "stationId::subSectionId"
     */
    assetsByKey: {
      'ADI-AHMD::SIG': [
        { id: 'A-SIG-0001', name: 'Track Circuit TX-01' },
        { id: 'A-SIG-0002', name: 'Point Machine PM-12' },
      ],
      'ADI-AHMD::TEL': [
        { id: 'A-TEL-0101', name: 'OFC 24F Span AHMD-1' },
        { id: 'A-TEL-0102', name: 'Joint Closure JC-3' },
      ],
      'ADI-NADI::TEL': [
        { id: 'A-TEL-0201', name: 'OFC 24F Span NADI-2' },
      ],
      'BRC-BHAR::SIG': [
        { id: 'B-SIG-1001', name: 'Signal RELAY R-7' },
      ],
    },
  }),
  actions: {
    stationsForDepot(depotId) {
      return this.stationsByDepot[depotId] || []
    },
    subSectionsForDepot(depotId) {
      return this.subSectionsByDepot[depotId] || []
    },
    /**
     * Return union of assets for all (stationId, subSectionId) combinations
     */
    assetsFor(stationIds = [], subSectionIds = []) {
      const out = new Map()
      for (const s of stationIds || []) {
        for (const sub of subSectionIds || []) {
          const key = `${s}::${sub}`
          const list = this.assetsByKey[key] || []
          for (const a of list) out.set(a.id, a)
        }
      }
      return Array.from(out.values())
    },
  },
})

