<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import DataTable from '@/components/DataTable.vue'
import FailureDetailsDrawer from '@/components/FailureDetailsDrawer.vue'
import Spinner from '@/components/ui/Spinner.vue'
import SearchSelect from '@/components/form/SearchSelect.vue'
import { Bell, Pencil, Trash2, FileDown, FileText, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, RotateCcw, Send } from 'lucide-vue-next'
import { useFailureStore } from '@/stores/failures'
import { useCircuitsStore } from '@/stores/circuits'
import { useSectionsStore } from '@/stores/sections'
import { useStationsStore } from '@/stores/stations'
import { useSupervisorsStore } from '@/stores/supervisors'
import { useShiftStore } from '@/stores/shifts'
import { useUIStore } from '@/stores/ui'

// --- Store setup ---
const failureStore = useFailureStore()
const circuitsStore = useCircuitsStore()
const sectionsStore = useSectionsStore()
const stationsStore = useStationsStore()
const supervisorsStore = useSupervisorsStore()
const shiftStore = useShiftStore()
const ui = useUIStore()
const router = useRouter()

// --- UI State ---
const drawerOpen = ref(false)
const activeItem = ref(null)
const isArchiveModalOpen = ref(false)
const failureToArchive = ref(null)
const archiveReason = ref('')

// --- Export Modal State ---
const showExportModal = ref(false)
const pendingExportAction = ref(null) // 'download' or 'send'
const exportOptions = ref({
    includeInfo: true,
    handedOverBy: '',
    takenOverBy: ''
})

function onNotify(row) {
  failureStore.sendFailureNotification(row.id, ['alerts'])
  ui.pushToast({ type: 'info', title: 'Notified', message: 'Alert notification sent.' })
}

function editFailure(row) {
  router.push({ path: '/logbook/new', query: { edit: row.id } })
}

function openDetails(row) {
  activeItem.value = row
  drawerOpen.value = true
}

function openArchiveModal(row) {
  failureToArchive.value = row
  isArchiveModalOpen.value = true
  archiveReason.value = ''
}

async function confirmArchive() {
  if (failureToArchive.value) {
    await failureStore.archiveFailure(failureToArchive.value.id, archiveReason.value)
    failureToArchive.value = null
    isArchiveModalOpen.value = false
    ui.pushToast({ type: 'success', title: 'Archived', message: 'Failure log archived.' })
  }
}
const query = ref('')
const selectedCircuits = ref([])
const selectedSections = ref([])
const selectedStations = ref([])
const selectedSupervisors = ref([])
const selectedStatuses = ref([])

const selectedShifts = ref([])
const selectedDate = ref('') // Default empty, auto-set to Today when shift selected
const sortKey = ref('reported_at')
const sortDir = ref('desc')
const currentPage = ref(1)
const rowsPerPage = ref(20)

// --- Data Fetching ---
// --- Data Fetching ---
const autoRefresh = ref(true)
let refreshInterval = null

function fetchList() {
  // Use silent fetch to avoid table flicker
  failureStore.fetchFailuresBackground()
}

onMounted(() => {
  failureStore.fetchFailures()
  // Fetch data for filter dropdowns if not already loaded
  if (circuitsStore.circuits.length === 0) circuitsStore.fetchCircuits()
  if (sectionsStore.sections.length === 0) sectionsStore.fetchSections()
  if (stationsStore.stations.length === 0) stationsStore.fetchStations()
  if (supervisorsStore.supervisors.length === 0) supervisorsStore.fetchSupervisors()
  if (shiftStore.shifts.length === 0) shiftStore.fetchShifts()

  // Start auto-refresh
  refreshInterval = setInterval(() => {
    if (autoRefresh.value) fetchList()
  }, 10000)
})

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval)
})

// --- Computed Data for UI ---
const loading = computed(() => failureStore.loading)
const error = computed(() => failureStore.error)

