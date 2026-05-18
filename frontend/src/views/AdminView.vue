<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import {
  createProduct,
  deleteProduct,
  getAdminProducts,
  getMeta,
  uploadProductImages,
  updateProduct,
} from "../api/client";

const categories = ref([]);
const eras = ref([]);
const products = ref([]);
const loading = ref(true);
const busy = ref(false);
const message = ref("");
const uploadMessage = ref("");
const editingId = ref(null);

const form = reactive({
  name: "",
  description: "",
  aisle: "",
  quantity: 1,
  categorySlug: "",
  eraSlug: "",
  imagesText: "",
});

const submitLabel = computed(() =>
  editingId.value ? "Update product" : "Create product",
);
const imagePreviewUrls = computed(() =>
  form.imagesText
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean),
);

// Hydrate form fields from a product, or reset to defaults if no product is given
function hydrateForm(product) {
  form.name = product?.name ?? "";
  form.description = product?.description ?? "";
  form.aisle = product?.aisle ?? "";
  form.quantity = product?.quantity ?? 1;
  form.categorySlug = product?.category.slug ?? categories.value[0]?.slug ?? "";
  form.eraSlug = product?.era.slug ?? eras.value[0]?.slug ?? "";
  form.imagesText = product
    ? product.images.map((image) => image.url).join("\n")
    : "";
}

async function refresh() {
  const [meta, adminProducts] = await Promise.all([
    getMeta(),
    getAdminProducts(),
  ]);
  categories.value = meta.categories;
  eras.value = meta.eras;
  products.value = adminProducts;
  if (!form.categorySlug && categories.value[0])
    form.categorySlug = categories.value[0].slug;
  if (!form.eraSlug && eras.value[0]) form.eraSlug = eras.value[0].slug;
}

function resetForm() {
  editingId.value = null;
  uploadMessage.value = "";
  hydrateForm();
}

async function handleFileUpload(event) {
  const input = event.target;
  const selectedFiles = Array.from(input.files ?? []);
  if (selectedFiles.length === 0) {
    return;
  }

  busy.value = true;
  uploadMessage.value = "Uploading images...";

  try {
    const uploaded = await uploadProductImages(selectedFiles);
    const nextUrls = uploaded.map((file) => file.url);
    form.imagesText = [form.imagesText, ...nextUrls].filter(Boolean).join("\n");
    uploadMessage.value = `${uploaded.length} image${uploaded.length > 1 ? "s" : ""} uploaded.`;
    input.value = "";
  } catch (uploadError) {
    console.error(uploadError);
    uploadMessage.value =
      "Image upload failed. Use JPG, PNG, GIF, or WEBP under 5 MB.";
  } finally {
    busy.value = false;
  }
}

async function submitForm() {
  busy.value = true;
  message.value = "";
  try {
    const images = form.imagesText
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean)
      .map((url, index) => ({ url, sortOrder: index }));

    const payload = {
      name: form.name,
      description: form.description,
      aisle: form.aisle,
      quantity: form.quantity,
      categorySlug: form.categorySlug,
      eraSlug: form.eraSlug,
      images,
    };

    if (editingId.value) {
      await updateProduct(editingId.value, payload);
      message.value = "Product updated.";
    } else {
      await createProduct(payload);
      message.value = "Product created.";
    }

    await refresh();
    resetForm();
  } catch (submitError) {
    console.error(submitError);
    message.value = "Save failed. Check inputs and try again.";
  } finally {
    busy.value = false;
  }
}

function startEdit(product) {
  editingId.value = product.id;
  hydrateForm(product);
}

async function removeProduct(id) {
  if (!confirm("Delete this product?")) return;
  busy.value = true;
  message.value = "";
  try {
    await deleteProduct(id);
    message.value = "Product deleted.";
    await refresh();
    if (editingId.value === id) resetForm();
  } catch (removeError) {
    console.error(removeError);
    message.value = "Delete failed.";
  } finally {
    busy.value = false;
  }
}

