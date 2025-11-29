<script setup>
import { ref, computed, onMounted, watch, onBeforeUnmount, nextTick } from 'vue'
import WidgetShell from '@/components/WidgetShell.vue'
import { useInfrastructureStore } from '@/stores/infrastructure_lists'
import { useCircuitsStore } from '@/stores/circuits'
import { useSectionsStore } from '@/stores/sections'
import { useStationsStore } from '@/stores/stations'
import { useSupervisorsStore } from '@/stores/supervisors'
import { useUIStore } from '@/stores/ui'
import Chart from 'chart.js/auto'
import axios from 'axios'
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'
import ExcelJS from 'exceljs'

import SearchSelect from '@/components/form/SearchSelect.vue'

const infrastructureStore = useInfrastructureStore()
const circuitsStore = useCircuitsStore()
const sectionsStore = useSectionsStore()
const stationsStore = useStationsStore()
const supervisorsStore = useSupervisorsStore()
const uiStore = useUIStore()

const activeTab = ref('operational') // operational, inventory
const activeInventoryTab = ref('depot') // depot, supervisor, station, section

// --- Operational Reports State ---
const opFilters = ref({
    scope: 'circuit', // system, circuit, depot, section, supervisor, subsection, station
    scopeId: [], // Changed to array for multi-select
    startDate: null,
    endDate: null,
    dateRangeType: 'today', // today, week, month, custom
    type: 'all' // all, failure, event
})

function setDateRange(type) {
    opFilters.value.dateRangeType = type
    const today = new Date()
    const yyyy = today.getFullYear()
    const mm = String(today.getMonth() + 1).padStart(2, '0')
    const dd = String(today.getDate()).padStart(2, '0')
    const todayStr = `${yyyy}-${mm}-${dd}`

    if (type === 'today') {
        opFilters.value.startDate = todayStr
        opFilters.value.endDate = todayStr
    } else if (type === '7d') {
        const lastWeek = new Date(today)
        lastWeek.setDate(today.getDate() - 7)
        opFilters.value.startDate = lastWeek.toISOString().split('T')[0]
        opFilters.value.endDate = todayStr
    } else if (type === '30d') {
        const lastMonth = new Date(today)
        lastMonth.setDate(today.getDate() - 30)
        opFilters.value.startDate = lastMonth.toISOString().split('T')[0]
        opFilters.value.endDate = todayStr
    } else if (type === 'custom') {
        // Keep existing values or reset if empty
        if (!opFilters.value.startDate) opFilters.value.startDate = todayStr
        if (!opFilters.value.endDate) opFilters.value.endDate = todayStr
    }
}

const statsData = ref(null)
const loadingStats = ref(false)
let statusChartInstance = null
let typeChartInstance = null

function destroyCharts() {
    if (statusChartInstance) {
        statusChartInstance.destroy()
        statusChartInstance = null
    }
    if (typeChartInstance) {
        typeChartInstance.destroy()
        typeChartInstance = null
    }
}

onBeforeUnmount(() => {
    destroyCharts()
})

watch(activeTab, async (newTab) => {
    if (newTab !== 'operational') {
        destroyCharts()
    } else {
        await nextTick()
        if (statsData.value) {
            renderCharts()
        } else {
            fetchOperationalStats()
        }
    }
})

// --- Inventory Reports State ---
const invFilters = ref({
    depotIds: [],
    supervisorId: null,
    stationId: null,
    sectionId: null,
    subsectionId: null
})
const inventoryData = ref([])
const loadingInventory = ref(false)

// --- Computed Options ---
const scopeOptions = [
    { value: 'circuit', label: 'Circuit' },
    { value: 'depot', label: 'Depot' },
    { value: 'section', label: 'Section' },
    { value: 'subsection', label: 'Sub-section' },
    { value: 'station', label: 'Station' },
    { value: 'supervisor', label: 'Supervisor' },
    { value: 'system', label: 'Whole System' }
]

const scopeIdOptions = computed(() => {
    const scope = opFilters.value.scope
    if (scope === 'circuit') return circuitsStore.circuits?.map(i => ({ value: i.id, label: i.circuit_id })) || []
    if (scope === 'depot') return infrastructureStore.depots?.map(i => ({ value: i.id, label: i.name })) || []
    if (scope === 'section') return sectionsStore.sections?.map(i => ({ value: i.id, label: i.name })) || []
    if (scope === 'station') return stationsStore.stations?.map(i => ({ value: i.id, label: i.code })) || []
    if (scope === 'supervisor') return supervisorsStore.supervisors?.map(i => ({ value: i.id, label: i.name })) || []
    if (scope === 'subsection') {
        const subs = []
        sectionsStore.sections?.forEach(s => {
            if(s.subsections) {
                s.subsections.forEach(sub => subs.push({ value: sub.id, label: `${sub.name} (${s.name})` }))
            }
        })
        return subs
    }
    return []
})