// --- Options for Filter Dropdowns ---
const circuitOptions = computed(() => circuitsStore.circuits.map(c => ({ label: `${c.circuit_id} (${c.name})`, value: c.id })))
const sectionOptions = computed(() => sectionsStore.sections.map(s => ({ label: s.name, value: s.id })))
const stationOptions = computed(() => stationsStore.stations.map(s => ({ label: s.name, value: s.id })))
const supervisorOptions = computed(() => supervisorsStore.supervisors.map(s => ({ label: s.name, value: s.id })))
const statusOptions = computed(() => ([
    { label: 'Active', value: 'Active' }, { label: 'In Progress', value: 'In Progress' },
    { label: 'Resolved', value: 'Resolved' }, { label: 'On Hold', value: 'On Hold' },
]))
const shiftOptions = computed(() => {
    return shiftStore.shifts.map(s => ({
        label: `${s.name} (${s.start_time.slice(0, 5)} - ${s.end_time.slice(0, 5)})`,
        value: s.name
    }))
})

// --- Filtering & Sorting Logic ---
function resetFilters() {
    query.value = ''
    selectedCircuits.value = []
    selectedSections.value = []
    selectedStations.value = []
    selectedSupervisors.value = []
    selectedStatuses.value = []

    selectedShifts.value = []
    selectedDate.value = ''
    currentPage.value = 1
}

// Watch selectedShifts to disable other filters
watch(selectedShifts, (newVal) => {
    if (newVal.length > 0) {
        // Disable other filters (UI handled by :disabled prop)
        // We also clear them to avoid confusion, as requested "disable all other filter"
        selectedCircuits.value = []
        selectedSections.value = []
        selectedStations.value = []
        selectedSupervisors.value = []
        selectedStatuses.value = []

        query.value = ''
        
        // Auto-set Date to Today if not set
        if (!selectedDate.value) {
            selectedDate.value = new Date().toISOString().slice(0, 10)
        }
    }
}
)

const filteredRows = computed(() => {
  const q = query.value.trim().toLowerCase()
  return failureStore.failures.filter(row => {
    if (!row) return false;
    // Check against text query
    const inQuery = q ? JSON.stringify(row).toLowerCase().includes(q) : true
    // Check against dropdown filters (IDs)
    const inCircuits = selectedCircuits.value.length ? selectedCircuits.value.includes(row.circuit?.id) : true
    const inSections = selectedSections.value.length ? selectedSections.value.includes(row.section?.id) : true
    const inStations = selectedStations.value.length ? selectedStations.value.includes(row.station?.id) : true
    const inSupervisors = selectedSupervisors.value.length ? selectedSupervisors.value.includes(row.assigned_to?.id) : true
    const inStatuses = selectedStatuses.value.length ? selectedStatuses.value.includes(row.current_status) : true
    
    // Check against Shift filter (and Date)
    let inShifts = true
    if (selectedShifts.value.length > 0) {
        const rowDate = new Date(row.reported_at)
        const rowTime = rowDate.getTime()

        // Use selectedDate or default to Today
        const filterDateStr = selectedDate.value || new Date().toISOString().slice(0, 10)
        const filterDate = new Date(filterDateStr)

        inShifts = selectedShifts.value.some(shiftName => {
            const shift = shiftStore.shifts.find(s => s.name === shiftName)
            if (!shift) return false

            const [startH, startM] = shift.start_time.split(':').map(Number)
            const [endH, endM] = shift.end_time.split(':').map(Number)
            
            // Construct Start and End DateTimes
            let startDateTime = new Date(filterDate)
            startDateTime.setHours(startH, startM, 0, 0)
            
            let endDateTime = new Date(filterDate)
            endDateTime.setHours(endH, endM, 0, 0)

            // Night Shift Logic (Start > End)
            // Example: 22:00 - 06:00.
            // If filtering for "Today" (e.g. 26th), Night Shift is 25th 22:00 to 26th 06:00.
            if (startDateTime > endDateTime) {
                startDateTime.setDate(startDateTime.getDate() - 1)
            }

            // Boundary Logic: > Start AND <= End
            // Note: User specified "22.01 to 06.00".
            // Standard JS Date comparison works.
            return rowTime > startDateTime.getTime() && rowTime <= endDateTime.getTime()
        })
    } else if (selectedDate.value) {
        // If no shift selected but Date is selected, filter by Date (00:00 - 23:59)
        const rowDate = new Date(row.reported_at)
        const filterDate = new Date(selectedDate.value)
        
        const startOfDay = new Date(filterDate)
        startOfDay.setHours(0, 0, 0, 0)
        
        const endOfDay = new Date(filterDate)
        endOfDay.setHours(23, 59, 59, 999)
        
        return rowDate >= startOfDay && rowDate <= endOfDay
    }
    
    return inQuery && inCircuits && inSections && inStations && inSupervisors && inStatuses && inShifts
  })
})

