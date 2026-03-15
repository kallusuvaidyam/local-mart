<template>
  <div class="min-h-screen bg-gray-50 flex">
    <AdminSidebar />
    <main class="flex-1 p-6">
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Orders</h1>
          <p class="text-xs text-gray-400 mt-0.5">
            Auto-refreshes every 30s
            <span v-if="lastRefreshed" class="ml-1"
              >— Last updated {{ lastRefreshed }}</span
            >
          </p>
        </div>

        <!-- Live indicator + manual refresh -->
        <div class="flex items-center gap-3">
          <div
            class="flex items-center gap-1.5 text-xs text-green-600 font-medium"
          >
            <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            Live
          </div>
          <button @click="activeTab === 'returns' ? fetchReturns() : fetchOrders()" class="btn-secondary text-sm py-1.5">
            🔄 Refresh
          </button>
        </div>
      </div>

      <!-- New order alert banner -->
      <transition name="slide-down">
        <div
          v-if="newOrderAlert"
          class="mb-4 bg-blue-600 text-white px-4 py-3 rounded-xl flex items-center justify-between shadow-lg"
        >
          <div class="flex items-center gap-3">
            <span class="text-xl">🛒</span>
            <div>
              <p class="font-bold text-sm">New order received!</p>
              <p class="text-xs text-blue-100">
                {{ newOrderAlert }} new pending order(s) waiting for
                confirmation
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="filterAndDismiss"
              class="bg-white text-blue-600 text-xs font-bold px-3 py-1.5 rounded-lg hover:bg-blue-50"
            >
              View Pending
            </button>
            <button
              @click="newOrderAlert = null"
              class="text-blue-200 hover:text-white text-lg leading-none"
            >
              ✕
            </button>
          </div>
        </div>
      </transition>

      <!-- Main Tabs: Orders / Returns -->
      <div class="flex gap-1 mb-4 border-b border-gray-200">
        <button
          @click="activeTab = 'orders'"
          :class="[
            'px-5 py-2 text-sm font-semibold border-b-2 transition',
            activeTab === 'orders'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700',
          ]"
        >
          Orders
        </button>
        <button
          @click="activeTab = 'returns'; fetchReturns()"
          :class="[
            'px-5 py-2 text-sm font-semibold border-b-2 transition flex items-center gap-1.5',
            activeTab === 'returns'
              ? 'border-orange-500 text-orange-600'
              : 'border-transparent text-gray-500 hover:text-gray-700',
          ]"
        >
          Returns
          <span
            v-if="pendingReturnsCount > 0"
            class="bg-orange-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center"
          >
            {{ pendingReturnsCount > 9 ? "9+" : pendingReturnsCount }}
          </span>
        </button>
      </div>

      <!-- ── ORDERS TAB ── -->
      <template v-if="activeTab === 'orders'">
        <!-- Filter Tabs -->
        <div class="flex gap-2 mb-4 overflow-x-auto pb-1">
          <button
            v-for="s in statuses"
            :key="s.value"
            @click="activeFilter = s.value; fetchOrders();"
            :class="[
              'px-4 py-1.5 rounded-full text-sm font-medium flex-shrink-0 transition flex items-center gap-1.5',
              activeFilter === s.value
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-600 border hover:border-blue-300',
            ]"
          >
            {{ s.label }}
            <span
              v-if="s.value === 'pending' && pendingCount > 0"
              class="bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center"
            >
              {{ pendingCount > 9 ? "9+" : pendingCount }}
            </span>
          </button>
        </div>

        <!-- Orders Table -->
        <LoadingSpinner v-if="loading" />
        <div v-else class="card overflow-hidden">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b">
              <tr class="text-left text-gray-500">
                <th class="px-4 py-3">Order</th>
                <th class="px-4 py-3">Customer</th>
                <th class="px-4 py-3">Area</th>
                <th class="px-4 py-3">Amount</th>
                <th class="px-4 py-3">Payment</th>
                <th class="px-4 py-3">Status</th>
                <th class="px-4 py-3">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr
                v-for="order in orders"
                :key="order.id"
                :class="[
                  'hover:bg-gray-50 transition',
                  order.status === 'pending' ? 'bg-yellow-50/40' : '',
                ]"
              >
                <td class="px-4 py-3">
                  <p class="font-bold text-gray-900">#{{ order.id }}</p>
                  <p class="text-xs text-gray-500">
                    {{ formatDate(order.ordered_at) }}
                  </p>
                  <p class="text-xs text-gray-400">
                    {{ order.item_count }} item(s)
                  </p>
                </td>

                <td class="px-4 py-3">
                  <p class="font-medium text-gray-900">{{ order.user_name }}</p>
                  <p class="text-xs text-gray-500">📞 {{ order.user_phone }}</p>
                </td>

                <td class="px-4 py-3">
                  <p class="text-xs font-medium text-gray-900">
                    {{ order.snap_block_name }}
                  </p>
                  <p class="text-xs text-gray-500">{{ order.snap_zone_name }}</p>
                </td>

                <td class="px-4 py-3">
                  <p class="font-bold text-gray-900">₹{{ order.total_amount }}</p>
                </td>

                <td class="px-4 py-3">
                  <span
                    v-if="order.payment_method === 'online'"
                    class="bg-green-100 text-green-700 text-xs font-medium px-2 py-0.5 rounded-full"
                  >
                    💳 Paid
                  </span>
                  <span
                    v-else
                    class="bg-yellow-100 text-yellow-700 text-xs font-medium px-2 py-0.5 rounded-full"
                  >
                    💵 COD
                  </span>
                </td>

                <td class="px-4 py-3">
                  <span :class="`badge-${order.status}`">
                    {{ statusConfig[order.status]?.icon }}
                    {{ statusConfig[order.status]?.label }}
                  </span>
                </td>

                <td class="px-4 py-3">
                  <div
                    v-if="order.allowed_next && order.allowed_next.length > 0"
                    class="flex flex-col gap-1.5"
                  >
                    <button
                      v-for="next in order.allowed_next"
                      :key="next"
                      @click="updateStatus(order.id, next)"
                      :disabled="updating === order.id"
                      :class="[
                        'text-xs font-semibold px-3 py-1.5 rounded-lg transition whitespace-nowrap disabled:opacity-50',
                        next === 'cancelled'
                          ? 'bg-red-100 text-red-600 hover:bg-red-200 border border-red-200'
                          : 'bg-blue-600 text-white hover:bg-blue-700',
                      ]"
                    >
                      <span v-if="updating === order.id">⏳ Wait...</span>
                      <span v-else>{{ statusConfig[next]?.action }}</span>
                    </button>
                  </div>

                  <p v-else class="text-xs text-gray-400 italic">
                    {{ order.status === 'delivered' ? '✅ Completed' : '❌ Cancelled' }}
                  </p>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="orders.length === 0" class="text-center py-14 text-gray-400">
            <p class="text-3xl mb-2">📭</p>
            <p>No orders found.</p>
          </div>
        </div>

        <p v-if="totalOrders > 0" class="text-xs text-gray-400 mt-3 text-right">
          Showing {{ orders.length }} of {{ totalOrders }} orders
        </p>
      </template>

      <!-- ── RETURNS TAB ── -->
      <template v-if="activeTab === 'returns'">
        <!-- Return Filter Tabs -->
        <div class="flex gap-2 mb-4 overflow-x-auto pb-1">
          <button
            v-for="s in returnStatuses"
            :key="s.value"
            @click="returnFilter = s.value; fetchReturns();"
            :class="[
              'px-4 py-1.5 rounded-full text-sm font-medium flex-shrink-0 transition',
              returnFilter === s.value
                ? 'bg-orange-500 text-white'
                : 'bg-white text-gray-600 border hover:border-orange-300',
            ]"
          >
            {{ s.label }}
          </button>
        </div>

        <LoadingSpinner v-if="loadingReturns" />
        <div v-else class="card overflow-hidden">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b">
              <tr class="text-left text-gray-500">
                <th class="px-4 py-3">Return / Order</th>
                <th class="px-4 py-3">Customer</th>
                <th class="px-4 py-3">Reason</th>
                <th class="px-4 py-3">Amount</th>
                <th class="px-4 py-3">Status</th>
                <th class="px-4 py-3">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr
                v-for="ret in returns"
                :key="ret.id"
                :class="[
                  'hover:bg-gray-50 transition',
                  ret.status === 'return_requested' ? 'bg-orange-50/40' : '',
                ]"
              >
                <td class="px-4 py-3">
                  <p class="font-bold text-gray-900">Return #{{ ret.id }}</p>
                  <p class="text-xs text-blue-600">Order #{{ ret.order_id }}</p>
                  <p class="text-xs text-gray-400">{{ formatDate(ret.created_at) }}</p>
                </td>

                <td class="px-4 py-3">
                  <p class="font-medium text-gray-900">{{ ret.user_name }}</p>
                  <p class="text-xs text-gray-500">📞 {{ ret.user_phone }}</p>
                </td>

                <td class="px-4 py-3 max-w-[180px]">
                  <p class="text-xs text-gray-700 line-clamp-2">{{ ret.reason }}</p>
                </td>

                <td class="px-4 py-3">
                  <p class="font-bold text-gray-900">₹{{ ret.total_amount }}</p>
                </td>

                <td class="px-4 py-3">
                  <span :class="`badge-${ret.status}`">
                    {{ returnConfig[ret.status]?.icon }}
                    {{ returnConfig[ret.status]?.label }}
                  </span>
                </td>

                <td class="px-4 py-3">
                  <div
                    v-if="ret.allowed_next && ret.allowed_next.length > 0"
                    class="flex flex-col gap-1.5"
                  >
                    <button
                      v-for="next in ret.allowed_next"
                      :key="next"
                      @click="updateReturnStatus(ret.id, next)"
                      :disabled="updatingReturn === ret.id"
                      :class="[
                        'text-xs font-semibold px-3 py-1.5 rounded-lg transition whitespace-nowrap disabled:opacity-50',
                        next === 'return_rejected'
                          ? 'bg-red-100 text-red-600 hover:bg-red-200 border border-red-200'
                          : 'bg-orange-500 text-white hover:bg-orange-600',
                      ]"
                    >
                      <span v-if="updatingReturn === ret.id">⏳ Wait...</span>
                      <span v-else>{{ returnConfig[next]?.action }}</span>
                    </button>
                  </div>

                  <p v-else class="text-xs text-gray-400 italic">
                    {{ ret.status === 'return_completed' ? '✅ Done' : '❌ Rejected' }}
                  </p>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="returns.length === 0" class="text-center py-14 text-gray-400">
            <p class="text-3xl mb-2">📦</p>
            <p>No return requests found.</p>
          </div>
        </div>

        <p v-if="totalReturns > 0" class="text-xs text-gray-400 mt-3 text-right">
          Showing {{ returns.length }} of {{ totalReturns }} returns
        </p>
      </template>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import AdminSidebar from "@/components/admin/Sidebar.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import { useToastStore } from "@/stores/toast";
