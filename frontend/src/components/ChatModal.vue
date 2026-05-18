<script setup>
import { ref, computed, watch, nextTick } from "vue";
import { useRouter } from "vue-router";
import { marked } from "marked";
import {
  chatMessages,
  chatLoading,
  chatError,
  sendMessage,
  clearChat,
} from "../stores/chat";

const props = defineProps({ isOpen: Boolean });
const emit = defineEmits(["close"]);
const router = useRouter();

const messageInput = ref("");
const messagesContainer = ref(null);

// Scroll to bottom when new messages arrive
watch(
  () => chatMessages.value.length,
  async () => {
    await nextTick();
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  },
);

async function handleSendMessage() {
  if (!messageInput.value.trim()) return;

  const message = messageInput.value;
  messageInput.value = "";

  await sendMessage(message);
}

function handleKeyDown(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    handleSendMessage();
  }
}

function handleClose() {
  clearChat();
  messageInput.value = "";
  emit("close");
}

function viewProduct(slug) {
  router.push({ name: "product-detail", params: { slug } });
}

function renderMarkdown(content) {
  return marked.parse(content);
}

// Intercept clicks on /products/ links rendered inside markdown so the router
// handles navigation instead of triggering a full page reload.
function handleContentClick(event) {
  const link = event.target?.closest("a");
  if (!link) return;
  const href = link.getAttribute("href");
  if (!href?.startsWith("/products/")) return;
  event.preventDefault();
  router.push(href);
}

// Only show product cards for items the AI actually mentioned by name.
function mentionedProducts(content, products) {
  const lower = content.toLowerCase();
  return products.filter((p) => lower.includes(p.name.toLowerCase()));
}

const hasMessages = computed(() => chatMessages.value.length > 0);
</script>

