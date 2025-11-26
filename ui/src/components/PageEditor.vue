<script setup lang="ts">
import { ref, watch, toRaw, inject, type Ref } from 'vue';
import type { Page, Selector } from '../model';
import { api } from '../api';
import TristateCheckbox from './TriStateCheckbox.vue';

const browserSession: Ref<{session_id: string} | null>  = inject('browserSession', ref(null));

const props = defineProps<{
  page: Page
}>();

const emit = defineEmits<{
  (e: 'save', page: Page): void
}>();

// Create a local copy to edit
const localPage = ref<Page>({ ...props.page });

// Watch for prop changes to switch selected page
watch(() => props.page, (newVal) => {
  // JSON parse/stringify is a quick way to deep clone to break reference
  localPage.value = JSON.parse(JSON.stringify(newVal));
});

const addSelector = (type: 'identifying' | 'interactive') => {
  const newSel: Selector = { alias: '', xpath: '', visible: null };
  if (type === 'identifying') localPage.value.identifying_selectors.push(newSel);
  else localPage.value.interactive_selectors.push(newSel);
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
    alert('Navigation command sent!');
  } catch (e) {
    alert('Failed to navigate to page');
  }
};
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
    </div>
    <form @submit.prevent="save">
      <div class="form-group">
        <label>Name</label>
        <input v-model="localPage.name" class="form-control" required>
      </div>
      <div class="form-group">
        <label>URL</label>
        <input v-model="localPage.url" class="form-control">
      </div>
      <div class="form-check mb-3">
        <input type="checkbox" v-model="localPage.can_be_navigated_to" class="form-check-input" id="editPageNav">
        <label class="form-check-label" for="editPageNav">Can be navigated to</label>
      </div>

      <h6>Identifying Selectors</h6>
      <div v-for="(sel, idx) in localPage.identifying_selectors" :key="'ident-row-'+idx" class="form-row mb-2 row">
        <div class="col"><input v-model="sel.alias" class="form-control" placeholder="Alias" required></div>
        <div class="col"><input v-model="sel.xpath" class="form-control" placeholder="XPath" required></div>
        <div class="col-auto"><TristateCheckbox v-model="sel.visible" /></div>
        <div class="col-auto"><button type="button" class="btn btn-danger btn-sm" @click="removeSelector('identifying', idx)">X</button></div>
      </div>
      <button type="button" class="btn btn-secondary btn-sm mb-3" @click="addSelector('identifying')">Add Selector</button>

      <h6>Interactive Selectors</h6>
      <div v-for="(sel, idx) in localPage.interactive_selectors" :key="'inter-row-'+idx" class="form-row mb-2 row">
        <div class="col"><input v-model="sel.alias" class="form-control" placeholder="Alias"></div>
        <div class="col"><input v-model="sel.xpath" class="form-control" placeholder="XPath"></div>
        <div class="col-auto"><TristateCheckbox v-model="sel.visible" /></div>
        <div class="col-auto"><button type="button" class="btn btn-danger btn-sm" @click="removeSelector('interactive', idx)">X</button></div>
      </div>
      <button type="button" class="btn btn-secondary btn-sm mb-3" @click="addSelector('interactive')">Add Selector</button>

      <div>
        <button type="submit" class="btn btn-success">Save Changes</button>
      </div>
    </form>
  </div>
</template>