const sortedRows = computed(() => {
    const data = [...filteredRows.value];
    if (!sortKey.value) return data;

    return data.sort((a, b) => {
        let valA, valB;

        // Handle nested properties for sorting
        switch (sortKey.value) {
            case 'circuit':
                valA = a.circuit?.name;
                valB = b.circuit?.name;
                break;
            case 'station':
                valA = a.station?.code;
                valB = b.station?.code;
                break;
            case 'sub_section':
                valA = a.sub_section?.name;
                valB = b.sub_section?.name;
                break;
            case 'assigned_to':
                valA = a.assigned_to?.name;
                valB = b.assigned_to?.name;
                break;
            default:
                valA = a[sortKey.value];
                valB = b[sortKey.value];
        }
          
        const dir = sortDir.value === 'asc' ? 1 : -1;
        
        // Handle nulls by sorting them to the bottom
        if (valA == null) return 1 * dir;
        if (valB == null) return -1 * dir;
        if (valA < valB) return -1 * dir;
        if (valA > valB) return 1 * dir;
        return 0;
    });
});


const totalPages = computed(() => Math.ceil(sortedRows.value.length / rowsPerPage.value))
const paginatedRows = computed(() => {
  const start = (currentPage.value - 1) * rowsPerPage.value
  const end = start + rowsPerPage.value
  return sortedRows.value.slice(start, end)
})

// --- Methods ---
function toggleSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'desc' // Default to descending for new sort keys
  }
}







function formatDuration(start, end) {
  if (!start || !end) return '–'
  const diff = new Date(end) - new Date(start)
  if (diff < 0) return '–'
  
  const days = Math.floor(diff / 86400000)
  const hours = Math.floor((diff % 86400000) / 3600000)
  const minutes = Math.round((diff % 3600000) / 60000)

  if (days > 0) return `${days}d ${hours}h ${minutes}m`
  if (hours > 0) return `${hours}h ${minutes}m`
  return `${minutes}m`
}

function formatSplitDate(ts) {
    if (!ts) return { date: '–', time: '' };
    const d = new Date(ts);
    // Date: 10 Dec 2025
    const date = d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    // Time: 24h format e.g. 18:45
    const time = d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', hour12: false });
    return { date, time };
}

const columns = [
  { key: 'fail_id',     label: 'Event ID', sortable: true },
  { key: 'reported_at', label: 'Reported', sortable: true },
  { key: 'resolved_at', label: 'Resolved', sortable: true },
  { key: 'duration',    label: 'Duration', sortable: false, align: 'text-center' },
  { key: 'circuit',     label: 'Circuit', sortable: true },
  { key: 'station',     label: 'Station', sortable: true },
  { key: 'sub_section', label: 'Sub-Section', sortable: true },
  { key: 'assigned_to', label: 'Assigned', sortable: true },
  { key: 'current_status', label: 'Status', sortable: true },
  { key: 'actions',     label: 'Actions', sortable: false, align: 'text-center', width: '120px' },
]

function badgeClasses(status) {
    if (status === 'Resolved') return 'badge-success'
    if (status === 'Active') return 'badge-danger'
    if (status === 'In Progress') return 'badge-warning'
    if (status === 'On Hold') return 'badge-hold'
    return 'badge-neutral'
}

