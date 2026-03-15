<template>
  <div>
    <Navbar />
    <div class="max-w-5xl mx-auto px-4 py-8">
      <LoadingSpinner v-if="loading" />
      <div v-else-if="product" class="grid md:grid-cols-2 gap-8">
        <!-- Image -->
        <div class="aspect-square bg-gray-100 rounded-xl overflow-hidden">
          <img
            :src="
              product.image_url ||
              'https://via.placeholder.com/500x500?text=No+Image'
            "
            :alt="product.name"
            class="w-full h-full object-cover"
            @error="
              (e) =>
                (e.target.src =
                  'https://via.placeholder.com/500x500?text=No+Image')
            "
          />
        </div>

        <!-- Info -->
        <div>
          <p class="text-sm text-blue-600 font-medium mb-1">
            {{ product.category?.name }}
          </p>
          <h1 class="text-2xl font-bold text-gray-900 mb-2">
            {{ product.name }}
          </h1>
          <p v-if="product.unit" class="text-sm text-gray-500 mb-3">
            {{ product.unit }}
          </p>

          <div class="flex items-center gap-3 mb-4">
            <span class="text-3xl font-bold text-gray-900"
              >₹{{ product.price }}</span
            >
            <span
              v-if="product.mrp && product.mrp > product.price"
              class="text-lg text-gray-400 line-through"
              >₹{{ product.mrp }}</span
            >
            <span
              v-if="discount > 0"
              class="bg-green-100 text-green-700 text-sm font-semibold px-2 py-0.5 rounded"
              >{{ discount }}% OFF</span
            >
          </div>

          <div v-if="reviews.total > 0" class="flex items-center gap-2 mb-4">
            <div class="flex text-yellow-400">
              <span v-for="i in 5" :key="i">{{
                i <= Math.round(reviews.average_rating) ? "★" : "☆"
              }}</span>
            </div>
            <span class="text-sm text-gray-600"
              >{{ reviews.average_rating }} ({{ reviews.total }} reviews)</span
            >
          </div>

          <p
            v-if="product.description"
            class="text-gray-600 text-sm leading-relaxed mb-1"
          >
            {{ product.description }}
          </p>
          <p
            v-if="product.return_policy"
            class="text-sm text-pink-700 leading-relaxed mb-1"
          >
            {{ product.return_policy }} days return policy.
          </p>

          <p
            v-if="product.stock_qty === 0"
            class="text-red-500 font-semibold mb-4"
          >
            Out of stock
          </p>
          <p v-else class="text-green-600 text-sm font-medium mb-4">
            ✓ {{ product.stock_qty }} in stock
          </p>

          <div v-if="product.stock_qty > 0" class="mb-6">
            <div class="flex items-center gap-3 mb-3">
              <div class="flex items-center border border-gray-300 rounded-lg">
                <button
                  @click="qty > 1 && qty--"
                  class="px-3 py-2 text-lg hover:bg-gray-50"
                >
                  −
                </button>
                <span class="px-4 py-2 font-semibold">{{ qty }}</span>
                <button
                  @click="qty < product.stock_qty && qty++"
                  class="px-3 py-2 text-lg hover:bg-gray-50"
                >
                  +
                </button>
              </div>
              <span class="text-sm text-gray-500"
                >{{ product.stock_qty }} available</span
              >
            </div>

            <div class="flex flex-col gap-2">
              <button
                @click="buyNow"
                :disabled="buyingNow"
                class="w-full bg-orange-500 hover:bg-orange-600 disabled:opacity-50 text-white font-bold py-3 rounded-xl transition"
              >
                {{ buyingNow ? "Please wait..." : "⚡ Buy Now" }}
              </button>
              <button
                @click="addToCart"
                :disabled="adding"
                class="w-full btn-primary py-3 rounded-xl"
              >
                {{ adding ? "Adding..." : "🛒 Add to Cart" }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Ad Slot 4: Before Reviews -->
      <AdSlot v-if="product" label="Product Detail — 300×250" height="120px" wrap-class="mt-8" />

      <div v-if="product" class="mt-6">
        <h2 class="text-lg font-bold text-gray-900 mb-4">Customer Reviews</h2>
        <div v-if="reviews.reviews?.length === 0" class="text-gray-500 text-sm">
          No reviews yet. Be the first!
        </div>
        <div v-else class="space-y-4">
          <div v-for="r in reviews.reviews" :key="r.id" class="card p-4">
            <div class="flex items-center gap-3 mb-2">
              <div class="flex text-yellow-400 text-sm">
                <span v-for="i in 5" :key="i">{{
                  i <= r.rating ? "★" : "☆"
                }}</span>
              </div>
              <span class="font-medium text-sm">{{ r.user_name }}</span>
              <span class="text-xs text-gray-400">{{
                formatDate(r.created_at)
              }}</span>
            </div>
            <p v-if="r.comment" class="text-sm text-gray-700">
              {{ r.comment }}
            </p>
          </div>
        </div>
      </div>

      <!-- Ad Slot 5: After Reviews (Sponsored Products area) -->
      <AdSlot v-if="product" label="Sponsored Products — 728×90" height="100px" wrap-class="mt-8" />

      <div v-if="!loading && !product" class="text-center py-16 text-gray-500">
        <p class="text-4xl mb-3">😕</p>
        <p>Product not found.</p>
        <router-link to="/products" class="btn-primary mt-4 inline-block"
          >Browse Products</router-link
        >
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import Navbar from "@/components/common/Navbar.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import AdSlot from "@/components/common/AdSlot.vue";
import { useAuthStore } from "@/stores/auth";
import { useCartStore } from "@/stores/cart";
import { useToastStore } from "@/stores/toast";
import api from "@/services/api";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const cart = useCartStore();
const toast = useToastStore();

const product = ref(null);
const reviews = ref({ total: 0, average_rating: 0, reviews: [] });
const loading = ref(true);
const adding = ref(false);
const buyingNow = ref(false);
const qty = ref(1);

const discount = computed(() => {
  if (!product.value?.mrp || product.value.mrp <= product.value.price) return 0;
  return Math.round(
    ((product.value.mrp - product.value.price) / product.value.mrp) * 100,
  );
});

function formatDate(d) {
  return d
    ? new Date(d).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
      })
    : "";
}

async function addToCart() {
  if (!auth.isLoggedIn) return router.push("/login");
  adding.value = true;
  try {
    await cart.addItem(product.value.id, qty.value);
    toast.success("Added to cart!");
  } catch (e) {
    toast.error(e.response?.data?.detail || "Failed to add to cart");
  } finally {
    adding.value = false;
  }
}

async function buyNow() {
  if (!auth.isLoggedIn) return router.push("/login");
  buyingNow.value = true;
  try {
    await cart.addItem(product.value.id, qty.value);
    router.push({ path: "/checkout", query: { buynow: product.value.id } });
  } catch (e) {
    toast.error(e.response?.data?.detail || "Failed, please try again");
  } finally {
    buyingNow.value = false;
  }
}

onMounted(async () => {
  try {
    const [pRes, rRes] = await Promise.all([
      api.get(`/products/${route.params.slug}`),
      api.get(`/reviews/product/${route.params.slug}`).catch(() => ({
        data: { total: 0, average_rating: 0, reviews: [] },
      })),
    ]);
    product.value = pRes.data;
    reviews.value = rRes.data;
    console.log("product.value", product.value);
  } catch {
    product.value = null;
  } finally {
    loading.value = false;
  }
});
</script>
