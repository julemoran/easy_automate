<script setup lang="ts">
import type { Selector } from '../model';
import { ref, inject, type Ref } from 'vue';
import { api } from '../api';

const props = defineProps<{
	selector: Selector;
	index: number;
	pageId: string | null;
}>();

const emit = defineEmits<{
	(e: 'edit', index: number): void;
	(e: 'delete', index: number): void;
}>();

const interactValue = ref("");
const showInteractDialog = ref(false);
  function openInteractDialog() {
    showInteractDialog.value = true;
  }

  // Expose openInteractDialog for parent access
  defineExpose({ openInteractDialog });
function closeInteractDialog() {
  showInteractDialog.value = false;
}
// Expect parent to provide browserSession and pageId
const browserSession: Ref<{session_id: string} | null>  = inject('browserSession', ref(null));

const interactError = ref("");

async function handleClick() {
	interactError.value = "";
	if (!browserSession || !browserSession.value?.session_id || !props.pageId) {
		interactError.value = "Missing session or page context.";
		return;
	}
	try {
		await api.clickElement(browserSession.value?.session_id, props.pageId, props.selector.alias);
		closeInteractDialog();
	} catch (e) {
		interactError.value = (e as Error).message || "Failed to click element.";
	}
}

async function handleSetValue() {
	interactError.value = "";
	if (!browserSession || !browserSession.value?.session_id || !props.pageId) {
		interactError.value = "Missing session or page context.";
		return;
	}
	try {
		await api.setElementValue(browserSession.value?.session_id, props.pageId, props.selector.alias, interactValue.value);
		closeInteractDialog();
	} catch (e) {
		interactError.value = (e as Error).message || "Failed to set value.";
	}
}
  
</script>

<template>
  <div>
    <!-- Only the interact modal is rendered, no buttons or selector text here -->
    <div v-if="showInteractDialog" class="modal fade" :class="{ show: showInteractDialog }" :style="showInteractDialog ? 'display: block; background: rgba(0,0,0,0.5);' : 'display: none;'" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Interact with Selector: {{ selector.alias }}</h5>
            <button type="button" class="btn-close" @click="closeInteractDialog"></button>
          </div>
          <div class="modal-body">
            <button type="button" class="btn btn-outline-primary me-2" @click="handleClick">Click Element</button>
            <input type="text" v-model="interactValue" placeholder="Set value..." class="form-control d-inline-block w-auto me-2 mt-2" style="width: 120px;" />
            <button type="button" class="btn btn-outline-success mt-2" @click="handleSetValue">Set Value</button>
            <div v-if="interactError" class="mt-2 text-danger small">{{ interactError }}</div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeInteractDialog">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
