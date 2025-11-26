<script setup lang="ts">
import { defineProps, defineEmits, ref } from 'vue';
import SelectorItem from './SelectorItem.vue';
import SelectorEditor from './SelectorEditor.vue';
import type { Selector } from '../model';

const props = defineProps<{
  selectors: Selector[];
  type: 'identifying' | 'interactive';
  title?: string;
}>();

const emit = defineEmits<{
  (e: 'add'): void;
  (e: 'update', selector: Selector, index: number): void;
  (e: 'remove', index: number): void;
}>();

const editingIndex = ref<number | null>(null);
const editingSelector = ref<Selector | null>(null);

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
</script>

<template>
  <div>
    <div class="d-flex align-items-center justify-content-between mb-2">
      <h5 class="mb-0">{{ props.title ?? 'Selectors' }}</h5>
      <button type="button" class="btn btn-primary btn-sm" title="Add" @click="$emit('add')">
        <i class="bi bi-plus"></i>
      </button>
    </div>
    <div v-for="(sel, idx) in selectors" :key="type + '-row-' + idx">
      <SelectorItem
        :selector="sel"
        :index="idx"
        @edit="openEdit"
        @delete="$emit('remove', idx)"
      />
    </div>

    <SelectorEditor
      v-if="editingSelector"
      v-model:selector="editingSelector"
      :show="!!editingSelector"
      @save="saveEdit"
      @cancel="cancelEdit"
    />
  </div>
</template>
