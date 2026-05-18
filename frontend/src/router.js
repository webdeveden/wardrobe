import { createRouter, createWebHistory } from "vue-router";
import CatalogView from "./views/CatalogView.vue";
import ProductDetailView from "./views/ProductDetailView.vue";
import AdminView from "./views/AdminView.vue";
import { isAdmin } from "./stores/auth";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "catalog",
      component: CatalogView,
    },
    {
      path: "/products/:slug",
      name: "product-detail",
      component: ProductDetailView,
    },
    {
      path: "/admin",
      name: "admin",
      component: AdminView,
      meta: { requiresAdmin: true },
    },
  ],
});

router.beforeEach((to) => {
  if (to.meta.requiresAdmin && !isAdmin.value) {
    return { name: "catalog" };
  }
});
