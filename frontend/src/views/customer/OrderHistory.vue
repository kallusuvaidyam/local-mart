<template>
  <div>
    <Navbar />
    <div class="max-w-3xl mx-auto px-4 py-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">My Orders</h1>
      <LoadingSpinner v-if="loading" />
      <div v-else-if="orders.length === 0" class="text-center py-16 text-gray-500">
        <p class="text-4xl mb-3">📦</p>
        <p class="mb-4">No orders yet.</p>
        <router-link to="/products" class="btn-primary">Start Shopping</router-link>
      </div>
      <div v-else class="space-y-4">
        <template v-for="(order, idx) in orders" :key="order.id">
          <div class="card p-4 hover:shadow-md transition">
            <div class="flex items-start justify-between mb-2">
              <div>
                <p class="font-bold text-gray-900">Order #{{ order.id }}</p>
                <p class="text-xs text-gray-500">{{ formatDate(order.ordered_at) }}</p>
              </div>
              <span :class="`badge-${order.status}`">{{ formatStatus(order.status) }}</span>
            </div>
            <p class="text-sm text-gray-600 mb-2">{{ order.item_count || order.items?.length }} item(s) · ₹{{ order.total_amount }}</p>
            <div class="flex justify-between items-center">
              <p class="text-xs text-gray-500 truncate">{{ order.snap_block_name }}</p>
              <router-link :to="`/orders/${order.id}`" class="text-sm text-blue-600 font-medium hover:underline">View Details →</router-link>
            </div>
          </div>
          <!-- Ad Slot 7: In-feed ad after every 3 orders (uncomment when ads are ready)
          <AdSlot v-if="(idx + 1) % 3 === 0 && idx < orders.length - 1" :label="`Order Feed Ad — ${Math.floor((idx+1)/3)}`" height="70px" />
          -->
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '@/components/common/Navbar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import AdSlot from '@/components/common/AdSlot.vue'
import api from '@/services/api'

const orders = ref([])
const loading = ref(true)

function formatDate(d) {
  return d ? new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : ''
}
function formatStatus(s) {
  return { pending: 'Pending', confirmed: 'Confirmed', out_for_delivery: 'Out for Delivery', delivered: 'Delivered', cancelled: 'Cancelled' }[s] || s
}

onMounted(async () => {
  try {
    const res = await api.get('/orders')
    orders.value = res.data.orders
  } finally { loading.value = false }
})
</script>