import api from "@/services/api";

const toast = useToastStore();

// Orders state
const orders = ref([]);
const loading = ref(true);
const updating = ref(null);
const activeFilter = ref("");
const totalOrders = ref(0);
const pendingCount = ref(0);
const lastRefreshed = ref("");
const newOrderAlert = ref(null);

// Returns state
const returns = ref([]);
const loadingReturns = ref(false);
const updatingReturn = ref(null);
const returnFilter = ref("");
const totalReturns = ref(0);
const pendingReturnsCount = ref(0);

// Tabs
const activeTab = ref("orders");

let pollingTimer = null;
let previousPendingCount = 0;

// ── Status configs ────────────────────────────────────────
const statusConfig = {
  pending:          { label: "Pending",          icon: "⏳", action: null },
  confirmed:        { label: "Confirmed",         icon: "✅", action: "✅ Confirm Order" },
  out_for_delivery: { label: "Out for Delivery",  icon: "🚴", action: "🚴 Out for Delivery" },
  delivered:        { label: "Delivered",          icon: "🎉", action: "🎉 Mark Delivered" },
  cancelled:        { label: "Cancelled",          icon: "❌", action: "❌ Cancel Order" },
};

const returnConfig = {
  return_requested: { label: "Requested",       icon: "🔄", action: null },
  return_approved:  { label: "Approved",        icon: "✅", action: "✅ Approve Return" },
  return_rejected:  { label: "Rejected",        icon: "❌", action: "❌ Reject Return" },
  return_picked_up: { label: "Picked Up",       icon: "📦", action: "📦 Mark Picked Up" },
  return_completed: { label: "Completed",       icon: "🎉", action: "🎉 Mark Completed" },
};