// --- Pagination Methods ---
function goToFirstPage() { currentPage.value = 1 }
function goToLastPage() { currentPage.value = totalPages.value }
function goToNextPage() { if (currentPage.value < totalPages.value) currentPage.value++ }
function goToPreviousPage() { if (currentPage.value > 1) currentPage.value-- }

// --- Export Methods ---
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'
import ExcelJS from 'exceljs'

async function generateExcelBlob(options = {}) {
    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('Logbook');

    worksheet.columns = [
        { header: 'Event ID', key: 'fail_id', width: 15 },
        { header: 'Reported', key: 'reported', width: 15 },
        { header: 'Resolved', key: 'resolved', width: 15 },
        { header: 'Duration', key: 'duration', width: 15 },
        { header: 'Circuit', key: 'circuit', width: 25 },
        { header: 'Station', key: 'station', width: 15 },
        { header: 'Sub-Section', key: 'sub_section', width: 20 },
        { header: 'Assigned', key: 'assigned', width: 20 },
        { header: 'Failure Remark', key: 'remark_fail', width: 30 },
        { header: 'Resolution Remark', key: 'remark_right', width: 30 },
    ];

    // Style header row
    worksheet.getRow(1).font = { bold: true };
    worksheet.getRow(1).alignment = { vertical: 'middle', horizontal: 'center', wrapText: true };

    const rowsToExport = selectedShifts.value.length > 0 ? filteredRows.value : paginatedRows.value;

    // Filter out Information messages if requested
    const finalRows = (options.includeInfo === false) 
        ? rowsToExport.filter(r => r.current_status !== 'Information') 
        : rowsToExport;

    finalRows.forEach(row => {
        // Date formatting: Date \n Time (24h)
        const formatDateTimeCell = (ts) => {
            if (!ts) return '–';
            const d = new Date(ts);
            const date = d.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit', year: 'numeric' });
            const time = d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', hour12: false });
            return `${date}\n${time}`;
        };

        const reportedVal = formatDateTimeCell(row.reported_at);
        const resolvedVal = formatDateTimeCell(row.resolved_at);

        // Circuit formatting: ID \n Name
        const circuitVal = row.circuit ? `${row.circuit.circuit_id}\n${row.circuit.name}` : '–';

        // Event ID formatting: Prefix-Year \n Sequence
        // e.g. ADI-2025-0051 -> ADI-2025 \n 0051
        let failIdVal = row.fail_id;
        const lastHyphenIndex = failIdVal.lastIndexOf('-');
        if (lastHyphenIndex !== -1) {
            failIdVal = `${failIdVal.substring(0, lastHyphenIndex)}\n${failIdVal.substring(lastHyphenIndex + 1)}`;
        }

        const rowData = {
            fail_id: failIdVal,
            reported: reportedVal,
            resolved: resolvedVal,
            duration: formatDuration(row.reported_at, row.resolved_at),
            circuit: circuitVal,
            station: row.station?.code || '–',
            sub_section: row.sub_section?.name || '–',
            assigned: row.assigned_to?.name || '–',
            remark_fail: row.remark_fail || '',
            remark_right: row.remark_right || ''
        };

        const excelRow = worksheet.addRow(rowData);
        
        // Enable text wrap for multiline cells
        excelRow.alignment = { vertical: 'middle', horizontal: 'left', wrapText: true };
        // Center align specific columns
        excelRow.getCell('reported').alignment = { vertical: 'middle', horizontal: 'center', wrapText: true };
        excelRow.getCell('resolved').alignment = { vertical: 'middle', horizontal: 'center', wrapText: true };
        excelRow.getCell('duration').alignment = { vertical: 'middle', horizontal: 'center' };
        
        // Color coding for main row
        let argb = null;
        if (row.current_status === 'Resolved') argb = 'FFD1E7DD';
        else if (row.current_status === 'Active') argb = 'FFF8D7DA';
        else if (row.current_status === 'In Progress') argb = 'FFFFF3CD';
        else if (row.current_status === 'On Hold') argb = 'FFE2E3E5';

        if (argb) {
            excelRow.eachCell((cell) => {
                cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: argb } };
                cell.border = { top: { style: 'thin' }, left: { style: 'thin' }, bottom: { style: 'thin' }, right: { style: 'thin' } };
            });
        } else {
             excelRow.eachCell((cell) => {
                cell.border = { top: { style: 'thin' }, left: { style: 'thin' }, bottom: { style: 'thin' }, right: { style: 'thin' } };
            });
        }
    });

    // Add Footer for Shift Handover
    if (options.handedOverBy || options.takenOverBy) {
        worksheet.addRow([]); // Spacer
        worksheet.addRow([]); // Spacer
        
        const footerRow = worksheet.addRow([
            `Charge Handed Over By: ${options.handedOverBy || '__________'}`, 
            null, null, null, null, null, null,
            `Charge Taken Over By: ${options.takenOverBy || '__________'}`
        ]);
        worksheet.mergeCells(`A${footerRow.number}:D${footerRow.number}`);
        worksheet.mergeCells(`H${footerRow.number}:J${footerRow.number}`);
        footerRow.font = { bold: true };
        footerRow.alignment = { horizontal: 'left' };
    }

    const buffer = await workbook.xlsx.writeBuffer();
    return new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
}

