<template>
  <div>
    <Navbar />
    <div class="max-w-3xl mx-auto px-4 py-10">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Terms of Service</h1>
      <p class="text-sm text-gray-500 mb-8">Last updated: March 15, 2026</p>

      <div class="prose prose-sm max-w-none text-gray-700 space-y-6">

        <section>
          <h2 class="text-lg font-bold text-gray-900">1. Acceptance of Terms</h2>
          <p>
            By accessing or using the Local Mart application and website ("Service"), you agree to be
            bound by these Terms of Service. If you do not agree, do not use the Service.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-bold text-gray-900">2. Account Registration</h2>
          <ul class="list-disc pl-5 space-y-1">
            <li>You must provide accurate and complete information during registration</li>
            <li>You are responsible for maintaining the confidentiality of your account credentials</li>
            <li>You must be at least 13 years old to create an account</li>
            <li>One account per person — multiple accounts may be suspended</li>
          </ul>
        </section>

        <section>
          <h2 class="text-lg font-bold text-gray-900">3. Orders &amp; Payments</h2>
          <ul class="list-disc pl-5 space-y-1">
            <li>All orders are subject to product availability and delivery area coverage</li>
            <li>Prices displayed are in Indian Rupees (INR) and include applicable taxes</li>
            <li>We support Cash on Delivery (COD) and Online Payment via Razorpay</li>
            <li>Once an order is confirmed, it cannot be modified — you may request cancellation before dispatch</li>
            <li>Delivery charges are calculated based on your delivery zone and order value</li>
          </ul>
        </section>

        <section>
          <h2 class="text-lg font-bold text-gray-900">4. Return &amp; Refund Policy</h2>
          <ul class="list-disc pl-5 space-y-1">
            <li>Returns can be requested within the return window period after delivery (default: 2 days)</li>
            <li>Return requests are subject to admin review and approval</li>
            <li>Items must be in original condition for return approval</li>
            <li>Approved returns will be picked up from your delivery address</li>
            <li>Refunds for online payments will be processed to the original payment method</li>
            <li>COD order refunds will be handled as store credit or bank transfer</li>
          </ul>
        </section>

        <section>
          <h2 class="text-lg font-bold text-gray-900">5. Product Information</h2>
          <p>
            We make every effort to display accurate product information including descriptions,
            images, and pricing. However, we do not guarantee that all information is completely
            accurate or error-free. Product images are for illustration purposes and actual products
            may vary slightly.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-bold text-gray-900">6. User Conduct</h2>
          <p>You agree not to:</p>
          <ul class="list-disc pl-5 space-y-1">
            <li>Use the Service for any unlawful purpose</li>
            <li>Submit false or misleading information</li>
            <li>Post fake reviews or spam content</li>
            <li>Attempt to gain unauthorized access to other accounts or our systems</li>
            <li>Interfere with the proper functioning of the Service</li>
            <li>Use automated tools to scrape or access the Service</li>
          </ul>
        </section>

        <section>
          <h2 class="text-lg font-bold text-gray-900">7. Reviews</h2>
          <ul class="list-disc pl-5 space-y-1">
            <li>Reviews can only be submitted for products you have purchased and received</li>
            <li>Reviews must be honest and based on your actual experience</li>
            <li>We reserve the right to remove reviews that violate these terms</li>
          </ul>
        </section>

        <section>
          <h2 class="text-lg font-bold text-gray-900">8. Intellectual Property</h2>
          <p>
            All content on the Service — including logos, text, images, and software — is the
            property of Local Mart or its content suppliers and is protected by intellectual
            property laws. You may not reproduce, distribute, or create derivative works without
            our written permission.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-bold text-gray-900">9. Limitation of Liability</h2>
          <p>
            Local Mart shall not be liable for any indirect, incidental, or consequential damages
            arising from your use of the Service. Our total liability shall not exceed the amount
            paid by you for the specific order in question.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-bold text-gray-900">10. Service Availability</h2>
          <p>
            We strive to keep the Service available 24/7 but do not guarantee uninterrupted access.
            We may temporarily suspend the Service for maintenance, updates, or unforeseen circumstances
            without prior notice.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-bold text-gray-900">11. Modifications</h2>
          <p>
            We reserve the right to modify these Terms at any time. Changes will be posted on this
            page with an updated date. Continued use of the Service after changes constitutes
            acceptance of the revised terms.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-bold text-gray-900">12. Governing Law</h2>
          <p>
            These Terms shall be governed by and construed in accordance with the laws of India.
            Any disputes shall be subject to the exclusive jurisdiction of the courts in the
            relevant district.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-bold text-gray-900">13. Contact Us</h2>
          <p>For questions regarding these Terms, contact us at:</p>
          <div class="bg-blue-50 rounded-xl p-4 mt-2">
            <p class="font-semibold text-gray-900">Local Mart</p>
            <p class="text-sm">Email: <a href="mailto:kumarkallu56345@gmail.com" class="text-blue-600 hover:underline">kumarkallu56345@gmail.com</a></p>
          </div>
        </section>

      </div>
    </div>

    <Footer />
  </div>
</template>

<script setup>
import Navbar from '@/components/common/Navbar.vue'
import Footer from '@/components/common/Footer.vue'
</script>
