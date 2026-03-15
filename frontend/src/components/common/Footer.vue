<template>
  <footer class="bg-white border-t border-gray-200 mt-12">
    <div class="max-w-7xl mx-auto px-4 py-8">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Brand -->
        <div>
          <p class="font-bold text-lg text-blue-600 mb-2">&#128722; Local Mart</p>
          <p class="text-sm text-gray-500 leading-relaxed">
            Your neighbourhood store — fresh groceries &amp; daily essentials
            delivered to your doorstep.
          </p>
        </div>

        <!-- Quick Links -->
        <div>
          <p class="font-semibold text-gray-900 mb-2 text-sm">Quick Links</p>
          <div class="flex flex-col gap-1.5">
            <router-link to="/products" class="text-sm text-gray-600 hover:text-blue-600">Shop Products</router-link>
            <router-link to="/orders" class="text-sm text-gray-600 hover:text-blue-600">My Orders</router-link>
            <router-link to="/profile" class="text-sm text-gray-600 hover:text-blue-600">My Profile</router-link>
          </div>
        </div>

        <!-- Legal -->
        <div>
          <p class="font-semibold text-gray-900 mb-2 text-sm">Legal</p>
          <div class="flex flex-col gap-1.5">
            <router-link to="/privacy-policy" class="text-sm text-gray-600 hover:text-blue-600">Privacy Policy</router-link>
            <router-link to="/terms" class="text-sm text-gray-600 hover:text-blue-600">Terms of Service</router-link>
            <a href="mailto:kumarkallu56345@gmail.com" class="text-sm text-gray-600 hover:text-blue-600">Contact Us</a>
          </div>
        </div>
      </div>

      <hr class="my-6" />

      <p class="text-center text-xs text-gray-400">
        &copy; {{ new Date().getFullYear() }} Local Mart. All rights reserved.
      </p>
    </div>
  </footer>
</template>
