<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getMeta, getProducts } from "../api/client";
import ProductCard from "../components/ProductCard.vue";
import { catalogShown, catalogTotal, chatOpen } from "../stores/catalog";
import ProductSkeleton from "../components/ProductSkeleton.vue";

const route = useRoute();
const router = useRouter();
const PAGE_SIZE = 18;

const categories = ref([]);
const eras = ref([]);
const loading = ref(true);
const error = ref("");
const filtersOpen = ref(false);
const result = ref({
  items: [],
  total: 0,
  page: 1,
  pageSize: PAGE_SIZE,
  totalPages: 1,
});

const filters = reactive({
  search: "",
  category: "",
  era: "",
  sort: "newest",
});

/** @type {ReturnType<typeof setTimeout> | null} */
let searchDebounceTimer = null;

function syncFromQuery() {
  filters.search =
    typeof route.query.search === "string" ? route.query.search : "";
  filters.category =
    typeof route.query.category === "string" ? route.query.category : "";
  filters.era = typeof route.query.era === "string" ? route.query.era : "";
  filters.sort =
    typeof route.query.sort === "string" ? route.query.sort : "newest";
}

const currentPage = computed(() => {
  const value = Number(route.query.page ?? 1);
  return Number.isNaN(value) || value < 1 ? 1 : value;
});

async function loadProducts() {
  loading.value = true;
  error.value = "";
  try {
    result.value = await getProducts({
      page: currentPage.value,
      pageSize: PAGE_SIZE,
      search: filters.search || undefined,
      category: filters.category || undefined,
      era: filters.era || undefined,
      sort: filters.sort,
    });
  } catch (loadError) {
    error.value = "Unable to load catalog right now.";
    console.error(loadError);
  } finally {
    loading.value = false;
    catalogShown.value = result.value.items.length;
    catalogTotal.value = result.value.total;
  }
}

function applyFilters(page = 1) {
  filtersOpen.value = false;
  router.push({
    query: {
      ...(filters.search ? { search: filters.search } : {}),
      ...(filters.category ? { category: filters.category } : {}),
      ...(filters.era ? { era: filters.era } : {}),
      ...(filters.sort ? { sort: filters.sort } : {}),
      page: String(page),
    },
  });
}

function resetFilters() {
  filters.search = "";
  filters.category = "";
  filters.era = "";
  filters.sort = "newest";
  filtersOpen.value = false;
  router.push({
    query: {
      page: "1",
    },
  });
}

watch(
  () => route.query,
  () => {
    syncFromQuery();
    loadProducts();
  },
  { immediate: true },
);

watch(
  () => filters.search,
  () => {
    if (searchDebounceTimer) {
      clearTimeout(searchDebounceTimer);
    }

    searchDebounceTimer = setTimeout(() => {
      applyFilters(1);
    }, 350);
  },
);

onMounted(async () => {
  const meta = await getMeta();
  categories.value = meta.categories;
  eras.value = meta.eras;
});
</script>

<template>
  <main class="w-full px-4 py-6 transition-all duration-300 md:px-8 md:py-8" :class="chatOpen ? 'lg:pr-[452px]' : ''">
    <!-- Search bar and filters toggle -->
    <div class="mb-8 space-y-3">
      <div class="flex justify-center gap-3">
        <input
          v-model="filters.search"
          type="search"
          placeholder="Search products"
          class="w-full max-w-md rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm focus:border-amber-600 focus:outline-none dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
        />
        <button
          type="button"
          @click="filtersOpen = !filtersOpen"
          class="md:hidden relative p-2 rounded-xl border border-slate-300 hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800"
          aria-label="Toggle filters"
        >
          <svg
            class="h-5 w-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
            />
          </svg>
        </button>
      </div>
    </div>

    <!-- Catalog section: right divider only when chat open | z-10: below chat (z-50) -->
    <!-- No divider on closed state (filter section has own border) -->
    <section
      class="relative z-10 mt-6 grid items-start gap-6 transition-all duration-300"
      :class="chatOpen ? 'md:grid-cols-[1fr]' : 'md:grid-cols-[260px_1fr]'"
    >
      <!-- Filters sidebar - hide when chat is open -->
      <aside
        v-show="!chatOpen"
        :class="[
          'md:sticky md:top-8 h-fit rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900',
          filtersOpen ? 'block' : 'hidden md:block',
        ]"
      >
        <h2
          class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-700 dark:text-slate-300"
        >
          Filters
        </h2>
        <form class="mt-4 space-y-3" @submit.prevent="applyFilters(1)">
          <select
            v-model="filters.category"
            class="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-amber-600 focus:outline-none dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
          >
            <option value="">All categories</option>
            <option
              v-for="category in categories"
              :key="category.id"
              :value="category.slug"
            >
              {{ category.name }}
            </option>
          </select>
          <select
            v-model="filters.era"
            class="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-amber-600 focus:outline-none dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
          >
            <option value="">All eras</option>
            <option v-for="era in eras" :key="era.id" :value="era.slug">
              {{ era.name }}
            </option>
          </select>
          <select
            v-model="filters.sort"
            class="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:border-amber-600 focus:outline-none dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
          >
            <option value="newest">Newest</option>
            <option value="aisle_asc">Aisle: A to Z</option>
            <option value="aisle_desc">Aisle: Z to A</option>
            <option value="name_asc">Name: A to Z</option>
            <option value="name_desc">Name: Z to A</option>
          </select>
          <div class="flex gap-2 pt-1">
            <button
              class="rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-700 dark:bg-amber-600 dark:text-slate-900 dark:hover:bg-amber-500"
              type="submit"
            >
              Apply
            </button>
            <button
              class="rounded-xl border border-slate-300 px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
              type="button"
              @click="resetFilters"
            >
              Reset
            </button>
          </div>
        </form>
      </aside>

      <!-- Products grid -->
      <div>
        <section>
          <div
            v-if="loading"
            class="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 2xl:grid-cols-5"
          >
            <ProductSkeleton v-for="i in 6" :key="i" />
          </div>
          <div
            v-else-if="error"
            class="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700"
          >
            {{ error }}
          </div>
          <div
            v-else-if="result.items.length === 0"
            class="rounded-2xl border border-slate-200 bg-white p-8 text-center text-slate-600 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300"
          >
            No products match your current filters.
          </div>
          <div
            v-else
            class="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 2xl:grid-cols-5"
          >
            <ProductCard
              v-for="product in result.items"
              :key="product.id"
              :product="product"
            />
          </div>

          <div
            v-if="result.totalPages > 1"
            class="mt-6 flex items-center justify-center gap-3"
          >
            <button
              class="rounded-xl border border-slate-300 px-4 py-2 text-sm hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50"
              :disabled="currentPage <= 1"
              @click="applyFilters(currentPage - 1)"
            >
              Previous
            </button>
            <span class="text-sm text-slate-600"
              >Page {{ currentPage }} of {{ result.totalPages }}</span
            >
            <button
              class="rounded-xl border border-slate-300 px-4 py-2 text-sm hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50"
              :disabled="currentPage >= result.totalPages"
              @click="applyFilters(currentPage + 1)"
            >
              Next
            </button>
          </div>
        </section>
      </div>
    </section>
  </main>
</template>
