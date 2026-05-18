<script setup>
import { ref } from "vue";
import { login, register } from "../api/client";
import { setAuth } from "../stores/auth";

const props = defineProps({ isOpen: Boolean });
const emit = defineEmits(["close"]);

const mode = ref("login");
const email = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);

function switchMode(to) {
  mode.value = to;
  error.value = "";
}

async function submit() {
  error.value = "";
  loading.value = true;
  try {
    const fn = mode.value === "login" ? login : register;
    const res = await fn(email.value.trim(), password.value);
    setAuth(res.token, res.user);
    email.value = "";
    password.value = "";
    emit("close");
  } catch (e) {
    const msg = e?.response?.data?.message;
    error.value = msg ?? (mode.value === "login" ? "Login failed. Check your credentials." : "Registration failed.");
  } finally {
    loading.value = false;
  }
}

function close() {
  error.value = "";
  emit("close");
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="props.isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="close"
    >
      <div
        class="w-full max-w-sm rounded-xl border border-slate-200 bg-white p-8 shadow-2xl dark:border-slate-700 dark:bg-slate-900"
      >
        <div class="mb-6 flex items-center justify-between">
          <h2 class="text-lg font-semibold text-slate-900 dark:text-slate-100">
            {{ mode === "login" ? "Sign in" : "Create account" }}
          </h2>
          <button
            type="button"
            @click="close"
            class="rounded p-1 hover:bg-slate-100 dark:hover:bg-slate-800"
            aria-label="Close"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Tab toggle -->
        <div class="mb-6 flex rounded-lg border border-slate-200 p-1 dark:border-slate-700">
          <button
            type="button"
            @click="switchMode('login')"
            class="flex-1 rounded-md py-1.5 text-sm font-medium transition"
            :class="mode === 'login'
              ? 'bg-amber-700 text-white dark:bg-amber-600'
              : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100'"
          >Sign in</button>
          <button
            type="button"
            @click="switchMode('register')"
            class="flex-1 rounded-md py-1.5 text-sm font-medium transition"
            :class="mode === 'register'
              ? 'bg-amber-700 text-white dark:bg-amber-600'
              : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100'"
          >Sign up</button>
        </div>

        <form @submit.prevent="submit" class="space-y-4">
          <div>
            <label class="mb-1 block text-sm text-slate-700 dark:text-slate-300">Email</label>
            <input
              v-model="email"
              type="email"
              required
              autocomplete="email"
              class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
            />
          </div>
          <div>
            <label class="mb-1 block text-sm text-slate-700 dark:text-slate-300">Password</label>
            <input
              v-model="password"
              type="password"
              required
              :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
              class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
            />
            <p v-if="mode === 'register'" class="mt-1 text-xs text-slate-500 dark:text-slate-400">
              At least 8 characters
            </p>
          </div>

          <div
            v-if="error"
            class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-900/30 dark:text-red-400"
          >
            {{ error }}
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full rounded-lg bg-amber-700 px-4 py-2 text-sm font-medium text-white transition hover:bg-amber-800 disabled:opacity-50 dark:bg-amber-600 dark:hover:bg-amber-700"
          >
            <span v-if="loading">{{ mode === "login" ? "Signing in…" : "Creating account…" }}</span>
            <span v-else>{{ mode === "login" ? "Sign in" : "Create account" }}</span>
          </button>
        </form>
      </div>
    </div>
  </Teleport>
</template>
