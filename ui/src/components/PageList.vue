<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, inject, type Ref } from 'vue';
import type { Page, Application } from '../model';
import { api } from '../api';

const props = defineProps<{
  application: Application,
  pages: Page[],
  selectedPageId: string | undefined
}>();

const emit = defineEmits<{
  (e: 'update-app', app: Application): void,
  (e: 'select-page', page: Page): void,
  (e: 'delete-page', id: string): void,
  (e: 'create-page', name: string): void,
  (e: 'update-page', page: Page): void
}>();

const localAppName = ref(props.application.name);
const showPageModal = ref(false);
const pageModalMode = ref<'create' | 'edit'>('create');
const modalPageName = ref('');
const editingPage = ref<Page | null>(null);

// Track current page id from browser session
const browserSession: Ref<{ session_id: string } | null> = inject('browserSession', ref(null));
const currentPageId = ref<string | null>(null);
let pollTimer: number | null = null;

const pollCurrentPage = async () => {
  if (!browserSession || !browserSession.value?.session_id) {
    currentPageId.value = null;
    schedulePoll();
    return;
  }
  try {
    const result = await api.getCurrentPage(browserSession.value.session_id);
    // result may be an array of pages or error
    if (Array.isArray(result) && result.length > 0 && result[0].id) {
      currentPageId.value = result[0].id;
    } else {
      currentPageId.value = null;
    }
  } catch {
    currentPageId.value = null;
  }
  schedulePoll();
};

const schedulePoll = () => {
  pollTimer && clearTimeout(pollTimer);
  pollTimer = window.setTimeout(pollCurrentPage, 1000);
};

onMounted(() => {
  pollCurrentPage();
});

onUnmounted(() => {
  pollTimer && clearTimeout(pollTimer);
});

// Keep local input synced if prop changes from outside
watch(() => props.application, (newVal) => {
  localAppName.value = newVal.name;
});

const handleAppUpdate = () => {
  emit('update-app', { ...props.application, name: localAppName.value });
};

const openCreatePageModal = () => {
  pageModalMode.value = 'create';
  modalPageName.value = '';
  editingPage.value = null;
  showPageModal.value = true;
};

const openEditPageModal = (page: Page) => {
  pageModalMode.value = 'edit';
  modalPageName.value = page.name;
  editingPage.value = page;
  showPageModal.value = true;
};

const handlePageModalSave = () => {
  if (!modalPageName.value) return;
  if (pageModalMode.value === 'create') {
    emit('create-page', modalPageName.value);
  } else if (editingPage.value) {
    emit('update-page', { ...editingPage.value, name: modalPageName.value });
  }
  showPageModal.value = false;
};

const navigateToPage = async (page: Page) => {
  if (!browserSession || !browserSession.value?.session_id) {
    alert('No browser session open');
    return;
  }
  try {
    await api.navigateToPage(browserSession.value.session_id, page.id!);
  } catch (e) {
    console.error(e);
    alert('Failed to navigate to page');
  }
};
</script>

<template>
  <div>
    <div class="d-flex align-items-center justify-content-between mb-2">
      <h5 class="mb-0">Pages</h5>
      <button class="btn btn-outline-primary btn-sm" title="Add Page" @click="openCreatePageModal">
        <i class="bi bi-plus"></i>
      </button>
    </div>

    <ul class="list-group mb-3">
      <li v-for="page in pages" :key="page.id"
        class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
        :class="{ active: selectedPageId === page.id }" @click="emit('select-page', page)">
        <span class="d-flex align-items-center">
          {{ page.name }}
          <span v-if="currentPageId === page.id" class="badge bg-info ms-2">Current</span>

        </span>
        <span class="btn-group btn-group-sm column-gap-1">
          <button v-if="page.can_be_navigated_to" class="btn btn-secondary btn-sm ms-2" title="Navigate to Page"
            @click.stop="navigateToPage(page)">
            <i class="bi bi-globe"></i>
          </button>
          <button class="btn btn-secondary" title="Edit" @click.stop="openEditPageModal(page)">
            <i class="bi bi-pencil"></i>
          </button>
          <button class="btn btn-danger" title="Delete" @click.stop="emit('delete-page', page.id!)">
            <i class="bi bi-trash"></i>
          </button>
        </span>
      </li>
    </ul>

    <!-- Page Create/Edit Modal -->
    <dialog class="modal fade" :class="{ show: showPageModal }"
      :style="showPageModal ? 'display: block; background: rgba(0,0,0,0.5);' : 'display: none;'" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ pageModalMode === 'create' ? 'Create Page' : 'Edit Page' }}</h5>
            <button type="button" class="btn-close" @click="showPageModal = false"></button>
          </div>
          <form @submit.prevent="handlePageModalSave">
            <div class="modal-body">
              <input v-model="modalPageName" class="form-control" placeholder="Page Name" required>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="showPageModal = false">Cancel</button>
              <button type="submit" class="btn btn-primary">Save</button>
            </div>
          </form>
        </div>
      </div>
    </dialog>
  </div>
</template>