<template>
  <!-- Mobile overlay - semi-transparent dark background (hidden on desktop) -->
  <div
    v-if="isOpen"
    class="fixed inset-0 z-40 bg-black/50 md:hidden"
    @click="handleClose"
  ></div>

  <!-- Chat modal: full-screen on mobile, vertically centered panel on desktop -->
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex flex-col bg-white dark:bg-slate-900 md:inset-auto md:right-0 md:top-[calc(50vh+35px)] md:h-[85vh] md:w-[420px] md:-translate-y-1/2 md:rounded-lg md:border-l-2 md:border-slate-300 md:shadow-2xl md:dark:border-slate-600"
  >
    <!-- Header: Title and close button -->
    <!-- flex items-center justify-between: space between title and close button -->
    <!-- border-b: bottom border separator | px-6 py-4: padding -->
    <div
      class="flex items-center justify-between border-b border-slate-200 px-6 py-4 dark:border-slate-800"
    >
      <div class="flex items-center gap-3">
        <div class="text-2xl">🧑‍⚖️</div>
        <div>
          <h2 class="text-lg font-semibold text-slate-900 dark:text-white">
            Priest
          </h2>
          <p class="text-xs text-slate-500 dark:text-slate-400">
            Your AI Wardrobe Assistant
          </p>
        </div>
      </div>
      <button
        @click="handleClose"
        class="rounded-lg p-2 hover:bg-slate-100 dark:hover:bg-slate-800"
        aria-label="Close chat"
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
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </div>

    <!-- Messages container: flex-1 takes remaining space, overflow-y-auto allows scrolling -->
    <!-- space-y-4: vertical spacing between messages | px-6 py-4: padding -->
    <div
      ref="messagesContainer"
      class="flex-1 overflow-y-auto space-y-4 px-6 py-4"
    >
      <!-- Empty state: centered welcome message when no messages -->
      <div v-if="!hasMessages" class="flex h-full items-center justify-center">
        <div class="text-center">
          <div class="mb-3 text-4xl">👋</div>
          <p class="text-slate-600 dark:text-slate-300">
            Hi! I'm Priest, your AI wardrobe assistant.
          </p>
          <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">
            Ask me about products, get recommendations, or ask for styling
            advice!
          </p>
        </div>
      </div>

      <!-- Messages list -->
      <div v-for="message in chatMessages" :key="message.id" class="space-y-2">
        <!-- User message: right-aligned with amber background -->
        <!-- flex justify-end: align to right | max-w-xs: limit width to prevent overflow -->
        <div v-if="message.role === 'user'" class="flex justify-end">
          <div class="max-w-xs rounded-2xl bg-amber-600 px-4 py-2 text-white">
            {{ message.content }}
          </div>
        </div>

        <!-- Assistant message: left-aligned with slate background -->
        <div v-else class="flex justify-start">
          <div class="max-w-xs space-y-2">
            <!-- Message bubble rendered as markdown -->
            <div
              class="prose-chat rounded-2xl bg-slate-100 px-4 py-2 text-slate-900 dark:bg-slate-800 dark:text-slate-100"
              v-html="renderMarkdown(message.content)"
              @click="handleContentClick"
            />

            <!-- Product cards: only for products the AI actually mentioned by name -->
            <template v-if="message.recommendedProducts">
              <div
                v-if="
                  mentionedProducts(
                    message.content,
                    message.recommendedProducts,
                  ).length > 0
                "
                class="grid grid-cols-2 gap-2"
              >
                <button
                  v-for="product in mentionedProducts(
                    message.content,
                    message.recommendedProducts,
                  )"
                  :key="product.id"
                  @click="viewProduct(product.slug)"
                  class="rounded-lg border border-slate-200 bg-slate-50 p-2 text-left text-xs transition hover:border-amber-400 hover:bg-amber-50 dark:border-slate-700 dark:bg-slate-800 dark:hover:border-amber-500 dark:hover:bg-slate-700"
                >
                  <p class="font-medium text-slate-900 dark:text-white">
                    {{ product.name }}
                  </p>
                  <span class="mt-1 block text-amber-600 dark:text-amber-400"
                    >View →</span
                  >
                </button>
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- Loading state: animated dots -->
      <!-- animate-bounce: CSS animation | animation-delay-*: staggered animation timing -->
      <div v-if="chatLoading" class="flex justify-start">
        <div class="space-y-2">
          <div class="flex gap-2">
            <div class="h-2 w-2 animate-bounce rounded-full bg-slate-400"></div>
            <div
              class="animation-delay-100 h-2 w-2 animate-bounce rounded-full bg-slate-400"
            ></div>
            <div
              class="animation-delay-200 h-2 w-2 animate-bounce rounded-full bg-slate-400"
            ></div>
          </div>
        </div>
      </div>

      <!-- Error state: red alert box -->
      <!-- border border-red-200: red border | bg-red-50: light red background | dark mode support -->
      <div
        v-if="chatError"
        class="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-900/20 dark:text-red-400"
      >
        {{ chatError }}
      </div>
    </div>

    <!-- Input area: sticky at bottom with border-top separator -->
    <!-- border-t: top border separator | px-6 py-4: padding -->
    <div class="border-t border-slate-200 px-6 py-4 dark:border-slate-800">
      <!-- flex gap-3: horizontal layout with spacing between input and button -->
      <div class="flex gap-3">
        <!-- Text input field -->
        <!-- flex-1: takes remaining space | focus:border-amber-600: highlight on focus -->
        <!-- disabled:opacity-50: faded when loading | dark mode support -->
        <input
          v-model="messageInput"
          type="text"
          placeholder="Ask me anything..."
          @keydown="handleKeyDown"
          :disabled="chatLoading"
          class="flex-1 rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm focus:border-amber-600 focus:outline-none disabled:opacity-50 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
        />
        <!-- Send button with icon -->
        <!-- disabled: when loading or input empty | hover:bg-amber-700: darker on hover -->
        <!-- disabled:cursor-not-allowed: show disabled cursor | disabled:opacity-50: faded when disabled -->
        <button
          @click="handleSendMessage"
          :disabled="chatLoading || !messageInput.trim()"
          class="rounded-xl bg-amber-600 px-4 py-2 text-white hover:bg-amber-700 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-amber-600 dark:hover:bg-amber-700"
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
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animation-delay-100 {
  animation-delay: 0.1s;
}
.animation-delay-200 {
  animation-delay: 0.2s;
}

.prose-chat :deep(p) {
  margin: 0;
}
.prose-chat :deep(p + p) {
  margin-top: 0.4rem;
}
.prose-chat :deep(strong) {
  font-weight: 600;
}
.prose-chat :deep(em) {
  font-style: italic;
}
.prose-chat :deep(ul) {
  list-style: disc;
  padding-left: 1.2rem;
  margin: 0.3rem 0;
}
.prose-chat :deep(ol) {
  list-style: decimal;
  padding-left: 1.2rem;
  margin: 0.3rem 0;
}
.prose-chat :deep(li + li) {
  margin-top: 0.2rem;
}
.prose-chat :deep(a) {
  color: #d97706;
  text-decoration: underline;
}
.prose-chat :deep(a:hover) {
  color: #b45309;
}
.prose-chat :deep(code) {
  background: rgba(0, 0, 0, 0.08);
  border-radius: 3px;
  padding: 0.1em 0.3em;
  font-size: 0.85em;
}
</style>
