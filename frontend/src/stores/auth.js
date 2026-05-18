import { ref, computed } from "vue";

/**
 * @typedef {{ id: number, email: string, role: "USER" | "ADMIN" }} AuthUser
 */

const TOKEN_KEY = "wardrobe-auth-token";

/** @type {import("vue").Ref<string | null>} */
export const authToken = ref(null);

/** @type {import("vue").Ref<AuthUser | null>} */
export const authUser = ref(null);

export const isAdmin = computed(() => authUser.value?.role === "ADMIN");
export const isLoggedIn = computed(() => authUser.value !== null);

/**
 * @param {string} token
 * @param {AuthUser} user
 */
export function setAuth(token, user) {
  authToken.value = token;
  authUser.value = user;
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearAuth() {
  authToken.value = null;
  authUser.value = null;
  localStorage.removeItem(TOKEN_KEY);
}

// Restore session from localStorage on app load
const stored = localStorage.getItem(TOKEN_KEY);
if (stored) {
  try {
    const payload = JSON.parse(atob(stored.split(".")[1]));
    if (payload.exp * 1000 > Date.now()) {
      authToken.value = stored;
      authUser.value = { id: payload.sub, email: payload.email, role: payload.role };
    } else {
      localStorage.removeItem(TOKEN_KEY);
    }
  } catch {
    localStorage.removeItem(TOKEN_KEY);
  }
}
