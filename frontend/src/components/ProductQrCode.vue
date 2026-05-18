<script setup>
import QRCode from "qrcode";
import { computed, onMounted, ref, watch } from "vue";

const props = defineProps({
  url: { type: String, required: true },
  label: String,
  filename: String,
});

const qrDataUrl = ref("");
const caption = computed(() => props.label ?? "Scan to open this product");

/** @type {Map<string, string>} */
const qrCache = new Map();

async function renderQrCode() {
  if (qrCache.has(props.url)) {
    qrDataUrl.value = qrCache.get(props.url);
    return;
  }

  // Generate new QR code and cache it
  const dataUrl = await QRCode.toDataURL(props.url, {
    width: 220,
    margin: 1,
    color: {
      dark: "#0f172a",
      light: "#ffffff",
    },
  });

  qrDataUrl.value = dataUrl;
  qrCache.set(props.url, dataUrl);
}

function downloadQrCode() {
  if (!qrDataUrl.value) return;

  const link = document.createElement("a");
  link.href = qrDataUrl.value;
  link.download = props.filename || "product-qr-code.png";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

onMounted(renderQrCode);
watch(() => props.url, renderQrCode);
</script>

<template>
  <div
    class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-950"
  >
    <img
      v-if="qrDataUrl"
      :src="qrDataUrl"
      :alt="caption"
      class="mx-auto h-44 w-44 rounded-xl object-contain"
    />
    <p
      class="mt-3 text-center text-sm font-medium text-slate-800 dark:text-slate-200"
    >
      {{ caption }}
    </p>
    <button
      v-if="qrDataUrl"
      @click="downloadQrCode"
      class="mt-3 mx-auto block rounded-lg bg-amber-600 px-4 py-2 text-sm font-medium text-white hover:bg-amber-700 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-2 dark:bg-amber-500 dark:hover:bg-amber-600"
    >
      Download QR Code
    </button>
    <!-- <p
      class="mt-1 break-all text-center text-xs text-slate-500 dark:text-slate-400"
    >
      {{ url }}
    </p> -->
  </div>
</template>