onMounted(async () => {
  try {
    await refresh();
    hydrateForm();
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <main class="mx-auto w-full max-w-7xl px-4 py-8 md:px-8 md:py-10">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-3xl font-semibold text-slate-900">Admin Products</h1>
      <RouterLink
        to="/"
        class="text-sm font-medium text-amber-800 hover:text-amber-900 dark:text-amber-400 dark:hover:text-amber-300"
        >Back to catalog</RouterLink
      >
    </div>

    <div class="grid gap-6 lg:grid-cols-[1.1fr,1.7fr]">
      <section
        class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900"
      >
        <h2 class="text-lg font-semibold text-slate-900 dark:text-slate-100">
          {{ submitLabel }}
        </h2>
        <p class="mt-1 text-sm text-slate-600 dark:text-slate-400">
          Add or edit product inventory, then upload local gallery images or
          paste image URLs.
        </p>

        <form class="mt-4 space-y-3" @submit.prevent="submitForm">
          <input
            v-model="form.name"
            required
            placeholder="Product name"
            class="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
          />
          <textarea
            v-model="form.description"
            required
            rows="4"
            placeholder="Description"
            class="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
          />
          <div class="grid grid-cols-2 gap-3">
            <input
              v-model="form.aisle"
              type="text"
              required
              placeholder="Aisle location"
              class="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
            />
            <input
              v-model.number="form.quantity"
              type="number"
              min="0"
              step="1"
              required
              placeholder="Quantity"
              class="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
            />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <select
              v-model="form.categorySlug"
              class="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
            >
              <option
                v-for="category in categories"
                :key="category.id"
                :value="category.slug"
              >
                {{ category.name }}
              </option>
            </select>
            <select
              v-model="form.eraSlug"
              class="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
            >
              <option v-for="era in eras" :key="era.id" :value="era.slug">
                {{ era.name }}
              </option>
            </select>
          </div>
          <textarea
            v-model="form.imagesText"
            required
            rows="4"
            placeholder="Image URLs, one per line"
            class="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
          />
          <div
            class="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-950"
          >
            <label
              class="block text-sm font-medium text-slate-800 dark:text-slate-200"
              >Upload local images</label
            >
            <p class="mt-1 text-xs text-slate-600 dark:text-slate-400">
              Selected files are uploaded to the backend and appended to the
              gallery URL list.
            </p>
            <input
              class="mt-3 block w-full text-sm text-slate-700 file:mr-4 file:rounded-lg file:border-0 file:bg-slate-900 file:px-3 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-slate-700"
              type="file"
              accept="image/png,image/jpeg,image/webp,image/gif"
              multiple
              :disabled="busy"
              @change="handleFileUpload"
            />
            <p v-if="uploadMessage" class="mt-2 text-xs text-amber-800">
              {{ uploadMessage }}
            </p>
          </div>
          <div
            v-if="imagePreviewUrls.length > 0"
            class="grid grid-cols-3 gap-3 md:grid-cols-4"
          >
            <img
              v-for="url in imagePreviewUrls"
              :key="url"
              :src="url"
              alt="Preview"
              class="h-20 w-full rounded-xl object-cover"
            />
          </div>
          <div class="flex gap-2">
            <button
              :disabled="busy"
              type="submit"
              class="rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50 dark:bg-amber-600 dark:text-slate-900 dark:hover:bg-amber-500"
            >
              {{ submitLabel }}
            </button>
            <button
              :disabled="busy"
              type="button"
              class="rounded-xl border border-slate-300 px-4 py-2.5 text-sm dark:border-slate-700 dark:text-slate-200"
              @click="resetForm"
            >
              Reset
            </button>
          </div>
        </form>

        <p v-if="message" class="mt-3 text-sm text-amber-800">{{ message }}</p>
      </section>

      <section
        class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900"
      >
        <h2 class="text-lg font-semibold text-slate-900 dark:text-slate-100">
          Current Inventory
        </h2>
        <p class="mt-1 text-sm text-slate-600 dark:text-slate-400">
          {{ products.length }} products
        </p>

        <div
          v-if="loading"
          class="mt-4 text-sm text-slate-600 dark:text-slate-400"
        >
          Loading products...
        </div>
        <div v-else class="mt-4 space-y-3">
          <article
            v-for="product in products"
            :key="product.id"
            class="rounded-xl border border-slate-200 p-4 dark:border-slate-800"
          >
            <div class="flex items-start justify-between gap-4">
              <div>
                <h3 class="font-medium text-slate-900 dark:text-slate-100">
                  {{ product.name }}
                </h3>
                <p class="text-sm text-slate-600 dark:text-slate-400">
                  {{ product.category.name }} • {{ product.era.name }} • Aisle
                  {{ product.aisle }}
                </p>
              </div>
              <div class="flex gap-2">
                <button
                  class="rounded-lg border border-slate-300 px-3 py-1.5 text-xs dark:border-slate-700 dark:text-slate-200"
                  @click="startEdit(product)"
                >
                  Edit
                </button>
                <button
                  class="rounded-lg border border-red-300 px-3 py-1.5 text-xs text-red-700"
                  @click="removeProduct(product.id)"
                >
                  Delete
                </button>
              </div>
            </div>
          </article>
        </div>
      </section>
    </div>
  </main>
</template>
