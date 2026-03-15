<template>
  <div>
    <router-view />
    <ToastContainer />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'
import ToastContainer from '@/components/common/ToastContainer.vue'

const auth = useAuthStore()
const cart = useCartStore()

onMounted(async () => {
  if (auth.isLoggedIn) {
    try {
      await Promise.all([auth.fetchMe(), cart.fetchCart()])
    } catch {}
  }
})
</script>
