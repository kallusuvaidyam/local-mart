<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <router-link to="/" class="text-3xl font-bold text-blue-600">🛒 Local Mart</router-link>
        <p class="text-gray-500 mt-2">Create your account</p>
      </div>
      <div class="card p-8">
        <!-- Step 1: Registration Form -->
        <template v-if="!showOtpForm">
          <h1 class="text-2xl font-bold text-gray-900 mb-6">Create Account</h1>
          <form @submit.prevent="doRegister" class="space-y-4">
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-1">Full Name</label>
              <input v-model="form.name" type="text" required class="input-field" placeholder="Your name" />
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-1">Email</label>
              <input v-model="form.email" type="email" required class="input-field" placeholder="yourname@gmail.com" />
              <p class="text-xs text-gray-400 mt-1">Only Gmail addresses are accepted</p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-1">Phone Number</label>
              <input v-model="form.phone" type="tel" required class="input-field" placeholder="10-digit mobile number" />
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-1">Password</label>
              <input v-model="form.password" type="password" required class="input-field" placeholder="Min 6 characters" />
            </div>
            <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>
            <button type="submit" :disabled="loading" class="btn-primary w-full py-2.5">
              {{ loading ? 'Sending OTP...' : 'Create Account' }}
            </button>
          </form>
        </template>

        <!-- Step 2: OTP Verification -->
        <template v-else>
          <h1 class="text-2xl font-bold text-gray-900 mb-2">Verify Your Email</h1>
          <p class="text-sm text-gray-500 mb-6">We've sent a 6-digit OTP to <strong class="text-gray-700">{{ form.email }}</strong></p>
          <form @submit.prevent="doVerify" class="space-y-4">
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-1">Enter OTP</label>
              <input
                v-model="otp"
                type="text"
                maxlength="6"
                required
                class="input-field text-center text-2xl tracking-[0.5em] font-bold"
                placeholder="000000"
                inputmode="numeric"
              />
            </div>
            <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>
            <p v-if="success" class="text-green-600 text-sm font-medium">{{ success }}</p>
            <button type="submit" :disabled="loading || otp.length < 6" class="btn-primary w-full py-2.5">
              {{ loading ? 'Verifying...' : 'Verify Email' }}
            </button>
          </form>
          <div class="flex items-center justify-between mt-4">
            <button @click="resendOtp" :disabled="resendCooldown > 0" class="text-sm text-blue-600 hover:underline disabled:text-gray-400 disabled:no-underline">
              {{ resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend OTP' }}
            </button>
            <button @click="showOtpForm = false; error = ''" class="text-sm text-gray-500 hover:underline">
              Change email
            </button>
          </div>
        </template>

        <p class="text-center text-sm text-gray-600 mt-4">
          Already have an account? <router-link to="/login" class="text-blue-600 font-medium hover:underline">Sign In</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const form = ref({ name: '', email: '', phone: '', password: '' })
const otp = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')
const showOtpForm = ref(false)
const resendCooldown = ref(0)
let cooldownTimer = null

function startCooldown() {
  resendCooldown.value = 60
  cooldownTimer = setInterval(() => {
    resendCooldown.value--
    if (resendCooldown.value <= 0) clearInterval(cooldownTimer)
  }, 1000)
}

async function doRegister() {
  if (!form.value.email.toLowerCase().endsWith('@gmail.com')) {
    error.value = 'Only Gmail addresses are allowed'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const res = await api.post('/auth/register', form.value)
    if (res.data.requires_verification) {
      showOtpForm.value = true
      startCooldown()
    }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Registration failed'
  } finally { loading.value = false }
}

async function doVerify() {
  loading.value = true
  error.value = ''
  try {
    await api.post('/auth/verify-email', { email: form.value.email, otp: otp.value })
    success.value = 'Email verified! Redirecting to login...'
    setTimeout(() => router.push('/login'), 1500)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Verification failed'
  } finally { loading.value = false }
}

async function resendOtp() {
  error.value = ''
  try {
    await api.post('/auth/resend-verify-otp', { email: form.value.email })
    startCooldown()
    success.value = 'New OTP sent!'
    setTimeout(() => success.value = '', 3000)
  } catch {
    error.value = 'Failed to resend OTP'
  }
}

onUnmounted(() => { if (cooldownTimer) clearInterval(cooldownTimer) })
</script>