const statuses = [
  { value: "",                 label: "All" },
  { value: "pending",          label: "Pending" },
  { value: "confirmed",        label: "Confirmed" },
  { value: "out_for_delivery", label: "Out for Delivery" },
  { value: "delivered",        label: "Delivered" },
  { value: "cancelled",        label: "Cancelled" },
];

const returnStatuses = [
  { value: "",                label: "All" },
  { value: "return_requested", label: "Requested" },
  { value: "return_approved",  label: "Approved" },
  { value: "return_picked_up", label: "Picked Up" },
  { value: "return_completed", label: "Completed" },
  { value: "return_rejected",  label: "Rejected" },
];

function formatDate(d) {
  return d
    ? new Date(d).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "";
}

// ── Fetch Orders ─────────────────────────────────────────
async function fetchOrders(silent = false) {
  if (!silent) loading.value = true;
  try {
    const params = { limit: 100 };
    if (activeFilter.value) params.status = activeFilter.value;
    const res = await api.get("/admin/orders", { params });
    orders.value = res.data.orders;
    totalOrders.value = res.data.total;

    const now = new Date();
    lastRefreshed.value = now.toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
    });
  } finally {
    if (!silent) loading.value = false;
  }
}

// ── Fetch Returns ─────────────────────────────────────────
async function fetchReturns(silent = false) {
  if (!silent) loadingReturns.value = true;
  try {
    const params = { limit: 100 };
    if (returnFilter.value) params.status = returnFilter.value;
    const res = await api.get("/admin/returns", { params });
    returns.value = res.data.returns;
    totalReturns.value = res.data.total;
  } finally {
    if (!silent) loadingReturns.value = false;
  }
}

