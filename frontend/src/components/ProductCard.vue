<script setup>
defineProps({ product: Object });
</script>

<template>
  <article
    class="group overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-xl dark:border-slate-800 dark:bg-slate-900"
  >
    <RouterLink :to="`/products/${product.slug}`" class="block">
      <img
        :src="product.images[0]?.url"
        :alt="product.images[0]?.alt || product.name"
        class="h-64 w-full object-cover"
      />
      <div class="space-y-3 p-4">
        <div
          class="flex items-center justify-between gap-4 text-xs uppercase tracking-[0.2em] text-slate-500"
        >
          <span>{{ product.category.name }}</span>
          <span>{{ product.era.name }}</span>
        </div>
        <div
          class="block text-lg font-semibold text-slate-900 group-hover:text-amber-700 dark:text-slate-100 dark:group-hover:text-amber-400"
        >
          {{ product.name }}
        </div>
        <p class="line-clamp-2 text-sm text-slate-600">
          {{ product.description }}
        </p>
        <div class="flex items-center justify-between">
          <span
            class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-900 dark:text-slate-100"
            >Aisle {{ product.aisle }}</span
          >
          <span
            class="rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-900"
          >
            Qty {{ product.quantity }}
          </span>
        </div>
      </div>
    </RouterLink>
  </article>
</template>
