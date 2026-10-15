<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { fetchMe } from "./api/client";
import { useRoute, useRouter } from "vue-router";
import ChatModal from "./components/ChatModal.vue";
import LoginModal from "./components/LoginModal.vue";
import { chatOpen } from "./stores/catalog";
import {
  isAdmin,
  isLoggedIn,
  clearAuth,
  setAuth,
  authUser,
} from "./stores/auth";

const THEME_STORAGE_KEY = "wardrobe-theme";
const SEARCH_DEBOUNCE_MS = 350;

const theme = ref("system");
const navSearch = ref("");
const menuOpen = ref(false);
const loginOpen = ref(false);
const route = useRoute();
const router = useRouter();
const isCatalogRoute = computed(() => route.name === "catalog");
/** @type {ReturnType<typeof setTimeout> | null} */
let navSearchDebounceTimer = null;

function resolveIsDark(mode) {
  if (mode === "dark") return true;
  if (mode === "light") return false;
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

function applyTheme(mode) {
  const isDark = resolveIsDark(mode);
  // We toggle the class on the root element to allow Tailwind's dark mode styles to apply
  document.documentElement.classList.toggle("dark", isDark);
  // This is needed to properly apply the correct color scheme for form controls and other native elements
  document.documentElement.style.colorScheme = isDark ? "dark" : "light";
}

// Redirect away from /admin instantly when the user logs out or loses admin role
watch(isAdmin, (admin) => {
  if (!admin && route.name === "admin") {
    router.push({ name: "catalog" });
  }
});

onMounted(() => {
  // Refresh token on load so DB role changes (e.g. ADMIN promotion) take effect without re-login
  if (isLoggedIn.value) {
    fetchMe()
      .then(({ token, user }) => setAuth(token, user))
      .catch(() => clearAuth());
  }

  const stored = localStorage.getItem(THEME_STORAGE_KEY);
  if (stored === "light" || stored === "dark" || stored === "system") {
    theme.value = stored;
  }

  applyTheme(theme.value);

  const media = window.matchMedia("(prefers-color-scheme: dark)");
  media.addEventListener("change", () => {
    if (theme.value === "system") {
      applyTheme("system");
    }
  });
});

watch(theme, (mode) => {
  localStorage.setItem(THEME_STORAGE_KEY, mode);
  applyTheme(mode);
});

watch(
  () => route.query.search,
  (search) => {
    if (typeof search === "string") {
      navSearch.value = search;
      return;
    }

    navSearch.value = "";
  },
  { immediate: true },
);

watch(navSearch, () => {
  if (navSearchDebounceTimer) {
    clearTimeout(navSearchDebounceTimer);
  }

  navSearchDebounceTimer = setTimeout(() => {
    const normalizedSearch = navSearch.value.trim();

    if (isCatalogRoute.value) {
      const currentSearch =
        typeof route.query.search === "string" ? route.query.search : "";

      if (currentSearch === normalizedSearch) {
        return;
      }

      router.push({
        query: {
          ...route.query,
          ...(normalizedSearch ? { search: normalizedSearch } : {}),
          page: "1",
        },
      });
      return;
    }

    router.push({
      name: "catalog",
      query: {
        ...(normalizedSearch ? { search: normalizedSearch } : {}),
        page: "1",
      },
    });
  }, SEARCH_DEBOUNCE_MS);
});

onBeforeUnmount(() => {
  if (navSearchDebounceTimer) {
    clearTimeout(navSearchDebounceTimer);
  }
});
</script>

<template>
  <div class="min-h-screen bg-canvas text-slate-900 dark:text-slate-100">
    <!-- Sticky header: stays visible on scroll | z-40: above content but below chat (z-50) -->
    <header
      class="sticky top-0 z-40 border-b border-black/10 bg-white/70 backdrop-blur dark:border-white/10 dark:bg-slate-900/70"
    >
      <div class="flex w-full items-center justify-between px-4 py-4 md:px-8">
        <RouterLink
          to="/"
          class="text-sm uppercase tracking-[0.35em] text-slate-700 dark:text-slate-300"
          >Wardrobe House</RouterLink
        >
        <span class="text-xs pl-3 pt-1 text-slate-500 dark:text-slate-400"
          >V1.0.0</span
        >
        <nav
          class="ml-auto flex items-center gap-3 text-sm text-slate-700 dark:text-slate-300 md:gap-5"
        >
          <!-- Desktop Menu -->
          <div class="hidden md:flex items-center gap-5">
            <RouterLink
              to="/"
              class="hover:text-amber-800 dark:hover:text-amber-400"
              >Catalog</RouterLink
            >
            <RouterLink
              v-if="isAdmin"
              to="/admin"
              class="hover:text-amber-800 dark:hover:text-amber-400"
              >Admin</RouterLink
            >
            <div v-if="isLoggedIn" class="flex items-center gap-2">
              <span
                class="flex h-7 w-7 items-center justify-center rounded-full bg-amber-700 text-xs font-semibold uppercase text-white dark:bg-amber-600"
                :title="authUser?.email"
                >{{ authUser?.email?.[0] }}</span
              >
              <button
                type="button"
                @click="clearAuth"
                class="hover:text-amber-800 dark:hover:text-amber-400"
              >
                Logout
              </button>
            </div>
            <button
              v-else
              type="button"
              @click="loginOpen = true"
              class="hover:text-amber-800 dark:hover:text-amber-400"
            >
              Login
            </button>
          </div>

          <!-- Chat Button -->
          <button
            @click="chatOpen = true"
            class="rounded-full p-2 hover:bg-slate-100 dark:hover:bg-slate-800"
            aria-label="Open Priest chat"
            title="Chat with Priest"
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
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
          </button>

          <div
            class="flex items-center gap-1 rounded-full border border-slate-300 bg-white p-1 dark:border-slate-700 dark:bg-slate-800"
            aria-label="Theme mode"
          >
            <button
              type="button"
              class="rounded-full p-1.5 transition hover:bg-slate-100 dark:hover:bg-slate-700"
              :class="
                theme === 'light'
                  ? 'bg-amber-100 text-amber-900 dark:bg-amber-500 dark:text-slate-900'
                  : ''
              "
              aria-label="Light theme"
              @click="theme = 'light'"
            >
              <svg
                viewBox="0 0 24 24"
                class="h-4 w-4"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <circle cx="12" cy="12" r="4" />
                <path d="M12 2v2" />
                <path d="M12 20v2" />
                <path d="m4.93 4.93 1.41 1.41" />
                <path d="m17.66 17.66 1.41 1.41" />
                <path d="M2 12h2" />
                <path d="M20 12h2" />
                <path d="m6.34 17.66-1.41 1.41" />
                <path d="m19.07 4.93-1.41 1.41" />
              </svg>
            </button>
            <button
              type="button"
              class="rounded-full p-1.5 transition hover:bg-slate-100 dark:hover:bg-slate-700"
              :class="
                theme === 'dark'
                  ? 'bg-amber-100 text-amber-900 dark:bg-amber-500 dark:text-slate-900'
                  : ''
              "
              aria-label="Dark theme"
              @click="theme = 'dark'"
            >
              <svg
                viewBox="0 0 24 24"
                class="h-4 w-4"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M12 3a6.7 6.7 0 1 0 9 9A8.5 8.5 0 1 1 12 3z" />
              </svg>
            </button>
            <button
              type="button"
              class="rounded-full p-1.5 transition hover:bg-slate-100 dark:hover:bg-slate-700"
              :class="
                theme === 'system'
                  ? 'bg-amber-100 text-amber-900 dark:bg-amber-500 dark:text-slate-900'
                  : ''
              "
              aria-label="System theme"
              @click="theme = 'system'"
            >
              <svg
                viewBox="0 0 24 24"
                class="h-4 w-4"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <rect x="3" y="4" width="18" height="12" rx="2" />
                <path d="M8 20h8" />
                <path d="M12 16v4" />
              </svg>
            </button>
          </div>

          <!-- Mobile Hamburger Menu -->
          <div class="relative md:hidden">
            <button
              type="button"
              @click="menuOpen = !menuOpen"
              class="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded"
              aria-label="Menu"
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
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>

            <!-- Dropdown Menu -->
            <div
              v-if="menuOpen"
              class="absolute right-0 mt-2 w-48 rounded-lg border border-slate-300 bg-white shadow-lg dark:border-slate-700 dark:bg-slate-900 z-50"
            >
              <div class="p-4 space-y-3">
                <RouterLink
                  to="/"
                  class="block text-sm hover:text-amber-800 dark:hover:text-amber-400"
                  @click="menuOpen = false"
                  >Catalog</RouterLink
                >
                <RouterLink
                  v-if="isAdmin"
                  to="/admin"
                  class="block text-sm hover:text-amber-800 dark:hover:text-amber-400"
                  @click="menuOpen = false"
                  >Admin</RouterLink
                >
                <template v-if="isLoggedIn">
                  <div class="flex items-center gap-2">
                    <span
                      class="flex h-6 w-6 items-center justify-center rounded-full bg-amber-700 text-xs font-semibold uppercase text-white dark:bg-amber-600"
                      :title="authUser?.email"
                      >{{ authUser?.email?.[0] }}</span
                    >
                    <button
                      type="button"
                      class="text-sm hover:text-amber-800 dark:hover:text-amber-400"
                      @click="
                        clearAuth();
                        menuOpen = false;
                      "
                    >
                      Logout
                    </button>
                  </div>
                </template>
                <button
                  v-else
                  type="button"
                  class="block text-sm hover:text-amber-800 dark:hover:text-amber-400"
                  @click="
                    loginOpen = true;
                    menuOpen = false;
                  "
                >
                  Login
                </button>
              </div>
            </div>
          </div>
        </nav>
      </div>
    </header>

    <RouterView />

    <!-- Chat Modal -->
    <ChatModal :isOpen="chatOpen" @close="chatOpen = false" />

    <!-- Login Modal -->
    <LoginModal :isOpen="loginOpen" @close="loginOpen = false" />
  </div>
</template>
