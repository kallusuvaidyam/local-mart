<template>
  <div :class="wrapClass">
    <div :class="containerClass">
      <!--
        Replace this placeholder with your ad network code:
        - Google AdSense: paste <ins class="adsbygoogle" ...> here
        - Custom ads: use your own API to fetch ad content
      -->
      <div class="ad-placeholder" :style="{ minHeight: height }">
        <p class="ad-label">Advertisement</p>
        <div class="ad-inner">
          <span class="ad-icon">&#128226;</span>
          <p class="ad-text">Ad Space — {{ label }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  label: { type: String, default: 'Banner' },
  height: { type: String, default: '90px' },
  wrapClass: { type: String, default: 'my-4' },
  containerClass: { type: String, default: '' },
});
</script>

<style scoped>
.ad-placeholder {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 1.5px dashed #cbd5e1;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}
.ad-label {
  position: absolute;
  top: 6px;
  right: 10px;
  font-size: 9px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.ad-inner {
  display: flex;
  align-items: center;
  gap: 8px;
}
.ad-icon {
  font-size: 20px;
  opacity: 0.4;
}
.ad-text {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 500;
}
</style>
