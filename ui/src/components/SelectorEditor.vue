<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';
import TristateCheckbox from './TriStateCheckbox.vue';
import type { Selector } from '../model';

const props = defineProps<{
  selector: Selector;
  show: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:selector', selector: Selector): void;
  (e: 'save'): void;
  (e: 'cancel'): void;
}>();

function updateAlias(e: Event) {
  emit('update:selector', { ...props.selector, alias: (e.target as HTMLInputElement).value });
}
function updateXpath(e: Event) {
  emit('update:selector', { ...props.selector, xpath: (e.target as HTMLInputElement).value });
}
function updateVisible(val: boolean | null) {
  emit('update:selector', { ...props.selector, visible: val });
}
</script>

<template>

  <div v-if="show" class="modal fade show" style="display: block; background: rgba(0,0,0,0.5);">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Edit Selector</h5>
          <button type="button" class="btn-close" @click="$emit('cancel')"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label class="form-label" for="edit-alias">Alias</label>
            <input id="edit-alias" :value="selector.alias" @input="updateAlias" class="form-control" />
          </div>
          <div class="mb-3">
            <label class="form-label" for="edit-xpath">XPath</label>
            <input id="edit-xpath" :value="selector.xpath" @input="updateXpath" class="form-control" />
          </div>
          <div class="mb-3">
            <label class="form-label" for="edit-visible">Visibility</label>
            <TristateCheckbox id="edit-visible" :modelValue="selector.visible" @update:modelValue="updateVisible" />
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('cancel')">Cancel</button>
          <button type="button" class="btn btn-primary" @click="$emit('save')">Save</button>
        </div>
      </div>
    </div>
  </div>

</template>