function generatePDFBlob(options = {}) {
    // Landscape orientation
    const doc = new jsPDF('l', 'mm', 'a4');
    const rowsToExport = selectedShifts.value.length > 0 ? filteredRows.value : paginatedRows.value;

    // Filter out Information messages if requested
    const finalRows = (options.includeInfo === false) 
        ? rowsToExport.filter(r => r.current_status !== 'Information') 
        : rowsToExport;

    const tableBody = [];

    const formatDateTimeCell = (ts) => {
        if (!ts) return '–';
        const d = new Date(ts);
        const date = d.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit', year: 'numeric' });
        const time = d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', hour12: false });
        return `${date}\n${time}`;
    };

    finalRows.forEach(row => {
        const reportedVal = formatDateTimeCell(row.reported_at);
        const resolvedVal = formatDateTimeCell(row.resolved_at);
        const circuitVal = row.circuit ? `${row.circuit.circuit_id}\n${row.circuit.name}` : '–';

        let failIdVal = row.fail_id;
        const lastHyphenIndex = failIdVal.lastIndexOf('-');
        if (lastHyphenIndex !== -1) {
            failIdVal = `${failIdVal.substring(0, lastHyphenIndex)}\n${failIdVal.substring(lastHyphenIndex + 1)}`;
        }

        tableBody.push([
            failIdVal,
            reportedVal,
            resolvedVal,
            formatDuration(row.reported_at, row.resolved_at),
            circuitVal,
            row.station?.code || '–',
            row.sub_section?.name || '–',
            row.assigned_to?.name || '–',
            row.remark_fail || '',
            row.remark_right || ''
        ]);
        
        // Note: Row coloring is handled in didParseCell based on row index and data source
    });

    autoTable(doc, {
        head: [['Event ID', 'Reported', 'Resolved', 'Duration', 'Circuit', 'Station', 'Sub-Section', 'Assigned', 'Failure Remark', 'Resolution Remark']],
        body: tableBody,
        styles: { fontSize: 8, valign: 'middle', lineWidth: 0.1, lineColor: [206, 212, 218] },
        headStyles: { fillColor: [41, 128, 185], halign: 'center', lineWidth: 0.1, lineColor: [206, 212, 218] },
        columnStyles: {
            0: { cellWidth: 20 }, // Fail ID
            1: { cellWidth: 22, halign: 'center' }, // Reported
            2: { cellWidth: 22, halign: 'center' }, // Resolved
            3: { cellWidth: 20, halign: 'center' }, // Duration
            4: { cellWidth: 30 }, // Circuit
            5: { cellWidth: 15 }, // Station
            6: { cellWidth: 25 }, // Sub-Section
            7: { cellWidth: 25 }, // Assigned
            8: { cellWidth: 40 }, // Failure Remark
            9: { cellWidth: 40 }, // Resolution Remark
        },
        didParseCell: function(data) {
            if (data.section === 'body') {
                 // Determine status from the original data
                 // autoTable passes data.row.index which corresponds to the index in tableBody
                 // We need to map this back to finalRows
                 const rowIndex = data.row.index;
                 const row = finalRows[rowIndex];
                 
                 if (row) {
                     const status = row.current_status;
                     if (status === 'Resolved') data.cell.styles.fillColor = [209, 231, 221];
                     else if (status === 'Active') data.cell.styles.fillColor = [248, 215, 218];
                     else if (status === 'In Progress') data.cell.styles.fillColor = [255, 243, 205];
                     else if (status === 'On Hold') data.cell.styles.fillColor = [226, 227, 229];
                 }
            }
        }
    });

    // Add Footer for Shift Handover
    if (options.handedOverBy || options.takenOverBy) {
        const finalY = doc.lastAutoTable.finalY + 10;
        doc.setFontSize(10);
        doc.text(`Charge Handed Over By: ${options.handedOverBy || '__________'}`, 14, finalY);
        doc.text(`Charge Taken Over By: ${options.takenOverBy || '__________'}`, 200, finalY);
    }

    return doc.output('blob');
}

