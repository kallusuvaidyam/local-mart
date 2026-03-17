<template>
  <div
    class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4"
  >
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <router-link to="/" class="text-3xl font-bold text-blue-600"
          >🛒 Local Mart</router-link
        >
        <p class="text-gray-500 mt-2">Your neighbourhood store</p>
      </div>
      <div class="card p-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-6">Sign In</h1>
        <form @submit.prevent="doLogin" class="space-y-4">
          <div>
            <label class="text-sm font-medium text-gray-700 block mb-1"
              >Email</label
            >
            <input
              v-model="form.email"
              type="email"
              required
              class="input-field"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label class="text-sm font-medium text-gray-700 block mb-1"
              >Password</label
            >
            <input
              v-model="form.password"
              type="password"
              required
              class="input-field"
              placeholder="••••••••"
            />
          </div>
          <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>
          <button
            type="submit"
            :disabled="loading"
            class="btn-primary w-full py-2.5"
          >
            {{ loading ? "Signing in..." : "Sign In" }}
          </button>
        </form>
        <p class="text-center text-sm text-gray-600 mt-4">
          Don't have an account?
          <router-link
            to="/register"
            class="text-blue-600 font-medium hover:underline"
            >Register</router-link
          >
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { useCartStore } from "@/stores/cart";

const auth = useAuthStore();
const cart = useCartStore();
const router = useRouter();
const form = ref({ email: "", password: "" });
const loading = ref(false);
const error = ref("");

async function doLogin() {
  console.log(form.value.email, form.value.password);

  loading.value = true;
  error.value = "";
  try {
    await auth.login(form.value.email, form.value.password);
    await cart.fetchCart();
    router.push(auth.isAdmin ? "/admin" : "/");
  } catch (e) {
    if (e.response?.status === 403) {
      error.value = "Email not verified. Please check your Gmail inbox for the OTP.";
    } else {
      error.value = e.response?.data?.detail || "Invalid email or password";
    }
  } finally {
    loading.value = false;
  }
}
</script>
