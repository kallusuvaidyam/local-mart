<template>
  <div>
    <Navbar />
    <div class="max-w-3xl mx-auto px-4 py-8">
      <router-link
        to="/orders"
        class="text-blue-600 text-sm hover:underline mb-4 inline-block"
        >&larr; Back to Orders</router-link
      >

      <LoadingSpinner v-if="loading" />
      <div v-else-if="order" class="space-y-4">
        <!-- Header -->
        <div class="card p-5">
          <div class="flex items-start justify-between">
            <div>
              <h1 class="text-xl font-bold text-gray-900">
                Order #{{ order.id }}
              </h1>
              <p class="text-sm text-gray-500 mt-1">
                Placed on {{ formatDate(order.ordered_at) }}
              </p>
            </div>
            <span :class="`badge-${effectiveStatus} text-base`">{{
              formatStatus(effectiveStatus)
            }}</span>
          </div>

          <!-- Unified Timeline -->
          <div class="mt-6 overflow-x-auto pb-2">
            <!-- Row 1: Order flow -->
            <div class="flex items-center min-w-[340px]">
              <template v-for="(step, i) in orderSteps" :key="step.key">
                <div class="flex flex-col items-center flex-shrink-0" style="min-width:52px">
                  <div :class="['w-10 h-10 rounded-full flex items-center justify-center text-[15px] border-[2.5px] transition-all',
                    isOrderStepDone(step.key)
                      ? 'bg-blue-600 text-white border-blue-600 shadow-md shadow-blue-200'
                      : 'bg-gray-50 text-gray-400 border-gray-300']">
                    {{ step.icon }}
                  </div>
                  <span class="text-[11px] mt-1.5 text-center leading-tight whitespace-nowrap"
                    :class="isOrderStepDone(step.key) ? 'text-blue-700 font-semibold' : 'text-gray-400'">
                    {{ step.label }}
                  </span>
                </div>
                <div v-if="i < orderSteps.length - 1"
                  :class="['flex-1 h-1 mx-1.5 rounded-full min-w-[20px] transition-all',
                    isOrderStepDone(step.key) ? 'bg-blue-500' : 'bg-gray-200']">
                </div>
              </template>
            </div>

            <!-- Return Status (separate card-like section below timeline) -->
            <template v-if="order.return_request">
              <!-- Return Rejected -->
              <div v-if="order.return_request.status === 'return_rejected'"
                class="mt-5 flex items-center gap-3 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
                <span class="text-lg">&#10060;</span>
                <div>
                  <p class="text-sm font-medium text-red-700">Return request was rejected</p>
                  <p v-if="order.return_request.admin_note" class="text-xs text-red-600 mt-0.5">
                    Admin: {{ order.return_request.admin_note }}
                  </p>
                </div>
              </div>

              <!-- Return progress -->
              <div v-else class="mt-5 bg-orange-50/50 border border-orange-100 rounded-xl p-4">
                <div class="flex items-center justify-between mb-3">
                  <h3 class="text-sm font-bold text-gray-800">Return Progress</h3>
                  <span :class="`badge-${order.return_request.status}`">
                    {{ formatStatus(order.return_request.status) }}
                  </span>
                </div>
                <div class="flex items-center min-w-[280px]">
                  <template v-for="(step, i) in returnSteps" :key="step.key">
                    <div class="flex flex-col items-center flex-shrink-0" style="min-width:48px">
                      <div :class="['w-9 h-9 rounded-full flex items-center justify-center text-sm border-[2.5px] transition-all',
                        isReturnStepDone(step.key)
                          ? 'bg-orange-500 text-white border-orange-500 shadow-md shadow-orange-200'
                          : 'bg-white text-gray-400 border-gray-300']">
                        {{ step.icon }}
                      </div>
                      <span class="text-[10px] mt-1 text-center leading-tight whitespace-nowrap"
                        :class="isReturnStepDone(step.key) ? 'text-orange-700 font-semibold' : 'text-gray-400'">
                        {{ step.label }}
                      </span>
                    </div>
                    <div v-if="i < returnSteps.length - 1"
                      :class="['flex-1 h-1 mx-1 rounded-full min-w-[14px] transition-all',
                        isReturnStepDone(step.key) ? 'bg-orange-400' : 'bg-gray-200']">
                    </div>
                  </template>
                </div>
              </div>

              <!-- Return info -->
              <div class="mt-3 text-sm text-gray-600 bg-gray-50 rounded-lg px-4 py-3 space-y-1">
                <p><span class="font-medium text-gray-800">Your reason:</span> {{ order.return_request.reason }}</p>
                <p v-if="order.return_request.admin_note && order.return_request.status !== 'return_rejected'">
                  <span class="font-medium text-gray-800">Admin note:</span> {{ order.return_request.admin_note }}
                </p>
                <p class="text-xs text-gray-400">Requested on {{ formatDate(order.return_request.created_at) }}</p>
              </div>
            </template>
          </div>
        </div>

        <!-- Items + price & return btn on right -->
        <div class="card p-5">
          <h2 class="font-bold text-gray-900 mb-4">Items Ordered</h2>
          <div class="space-y-3">
            <div v-for="item in order.items" :key="item.id" class="flex gap-3">
              <ProductImage
                :src="item.product_image"
                :alt="item.product_name"
                container-class="w-14 h-14 rounded-lg flex-shrink-0"
              />
              <div class="flex-1 min-w-0">
                <p class="font-medium text-sm">{{ item.product_name }}</p>
                <p class="text-xs text-gray-500">
                  &#8377;{{ item.unit_price }} &times; {{ item.quantity }}
                </p>
              </div>
              <div class="flex flex-col items-end flex-shrink-0">
                <p class="font-bold text-lg">&#8377;{{ item.line_total }}</p>
                <!-- Return btn: only if delivered, no return yet, and within return window -->
                <template v-if="order.status === 'delivered' && !order.return_request && returnWindowOpen">
                  <button
                    @click="showReturnForm = true"
                    class="mt-1 text-xs font-semibold px-3 py-1 rounded-lg bg-orange-50 text-orange-600 hover:bg-orange-100 border border-orange-200 transition whitespace-nowrap"
                  >
                    &#x1F504; Return
                  </button>
                  <p class="text-[10px] text-gray-400 mt-0.5">{{ returnCountdown }}</p>
                </template>
                <!-- Window expired -->
                <p v-else-if="order.status === 'delivered' && !order.return_request && !returnWindowOpen"
                  class="text-[10px] text-red-400 mt-1">Return window expired</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Return Request Form (inline) -->
        <div v-if="showReturnForm && !order.return_request && returnWindowOpen" class="card p-5 border-2 border-orange-200">
          <h2 class="font-bold text-gray-900 mb-1">Request a Return</h2>
          <p class="text-xs text-gray-500 mb-3">Please tell us why you want to return this order.</p>
          <textarea
            v-model="returnReason"
            rows="3"
            placeholder="e.g. Wrong item delivered, product damaged, etc."
            class="input-field text-sm resize-none mb-3"
            :disabled="submittingReturn"
          ></textarea>
          <div class="flex gap-2">
            <button
              @click="submitReturn"
              :disabled="!returnReason.trim() || submittingReturn"
              class="btn-primary text-sm py-1.5 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ submittingReturn ? "Submitting..." : "Submit Return Request" }}
            </button>
            <button
              @click="showReturnForm = false; returnReason = ''"
              :disabled="submittingReturn"
              class="btn-secondary text-sm py-1.5"
            >
              Cancel
            </button>
          </div>
        </div>

        <!-- Ad Slot 6: Between Items & Delivery -->
        <AdSlot label="Order Detail — Banner" height="80px" />

        <!-- Delivery Address -->
        <div class="card p-5">
          <h2 class="font-bold text-gray-900 mb-2">Delivery Details</h2>
          <p class="text-sm font-medium text-blue-600">
            {{ order.snap_block_name }} &mdash; {{ order.snap_zone_name }}
          </p>
          <p class="text-sm text-gray-700 mt-1">{{ parsedAddress }}</p>
          <p v-if="order.notes" class="text-sm text-gray-500 mt-2 italic">
            Note: {{ order.notes }}
          </p>
        </div>

        <!-- Review section (if delivered) -->
        <div v-if="order.status === 'delivered'" class="card p-5">
          <h2 class="font-bold text-gray-900 mb-4">Rate Your Order</h2>
          <div
            v-for="item in order.items"
            :key="'review-' + item.id"
            class="mb-5 pb-5 border-b last:border-b-0 last:mb-0 last:pb-0"
          >
            <template v-if="!reviewForm[item.product_id]?.submitted">
              <p class="text-sm font-medium text-gray-700 mb-2">
                {{ item.product_name }}
              </p>
              <div
                class="flex gap-1 text-2xl mb-2"
                :class="
                  reviewForm[item.product_id]?.submitting
                    ? 'opacity-50 pointer-events-none'
                    : 'cursor-pointer'
                "
              >
                <span
                  v-for="i in 5"
                  :key="i"
                  @click="setRating(item.product_id, i)"
                  :class="
                    (reviewForm[item.product_id]?.rating || 0) >= i
                      ? 'text-yellow-400'
                      : 'text-gray-300'
                  "
                  >&#9733;</span
                >
              </div>
              <textarea
                v-model="reviewForm[item.product_id].comment"
                rows="2"
                placeholder="Share your experience..."
                class="input-field text-sm resize-none mb-2"
                :disabled="reviewForm[item.product_id]?.submitting"
              ></textarea>
              <button
                @click="submitReview(item.product_id)"
                :disabled="
                  !reviewForm[item.product_id]?.rating ||
                  reviewForm[item.product_id]?.submitting
                "
                class="btn-primary text-sm py-1.5 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{
                  reviewForm[item.product_id]?.submitting
                    ? "Submitting..."
                    : "Submit Review"
                }}
              </button>
            </template>

            <div
              v-else
              class="flex items-center gap-3 bg-green-50 border border-green-200 rounded-lg px-4 py-3"
            >
              <span class="text-lg">&#9989;</span>
              <div>
                <p class="text-sm font-medium text-green-700">
                  {{ item.product_name }}
                </p>
                <p class="text-xs text-green-600">
                  Review submitted! Thank you.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import Navbar from "@/components/common/Navbar.vue";
