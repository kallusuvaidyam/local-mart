<template>
  <div class="min-h-screen bg-gray-50 flex">
    <AdminSidebar />
    <main class="flex-1 p-6">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold text-gray-900">Products</h1>
        <button @click="openForm()" class="btn-primary">+ Add Product</button>
      </div>

      <!-- Modal Form -->
      <div
        v-if="showForm"
        class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4"
      >
        <div
          class="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto p-6"
        >
          <h2 class="font-bold text-lg mb-4">
            {{ editing ? "Edit Product" : "Add Product" }}
          </h2>
          <form @submit.prevent="saveProduct" class="space-y-3">
            <input
              v-model="form.name"
              placeholder="Product Name *"
              required
              class="input-field"
            />
            <select v-model="form.category_id" required class="input-field">
              <option value="">Select Category *</option>
              <option v-for="c in categories" :key="c.id" :value="c.id">
                {{ c.name }}
              </option>
            </select>
            <div class="grid grid-cols-2 gap-2">
              <input
                v-model="form.price"
                type="number"
                step="0.01"
                placeholder="Price *"
                required
                class="input-field"
              />
              <input
                v-model="form.mrp"
                type="number"
                step="0.01"
                placeholder="MRP (optional)"
                class="input-field"
              />
            </div>
            <div class="grid grid-cols-2 gap-2">
              <input
                v-model="form.stock_qty"
                type="number"
                placeholder="Stock Qty"
                class="input-field"
              />
              <input
                v-model="form.unit"
                placeholder="Unit (e.g. 500g)"
                class="input-field"
              />
              <input
                v-model="form.return_policy"
                type="number"
                placeholder="Return Policy"
                class="input-field"
              />
            </div>
            <textarea
              v-model="form.description"
              rows="2"
              placeholder="Description"
              class="input-field resize-none"
            ></textarea>
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-1"
                >Product Image</label
              >
              <input
                type="file"
                accept="image/*"
                @change="(e) => (imageFile = e.target.files[0])"
                class="text-sm w-full"
              />
              <img
                v-if="form.image_url"
                :src="form.image_url"
                class="mt-2 h-20 w-20 object-cover rounded"
              />
            </div>
            <label class="flex items-center gap-2 text-sm">
              <input type="checkbox" v-model="form.is_featured" /> Featured
              product
            </label>
            <p v-if="formError" class="text-red-500 text-sm">{{ formError }}</p>
            <div class="flex gap-2 pt-2">
              <button
                type="submit"
                :disabled="saving"
                class="btn-primary flex-1"
              >
                {{ saving ? "Saving..." : "Save" }}
              </button>
              <button
                type="button"
                @click="showForm = false"
                class="btn-secondary flex-1"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Product Table -->
      <LoadingSpinner v-if="loading" />
      <div v-else class="card overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b">
            <tr class="text-left text-gray-500">
              <th class="px-4 py-3">Product</th>
              <th class="px-4 py-3">Category</th>
              <th class="px-4 py-3">Price</th>
              <th class="px-4 py-3">Stock</th>
              <th class="px-4 py-3">Status</th>
              <th class="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="p in products" :key="p.id" class="hover:bg-gray-50">
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <img
                    :src="
                      p.image_url || 'https://via.placeholder.com/40x40?text=?'
                    "
                    class="w-10 h-10 object-cover rounded"
                  />
                  <div>
                    <p class="font-medium text-gray-900">{{ p.name }}</p>
                    <p v-if="p.unit" class="text-xs text-gray-500">
                      {{ p.unit }}
                    </p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3 text-gray-600">{{ p.category?.name }}</td>
              <td class="px-4 py-3 font-semibold">₹{{ p.price }}</td>
              <td class="px-4 py-3">
                <span
                  :class="p.stock_qty > 0 ? 'text-green-600' : 'text-red-500'"
                  class="font-medium"
                  >{{ p.stock_qty }}</span
                >
              </td>
              <td class="px-4 py-3">
                <span
                  :class="p.is_active ? 'badge-confirmed' : 'badge-cancelled'"
                  >{{ p.is_active ? "Active" : "Inactive" }}</span
                >
              </td>
              <td class="px-4 py-3">
                <div class="flex gap-2">
                  <button
                    @click="openForm(p)"
                    class="text-blue-600 text-xs hover:underline"
                  >
                    Edit
                  </button>
                  <button
                    @click="toggleProduct(p)"
                    :class="p.is_active ? 'text-red-500' : 'text-green-600'"
                    class="text-xs hover:underline"
                  >
                    {{ p.is_active ? "Deactivate" : "Activate" }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import AdminSidebar from "@/components/admin/Sidebar.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import { useToastStore } from "@/stores/toast";
import api from "@/services/api";

const toast = useToastStore();
const products = ref([]);
const categories = ref([]);
const loading = ref(true);
const showForm = ref(false);
const saving = ref(false);
const formError = ref("");
const editing = ref(null);
const imageFile = ref(null);
const form = ref({
  name: "",
  category_id: "",
  price: "",
  mrp: "",
  stock_qty: 0,
  unit: "",
  return_policy: 2,
  description: "",
  is_featured: false,
  image_url: "",
});

function openForm(p = null) {
  editing.value = p;
  imageFile.value = null;
  formError.value = "";
  form.value = p
    ? {
        name: p.name,
        category_id: p.category_id,
        price: p.price,
        mrp: p.mrp || "",
        stock_qty: p.stock_qty,
        unit: p.unit || "",
        return_policy: p.return_policy || 2,
        description: p.description || "",
        is_featured: p.is_featured,
        image_url: p.image_url,
      }
    : {
        name: "",
        category_id: "",
        price: "",
        mrp: "",
        stock_qty: 0,
        unit: "",
        return_policy: 2,
        description: "",
        is_featured: false,
        image_url: "",
      };
  showForm.value = true;
}

async function saveProduct() {
  saving.value = true;
  formError.value = "";
  try {
    const fd = new FormData();
    Object.entries(form.value).forEach(([k, v]) => {
      if (k !== "image_url" && v !== "") fd.append(k, v);
    });
    if (imageFile.value) fd.append("image", imageFile.value);

    if (editing.value)
      await api.put(`/products/${editing.value.id}`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
    else
      await api.post("/products", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });

    toast.success(editing.value ? "Product updated!" : "Product added!");
    showForm.value = false;
    await fetchProducts();
  } catch (e) {
    formError.value = e.response?.data?.detail || "Failed to save product";
  } finally {
    saving.value = false;
  }
}

async function toggleProduct(p) {
  await api.put(
    `/products/${p.id}`,
    { is_active: !p.is_active },
    { headers: { "Content-Type": "multipart/form-data" } },
  );
  await fetchProducts();
}

async function fetchProducts() {
  const res = await api.get("/products", { params: { limit: 100 } });
  products.value = res.data.products || res.data;
}

onMounted(async () => {
  try {
    const [catRes] = await Promise.all([
      api.get("/categories"),
      fetchProducts(),
    ]);
    categories.value = catRes.data;
  } finally {
    loading.value = false;
  }
});
</script>
