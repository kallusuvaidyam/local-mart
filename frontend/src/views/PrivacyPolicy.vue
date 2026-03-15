<template>
  <div>
    <Navbar />
    <div class="max-w-3xl mx-auto px-4 py-10">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Privacy Policy</h1>
      <p class="text-sm text-gray-500 mb-8">Last updated: March 15, 2026</p>

      <div class="prose prose-sm max-w-none text-gray-700 space-y-6">

        <section>
          <h2 class="text-lg font-bold text-gray-900">1. Introduction</h2>
          <p>
            Local Mart ("we", "our", or "us") operates the Local Mart mobile application and website
            (collectively, the "Service"). This Privacy Policy explains how we collect, use, disclose,
            and safeguard your information when you use our Service.
          </p>
          <p>
            By using the Service, you agree to the collection and use of information in accordance with
            this policy. If you do not agree, please do not use the Service.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-bold text-gray-900">2. Information We Collect</h2>

          <h3 class="text-base font-semibold text-gray-800 mt-3">2.1 Personal Information</h3>
          <p>When you register an account or place an order, we collect:</p>
          <ul class="list-disc pl-5 space-y-1">
            <li><strong>Name</strong> — to personalize your experience and order communications</li>
            <li><strong>Email address</strong> — for account login, order confirmations, and status updates</li>
            <li><strong>Phone number</strong> — for delivery coordination and account verification</li>
            <li><strong>Password</strong> — stored securely as a cryptographic hash (we never store plain-text passwords)</li>
          </ul>

          <h3 class="text-base font-semibold text-gray-800 mt-3">2.2 Delivery Address</h3>
          <p>We collect your delivery address details including:</p>
          <ul class="list-disc pl-5 space-y-1">
            <li>Street address, landmark, and pincode</li>
            <li>Delivery block and zone (to calculate delivery availability and charges)</li>
          </ul>

          <h3 class="text-base font-semibold text-gray-800 mt-3">2.3 Order &amp; Payment Data</h3>
          <ul class="list-disc pl-5 space-y-1">
            <li>Order details (items, quantities, prices, delivery charges)</li>
            <li>Payment method chosen (Cash on Delivery or Online Payment)</li>
            <li>Razorpay transaction IDs (for online payments only — we do NOT store card numbers, UPI IDs, or bank details)</li>
            <li>Order notes and delivery instructions</li>
          </ul>

          <h3 class="text-base font-semibold text-gray-800 mt-3">2.4 Automatically Collected Information</h3>
          <ul class="list-disc pl-5 space-y-1">
            <li>Device type and browser information</li>
            <li>IP address and general location</li>
            <li>Usage data (pages visited, time spent)</li>
          </ul>
        </section>

        <section>
          <h2 class="text-lg font-bold text-gray-900">3. How We Use Your Information</h2>
          <ul class="list-disc pl-5 space-y-1">
            <li>To create and manage your account</li>
            <li>To process and fulfill your orders</li>
            <li>To send order confirmations, status updates, and delivery notifications via email</li>
            <li>To calculate delivery charges based on your delivery zone</li>
            <li>To process payments securely through Razorpay</li>
            <li>To enable product reviews and return requests</li>
            <li>To improve our Service and user experience</li>
            <li>To respond to customer support inquiries</li>
          </ul>
        </section>

        <section>
          <h2 class="text-lg font-bold text-gray-900">4. Third-Party Services</h2>
          <p>We use the following third-party services that may have access to your data:</p>

          <div class="bg-gray-50 rounded-xl p-4 space-y-3 mt-2">
            <div>
              <p class="font-semibold text-gray-800">Razorpay (Payment Gateway)</p>
              <p class="text-sm">Processes online payments. Your payment details (card, UPI, net banking) are handled directly by Razorpay and are never stored on our servers. Razorpay's privacy policy:
                <a href="https://razorpay.com/privacy/" target="_blank" rel="noopener" class="text-blue-600 hover:underline">razorpay.com/privacy</a>
              </p>
            </div>
            <div>
              <p class="font-semibold text-gray-800">Cloudinary (Image Hosting)</p>
              <p class="text-sm">Stores and delivers product images. No personal user data is shared with Cloudinary.</p>
            </div>
            <div>
              <p class="font-semibold text-gray-800">Google SMTP (Email Service)</p>
              <p class="text-sm">Used to send transactional emails such as order confirmations and status updates to your registered email address.</p>
            </div>
          </div>
        </section>

        <section>
          <h2 class="text-lg font-bold text-gray-900">5. Data Security</h2>
          <p>
            We implement appropriate security measures to protect your personal information:
          </p>
          <ul class="list-disc pl-5 space-y-1">
            <li>Passwords are hashed using industry-standard algorithms</li>
            <li>Authentication uses JWT (JSON Web Tokens) with expiration</li>
            <li>Payment processing is handled entirely by PCI-DSS compliant Razorpay</li>
            <li>HTTPS encryption for all data in transit</li>
          </ul>
        </section>

        <section>
          <h2 class="text-lg font-bold text-gray-900">6. Data Retention</h2>
          <p>
            We retain your personal data as long as your account is active or as needed to provide
            you services. Order history is retained for record-keeping and dispute resolution.
            You may request account deletion by contacting us.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-bold text-gray-900">7. Your Rights</h2>
          <p>You have the right to:</p>
          <ul class="list-disc pl-5 space-y-1">
            <li><strong>Access</strong> — View your personal data from your Profile page</li>
            <li><strong>Update</strong> — Edit your name, phone, and password anytime</li>
            <li><strong>Delete</strong> — Request account and data deletion by contacting us</li>
            <li><strong>Withdraw consent</strong> — Stop using the Service at any time</li>
          </ul>
        </section>

        <section>
          <h2 class="text-lg font-bold text-gray-900">8. Children's Privacy</h2>
          <p>
            Our Service is not intended for children under the age of 13. We do not knowingly collect
            personal data from children. If you believe a child has provided us with personal data,
            please contact us so we can delete it.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-bold text-gray-900">9. Changes to This Policy</h2>
          <p>
            We may update this Privacy Policy from time to time. Changes will be posted on this page
            with an updated "Last updated" date. Continued use of the Service after changes constitutes
            acceptance of the revised policy.
          </p>
        </section>

        <section>
          <h2 class="text-lg font-bold text-gray-900">10. Contact Us</h2>
          <p>If you have questions about this Privacy Policy or your data, contact us at:</p>
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
