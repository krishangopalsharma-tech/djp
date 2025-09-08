import { defineStore } from 'pinia'

const uid = () => Math.random().toString(36).slice(2) + Date.now().toString(36)

export const useDepotStore = defineStore('depot', {
  state: () => ({
    depots: [], // [{ uid, name, code, location, equipments: [] }]
  }),
  actions: {
    addDepot(payload = {}) {
      this.depots.push({
        uid: payload.uid || uid(),
        name: payload.name || '',
        code: payload.code || '',
        location: payload.location || '',
        equipments: Array.isArray(payload.equipments) ? [...payload.equipments] : [],
      })
    },
    removeDepot(uidOrIndex) {
      const idx = typeof uidOrIndex === 'number'
        ? uidOrIndex
        : this.depots.findIndex(d => d.uid === uidOrIndex)
      if (idx >= 0) this.depots.splice(idx, 1)
    },
    setEquipments(depotUid, equipments) {
      const d = this.depots.find(x => x.uid === depotUid)
      if (d) d.equipments = JSON.parse(JSON.stringify(equipments || []))
    },
  }
})
