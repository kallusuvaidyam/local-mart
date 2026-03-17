<template>
  <div class="min-h-screen bg-gray-50 flex">
    <AdminSidebar />
    <main class="flex-1 p-6">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold text-gray-900">Categories</h1>
        <button @click="openForm()" class="btn-primary">+ Add Category</button>
      </div>

      <!-- Form Modal -->
      <div v-if="showForm" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl w-full max-w-sm p-6">
          <h2 class="font-bold text-lg mb-4">{{ editing ? 'Edit' : 'Add' }} Category</h2>
          <div class="space-y-3">
            <input v-model="form.name" placeholder="Category Name *" required class="input-field" />
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-1">Category Image</label>
              <input type="file" accept="image/*" @change="onFileChange" class="text-sm" />
              <div v-if="imagePreview || (editing && editing.image_url && !form.remove_image)" class="mt-2 flex items-center gap-2">
                <img :src="imagePreview || editing?.image_url" class="w-12 h-12 object-cover rounded" />
                <button @click="removeImage" class="text-xs text-red-500 hover:underline">Remove image</button>
              </div>
            </div>
          </div>
          <p v-if="formError" class="text-red-500 text-sm mt-2">{{ formError }}</p>
          <div class="flex gap-2 mt-4">
            <button @click="saveCategory" :disabled="saving" class="btn-primary flex-1">{{ saving ? 'Saving...' : 'Save' }}</button>
            <button @click="showForm = false" class="btn-secondary flex-1">Cancel</button>
          </div>
        </div>
      </div>

      <!-- Active / All toggle -->
      <div class="flex gap-2 mb-4">
        <button
          @click="showInactive = false; fetchCategories()"
          :class="['px-3 py-1 rounded-full text-sm font-medium transition', !showInactive ? 'bg-blue-600 text-white' : 'bg-white border hover:border-blue-300 text-gray-600']"
        >Active</button>
        <button
          @click="showInactive = true; fetchCategories()"
          :class="['px-3 py-1 rounded-full text-sm font-medium transition', showInactive ? 'bg-blue-600 text-white' : 'bg-white border hover:border-blue-300 text-gray-600']"
        >All (incl. inactive)</button>
      </div>

      <LoadingSpinner v-if="loading" />
      <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div v-for="cat in categories" :key="cat.id" class="card p-4 text-center">
          <img
            :src="cat.image_url || 'https://via.placeholder.com/80x80?text=?'"
            class="w-16 h-16 object-cover rounded-lg mx-auto mb-2"
            @error="e => e.target.src = 'https://via.placeholder.com/80x80?text=?'"
          />
          <p class="font-semibold text-gray-900 text-sm">{{ cat.name }}</p>
          <p class="text-xs text-gray-500 mb-1">{{ cat.slug }}</p>
          <span :class="cat.is_active ? 'badge-confirmed' : 'badge-cancelled'" class="mb-2 inline-block text-xs">
            {{ cat.is_active ? 'Active' : 'Inactive' }}
          </span>
          <div class="flex gap-2 justify-center mt-1">
            <button @click="openForm(cat)" class="text-blue-600 text-xs hover:underline">Edit</button>
            <button
              @click="toggleCat(cat)"
              :class="cat.is_active ? 'text-red-500' : 'text-green-600'"
              :disabled="toggling === cat.id"
              class="text-xs hover:underline disabled:opacity-50"
            >
              {{ toggling === cat.id ? '...' : cat.is_active ? 'Deactivate' : 'Activate' }}
            </button>
          </div>
        </div>
        <div v-if="categories.length === 0" class="col-span-4 text-center text-gray-400 py-12">
          No categories found.
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminSidebar from '@/components/admin/Sidebar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import { useToastStore } from '@/stores/toast'
import api from '@/services/api'

const toast = useToastStore()
const categories = ref([])
const loading = ref(true)
const showForm = ref(false)
const saving = ref(false)
const toggling = ref(null)
const formError = ref('')
const editing = ref(null)
const showInactive = ref(false)
const form = ref({ name: '', remove_image: false })
const imageFile = ref(null)
const imagePreview = ref(null)

function onFileChange(e) {
  const file = e.target.files[0]
  if (file) {
    imageFile.value = file
    imagePreview.value = URL.createObjectURL(file)
    form.value.remove_image = false
  }
}

function removeImage() {
  imageFile.value = null
  imagePreview.value = null
  form.value.remove_image = true
}

async function fetchCategories() {
  loading.value = true
  try {
    const res = await api.get('/categories', { params: { show_all: showInactive.value } })
    categories.value = res.data
  } finally {
    loading.value = false
  }
}

function openForm(cat = null) {
  editing.value = cat
  form.value = cat ? { name: cat.name, remove_image: false } : { name: '', remove_image: false }
  imageFile.value = null
  imagePreview.value = null
  formError.value = ''
  showForm.value = true
}

async function saveCategory() {
  if (!form.value.name.trim()) { formError.value = 'Category name is required'; return }
  saving.value = true
  formError.value = ''
  try {
    const fd = new FormData()
    fd.append('name', form.value.name.trim())
    if (imageFile.value) fd.append('image', imageFile.value)
    if (editing.value) {
      fd.append('remove_image', form.value.remove_image)
      await api.put(`/categories/${editing.value.id}`, fd)
    } else {
      await api.post('/categories', fd)
    }
    toast.success(editing.value ? 'Category updated!' : 'Category added!')
    showForm.value = false
    await fetchCategories()
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Failed to save'
  } finally { saving.value = false }
}

async function toggleCat(cat) {
  toggling.value = cat.id
  try {
    const fd = new FormData()
    fd.append('is_active', !cat.is_active)
    await api.put(`/categories/${cat.id}`, fd)
    toast.success(cat.is_active ? `"${cat.name}" deactivated` : `"${cat.name}" activated`)
    await fetchCategories()
  } catch {
    toast.error('Failed to update status')
  } finally { toggling.value = null }
}

onMounted(fetchCategories)
</script>
