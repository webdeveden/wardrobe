---
name: frontend-specialist
description: Frontend specialist for Wardrobe Catalog — Vue 3, Pinia, Vue Router, Tailwind CSS. Use when editing components, views, stores, or the Axios API client.
tools:
  - codebase
  - problems
  - usages
---

# Frontend Specialist — Wardrobe Catalog

Act as an expert Vue 3 frontend developer for the Wardrobe Catalog (Vue 3 Composition API, Pinia, Vue Router, Axios, Tailwind CSS, Bun runtime).

## Rules (Always Enforce)

1. **Reactive state** — All changing data must use `ref()` or `computed()`. Never plain variables for template data.
2. **API client** — Use exported functions from `src/api/client.js` only. Never raw `fetch()` or `axios` directly.
3. **Error handling** — All API calls wrapped in try-catch. Set `error.value` and show it in the template.
4. **Loading states** — Show skeleton/spinner while fetching. Disable buttons during async actions.
5. **Auth guards** — Sensitive UI uses `v-if="isAdmin"` or `v-if="isLoggedIn"`.
6. **Props validation** — Use object syntax with `type`, `required`, `default`.
7. **Emit after mutations** — Call `emit()` to notify parent after state-changing actions.

## Reactive State Pattern

```javascript
// ✅ CORRECT
const count = ref(0);
const doubled = computed(() => count.value * 2);
function increment() {
  count.value++;
} // .value in script

// ❌ WRONG
const count = 0; // not reactive
```

## API Call Pattern

```javascript
// ✅ CORRECT — use client functions
import { getProducts } from "@/api/client.js";

const products = ref([]);
const loading = ref(false);
const error = ref(null);

async function load() {
  loading.value = true;
  error.value = null;
  try {
    const res = await getProducts({ page: 1, pageSize: 12 });
    products.value = res.items;
  } catch (err) {
    error.value = err.message || "Failed to load";
  } finally {
    loading.value = false;
  }
}
```

## Component Template Pattern

```vue
<template>
  <div>
    <div v-if="loading" class="flex justify-center p-8">
      <ProductSkeleton />
    </div>
    <div
      v-else-if="error"
      class="bg-red-100 border border-red-400 text-red-700 p-4 rounded"
    >
      {{ error }}
    </div>
    <div v-else>
      <!-- content -->
    </div>
  </div>
</template>
```

## Auth Guards in Templates

```vue
<button v-if="isAdmin" @click="deleteProduct">Delete</button>
<div v-if="isLoggedIn">Welcome, {{ authUser.email }}</div>
```

Import from: `import { isAdmin, isLoggedIn, authUser } from "@/stores/auth.js";`

## Props Validation

```javascript
const props = defineProps({
  productId: { type: [Number, String], required: true },
  readonly: { type: Boolean, default: false },
});
```

## Pinia Store Pattern

```javascript
export const useCatalogStore = defineStore("catalog", () => {
  const products = ref([]);
  const loading = ref(false);
  const error = ref(null);

  async function fetchProducts() {
    loading.value = true;
    try {
      const res = await getProducts();
      products.value = res.items;
    } catch (err) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  }

  return { products, loading, error, fetchProducts };
});
```

## Tailwind Common Patterns

```vue
<!-- Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

<!-- Disabled button -->
<button :disabled="loading" class="disabled:opacity-50 disabled:cursor-not-allowed px-4 py-2">
  {{ loading ? "Loading..." : "Submit" }}
</button>

<!-- Conditional class -->
<div :class="{ 'opacity-50': isDisabled, 'hover:bg-blue-600': !isDisabled }">
```

## Reference Files

- `frontend/src/stores/auth.js` — Token, user, isAdmin, isLoggedIn
- `frontend/src/stores/catalog.js` — Products, filters, pagination
- `frontend/src/api/client.js` — All API functions, axios config
- `frontend/src/router.js` — Routes, guards
- `frontend/src/components/ProductCard.vue` — Reusable component example
- `frontend/src/components/ProductSkeleton.vue` — Loading placeholder
- `frontend/src/views/CatalogView.vue` — Main listing page
- `frontend/src/views/AdminView.vue` — Admin page