const depotOptions = computed(() => infrastructureStore.depots?.map(d => ({ value: d.id, label: d.name })) || [])
const supervisorOptions = computed(() => supervisorsStore.supervisors?.map(s => ({ value: s.id, label: s.name })) || [])
const stationOptions = computed(() => stationsStore.stations?.map(s => ({ value: s.id, label: s.code })) || [])
const sectionOptions = computed(() => sectionsStore.sections?.map(s => ({ value: s.id, label: s.name })) || [])
const subsectionOptions = computed(() => {
    if (!invFilters.value.sectionId) return []
    const section = sectionsStore.sections?.find(s => s.id === invFilters.value.sectionId)
    return section?.subsections?.map(sub => ({ value: sub.id, label: sub.name })) || []
})

// --- Lifecycle ---
onMounted(async () => {
    await Promise.all([
        infrastructureStore.fetchDepots(),
        circuitsStore.fetchCircuits(),
        sectionsStore.fetchSections(),
        stationsStore.fetchStations(),
        supervisorsStore.fetchSupervisors()
    ])
})

// --- Operational Reports Logic ---
// Watch for scope changes to reset scopeId
watch(() => opFilters.value.scope, () => {
    opFilters.value.scopeId = []
})

// --- Operational Reports Logic ---
async function fetchOperationalStats() {
    loadingStats.value = true
    try {
        let scopeIdParam = opFilters.value.scopeId
        if (Array.isArray(scopeIdParam)) {
            scopeIdParam = scopeIdParam.join(',')
        }

        const params = {
            scope: opFilters.value.scope,
            scope_id: scopeIdParam,
            start_date: opFilters.value.startDate,
            end_date: opFilters.value.endDate,
            type: opFilters.value.type
        }

        const response = await axios.get('/api/v1/reports/operational/stats/', { params })
        statsData.value = response.data
        renderCharts()
        
        // Also fetch the records for preview
        fetchOperationalRecords()
    } catch (error) {
        console.error("Error fetching stats:", error)
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Failed to fetch operational statistics.' })
    } finally {
        loadingStats.value = false
    }
}

const operationalRecords = ref([])
const loadingRecords = ref(false)

async function fetchOperationalRecords() {
    loadingRecords.value = true
    try {
        let scopeIdParam = opFilters.value.scopeId
        if (Array.isArray(scopeIdParam)) {
            scopeIdParam = scopeIdParam.join(',')
        }

        const params = {
            scope: opFilters.value.scope,
            scope_id: scopeIdParam,
            start_date: opFilters.value.startDate,
            end_date: opFilters.value.endDate,
            type: opFilters.value.type
        }
        
        const response = await axios.get('/api/v1/reports/operational/export/', { params })
        operationalRecords.value = response.data
    } catch (error) {
        console.error("Error fetching records:", error)
        // Don't show toast here to avoid double toasts with stats error
    } finally {
        loadingRecords.value = false
    }
}

