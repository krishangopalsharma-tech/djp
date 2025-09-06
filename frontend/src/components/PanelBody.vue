<script setup>
import BarChart from '@/components/BarChart.vue'
import LineChart from '@/components/LineChart.vue'
import PieChart from '@/components/PieChart.vue'
import DoughnutChart from '@/components/DoughnutChart.vue'
import RecentFailures from '@/components/RecentFailures.vue'
import { getCssVar, withAlpha } from '@/lib/theme'
import FailureBySeverityCard from '@/components/analytics/FailureBySeverityCard.vue'

const props = defineProps({
  panel: { type: Object, required: true },
  state: { type: Object, required: true },
  data:  { type: Object, required: true },
  chartOptions: { type: Object, required: true },
})
</script>

<template>
  <div class="h-full w-full p-3">
    <!-- Table -->
    <div v-if="state.type==='table'" class="h-full overflow-auto">
      <!-- Aggregation tables -->
      <table v-if="panel.kind!=='recent'" class="min-w-full text-sm">
        <thead>
          <tr class="bg-gray-50">
            <th class="px-3 py-2 text-left">Label</th>
            <th class="px-3 py-2 text-right">Value</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(v,i) in (data.datasets?.[0]?.data || [])"
            :key="i"
            class="border-t"
          >
            <td class="px-3 py-2">{{ data.labels?.[i] }}</td>
            <td class="px-3 py-2 text-right">{{ v }}</td>
          </tr>
          <tr v-if="!(data.labels?.length)" class="border-t">
            <td colspan="2" class="px-3 py-6 text-center text-gray-500">No data</td>
          </tr>
        </tbody>
      </table>

      <!-- Recent failures table -->
      <RecentFailures
        v-else
        :items="data.recent || []"
        :show-toolbar="false"
        :show-bottom-actions="false"
        :show-row-actions="true"
        :loading="false"
        storage-key="rf-analytics"
      />
    </div>

    <!-- Charts -->
    <!-- Special: Failure by Severity card -->
    <div v-if="panel.kind==='failureSeverity' && state.type==='bar'" class="h-full">
      <FailureBySeverityCard :range="state.range" :records="data.records || []" :severity="state.severity || 'all'" />
    </div>
    
    <div v-else-if="state.type==='bar'" class="h-full">
      <BarChart
        :data="{
          labels: data.labels,
          datasets: [{
            ...data.datasets?.[0],
          }]
        }"
        :options="chartOptions"
      />
    </div>

    <div v-else-if="state.type==='line'" class="h-full">
      <LineChart
        :data="{
          labels: data.labels,
          datasets: [{
            ...data.datasets?.[0],
            fill: true,
            tension: 0.3,
            backgroundColor: withAlpha(getCssVar('--slate-gray', '#6c757d'), 0.2),
            borderColor: getCssVar('--slate-gray', '#6c757d')
          }]
        }"
        :options="chartOptions"
      />
    </div>

    <div v-else-if="state.type==='pie'" class="h-full">
      <PieChart
        :data="{ labels: data.labels, datasets: [{ ...data.datasets?.[0] }] }"
        :options="chartOptions"
      />
    </div>

    <div v-else-if="state.type==='doughnut'" class="h-full">
      <DoughnutChart
        :data="{ labels: data.labels, datasets: [{ ...data.datasets?.[0] }] }"
        :options="{ ...chartOptions, cutout: '60%' }"
      />
    </div>

    <!-- Fallback -->
    <div v-else class="h-full flex items-center justify-center text-sm text-gray-500">
      No content.
    </div>
  </div>
</template>
