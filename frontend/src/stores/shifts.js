import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useShiftStore = defineStore('shifts', () => {
    const shifts = ref([])
    const loading = ref(false)
    const error = ref(null)

    const morningShift = computed(() => shifts.value.find(s => s.name === 'Morning'))
    const eveningShift = computed(() => shifts.value.find(s => s.name === 'Evening'))
    const nightShift = computed(() => shifts.value.find(s => s.name === 'Night'))

    async function fetchShifts() {
        loading.value = true
        error.value = null
        try {
            const response = await fetch('/api/v1/shifts/')
            if (!response.ok) throw new Error('Failed to fetch shifts')
            shifts.value = await response.json()
        } catch (err) {
            error.value = err.message
        } finally {
            loading.value = false
        }
    }

    async function updateShift(id, data) {
        loading.value = true
        error.value = null
        try {
            const response = await fetch(`/api/v1/shifts/${id}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify(data),
            })
            if (!response.ok) throw new Error('Failed to update shift')
            const updatedShift = await response.json()
            const index = shifts.value.findIndex(s => s.id === id)
            if (index !== -1) shifts.value[index] = updatedShift
            return true
        } catch (err) {
            error.value = err.message
            return false
        } finally {
            loading.value = false
        }
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    return {
        shifts,
        loading,
        error,
        morningShift,
        eveningShift,
        nightShift,
        fetchShifts,
        updateShift,
    }
})