// ── Fetch Pending Count ──────────────────────────────────
async function fetchPendingCount() {
  try {
    const [ordersRes, returnsRes] = await Promise.all([
      api.get("/admin/orders", { params: { status: "pending", limit: 1 } }),
      api.get("/admin/returns", { params: { status: "return_requested", limit: 1 } }),
    ]);

    const currentPending = ordersRes.data.total;
    pendingCount.value = currentPending;
    pendingReturnsCount.value = returnsRes.data.total;

    if (previousPendingCount > 0 && currentPending > previousPendingCount) {
      const newCount = currentPending - previousPendingCount;
      newOrderAlert.value = newCount;

      if (Notification.permission === "granted") {
        new Notification("🛒 New Order on Local Mart!", {
          body: `${newCount} new order(s) waiting for confirmation`,
          icon: "/vite.svg",
        });
      }

      await fetchOrders(true);
    }

    previousPendingCount = currentPending;
  } catch {}
}

// ── Update Order Status ──────────────────────────────────
async function updateStatus(orderId, newStatus) {
  updating.value = orderId;
  try {
    await api.patch(`/admin/orders/${orderId}/status`, { status: newStatus });
    toast.success(`Order #${orderId} → ${statusConfig[newStatus]?.label}`);
    await Promise.all([fetchOrders(true), fetchPendingCount()]);
  } catch (e) {
    toast.error(e.response?.data?.detail || "Failed to update status");
  } finally {
    updating.value = null;
  }
}

// ── Update Return Status ─────────────────────────────────
async function updateReturnStatus(returnId, newStatus) {
  updatingReturn.value = returnId;
  try {
    await api.patch(`/admin/returns/${returnId}/status`, { status: newStatus });
    toast.success(`Return #${returnId} → ${returnConfig[newStatus]?.label}`);
    await Promise.all([fetchReturns(true), fetchPendingCount()]);
  } catch (e) {
    toast.error(e.response?.data?.detail || "Failed to update return status");
  } finally {
    updatingReturn.value = null;
  }
}

function filterAndDismiss() {
  activeTab.value = "orders";
  activeFilter.value = "pending";
  fetchOrders();
  newOrderAlert.value = null;
}

function startPolling() {
  if ("Notification" in window && Notification.permission === "default") {
    Notification.requestPermission();
  }

  pollingTimer = setInterval(async () => {
    await fetchPendingCount();
  }, 30000);
}

onMounted(async () => {
  await Promise.all([fetchOrders(), fetchPendingCount()]);
  startPolling();
});

onUnmounted(() => {
  if (pollingTimer) clearInterval(pollingTimer);
});
</script>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}
.slide-down-enter-from {
  transform: translateY(-20px);
  opacity: 0;
}
.slide-down-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}
</style>