async function downloadReports() {
    // console.log('Selected Shifts:', selectedShifts.value);
    if (selectedShifts.value.length > 0) {
        pendingExportAction.value = 'download';
        showExportModal.value = true;
    } else {
        await executeDownload({});
    }
}

async function executeDownload(options) {
    const dateStr = new Date().toISOString().slice(0, 10);
    
    // Download Excel
    const excelBlob = await generateExcelBlob(options);
    const excelLink = document.createElement('a');
    excelLink.href = URL.createObjectURL(excelBlob);
    excelLink.download = `logbook_export_${dateStr}.xlsx`;
    excelLink.click();

    // Download PDF
    const pdfBlob = generatePDFBlob(options);
    const pdfLink = document.createElement('a');
    pdfLink.href = URL.createObjectURL(pdfBlob);
    pdfLink.download = `logbook_export_${dateStr}.pdf`;
    pdfLink.click();
}

const sendingReports = ref(false);

async function sendReports() {
    if (selectedShifts.value.length > 0) {
        pendingExportAction.value = 'send';
        showExportModal.value = true;
    } else {
        await executeSend({});
    }
}

async function executeSend(options) {
    sendingReports.value = true;
    try {
        const dateStr = new Date().toISOString().slice(0, 10);
        const excelBlob = await generateExcelBlob(options);
        const pdfBlob = generatePDFBlob(options);

        const formData = new FormData();
        formData.append('files', excelBlob, `logbook_export_${dateStr}.xlsx`);
        formData.append('files', pdfBlob, `logbook_export_${dateStr}.pdf`);

        const response = await fetch('/api/v1/reports/send/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: formData,
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Failed to send reports');
        }

        ui.pushToast({ type: 'success', title: 'Sent', message: 'Reports sent to Telegram.' });
    } catch (err) {
        ui.pushToast({ type: 'error', title: 'Error', message: err.message });
    } finally {
        sendingReports.value = false;
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

async function confirmExport() {
    showExportModal.value = false;
    const options = { ...exportOptions.value };
    
    if (pendingExportAction.value === 'download') {
        await executeDownload(options);
    } else if (pendingExportAction.value === 'send') {
        await executeSend(options);
    }
    pendingExportAction.value = null;
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex justify-between items-center px-1">
      <router-link to="/logbook/new" class="btn btn-primary">New Log Entry</router-link>
      <div class="flex items-center gap-3">
          <label class="flex items-center gap-2 cursor-pointer select-none text-sm font-medium">
            <input type="checkbox" v-model="autoRefresh" class="checkbox checkbox-primary w-4 h-4" />
            <span>Auto-refresh</span>
          </label>
          <button @click="resetFilters" class="btn btn-outline gap-2" title="Reset Filters">
              <RotateCcw class="w-4 h-4" />
              <span>Reset</span>
          </button>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="sticky top-0 z-10 bg-app py-4 card !overflow-visible">
       <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-8 gap-2">
        <input v-model="query" :disabled="selectedShifts.length > 0" type="search" placeholder="Search anything..." class="h-11 w-full rounded-lg border-app bg-card text-app px-3 text-sm disabled:opacity-50" />
        <SearchSelect v-model="selectedCircuits" :options="circuitOptions" placeholder="Filter by Circuit" multiple :disabled="selectedShifts.length > 0" />
        <SearchSelect v-model="selectedSections" :options="sectionOptions" placeholder="Filter by Section" multiple :disabled="selectedShifts.length > 0" />
        <SearchSelect v-model="selectedStations" :options="stationOptions" placeholder="Filter by Station" multiple :disabled="selectedShifts.length > 0" />
        <SearchSelect v-model="selectedSupervisors" :options="supervisorOptions" placeholder="Filter by Supervisor" multiple :disabled="selectedShifts.length > 0" />
        <SearchSelect v-model="selectedStatuses" :options="statusOptions" placeholder="Filter by Status" multiple :disabled="selectedShifts.length > 0" />
        <input v-model="selectedDate" type="date" class="h-11 w-full rounded-lg border-app bg-card text-app px-3 text-sm" placeholder="Filter by Date" />
        <SearchSelect v-model="selectedShifts" :options="shiftOptions" placeholder="Filter by Shift" multiple />
      </div>
    </div>

    <div v-if="error" class="card p-6 text-center text-red-500">{{ error }}</div>

    <div class="card p-4">
    <DataTable
        :columns="columns"
        :rows="paginatedRows"
        :sort-key="sortKey"
        :sort-dir="sortDir"
        :loading="loading"
        @sort="toggleSort"
        @rowclick="openDetails"
    >
        <template #body-cell-comp="{ row, column }">
        <tr :class="{ 'opacity-60': row.is_archived }">
            <component :is="column.cell" :row="row" />
        </tr>
        </template>
        <template #reported_at="{ row }">
            <div class="text-xs">
                <div class="font-medium whitespace-nowrap">{{ formatSplitDate(row.reported_at).date }}</div>
                <div class="text-muted">{{ formatSplitDate(row.reported_at).time }}</div>
            </div>
        </template>
        <template #resolved_at="{ row }">
             <div class="text-xs" v-if="row.resolved_at">
                <div class="font-medium whitespace-nowrap">{{ formatSplitDate(row.resolved_at).date }}</div>
                <div class="text-muted">{{ formatSplitDate(row.resolved_at).time }}</div>
            </div>
            <span v-else>–</span>
        </template>
        <template #duration="{ row }">{{ formatDuration(row.reported_at, row.resolved_at) }}</template>
        <template #circuit="{ row }">
            <div class="text-xs">
                <div class="font-medium whitespace-nowrap">{{ row.circuit?.circuit_id || '–' }}</div>
                <div class="whitespace-nowrap font-medium" style="color: #E1AA36;">{{ row.circuit?.name || '' }}</div>
            </div>
        </template>
        <template #station="{ row }">{{ row.station?.code || '–' }}</template>
        <template #sub_section="{ row }">{{ row.sub_section?.name || '–' }}</template>
        <template #assigned_to="{ row }">{{ row.assigned_to?.name || '–' }}</template>
        <template #current_status="{ row }"><span class="badge" :class="badgeClasses(row.current_status)">{{ row.current_status }}</span></template>
        <template #actions="{ row }">
        <div class="flex items-center justify-center gap-1.5">
            <button class="btn-ghost border-app rounded-md hover-primary p-2" title="Notify" @click.stop="onNotify(row)"><Bell class="w-4 h-4" /></button>
            <button class="btn-ghost border-app rounded-md hover-primary p-2" title="Edit" @click.stop="editFailure(row)"><Pencil class="w-4 h-4" /></button>
            <button class="btn-ghost border-app rounded-md hover-primary p-2" title="Archive" @click.stop="openArchiveModal(row)"><Trash2 class="w-4 h-4" /></button>
        </div>
        </template>
    </DataTable>
    </div>
    
    <!-- Pagination Controls -->
    <div class="mt-4 flex items-center justify-between">
    <div class="flex items-center justify-center gap-2 p-2 rounded-lg">
        <button @click="downloadReports" class="btn btn-outline btn-sm gap-2"><FileDown class="w-4 h-4" /><span>Export</span></button>
        <button @click="sendReports" :disabled="sendingReports" class="btn btn-outline btn-sm gap-2">
        <Spinner v-if="sendingReports" class="w-4 h-4" />
        <Send v-else class="w-4 h-4" />
        <span>Send Logs</span>
        </button>
    </div>
    <div class="flex items-center justify-end gap-2 p-2 rounded-lg">
        <button @click="goToFirstPage" :disabled="currentPage === 1" class="btn-ghost p-2" title="First"><ChevronsLeft class="w-4 h-4" /></button>
        <button @click="goToPreviousPage" :disabled="currentPage === 1" class="btn-ghost p-2" title="Previous"><ChevronLeft class="w-4 h-4" /></button>
        <span class="text-sm text-muted">Page {{ currentPage }} of {{ totalPages }}</span>
        <button @click="goToNextPage" :disabled="currentPage >= totalPages" class="btn-ghost p-2" title="Next"><ChevronRight class="w-4 h-4" /></button>
        <button @click="goToLastPage" :disabled="currentPage >= totalPages" class="btn-ghost p-2" title="Last"><ChevronsRight class="w-4 h-4" /></button>
    </div>
    </div>

    <FailureDetailsDrawer v-model="drawerOpen" :item="activeItem" />

    <!-- Archive Confirmation Modal -->
    <div v-if="isArchiveModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div class="bg-card rounded-lg p-6 shadow-xl w-full max-w-md">
        <h3 class="text-lg font-bold">Confirm Archival</h3>
        <p class="mt-2">
          Are you sure you want to archive failure log
          <span class="font-semibold">{{ failureToArchive?.fail_id }}</span>?
        </p>
        <div class="mt-4">
          <label for="archiveReason" class="block text-sm font-medium text-app">Reason for archiving</label>
          <textarea v-model="archiveReason" id="archiveReason" rows="3" class="field-textarea mt-1"></textarea>
        </div>
        <div class="mt-6 flex justify-end gap-3">
          <button @click="isArchiveModalOpen = false" class="btn btn-outline">Cancel</button>
          <button @click="confirmArchive" class="btn btn-danger">Archive</button>
        </div>
      </div>
    </div>


    <!-- Export Options Modal -->
    <div v-if="showExportModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div class="bg-card rounded-lg p-6 shadow-xl w-full max-w-md">
        <h3 class="text-lg font-bold mb-4">Export Options</h3>
        
        <div class="space-y-4">
            <div class="flex items-center gap-2">
                <input type="checkbox" id="includeInfo" v-model="exportOptions.includeInfo" class="checkbox checkbox-primary" />
                <label for="includeInfo" class="cursor-pointer select-none">Include Information Messages?</label>
            </div>

            <div>
                <label class="block text-sm font-medium mb-1">Charge Handed Over By</label>
                <input v-model="exportOptions.handedOverBy" type="text" class="field-input w-full" placeholder="Name" />
            </div>

            <div>
                <label class="block text-sm font-medium mb-1">Charge Taken Over By</label>
                <input v-model="exportOptions.takenOverBy" type="text" class="field-input w-full" placeholder="Name" />
            </div>
        </div>

        <div class="mt-6 flex justify-end gap-3">
          <button @click="showExportModal = false" class="btn btn-outline">Cancel</button>
          <button @click="confirmExport" class="btn btn-primary">
              {{ pendingExportAction === 'send' ? 'Send' : 'Export' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>