<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { getProduct } from "../api/client";
import ProductQrCode from "../components/ProductQrCode.vue";
import ProductSkeleton from "../components/ProductSkeleton.vue";
import { chatOpen } from "../stores/catalog";

const route = useRoute();
const loading = ref(true);
const error = ref("");
const product = ref(null);
const activeImage = ref(0);

const imageList = computed(() => product.value?.images ?? []);
const productUrl = computed(() => {
  if (!product.value || typeof window === "undefined") {
    return "";
  }

  return new URL(
    `/products/${product.value.slug}`,
    window.location.origin,
  ).toString();
});

async function loadProduct(slug) {
  if (typeof slug !== "string") {
    error.value = "Invalid product.";
    loading.value = false;
    return;
  }
  loading.value = true;
  error.value = "";
  activeImage.value = 0;
  try {
    product.value = await getProduct(slug);
  } catch (loadError) {
    console.error(loadError);
    error.value = "Product not found or unavailable.";
  } finally {
    loading.value = false;
  }
}

onMounted(() => loadProduct(route.params.slug));
watch(() => route.params.slug, loadProduct);
</script>

<template>
  <main class="mx-auto w-full max-w-7xl px-4 py-8 transition-all duration-300 md:px-8 md:py-10" :class="chatOpen ? 'lg:pr-[452px]' : ''">
    <RouterLink
      to="/"
      class="text-sm font-medium text-amber-800 hover:text-amber-900 dark:text-amber-400 dark:hover:text-amber-300"
    >
      ← Back to catalog
    </RouterLink>

    <section
      v-if="loading"
      class="mt-6 rounded-2xl border border-slate-200 bg-white p-8 text-center text-slate-600 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300"
    >
      <ProductSkeleton />
    </section>
    <section
      v-else-if="error"
      class="mt-6 rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700"
    >
      {{ error }}
    </section>

    <section
      v-else-if="product"
      class="mt-6 grid gap-8 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900 md:grid-cols-2 md:p-8"
    >
      <div>
        <img
          :src="imageList[activeImage]?.url"
          :alt="imageList[activeImage]?.alt || product.name"
          class="h-[420px] w-full rounded-2xl object-cover"
        />
        <div class="mt-3 grid grid-cols-4 gap-2">
          <button
            v-for="(image, index) in imageList"
            :key="image.id"
            class="overflow-hidden rounded-xl border"
            :class="
              index === activeImage
                ? 'border-amber-600 dark:border-amber-400'
                : 'border-slate-200 dark:border-slate-700'
            "
            @click="activeImage = index"
          >
            <img
              :src="image.url"
              :alt="image.alt || product.name"
              class="h-20 w-full object-cover"
            />
          </button>
        </div>
      </div>

      <div>
        <p
          class="text-xs uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400"
        >
          {{ product.category.name }} / {{ product.era.name }}
        </p>
        <h1
          class="mt-2 text-4xl font-semibold text-slate-900 dark:text-slate-100"
        >
          {{ product.name }}
        </h1>
        <p class="mt-4 text-slate-700 dark:text-slate-300">
          {{ product.description }}
        </p>

        <div class="mt-6 flex items-center gap-4">
          <p
            class="text-xl font-semibold uppercase tracking-[0.2em] text-slate-900 dark:text-slate-100"
          >
            Aisle {{ product.aisle }}
          </p>
          <span
            class="rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-900"
            >Qty {{ product.quantity }}</span
          >
        </div>

        <div class="mt-8 max-w-sm">
          <ProductQrCode
            :url="productUrl"
            label="Scan to open this product detail page"
            :filename="`${product.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_qr.png`"
          />
        </div>
      </div>
    </section>
  </main>
</template>
