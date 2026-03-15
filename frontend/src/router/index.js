import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  // Public
  { path: '/', component: () => import('@/views/customer/Home.vue') },
  { path: '/login', component: () => import('@/views/auth/Login.vue') },
  { path: '/register', component: () => import('@/views/auth/Register.vue') },
  { path: '/products', component: () => import('@/views/customer/ProductList.vue') },
  { path: '/products/:slug', component: () => import('@/views/customer/ProductDetail.vue') },
  { path: '/privacy-policy', component: () => import('@/views/PrivacyPolicy.vue') },
  { path: '/terms', component: () => import('@/views/TermsOfService.vue') },

  // Protected - Customer
  {
    path: '/cart',
    component: () => import('@/views/customer/Cart.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/checkout',
    component: () => import('@/views/customer/Checkout.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/orders',
    component: () => import('@/views/customer/OrderHistory.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/orders/:id',
    component: () => import('@/views/customer/OrderDetail.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    component: () => import('@/views/customer/Profile.vue'),
    meta: { requiresAuth: true },
  },

  // Admin
  {
    path: '/admin',
    component: () => import('@/views/admin/Dashboard.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/admin/products',
    component: () => import('@/views/admin/Products.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/admin/categories',
    component: () => import('@/views/admin/Categories.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/admin/orders',
    component: () => import('@/views/admin/Orders.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/admin/blocks',
    component: () => import('@/views/admin/Blocks.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },

  {
    path: '/admin/users',
    component: () => import('@/views/admin/Users.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/admin/analytics',
    component: () => import('@/views/admin/OrderAnalytics.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },

  // 404
  { path: '/:pathMatch(.*)*', component: () => import('@/views/NotFound.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) return next('/login')
  if (to.meta.requiresAdmin && !auth.isAdmin) return next('/')
  if ((to.path === '/login' || to.path === '/register') && auth.isLoggedIn) {
    return next(auth.isAdmin ? '/admin' : '/')
  }
  next()
})

export default router
