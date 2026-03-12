<template>
  <div
    class="card overflow-hidden hover:shadow-md transition-shadow group h-full flex flex-col"
  >
    <router-link :to="`/products/${product.slug}`">
      <ProductImage
        :src="product.image_url"
        :alt="product.name"
        container-class="aspect-square w-full"
        img-class="group-hover:scale-105 transition-transform duration-300"
      />
    </router-link>

    <div class="p-3 flex flex-col flex-1">
      <!-- Category -->
      <p class="text-xs text-blue-600 font-medium mb-1">
        {{ product.category?.name }}
      </p>

      <!-- Product Name -->
      <router-link :to="`/products/${product.slug}`">
        <h3
          class="font-semibold text-gray-900 text-sm leading-snug line-clamp-2 hover:text-blue-600"
        >
          {{ product.name }}
        </h3>
      </router-link>

      <!-- Unit -->
      <p v-if="product.unit" class="text-xs text-gray-500 mt-0.5">
        {{ product.unit }}
      </p>

      <!-- Price -->
      <div class="flex items-center gap-2 mt-2">
        <span class="text-base font-bold text-gray-900">
          ₹{{ product.price }}
        </span>

        <span
          v-if="product.mrp && product.mrp > product.price"
          class="text-xs text-gray-400 line-through"
        >
          ₹{{ product.mrp }}
        </span>

        <span v-if="discount > 0" class="text-xs text-green-600 font-medium">
          {{ discount }}% off
        </span>
      </div>

      <!-- Stock -->
      <div class="mt-2">
        <span
          v-if="product.stock_qty === 0"
          class="text-xs text-red-500 font-medium"
        >
          Out of stock
        </span>

        <!-- Buttons -->
        <div v-else class="flex gap-2">
          <!-- Add to Cart -->
          <button
            @click.prevent="addToCart"
            :disabled="adding"
            class="w-full btn-primary text-sm py-1.5"
          >
            {{ adding ? "Adding..." : "+ Add to Cart" }}
          </button>

          <!-- Buy Now -->
          <button
            @click.prevent="buyNow"
            :disabled="adding"
            class="w-full border border-blue-600 text-blue-600 rounded-md text-sm py-1.5 hover:bg-blue-50"
          >
            Buy Now
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { useCartStore } from "@/stores/cart";
import { useToastStore } from "@/stores/toast";
import ProductImage from "@/components/common/ProductImage.vue";

const props = defineProps({
  product: Object,
});

const auth = useAuthStore();
const cart = useCartStore();
const toast = useToastStore();
const router = useRouter();

const adding = ref(false);

// ─── Discount Calculation ─────────────────────────

const discount = computed(() => {
  if (!props.product.mrp || props.product.mrp <= props.product.price) return 0;

  return Math.round(
    ((props.product.mrp - props.product.price) / props.product.mrp) * 100,
  );
});

// ─── Add To Cart ──────────────────────────────────

async function addToCart() {
  if (!auth.isLoggedIn) {
    return router.push("/login");
  }

  adding.value = true;

  try {
    await cart.addItem(props.product.id, 1);

    toast.success(`${props.product.name} added to cart!`);
  } catch (e) {
    toast.error(e.response?.data?.detail || "Failed to add to cart");
  } finally {
    adding.value = false;
  }
}

// ─── Buy Now (Direct Checkout) ─────────────────────

async function buyNow() {
  if (!auth.isLoggedIn) {
    return router.push("/login");
  }

  adding.value = true;

  try {
    await cart.addItem(props.product.id, 1);

    await cart.fetchCart();

    router.push("/checkout");
  } catch (e) {
    toast.error(e.response?.data?.detail || "Failed to process order");
  } finally {
    adding.value = false;
  }
}
</script>