function renderCharts() {
    if (!statsData.value) return

    // Status Chart
    const ctxStatus = document.getElementById('statusChart')
    if (ctxStatus) {
        if (statusChartInstance) statusChartInstance.destroy()
        statusChartInstance = new Chart(ctxStatus, {
            type: 'pie',
            data: {
                labels: statsData.value.status_distribution.map(d => d.current_status),
                datasets: [{
                    data: statsData.value.status_distribution.map(d => d.count),
                    backgroundColor: ['#ef4444', '#22c55e', '#eab308', '#3b82f6', '#6b7280', '#a855f7'] // Colors
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        })
    }

    // Type Chart
    const ctxType = document.getElementById('typeChart')
    if (ctxType) {
        if (typeChartInstance) typeChartInstance.destroy()
        typeChartInstance = new Chart(ctxType, {
            type: 'pie',
            data: {
                labels: statsData.value.type_distribution.map(d => d.entry_type === 'message' ? 'General Message' : 'Failure'),
                datasets: [{
                    data: statsData.value.type_distribution.map(d => d.count),
                    backgroundColor: ['#6366f1', '#f43f5e']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        })
    }
}




// --- Inventory Reports Logic ---
async function fetchInventoryReport() {
    loadingInventory.value = true
    inventoryData.value = []
    try {
        let url = ''
        let params = {}

        if (activeInventoryTab.value === 'depot') {
            url = '/api/v1/reports/inventory/depot_equipment/'
            params = { depot_ids: invFilters.value.depotIds }
        } else if (activeInventoryTab.value === 'supervisor') {
            url = '/api/v1/reports/inventory/supervisor_assets/'
            params = { supervisor_id: invFilters.value.supervisorId }
        } else if (activeInventoryTab.value === 'station') {
            url = '/api/v1/reports/inventory/station_equipment/'
            params = { station_id: invFilters.value.stationId }
        } else if (activeInventoryTab.value === 'section') {
            url = '/api/v1/reports/inventory/section_assets/'
            params = { section_id: invFilters.value.sectionId, subsection_id: invFilters.value.subsectionId }
        }

        const response = await axios.get(url, { params })
        inventoryData.value = response.data
    } catch (error) {
        console.error("Error fetching inventory:", error)
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Failed to fetch inventory report.' })
    } finally {
        loadingInventory.value = false
    }
}

watch(activeInventoryTab, () => {
    inventoryData.value = []
    // Reset relevant filters if needed, or keep them
})

// --- Export Logic ---
async function exportOperationalReport(format) {
    if (operationalRecords.value.length === 0) {
        uiStore.pushToast({ type: 'warning', title: 'No Data', message: 'No records to export.' })
        return
    }

    const toastId = uiStore.pushToast({ type: 'info', title: 'Exporting...', message: 'Generating report.', duration: 0 })

    try {
        if (format === 'excel') {
            await generateOperationalExcel(operationalRecords.value)
        } else {
            generateOperationalPDF(operationalRecords.value)
        }
        uiStore.removeToast(toastId)
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Report downloaded.' })

    } catch (error) {
        console.error("Export failed:", error)
        uiStore.removeToast(toastId)
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Failed to export report.' })
    }
}

async function generateOperationalExcel(data) {
    const workbook = new ExcelJS.Workbook()
    const worksheet = workbook.addWorksheet('Operational Report')

    // Columns
    worksheet.columns = [
        { header: 'ID', key: 'fail_id', width: 15 },
        { header: 'Date', key: 'reported_at', width: 20 },
        { header: 'Type', key: 'entry_type', width: 15 },
        { header: 'Status', key: 'current_status', width: 15 },
        { header: 'Circuit', key: 'circuit', width: 15 },
        { header: 'Station', key: 'station', width: 10 },
        { header: 'Section', key: 'section', width: 20 },
        { header: 'Sub-Section', key: 'sub_section', width: 20 },
        { header: 'Duration', key: 'duration', width: 15 },
        { header: 'Assigned To', key: 'assigned_to', width: 20 },
    ]

    // Style Header
    worksheet.getRow(1).font = { bold: true }
    worksheet.getRow(1).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFE0E0E0' } }

    // Add Data
    data.forEach(item => {
        const row = worksheet.addRow({
            fail_id: item.fail_id,
            reported_at: new Date(item.reported_at).toLocaleString(),
            entry_type: item.entry_type === 'message' ? 'Message' : 'Failure',
            current_status: item.current_status,
            circuit: item.circuit?.circuit_id || '-',
            station: item.station?.code || '-',
            section: item.section?.name || '-',
            sub_section: item.sub_section?.name || '-',
            duration: formatDuration(item),
            assigned_to: item.assigned_to?.name || '-',
        })

        // Color coding
        let argb = null
        if (item.current_status === 'Resolved') argb = 'FFD1E7DD'
        else if (item.current_status === 'Active') argb = 'FFF8D7DA'
        else if (item.current_status === 'In Progress') argb = 'FFFFF3CD'
        else if (item.current_status === 'On Hold') argb = 'FFE2E3E5'

        if (argb) {
            row.eachCell((cell) => {
                cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: argb } }
                cell.border = { top: { style: 'thin' }, left: { style: 'thin' }, bottom: { style: 'thin' }, right: { style: 'thin' } }
            })
        }
    })

    // Write Buffer
    const buffer = await workbook.xlsx.writeBuffer()
    const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `Operational_Report_${new Date().toISOString().slice(0,10)}.xlsx`
    link.click()
}

function generateOperationalPDF(data) {
    const doc = new jsPDF({ orientation: 'landscape' })
    
    doc.setFontSize(16)
    doc.text('Operational Report', 14, 15)
    doc.setFontSize(10)
    doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 22)

    const tableBody = data.map(item => [
        item.fail_id,
        new Date(item.reported_at).toLocaleDateString(),
        item.current_status,
        item.circuit?.circuit_id || '-',
        item.station?.code || '-',
        item.section?.name || '-',
        item.sub_section?.name || '-',
        formatDuration(item)
    ])

    autoTable(doc, {
        startY: 25,
        head: [['ID', 'Date', 'Status', 'Circuit', 'Station', 'Section', 'Sub-Section', 'Duration']],
        body: tableBody,
        styles: { fontSize: 8 },
        headStyles: { fillColor: [66, 66, 66] },
        didParseCell: function(dataHook) {
            if (dataHook.section === 'body') {
                const item = data[dataHook.row.index]
                if (item.current_status === 'Resolved') dataHook.cell.styles.fillColor = [209, 231, 221]
                else if (item.current_status === 'Active') dataHook.cell.styles.fillColor = [248, 215, 218]
                else if (item.current_status === 'In Progress') dataHook.cell.styles.fillColor = [255, 243, 205]
                else if (item.current_status === 'On Hold') dataHook.cell.styles.fillColor = [226, 227, 229]
            }
        }
    })

    doc.save(`Operational_Report_${new Date().toISOString().slice(0,10)}.pdf`)
}

function formatDuration(item) {
    let totalMinutes = 0
    let isActive = false

    if (item.duration_minutes !== null) {
        totalMinutes = item.duration_minutes
    } else {
        // Calculate live duration for active failures
        const start = new Date(item.reported_at)
        const now = new Date()
        const diffMs = now - start
        totalMinutes = Math.floor(diffMs / 60000)
        isActive = true
    }

    const days = Math.floor(totalMinutes / (24 * 60))
    const hours = Math.floor((totalMinutes % (24 * 60)) / 60)
    const mins = totalMinutes % 60

    let durationStr = ''
    if (days > 0) {
        durationStr = `${days}d ${hours}h ${mins}m`
    } else {
        durationStr = `${hours}h ${mins}m`
    }

    return isActive ? `${durationStr} (Active)` : durationStr
}

async function exportInventoryReport(format) {
    if (inventoryData.value.length === 0) {
        uiStore.pushToast({ type: 'warning', title: 'No Data', message: 'Generate the report first.' })
        return
    }

    if (format === 'excel') {
        const workbook = new ExcelJS.Workbook()
        const worksheet = workbook.addWorksheet(`${activeInventoryTab.value} Inventory`)

        // Define columns based on active tab
        if (activeInventoryTab.value === 'depot') {
            worksheet.columns = [
                { header: 'Depot', key: 'depot', width: 20 },
                { header: 'Station', key: 'station', width: 15 },
                { header: 'Equipment', key: 'name', width: 25 },
                { header: 'Make/Model', key: 'make', width: 20 },
                { header: 'Qty', key: 'qty', width: 10 },
                { header: 'Status', key: 'status', width: 15 }
            ]
            inventoryData.value.forEach(depot => {
                depot.equipments.forEach(eq => {
                    worksheet.addRow({
                        depot: depot.depot_name,
                        station: eq.station,
                        name: eq.name,
                        make: eq.make_modal,
                        qty: eq.quantity,
                        status: eq.status
                    })
                })
            })
        } else if (activeInventoryTab.value === 'supervisor') {
            worksheet.columns = [
                { header: 'Supervisor', key: 'name', width: 20 },
                { header: 'Mobile', key: 'mobile', width: 15 },
                { header: 'Asset Type', key: 'type', width: 20 },
                { header: 'Asset Name', key: 'asset', width: 25 },
                { header: 'Location', key: 'location', width: 20 }
            ]
            inventoryData.value.forEach(sup => {
                sup.assets.forEach(asset => {
                    worksheet.addRow({
                        name: sup.name,
                        mobile: sup.mobile,
                        type: asset.type,
                        asset: asset.name,
                        location: asset.location
                    })
                })
            })
        } else if (activeInventoryTab.value === 'station') {
            worksheet.columns = [
                { header: 'Station', key: 'station', width: 20 },
                { header: 'Equipment', key: 'name', width: 25 },
                { header: 'Make/Model', key: 'make', width: 20 },
                { header: 'Address', key: 'address', width: 20 },
                { header: 'Location', key: 'location', width: 20 },
                { header: 'Qty', key: 'qty', width: 10 },
                { header: 'Install Date', key: 'install', width: 15 },
                { header: 'Codal Life', key: 'life', width: 10 }
            ]
            inventoryData.value.forEach(st => {
                st.equipments.forEach(eq => {
                    worksheet.addRow({
                        station: `${st.station_name} (${st.station_code})`,
                        name: eq.name,
                        make: eq.make_modal,
                        address: eq.address,
                        location: eq.location,
                        qty: eq.quantity,
                        install: eq.installation_date,
                        life: eq.codal_life
                    })
                })
            })
        } else if (activeInventoryTab.value === 'section') {
            worksheet.columns = [
                { header: 'Section', key: 'section', width: 20 },
                { header: 'Sub-section', key: 'sub', width: 20 },
                { header: 'Asset', key: 'asset', width: 25 },
                { header: 'Qty', key: 'qty', width: 10 },
                { header: 'Unit', key: 'unit', width: 10 },
                { header: 'Install Date', key: 'install', width: 15 },
                { header: 'Life (Yrs)', key: 'life', width: 10 }
            ]
            inventoryData.value.forEach(sec => {
                sec.subsections.forEach(sub => {
                    sub.assets.forEach(asset => {
                        worksheet.addRow({
                            section: sec.section_name,
                            sub: sub.subsection_name,
                            asset: asset.name,
                            qty: asset.quantity,
                            unit: asset.unit,
                            install: asset.installation_date,
                            life: asset.codal_life
                        })
                    })
                })
            })
        }

        // Style Header
        worksheet.getRow(1).font = { bold: true }
        worksheet.getRow(1).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFE0E0E0' } }

        // Write Buffer
        const buffer = await workbook.xlsx.writeBuffer()
        const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        const link = document.createElement('a')
        link.href = URL.createObjectURL(blob)
        link.download = `Inventory_Report_${activeInventoryTab.value}_${new Date().toISOString().slice(0,10)}.xlsx`
        link.click()
    }
}

</script>

<template>
  <div class="space-y-6">
    <div>
        <!-- Main Tabs -->
        <div class="chip-group">
            <button 
                @click="activeTab = 'operational'"
                class="chip"
                :class="activeTab === 'operational' ? 'selected-primary' : 'text-app hover-primary'"
                :aria-pressed="String(activeTab === 'operational')"
            >
                Operational Reports
            </button>
            <button 
                @click="activeTab = 'inventory'"
                class="chip"
                :class="activeTab === 'inventory' ? 'selected-primary' : 'text-app hover-primary'"
                :aria-pressed="String(activeTab === 'inventory')"
            >
                Inventory Reports
            </button>
        </div>
    </div>

    <!-- OPERATIONAL REPORTS TAB -->
    <div v-if="activeTab === 'operational'" class="space-y-4">
        <!-- Filters -->
        <WidgetShell title="Report Configuration" :range="opFilters.dateRangeType" @update:range="setDateRange">
            <template #filters>
                <div class="flex items-center gap-2 text-sm">
                    <span class="font-medium text-muted">Date Range:</span>
                    <div v-if="opFilters.dateRangeType === 'custom'" class="flex gap-2">
                        <input type="date" v-model="opFilters.startDate" class="field h-8 w-32">
                        <input type="date" v-model="opFilters.endDate" class="field h-8 w-32">
                    </div>
                    <div v-else class="text-app bg-gray-50 px-3 py-1 rounded-md border border-gray-200">
                        {{ opFilters.startDate }} <span class="text-muted mx-1">to</span> {{ opFilters.endDate }}
                    </div>
                </div>
            </template>

            <template #actions>
                <button class="btn btn-outline" @click="exportOperationalReport('pdf')">Export PDF</button>
                <button class="btn btn-primary" @click="exportOperationalReport('excel')">Export Excel</button>
            </template>

            <div class="flex flex-wrap items-end gap-4">
                <div class="w-32">
                    <label class="block text-sm font-medium mb-1">Scope</label>
                    <select v-model="opFilters.scope" class="field h-9 w-full">
                        <option v-for="opt in scopeOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                    </select>
                </div>
                
                <div v-if="opFilters.scope !== 'system'" class="w-48">
                    <label class="block text-sm font-medium mb-1">Select {{ opFilters.scope }}</label>
                    <SearchSelect 
                        v-model="opFilters.scopeId" 
                        :options="scopeIdOptions" 
                        placeholder="Select..." 
                        :multiple="true"
                        inputClass="h-9"
                    />
                </div>

                <div class="w-56">
                    <label class="block text-sm font-medium mb-1">Failure Type</label>
                    <select v-model="opFilters.type" class="field h-9 w-full">
                        <option value="all">All Types</option>
                        <option value="failure">Failures Only</option>
                        <option value="event">General Messages Only</option>
                    </select>
                </div>

                <div v-if="opFilters.dateRangeType === 'custom'" class="flex gap-2 w-64">
                   <div class="flex-1">
                        <label class="block text-xs text-muted mb-1">Start</label>
                        <input type="date" v-model="opFilters.startDate" class="field h-9 w-full text-xs">
                   </div>
                   <div class="flex-1">
                        <label class="block text-xs text-muted mb-1">End</label>
                        <input type="date" v-model="opFilters.endDate" class="field h-9 w-full text-xs">
                   </div>
                </div>

                <div class="ml-auto">
                    <button @click="fetchOperationalStats" class="btn btn-primary h-9 px-6 flex items-center justify-center gap-2" :disabled="loadingStats">
                        <span v-if="loadingStats" class="loader-spinner w-4 h-4"></span>
                        Preview
                    </button>
                </div>
            </div>


            <!-- Preview Table -->
            <div class="mt-6 border-t pt-4">
                <h4 class="text-sm font-medium text-muted mb-2">Report Preview ({{ operationalRecords.length }} records)</h4>
                
                <div v-if="loadingRecords" class="py-8 text-center text-muted">
                    Loading records...
                </div>
                
                <div v-else-if="operationalRecords.length === 0" class="py-8 text-center text-muted bg-gray-50 rounded-lg border border-dashed">
                    No records found for the selected criteria.
                </div>

                <div v-else class="overflow-x-auto border rounded-lg max-h-[400px] overflow-y-auto">
                    <table class="w-full text-sm text-left">
                        <thead class="text-xs text-muted uppercase bg-gray-50 sticky top-0 z-10">
                            <tr>
                                <th class="px-4 py-2">ID</th>
                                <th class="px-4 py-2">Date</th>
                                <th class="px-4 py-2">Status</th>
                                <th class="px-4 py-2">Circuit</th>
                                <th class="px-4 py-2">Station</th>
                                <th class="px-4 py-2">Section</th>
                                <th class="px-4 py-2">Sub-Section</th>
                                <th class="px-4 py-2">Duration</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="item in operationalRecords" :key="item.fail_id" class="border-b hover:bg-gray-50">
                                <td class="px-4 py-2 font-medium">{{ item.fail_id }}</td>
                                <td class="px-4 py-2 whitespace-nowrap">{{ new Date(item.reported_at).toLocaleDateString() }}</td>
                                <td class="px-4 py-2">
                                    <span class="px-2 py-0.5 rounded text-xs font-medium"
                                        :class="{
                                            'bg-green-100 text-green-800': item.current_status === 'Resolved',
                                            'bg-red-100 text-red-800': item.current_status === 'Active',
                                            'bg-yellow-100 text-yellow-800': item.current_status === 'In Progress',
                                            'bg-gray-100 text-gray-800': item.current_status === 'On Hold'
                                        }"
                                    >
                                        {{ item.current_status }}
                                    </span>
                                </td>
                                <td class="px-4 py-2">{{ item.circuit?.circuit_id || '-' }}</td>
                                <td class="px-4 py-2">{{ item.station?.code || '-' }}</td>
                                <td class="px-4 py-2">{{ item.section?.name || '-' }}</td>
                                <td class="px-4 py-2">{{ item.sub_section?.name || '-' }}</td>
                                <td class="px-4 py-2">{{ formatDuration(item) }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </WidgetShell>

        <!-- Charts -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <WidgetShell title="Status Distribution">
                <div class="h-64 relative">
                    <canvas id="statusChart"></canvas>
                </div>
            </WidgetShell>
            <WidgetShell title="Type Distribution">
                <div class="h-64 relative">
                    <canvas id="typeChart"></canvas>
                </div>
            </WidgetShell>
        </div>
    </div>

    <!-- INVENTORY REPORTS TAB -->
    <div v-if="activeTab === 'inventory'" class="space-y-6">
        <!-- Sub Tabs -->
        <div class="flex gap-4 border-b border-app/20 overflow-x-auto">
            <button 
                v-for="tab in ['depot', 'supervisor', 'station', 'section']" 
                :key="tab"
                @click="activeInventoryTab = tab; inventoryData = []"
                class="pb-2 px-1 text-sm font-medium capitalize border-b-2 transition-colors whitespace-nowrap"
                :class="activeInventoryTab === tab ? 'border-slate-500 text-slate-700' : 'border-transparent text-app/60 hover:text-app'"
            >
                {{ tab }} Inventory
            </button>
        </div>

        <!-- Filters & Actions -->
        <div class="card p-4 space-y-4">
            <div class="flex flex-wrap items-end gap-4">
                <!-- Depot Filters -->
                <div v-if="activeInventoryTab === 'depot'" class="flex-grow min-w-[200px]">
                    <label class="block text-sm font-medium mb-1">Select Depot(s)</label>
                    <select v-model="invFilters.depotIds" multiple class="field h-24 w-full">
                        <option v-for="opt in depotOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                    </select>
                    <p class="text-xs text-muted mt-1">Hold Ctrl/Cmd to select multiple</p>
                </div>

                <!-- Supervisor Filters -->
                <div v-if="activeInventoryTab === 'supervisor'" class="flex-grow min-w-[200px]">
                    <label class="block text-sm font-medium mb-1">Select Supervisor</label>
                    <select v-model="invFilters.supervisorId" class="field h-9 w-full">
                        <option :value="null">All Supervisors</option>
                        <option v-for="opt in supervisorOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                    </select>
                </div>

                <!-- Station Filters -->
                <div v-if="activeInventoryTab === 'station'" class="flex-grow min-w-[200px]">
                    <label class="block text-sm font-medium mb-1">Select Station</label>
                    <select v-model="invFilters.stationId" class="field h-9 w-full">
                        <option :value="null">All Stations</option>
                        <option v-for="opt in stationOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                    </select>
                </div>

                <!-- Section Filters -->
                <div v-if="activeInventoryTab === 'section'" class="flex-grow min-w-[200px] flex gap-4">
                    <div class="flex-1">
                        <label class="block text-sm font-medium mb-1">Select Section</label>
                        <select v-model="invFilters.sectionId" class="field h-9 w-full">
                            <option :value="null">All Sections</option>
                            <option v-for="opt in sectionOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                        </select>
                    </div>
                    <div class="flex-1">
                        <label class="block text-sm font-medium mb-1">Select Sub-section</label>
                        <select v-model="invFilters.subsectionId" class="field h-9 w-full" :disabled="!invFilters.sectionId">
                            <option :value="null">All Sub-sections</option>
                            <option v-for="opt in subsectionOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                        </select>
                    </div>
                </div>

                <button class="btn btn-primary h-9 mb-[1px]" @click="fetchInventoryReport" :disabled="loadingInventory">
                    {{ loadingInventory ? 'Loading...' : 'Generate Report' }}
                </button>
                 <button class="btn btn-outline h-9 mb-[1px]" @click="exportInventoryReport('excel')" :disabled="inventoryData.length === 0">
                    Export Excel
                </button>
            </div>
        </div>

        <!-- Results Table -->
        <div v-if="inventoryData.length > 0" class="card overflow-hidden">
            <div class="overflow-x-auto max-h-[600px]">
                
                <!-- Depot Table -->
                <table v-if="activeInventoryTab === 'depot'" class="w-full text-sm">
                    <thead>
                        <tr class="text-left bg-app/5 sticky top-0">
                            <th class="p-3">Depot</th>
                            <th class="p-3">Station</th>
                            <th class="p-3">Equipment</th>
                            <th class="p-3">Make/Model</th>
                            <th class="p-3">Qty</th>
                            <th class="p-3">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <template v-for="depot in inventoryData" :key="depot.depot_name">
                            <tr v-for="(eq, idx) in depot.equipments" :key="idx" class="border-b border-app/10 hover:bg-app/5">
                                <td class="p-3 font-medium" v-if="idx === 0" :rowspan="depot.equipments.length">{{ depot.depot_name }}</td>
                                <td class="p-3">{{ eq.station }}</td>
                                <td class="p-3">{{ eq.name }}</td>
                                <td class="p-3">{{ eq.make_modal }}</td>
                                <td class="p-3">{{ eq.quantity }}</td>
                                <td class="p-3"><span class="badge badge-success">{{ eq.status }}</span></td>
                            </tr>
                        </template>
                    </tbody>
                </table>

                <!-- Supervisor Table -->
                <table v-if="activeInventoryTab === 'supervisor'" class="w-full text-sm">
                    <thead>
                        <tr class="text-left bg-app/5 sticky top-0">
                            <th class="p-3">Supervisor</th>
                            <th class="p-3">Mobile</th>
                            <th class="p-3">Asset Type</th>
                            <th class="p-3">Asset Name</th>
                            <th class="p-3">Location</th>
                        </tr>
                    </thead>
                    <tbody>
                        <template v-for="sup in inventoryData" :key="sup.name">
                            <tr v-for="(asset, idx) in sup.assets" :key="idx" class="border-b border-app/10 hover:bg-app/5">
                                <td class="p-3 font-medium" v-if="idx === 0" :rowspan="sup.assets.length">{{ sup.name }}</td>
                                <td class="p-3" v-if="idx === 0" :rowspan="sup.assets.length">{{ sup.mobile }}</td>
                                <td class="p-3">{{ asset.type }}</td>
                                <td class="p-3">{{ asset.name }}</td>
                                <td class="p-3">{{ asset.location }}</td>
                            </tr>
                        </template>
                    </tbody>
                </table>

                <!-- Station Table -->
                <table v-if="activeInventoryTab === 'station'" class="w-full text-sm">
                    <thead>
                        <tr class="text-left bg-app/5 sticky top-0">
                            <th class="p-3">Station</th>
                            <th class="p-3">Equipment</th>
                            <th class="p-3">Make/Model</th>
                            <th class="p-3">Address</th>
                            <th class="p-3">Location</th>
                            <th class="p-3">Qty</th>
                            <th class="p-3">Install Date</th>
                            <th class="p-3">Codal Life</th>
                        </tr>
                    </thead>
                    <tbody>
                        <template v-for="st in inventoryData" :key="st.station_code">
                            <tr v-for="(eq, idx) in st.equipments" :key="idx" class="border-b border-app/10 hover:bg-app/5">
                                <td class="p-3 font-medium" v-if="idx === 0" :rowspan="st.equipments.length">{{ st.station_name }} ({{ st.station_code }})</td>
                                <td class="p-3">{{ eq.name }}</td>
                                <td class="p-3">{{ eq.make_modal }}</td>
                                <td class="p-3">{{ eq.address }}</td>
                                <td class="p-3">{{ eq.location }}</td>
                                <td class="p-3">{{ eq.quantity }}</td>
                                <td class="p-3">{{ eq.installation_date }}</td>
                                <td class="p-3">{{ eq.codal_life }}</td>
                            </tr>
                        </template>
                    </tbody>
                </table>

                <!-- Section Table -->
                <table v-if="activeInventoryTab === 'section'" class="w-full text-sm">
                    <thead>
                        <tr class="text-left bg-app/5 sticky top-0">
                            <th class="p-3">Section</th>
                            <th class="p-3">Sub-section</th>
                            <th class="p-3">Asset</th>
                            <th class="p-3">Qty</th>
                            <th class="p-3">Unit</th>
                            <th class="p-3">Install Date</th>
                            <th class="p-3">Life (Yrs)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <template v-for="sec in inventoryData" :key="sec.section_name">
                            <template v-for="sub in sec.subsections" :key="sub.subsection_name">
                                <tr v-for="(asset, idx) in sub.assets" :key="idx" class="border-b border-app/10 hover:bg-app/5">
                                    <td class="p-3 font-medium" v-if="idx === 0 && sub === sec.subsections[0]" :rowspan="sec.subsections.reduce((acc, s) => acc + s.assets.length, 0)">{{ sec.section_name }}</td>
                                    <td class="p-3" v-if="idx === 0" :rowspan="sub.assets.length">{{ sub.subsection_name }}</td>
                                    <td class="p-3">{{ asset.name }}</td>
                                    <td class="p-3">{{ asset.quantity }}</td>
                                    <td class="p-3">{{ asset.unit }}</td>
                                    <td class="p-3">{{ asset.installation_date }}</td>
                                    <td class="p-3">{{ asset.codal_life }}</td>
                                </tr>
                            </template>
                        </template>
                    </tbody>
                </table>

            </div>
        </div>
        <div v-else-if="!loadingInventory" class="text-center py-10 text-muted">
            Select filters and click "Generate Report" to view data.
        </div>
    </div>
  </div>
</template>

<style scoped>
/* Using global styles from tailwind.css */
</style>

