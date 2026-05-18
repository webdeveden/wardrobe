import { ref, computed } from "vue";
import { sendChatMessage } from "../api/client";

/**
 * @typedef {import("./types.js").ChatMessage} ChatMessage
 */

/** @type {import("vue").Ref<import("../types.js").ChatMessage[]>} */
export const chatMessages = ref([]);
export const chatLoading = ref(false);
export const chatError = ref("");

let messageIdCounter = 0;

function generateMessageId() {
  return `msg-${++messageIdCounter}`;
}

export const hasMessages = computed(() => chatMessages.value.length > 0);

/**
 * @param {string} content
 * @returns {Promise<void>}
 */
export async function sendMessage(content) {
  if (!content.trim()) return;

  /** @type {import("../types.js").ChatMessage} */
  const userMessage = {
    id: generateMessageId(),
    role: "user",
    content: content.trim(),
    timestamp: new Date(),
  };

  chatMessages.value.push(userMessage);
  chatLoading.value = true;
  chatError.value = "";

  try {
    const response = await sendChatMessage(content);

    /** @type {import("../types.js").ChatMessage} */
    const assistantMessage = {
      id: generateMessageId(),
      role: "assistant",
      content: response.reply,
      recommendedProducts: response.recommendedProducts,
      timestamp: new Date(),
    };

    chatMessages.value.push(assistantMessage);
  } catch (error) {
    chatError.value =
      error instanceof Error ? error.message : "Failed to send message";
    console.error("Chat error:", error);
  } finally {
    chatLoading.value = false;
  }
}

export function clearChat() {
  chatMessages.value = [];
  chatError.value = "";
  messageIdCounter = 0;
}
