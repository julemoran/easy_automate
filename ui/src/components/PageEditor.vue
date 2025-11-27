<script setup lang="ts">
import { ref, watch, inject, provide, type Ref, toRaw } from 'vue';
import type { Page, Selector } from '../model';
import { api } from '../api';
import SelectorList from './SelectorList.vue';


const browserSession: Ref<{session_id: string} | null>  = inject('browserSession', ref(null));

const props = defineProps<{
  page: Page
}>();

const emit = defineEmits<(e: 'save', page: Page) => void>();

// Create a local copy to edit
const localPage = ref<Page>({ ...props.page });

// Watch for prop changes to switch selected page
watch(() => props.page, (newVal) => {
  // Use JSON.parse/stringify for deep clone to avoid structuredClone errors
  localPage.value = JSON.parse(JSON.stringify(newVal));
});


const addSelector = (type: 'identifying' | 'interactive') => {
  const newSel: Selector = { alias: '', xpath: '', visible: null };
  if (type === 'identifying') localPage.value.identifying_selectors.push(newSel);
  else localPage.value.interactive_selectors.push(newSel);
};

const cloneSelector = (type: 'identifying' | 'interactive', idx: number) => {
  if (type === 'identifying') {
    const sel = localPage.value.identifying_selectors[idx];
    if (sel) {
      const newSel = JSON.parse(JSON.stringify(sel));
      localPage.value.identifying_selectors.push(newSel);
    }
  } else {
    const sel = localPage.value.interactive_selectors[idx];
    if (sel) {
      const newSel = JSON.parse(JSON.stringify(sel));
      localPage.value.interactive_selectors.push(newSel);
    }
  }
};

const updateSelector = (type: 'identifying' | 'interactive', selector: Selector, index: number) => {
  if (type === 'identifying') {
    localPage.value.identifying_selectors.splice(index, 1, selector);
  } else {
    localPage.value.interactive_selectors.splice(index, 1, selector);
  }
};

const removeSelector = (type: 'identifying' | 'interactive', index: number) => {
  if (type === 'identifying') localPage.value.identifying_selectors.splice(index, 1);
  else localPage.value.interactive_selectors.splice(index, 1);
};

const save = () => {
  emit('save', localPage.value);
};

const navigateToPage = async () => {
  if (!browserSession || !browserSession.value?.session_id) {
    alert('No browser session open');
    return;
  }
  try {
    await api.navigateToPage(browserSession.value.session_id, localPage.value.id!);
  } catch (e) {
    console.error(e);
    alert('Failed to navigate to page');
  }
};

// Show DOM modal logic
const showDomModal = ref(false);
const domContent = ref('');
const domLoading = ref(false);
const domError = ref('');

const showCleanedDomModal = ref(false);
const cleanedDomContent = ref('');
const cleanedDomLoading = ref(false);
const cleanedDomError = ref('');

// Check Selectors modal logic
const showCheckSelectorsModal = ref(false);
const checkSelectorsContent = ref('');
const checkSelectorsLoading = ref(false);
const checkSelectorsError = ref('');

const fetchCheckSelectors = async () => {
  checkSelectorsError.value = '';
  checkSelectorsContent.value = '';
  if (!browserSession || !browserSession.value?.session_id) {
    checkSelectorsError.value = 'No browser session open';
    showCheckSelectorsModal.value = true;
    return;
  }
  checkSelectorsLoading.value = true;
  showCheckSelectorsModal.value = true;
  try {
    const result = await api.checkSelectors(browserSession.value.session_id);
    checkSelectorsContent.value = JSON.stringify(result, null, 2);
  } catch (e) {
    checkSelectorsError.value = 'Failed to fetch check-selectors output';
  } finally {
    checkSelectorsLoading.value = false;
  }
};
const fetchDom = async () => {
  domError.value = '';
  domContent.value = '';
  if (!browserSession || !browserSession.value?.session_id) {
    domError.value = 'No browser session open';
    showDomModal.value = true;
    return;
  }
  domLoading.value = true;
  showDomModal.value = true;
  try {
    const dom = await api.getDom(browserSession.value.session_id);
    domContent.value = dom;
  } catch (e) {
    domError.value = 'Failed to fetch DOM';
  } finally {
    domLoading.value = false;
  }
};

const fetchCleanedDom = async () => {
  cleanedDomError.value = '';
  cleanedDomContent.value = '';
  if (!browserSession || !browserSession.value?.session_id) {
    cleanedDomError.value = 'No browser session open';
    showCleanedDomModal.value = true;
    return;
  }
  cleanedDomLoading.value = true;
  showCleanedDomModal.value = true;
  try {
    const dom = await api.getCleanedDom(browserSession.value.session_id);
    cleanedDomContent.value = dom;
  } catch (e) {
    cleanedDomError.value = 'Failed to fetch cleaned DOM';
  } finally {
    cleanedDomLoading.value = false;
  }
};

provide('pageId', localPage.value.id ?? null);
</script>

