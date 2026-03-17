<template>
  <div>
    <Navbar />

    <!-- Hero Banner -->
    <div
      class="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-14 px-4"
    >
      <div class="max-w-4xl mx-auto text-center">
        <h1 class="text-3xl md:text-5xl font-bold mb-4">
          Your Neighbourhood Store
        </h1>
        <p class="text-blue-100 text-lg mb-8">
          Fresh groceries & daily essentials delivered to your doorstep within
          3–4 blocks
        </p>
        <div class="flex gap-3 justify-center">
          <router-link
            to="/products"
            class="bg-white text-blue-600 font-bold px-6 py-3 rounded-xl hover:bg-blue-50 transition"
          >
            Shop Now →
          </router-link>
        </div>
      </div>
    </div>

    <!-- Ad Slot 1: After Hero (uncomment when ads are ready)
    <div class="max-w-5xl mx-auto px-4 pt-6">
      <AdSlot label="Home Top Banner — 728×90" height="90px" wrap-class="" />
    </div>
    -->

    <!-- Categories -->
    <div class="max-w-7xl mx-auto px-4 py-10">
      <h2 class="text-xl font-bold text-gray-900 mb-5">Shop by Category</h2>
      <div v-if="loadingCats" class="flex gap-3 overflow-x-auto pb-2">
        <div
          v-for="i in 6"
          :key="i"
          class="flex-shrink-0 w-20 h-20 bg-gray-200 rounded-xl animate-pulse"
        ></div>
      </div>
      <div v-else class="grid grid-cols-4 md:grid-cols-8 gap-3">
        <router-link
          v-for="cat in categories"
          :key="cat.id"
          :to="`/products?category=${cat.slug}`"
          class="flex flex-col items-center gap-2 p-3 bg-white rounded-xl border border-gray-100 hover:border-blue-300 hover:shadow-sm transition text-center"
        >
          <img
            v-if="cat.image_url"
            :src="cat.image_url"
            :alt="cat.name"
            class="w-10 h-10 object-cover rounded-lg"
            @error="e => e.target.style.display='none'"
          />
          <span v-else class="text-2xl">{{ getCatEmoji(cat.name) }}</span>
          <span class="text-xs font-medium text-gray-700 leading-tight">{{
            cat.name
          }}</span>
        </router-link>
      </div>
    </div>

    <!-- Featured Products -->
    <div class="max-w-7xl mx-auto px-4 pb-12">
      <div class="flex items-center justify-between mb-5">
        <h2 class="text-xl font-bold text-gray-900">Featured Products</h2>
        <router-link
          to="/products"
          class="text-blue-600 text-sm font-medium hover:underline"
          >View all →</router-link
        >
      </div>
      <LoadingSpinner v-if="loadingProducts" />
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <ProductCard v-for="p in featured" :key="p.id" :product="p" />
      </div>
      <div
        v-if="!loadingProducts && featured.length === 0"
        class="text-center text-gray-500 py-10"
      >
        No featured products yet.
      </div>
    </div>

    <!-- Ad Slot 2: Before Why Us (uncomment when ads are ready)
    <div class="max-w-5xl mx-auto px-4 pb-4">
      <AdSlot label="Home Mid Banner — 728×90" height="90px" wrap-class="" />
    </div>
    -->

    <!-- Why us -->
    <div class="bg-white border-t border-gray-100 py-10">
      <div
        class="max-w-4xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-6 text-center"
      >
        <div v-for="item in perks" :key="item.title">
          <div class="text-3xl mb-2">{{ item.icon }}</div>
          <p class="font-semibold text-gray-900 text-sm">{{ item.title }}</p>
          <p class="text-xs text-gray-500">{{ item.desc }}</p>
        </div>
      </div>
    </div>

    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import Navbar from "@/components/common/Navbar.vue";
import ProductCard from "@/components/product/ProductCard.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import AdSlot from "@/components/common/AdSlot.vue";
import Footer from "@/components/common/Footer.vue";
import api from "@/services/api";

const categories = ref([]);
const featured = ref([]);
const loadingCats = ref(true);
const loadingProducts = ref(true);

const perks = [
  { icon: "🚴", title: "Fast Delivery", desc: "Within your block" },
  { icon: "🛡️", title: "Fresh Products", desc: "Quality guaranteed" },
  { icon: "💰", title: "Best Prices", desc: "No hidden charges" },
  { icon: "📞", title: "24/7 Support", desc: "Always here to help" },
];

const catEmojis = {
  Vegetables: "🥦",
  Fruits: "🍎",
  Dairy: "🥛",
  Bakery: "🍞",
  Beverages: "🥤",
  Snacks: "🍿",
  Household: "🧹",
  "Personal Care": "🧴",
};
function getCatEmoji(name) {
  return catEmojis[name] || "📦";
}

onMounted(async () => {
  try {
    const [catRes, prodRes] = await Promise.all([
      api.get("/categories"),
      api.get("/products/featured"),
    ]);
    categories.value = catRes.data;
    featured.value = prodRes.data;
  } finally {
    loadingCats.value = false;
    loadingProducts.value = false;
  }
});
</script>
