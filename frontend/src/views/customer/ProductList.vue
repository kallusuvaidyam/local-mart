<template>
  <div>
    <Navbar />
    <div class="max-w-7xl mx-auto px-4 py-6">

      <!-- Mobile filter toggle btn -->
      <button
        @click="showFilters = !showFilters"
        class="md:hidden flex items-center gap-2 mb-4 px-4 py-2 rounded-xl border border-gray-200 bg-white text-sm font-medium text-gray-700 shadow-sm active:bg-gray-50"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/>
        </svg>
        Filters
        <span v-if="activeFilterCount" class="bg-blue-600 text-white text-[10px] font-bold rounded-full w-5 h-5 flex items-center justify-center">
          {{ activeFilterCount }}
        </span>
        <svg :class="['w-4 h-4 ml-auto transition-transform', showFilters ? 'rotate-180' : '']" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
        </svg>
      </button>

      <div class="flex flex-col md:flex-row gap-6">
        <!-- Sidebar Filters -->
        <aside
          :class="[
            'w-full md:w-56 flex-shrink-0 transition-all duration-300 overflow-hidden',
            showFilters ? 'max-h-[600px] opacity-100' : 'max-h-0 md:max-h-none opacity-0 md:opacity-100',
          ]"
        >
          <div class="card p-4 sticky top-20">
            <div class="flex items-center justify-between mb-3">
              <h3 class="font-bold text-gray-900">Filters</h3>
              <button
                v-if="activeFilterCount"
                @click="resetFilters"
                class="text-xs text-red-500 hover:text-red-600 font-medium"
              >
                Clear all
              </button>
            </div>

            <!-- Category -->
            <div class="mb-4">
              <button
                @click="showCategory = !showCategory"
                class="w-full flex items-center justify-between text-sm font-medium text-gray-700 py-1"
              >
                Category
                <svg :class="['w-4 h-4 transition-transform', showCategory ? 'rotate-180' : '']" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
                </svg>
              </button>
              <div v-show="showCategory" class="mt-1 space-y-0.5 max-h-52 overflow-y-auto">
                <button
                  @click="setCategory('')"
                  :class="[
                    'w-full text-left text-sm px-2.5 py-1.5 rounded-lg transition-colors',
                    !filters.category
                      ? 'bg-blue-50 text-blue-600 font-medium'
                      : 'text-gray-600 hover:bg-gray-50',
                  ]"
                >
                  All
                </button>
                <button
                  v-for="cat in categories"
                  :key="cat.id"
                  @click="setCategory(cat.slug)"
                  :class="[
                    'w-full text-left text-sm px-2.5 py-1.5 rounded-lg transition-colors',
                    filters.category === cat.slug
                      ? 'bg-blue-50 text-blue-600 font-medium'
                      : 'text-gray-600 hover:bg-gray-50',
                  ]"
                >
                  {{ cat.name }}
                </button>
              </div>
            </div>

            <hr class="mb-3" />

            <!-- Price Range -->
            <div class="mb-4">
              <button
                @click="showPrice = !showPrice"
                class="w-full flex items-center justify-between text-sm font-medium text-gray-700 py-1"
              >
                Price Range
                <svg :class="['w-4 h-4 transition-transform', showPrice ? 'rotate-180' : '']" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
                </svg>
              </button>
              <div v-show="showPrice" class="mt-2">
                <div class="flex gap-2">
                  <input
                    v-model.number="filters.min_price"
                    type="number"
                    placeholder="Min"
                    class="input-field text-sm py-1.5"
                    @keyup.enter="applyFilters"
                  />
                  <span class="text-gray-300 self-center">—</span>
                  <input
                    v-model.number="filters.max_price"
                    type="number"
                    placeholder="Max"
                    class="input-field text-sm py-1.5"
                    @keyup.enter="applyFilters"
                  />
                </div>
              </div>
            </div>

            <button @click="applyFilters" class="btn-primary w-full text-sm py-2">
              Apply Filters
            </button>
          </div>
        </aside>

        <!-- Product Grid -->
        <div class="flex-1">
          <div class="flex items-center justify-between mb-4">
            <h1 class="text-lg font-bold text-gray-900">
              {{
                filters.search
                  ? `Results for "${filters.search}"`
                  : "All Products"
              }}
              <span class="text-sm font-normal text-gray-500 ml-2"
                >({{ total }} items)</span
              >
            </h1>
          </div>

          <!-- Active filter chips -->
          <div v-if="activeFilterCount" class="flex flex-wrap gap-2 mb-4">
            <span v-if="filters.category"
              class="inline-flex items-center gap-1 bg-blue-50 text-blue-700 text-xs font-medium px-2.5 py-1 rounded-full">
              {{ categoryName }}
              <button @click="setCategory('')" class="hover:text-blue-900">&times;</button>
            </span>
            <span v-if="filters.min_price || filters.max_price"
              class="inline-flex items-center gap-1 bg-blue-50 text-blue-700 text-xs font-medium px-2.5 py-1 rounded-full">
              &#8377;{{ filters.min_price || 0 }} — &#8377;{{ filters.max_price || '∞' }}
              <button @click="filters.min_price = ''; filters.max_price = ''; applyFilters()" class="hover:text-blue-900">&times;</button>
            </span>
            <span v-if="filters.search"
              class="inline-flex items-center gap-1 bg-blue-50 text-blue-700 text-xs font-medium px-2.5 py-1 rounded-full">
              "{{ filters.search }}"
              <button @click="filters.search = ''; applyFilters()" class="hover:text-blue-900">&times;</button>
            </span>
          </div>

          <LoadingSpinner v-if="loading" />
          <div
            v-else-if="products.length === 0"
            class="text-center text-gray-500 py-16"
          >
            <p class="text-4xl mb-3">&#128269;</p>
            <p>No products found. Try different filters.</p>
          </div>
          <div
            v-else
            class="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-3 gap-4"
          >
            <template v-for="(p, idx) in products" :key="p.id">
              <ProductCard :product="p" />
              <!-- Ad Slot 3: In-feed ad after every 6 products (uncomment when ads are ready)
              <div v-if="(idx + 1) % 6 === 0 && idx < products.length - 1" class="col-span-2 sm:col-span-2 lg:col-span-3">
                <AdSlot :label="`In-Feed Ad — Row ${Math.floor((idx+1)/6)}`" height="80px" wrap-class="my-1" />
              </div>
              -->
            </template>
          </div>

          <!-- Pagination -->
          <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-8">
            <button
              v-for="p in totalPages"
              :key="p"
              @click="goToPage(p)"
              :class="[
                'w-9 h-9 rounded-lg text-sm font-medium',
                page === p
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border border-gray-200 hover:border-blue-300',
              ]"
            >
              {{ p }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import Navbar from "@/components/common/Navbar.vue";
import ProductCard from "@/components/product/ProductCard.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import AdSlot from "@/components/common/AdSlot.vue";
import api from "@/services/api";

const route = useRoute();
const router = useRouter();
const products = ref([]);
const categories = ref([]);
const total = ref(0);
const totalPages = ref(1);
const page = ref(1);
const loading = ref(true);

// Filter panel toggles
const showFilters = ref(false);
const showCategory = ref(true);
const showPrice = ref(true);

const filters = ref({
  category: route.query.category || "",
  search: route.query.search || "",
  min_price: route.query.min_price || "",
  max_price: route.query.max_price || "",
});

const activeFilterCount = computed(() => {
  let count = 0;
  if (filters.value.category) count++;
  if (filters.value.min_price || filters.value.max_price) count++;
  if (filters.value.search) count++;
  return count;
});

const categoryName = computed(() => {
  const cat = categories.value.find(c => c.slug === filters.value.category);
  return cat?.name || filters.value.category;
});

function setCategory(slug) {
  filters.value.category = slug;
  page.value = 1;
  fetchProducts();
}

async function fetchProducts() {
  loading.value = true;
  try {
    const params = { page: page.value, limit: 20 };
    if (filters.value.category) params.category = filters.value.category;
    if (filters.value.search) params.search = filters.value.search;
    if (filters.value.min_price) params.min_price = filters.value.min_price;
    if (filters.value.max_price) params.max_price = filters.value.max_price;
    const res = await api.get("/products", { params });
    products.value = res.data.products;
    total.value = res.data.total;
    totalPages.value = res.data.pages;
  } finally {
    loading.value = false;
  }
}

function applyFilters() {
  page.value = 1;
  fetchProducts();
}
function resetFilters() {
  filters.value = { category: "", search: "", min_price: "", max_price: "" };
  page.value = 1;
  fetchProducts();
}
function goToPage(p) {
  page.value = p;
  fetchProducts();
}

watch(
  () => route.query,
  (q) => {
    filters.value.search = q.search || "";
    filters.value.category = q.category || "";
    fetchProducts();
  },
);

onMounted(async () => {
  const catRes = await api.get("/categories");
  categories.value = catRes.data;
  fetchProducts();
});
</script>