import ProductImage from "@/components/common/ProductImage.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import AdSlot from "@/components/common/AdSlot.vue";
import { useToastStore } from "@/stores/toast";
import api from "@/services/api";

const route = useRoute();
const toast = useToastStore();
const order = ref(null);
const loading = ref(true);
const reviewForm = ref({});
const now = ref(Date.now());
let countdownTimer = null;

// Return state
const showReturnForm = ref(false);
const returnReason = ref("");
const submittingReturn = ref(false);

const orderSteps = [
  { key: "pending", icon: "\u{1F4CB}", label: "Ordered" },
  { key: "confirmed", icon: "\u2705", label: "Confirmed" },
  { key: "out_for_delivery", icon: "\u{1F6B4}", label: "On the way" },
  { key: "delivered", icon: "\u{1F389}", label: "Delivered" },
];
const orderStatusOrder = ["pending", "confirmed", "out_for_delivery", "delivered"];

const returnSteps = [
  { key: "return_requested", icon: "\u{1F504}", label: "Requested" },
  { key: "return_approved",  icon: "\u2705", label: "Approved" },
  { key: "return_picked_up", icon: "\u{1F4E6}", label: "Picked Up" },
  { key: "return_completed", icon: "\u{1F389}", label: "Completed" },
];
const returnStatusOrder = ["return_requested", "return_approved", "return_picked_up", "return_completed"];

