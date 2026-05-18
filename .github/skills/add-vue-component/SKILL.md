---
name: add-vue-component
description: Create a new Vue 3 Composition API component for the Wardrobe Catalog frontend. Use this skill when scaffolding views, modals, cards, or any reusable UI piece. Ensures ref/computed reactivity, Axios API calls with error handling, loading states, Tailwind CSS, and auth guards are applied correctly.
---

# Add Vue Component

Use this skill when the user asks to add, create, or scaffold a new Vue 3 component or view.

## Checklist — every component must have all of these

- [ ] All mutable state wrapped in `ref()` or `reactive()`
- [ ] Derived values use `computed()` — never plain variables
- [ ] API calls wrapped in `try-catch` with an `error` ref displayed to the user
- [ ] `loading` ref toggled around every async operation
- [ ] Auth checks before rendering sensitive UI (`v-if="isAdmin"`)
- [ ] Tailwind classes spell-checked (e.g., `flex-col` not `flex_col`, `w-1/2` not `w-50%`)
- [ ] Props declared with `defineProps` and typed with JSDoc `@typedef`
- [ ] Component name PascalCase, file name matches
- [ ] No hardcoded API URLs — use the Axios client from `src/api/client.js`
- [ ] Loading and error states visible in the template

## File locations

- Views (full pages): `frontend/src/views/`
- Reusable components: `frontend/src/components/`
- Pinia stores: `frontend/src/stores/`
- Axios client: `frontend/src/api/client.js`
- Auth store: `frontend/src/stores/auth.js`

## Component template

```vue
<script setup>
import { ref, computed, onMounted } from "vue";
import { useAuthStore } from "../stores/auth.js";
import { getProducts } from "../api/client.js";

const auth = useAuthStore();
const isAdmin = computed(() => auth.isAdmin);

const items = ref([]);
const loading = ref(false);
const error = ref(null);

async function fetchItems() {
  loading.value = true;
  error.value = null;
  try {
    items.value = await getProducts();
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

onMounted(fetchItems);
</script>

<template>
  <div class="p-4">
    <div v-if="loading" class="text-gray-500">Loading…</div>
    <div v-else-if="error" class="text-red-600">{{ error }}</div>
    <ul v-else class="grid grid-cols-3 gap-4">
      <li v-for="item in items" :key="item.id">{{ item.name }}</li>
    </ul>
    <button v-if="isAdmin" class="mt-4 btn-primary" @click="doAdminAction">
      Admin Action
    </button>
  </div>
</template>
```

## Props pattern

```vue
<script setup>
/** @typedef {{ id: number, name: string, slug: string }} Product */
const props = defineProps({
  /** @type {import('vue').PropType<Product>} */
  product: { type: Object, required: true },
});
</script>
```

## Pinia store usage

```js
// Read state
const catalog = useCatalogStore();
const products = computed(() => catalog.products);

// Trigger action
await catalog.fetchProducts({ page: 1 });
```

## Common mistakes to avoid

- Do NOT write `const count = 0` — use `const count = ref(0)`
- Do NOT hardcode `http://localhost:4000` — import from the Axios client
- Do NOT render admin buttons without `v-if="isAdmin"`
- Do NOT forget `loading.value = false` in the `finally` block
- Do NOT use `flex_col` or other Tailwind typos — check IntelliSense
