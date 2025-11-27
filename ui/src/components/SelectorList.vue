<script setup lang="ts">
import { computed } from 'vue';
import { defineProps, defineEmits, ref, inject, type Ref } from 'vue';
import { api } from '../api';
const browserSession: Ref<{session_id: string} | null>  = inject('browserSession', ref(null));
import SelectorEditor from './SelectorEditor.vue';
import type { Selector } from '../model';

const props = defineProps<{
  selectors: Selector[];
  type: 'identifying' | 'interactive';
  title?: string;
  pageId: string | number | null;
}>();

const emit = defineEmits<{
  (e: 'add'): void;
  (e: 'update', selector: Selector, index: number): void;
  (e: 'remove', index: number): void;
  (e: 'clone', index: number): void;
}>();


const editingIndex = ref<number | null>(null);
const editingSelector = ref<Selector | null>(null);

const interactIndex = ref<number | null>(null);
const interactValue = ref("");
const interactError = ref("");

function openInteract(idx: number) {
  interactIndex.value = idx;
  interactValue.value = "";
  interactError.value = "";
}

function closeInteract() {
  interactIndex.value = null;
  interactValue.value = "";
  interactError.value = "";
}

async function handleClick(idx: number) {
  interactError.value = "";
  const sel = props.selectors[idx];
  if (!browserSession.value?.session_id || !props.pageId || !sel) {
    interactError.value = "Missing session, page context, or selector.";
    return;
  }
  try {
    await api.clickElement(browserSession.value.session_id, String(props.pageId), sel.alias);
    closeInteract();
  } catch (e) {
    interactError.value = (e as Error).message || "Failed to click element.";
  }
}

async function handleSetValue(idx: number) {
  interactError.value = "";
  const sel = props.selectors[idx];
  if (!browserSession.value?.session_id || !props.pageId || !sel) {
    interactError.value = "Missing session, page context, or selector.";
    return;
  }
  try {
    await api.setElementValue(browserSession.value.session_id, String(props.pageId), sel.alias, interactValue.value);
    closeInteract();
  } catch (e) {
    interactError.value = (e as Error).message || "Failed to set value.";
  }
}

function openEdit(index: number) {
  editingIndex.value = index;
  const sel = props.selectors[index];
  if (!sel) {
    editingSelector.value = { alias: '', xpath: '', visible: null };
    return;
  }
  editingSelector.value = {
    alias: sel.alias ?? '',
    xpath: sel.xpath ?? '',
    visible: sel.visible ?? null
  };
}

function saveEdit() {
  if (editingIndex.value !== null && editingSelector.value) {
    emit('update', editingSelector.value, editingIndex.value);
    editingIndex.value = null;
    editingSelector.value = null;
  }
}

function cancelEdit() {
  editingIndex.value = null;
  editingSelector.value = null;
}

function handleAdd() {
  emit('add');
  // Open edit dialog for the newly added selector
  setTimeout(() => {
    const idx = props.selectors.length - 1;
    openEdit(idx);
  }, 0);
}

function handleClone(index: number) {
  emit('clone', index);
  // Open edit dialog for the newly cloned selector
  setTimeout(() => {
    const idx = props.selectors.length - 1;
    openEdit(idx);
  }, 0);
}
</script>

<template>
  <div>
    <div class="d-flex align-items-center justify-content-between mb-2">
      <h5 class="mb-0">{{ props.title ?? 'Selectors' }}</h5>
      <button type="button" class="btn btn-primary btn-sm" title="Add" @click="handleAdd">
        <i class="bi bi-plus"></i>
      </button>
    </div>
    <ul class="list-group mb-3">
      <li v-for="(sel, idx) in selectors" :key="type + '-row-' + idx"
          class="list-group-item">
        <div class="d-flex align-items-center">
          <span class="flex-grow-1">
            <span class="fw-bold me-2">{{ sel.alias }}</span>
            <span class="text-muted small me-2 d-none d-md-inline">{{ sel.xpath }}</span>
            <span v-if="sel.visible === true" class="me-2" title="Visible">
              <i class="bi bi-eye"></i>
            </span>
            <span v-else-if="sel.visible === false" class="me-2" title="Invisible">
              <i class="bi bi-eye-slash"></i>
            </span>
          </span>
          <span class="btn-group btn-group-sm ms-auto">
            <button class="btn btn-outline-secondary" title="Edit" @click.stop="openEdit(idx)">
              <i class="bi bi-pencil"></i>
            </button>
            <button class="btn btn-outline-danger" title="Delete" @click.stop="$emit('remove', idx)">
              <i class="bi bi-trash"></i>
            </button>
            <button class="btn btn-outline-info" title="Clone" @click.stop="handleClone(idx)">
              <i class="bi bi-files"></i>
            </button>
            <button class="btn btn-outline-primary" title="Interact" @click.stop="openInteract(idx)">
              <i class="bi bi-hand-index"></i>
            </button>
          </span>
        </div>
        <!-- Interact Modal for this selector -->
        <dialog v-if="interactIndex === idx" class="modal fade show" style="display: block; background: rgba(0,0,0,0.5);" tabindex="-1">
          <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">Interact with Selector: {{ sel.alias }}</h5>
                <button type="button" class="btn-close" @click="closeInteract"></button>
              </div>
              <div class="modal-body">
                <textarea type="text" v-model="interactValue" placeholder="Set value..." class="form-control d-inline-block w-full me-2 mt-2"/>
                <button type="button" class="btn btn-outline-primary me-2" @click="handleClick(idx)">Click Element</button>
                <button type="button" class="btn btn-outline-success mt-2" @click="handleSetValue(idx)">Set Value</button>
                <div v-if="interactError" class="mt-2 text-danger small">{{ interactError }}</div>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="closeInteract">Close</button>
              </div>
            </div>
          </div>
        </dialog>
      </li>
    </ul>
    <SelectorEditor
      v-if="editingSelector"
      v-model:selector="editingSelector"
      :show="!!editingSelector"      
      @save="saveEdit"
      @cancel="cancelEdit"
    />
  </div>
</template>