const effectiveStatus = computed(() => {
  if (order.value?.return_request) return order.value.return_request.status;
  return order.value?.status || "pending";
});

// Return window logic
const returnDeadline = computed(() => {
  if (!order.value?.delivered_at) return null;
  const days = order.value.return_window_days ?? 2;
  return new Date(order.value.delivered_at).getTime() + days * 24 * 60 * 60 * 1000;
});

const returnWindowOpen = computed(() => {
  if (!returnDeadline.value) return false;
  return now.value < returnDeadline.value;
});

const returnCountdown = computed(() => {
  if (!returnDeadline.value) return "";
  const diff = returnDeadline.value - now.value;
  if (diff <= 0) return "";
  const hrs = Math.floor(diff / (1000 * 60 * 60));
  const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  if (hrs >= 24) {
    const d = Math.floor(hrs / 24);
    const h = hrs % 24;
    return `${d}d ${h}h left`;
  }
  return `${hrs}h ${mins}m left`;
});

function isOrderStepDone(key) {
  if (order.value?.status === "cancelled") return false;
  return orderStatusOrder.indexOf(order.value?.status) >= orderStatusOrder.indexOf(key);
}

function isReturnStepDone(key) {
  const current = order.value?.return_request?.status;
  if (!current || current === "return_rejected") return false;
  return returnStatusOrder.indexOf(current) >= returnStatusOrder.indexOf(key);
}