<template>
  <div>
    <div class="d-flex align-items-center mb-2">
      <h4 class="me-3">Edit Page: {{ localPage.name }}</h4>
      <button
        v-if="localPage.can_be_navigated_to"
        class="btn btn-outline-primary btn-sm"
        type="button"
        @click="navigateToPage"
      >
        Navigate to Page
      </button>
      <button
        class="btn btn-outline-info btn-sm ms-2"
        type="button"
        @click="fetchDom"
        title="Show DOM"
      >
        Show DOM
      </button>
      <button
        class="btn btn-outline-warning btn-sm ms-2"
        type="button"
        @click="fetchCleanedDom"
        title="Show Cleaned DOM"
      >
        Show Cleaned DOM
      </button>
        <button
          class="btn btn-outline-secondary btn-sm ms-2"
          type="button"
          @click="fetchCheckSelectors"
          title="Show Check Selectors Output"
        >
          Check Selectors
        </button>
    </div>
    <form @submit.prevent="save">
      <div class="form-group">
        <label for="editPageName">Name</label>
        <input id="editPageName" v-model="localPage.name" class="form-control" required>
      </div>
      <div class="form-group">
        <label for="editPageUrl">URL</label>
        <input id="editPageUrl" v-model="localPage.url" class="form-control">
      </div>
      <div class="form-check mb-3">
        <input type="checkbox" v-model="localPage.can_be_navigated_to" class="form-check-input" id="editPageNav">
        <label class="form-check-label" for="editPageNav">Can be navigated to</label>
      </div>

      <SelectorList
        :selectors="localPage.identifying_selectors"
        type="identifying"
        title="Identifying Selectors"
        :page-id="localPage.id ?? null"
        @add="() => addSelector('identifying')"
        @update="(selector, idx) => updateSelector('identifying', selector, idx)"
        @remove="idx => removeSelector('identifying', idx)"
        @clone="idx => cloneSelector('identifying', idx)"
      />

      <SelectorList
        :selectors="localPage.interactive_selectors"
        type="interactive"
        title="Interactive Selectors"
        :page-id="localPage.id ?? null"
        @add="() => addSelector('interactive')"
        @update="(selector, idx) => updateSelector('interactive', selector, idx)"
        @remove="idx => removeSelector('interactive', idx)"
        @clone="idx => cloneSelector('interactive', idx)"
      />

      <div>
        <button type="submit" class="btn btn-success">Save Changes</button>
      </div>
    </form>

    <!-- DOM Modal -->
    <dialog class="modal fade" :class="{ show: showDomModal }" :style="showDomModal ? 'display: block; background: rgba(0,0,0,0.5);' : 'display: none;'" tabindex="-1">
      <div class="modal-dialog modal-xl modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Page DOM</h5>
            <button type="button" class="btn-close" @click="showDomModal = false"></button>
          </div>
          <div class="modal-body" style="max-height: 70vh; overflow-y: auto;">
            <div v-if="domLoading" class="text-center py-3">
              <span class="spinner-border"></span> Loading DOM...
            </div>
            <div v-else-if="domError" class="alert alert-danger">{{ domError }}</div>
            <pre v-else style="white-space: pre-wrap; word-break: break-all; background: #f8f9fa; padding: 1em; border-radius: 4px;">
              {{ domContent }}
            </pre>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showDomModal = false">Close</button>
          </div>
        </div>
      </div>
    </dialog>

    <!-- Cleaned DOM Modal -->
    <dialog class="modal fade" :class="{ show: showCleanedDomModal }" :style="showCleanedDomModal ? 'display: block; background: rgba(0,0,0,0.5);' : 'display: none;'" tabindex="-1">
      <div class="modal-dialog modal-xl modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Cleaned Page DOM</h5>
            <button type="button" class="btn-close" @click="showCleanedDomModal = false"></button>
          </div>
          <div class="modal-body" style="max-height: 70vh; overflow-y: auto;">
            <div v-if="cleanedDomLoading" class="text-center py-3">
              <span class="spinner-border"></span> Loading Cleaned DOM...
            </div>
            <div v-else-if="cleanedDomError" class="alert alert-danger">{{ cleanedDomError }}</div>
            <pre v-else style="white-space: pre-wrap; word-break: break-all; background: #f8f9fa; padding: 1em; border-radius: 4px;">
              {{ cleanedDomContent }}
            </pre>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showCleanedDomModal = false">Close</button>
          </div>
        </div>
      </div>
    </dialog>
  </div>
      <!-- Check Selectors Modal -->
      <dialog class="modal fade" :class="{ show: showCheckSelectorsModal }" :style="showCheckSelectorsModal ? 'display: block; background: rgba(0,0,0,0.5);' : 'display: none;'" tabindex="-1">
        <div class="modal-dialog modal-xl modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Check Selectors Output</h5>
              <button type="button" class="btn-close" @click="showCheckSelectorsModal = false"></button>
            </div>
            <div class="modal-body" style="max-height: 70vh; overflow-y: auto;">
              <div v-if="checkSelectorsLoading" class="text-center py-3">
                <span class="spinner-border"></span> Loading Check Selectors Output...
              </div>
              <div v-else-if="checkSelectorsError" class="alert alert-danger">{{ checkSelectorsError }}</div>
              <pre v-else style="white-space: pre-wrap; word-break: break-all; background: #f8f9fa; padding: 1em; border-radius: 4px;">
                {{ checkSelectorsContent }}
              </pre>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="showCheckSelectorsModal = false">Close</button>
            </div>
          </div>
        </div>
      </dialog>
</template>