function formatDate(d) {
  return d ? new Date(d).toLocaleString("en-IN") : "";
}

function formatStatus(s) {
  return (
    {
      pending: "Pending",
      confirmed: "Confirmed",
      out_for_delivery: "Out for Delivery",
      delivered: "Delivered",
      cancelled: "Cancelled",
      return_requested: "Return Requested",
      return_approved:  "Return Approved",
      return_picked_up: "Return Picked Up",
      return_completed: "Return Completed",
      return_rejected:  "Return Rejected",
    }[s] || s
  );
}

const parsedAddress = computed(() => {
  try {
    const a = JSON.parse(order.value?.snap_address || "{}");
    return [
      a.address_line1,
      a.address_line2,
      a.landmark ? `Near ${a.landmark}` : "",
      a.pincode,
    ]
      .filter(Boolean)
      .join(", ");
  } catch {
    return "";
  }
});

function setRating(productId, rating) {
  reviewForm.value[productId] = { ...reviewForm.value[productId], rating };
}

async function submitReview(productId) {
  const form = reviewForm.value[productId];
  if (!form?.rating || form.submitting) return;

  reviewForm.value[productId].submitting = true;
  try {
    await api.post("/reviews", {
      product_id: productId,
      order_id: order.value.id,
      rating: form.rating,
      comment: form.comment,
    });
    reviewForm.value[productId] = { submitted: true };
    toast.success("Review submitted!");
  } catch (e) {
    reviewForm.value[productId].submitting = false;
    toast.error(e.response?.data?.detail || "Failed to submit review");
  }
}

async function submitReturn() {
  if (!returnReason.value.trim() || submittingReturn.value) return;
  submittingReturn.value = true;
  try {
    const res = await api.post(`/returns/${order.value.id}`, {
      reason: returnReason.value.trim(),
    });
    order.value.return_request = res.data.return;
    showReturnForm.value = false;
    returnReason.value = "";
    toast.success("Return request submitted!");
  } catch (e) {
    toast.error(e.response?.data?.detail || "Failed to submit return request");
  } finally {
    submittingReturn.value = false;
  }
}

onMounted(async () => {
  try {
    const res = await api.get(`/orders/${route.params.id}`);
    order.value = res.data;

    res.data.items.forEach((item) => {
      reviewForm.value[item.product_id] = {
        rating: 0,
        comment: "",
        submitted: item.already_reviewed ?? false,
      };
    });

    // Live countdown timer for return window
    countdownTimer = setInterval(() => {
      now.value = Date.now();
    }, 60000);
  } finally {
    loading.value = false;
  }
});

onUnmounted(() => {
  if (countdownTimer) clearInterval(countdownTimer);
});
</script>
