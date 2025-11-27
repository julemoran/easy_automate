<script setup lang="ts">
import { ref } from 'vue';
import type { Application } from '../model';

const props = defineProps<{
  applications: Application[],
  selectedAppId: string | undefined
}>();

const emit = defineEmits<{
  (e: 'select', app: Application): void,
  (e: 'create', name: string): void,
  (e: 'delete', id: string): void,
  (e: 'update', app: Application): void
}>();

const newAppMode = ref(false);
const showEditModal = ref(false);
const editApp = ref<Application | null>(null);
const editAppName = ref('');

const openCreateModal = () => {
  newAppMode.value = true;
  editApp.value = null;
  editAppName.value = '';
  showEditModal.value = true;
};

const openEditModal = (app: Application) => {
  newAppMode.value = false;
  editApp.value = app;
  editAppName.value = app.name;
  showEditModal.value = true;
};

const handleEditSave = () => {
  if (newAppMode.value) {
    if (!editAppName.value) return;
    emit('create', editAppName.value);
  } else {
    if (!editApp.value) return;
    emit('update', { ...editApp.value, name: editAppName.value });
  }
  showEditModal.value = false;
};
</script>

<template>
  <div>
    <div class="d-flex align-items-center justify-content-between mb-2">
      <h4 class="mb-0">Applications</h4>
      <button class="btn btn-outline-primary btn-sm" title="Add" @click="openCreateModal">
        <i class="bi bi-plus"></i>
      </button>
    </div>
    <ul class="list-group mb-3">
      <li v-for="app in applications" :key="app.id"
          class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
          :class="{ active: selectedAppId === app.id }"
          @click="emit('select', app)">
        <span>{{ app.name }}</span>
        <span class="btn-group btn-group-sm column-gap-1">
          <button class="btn btn-secondary" title="Edit" @click.stop="openEditModal(app)">
            <i class="bi bi-pencil"></i>
          </button>
          <button class="btn btn-danger" title="Delete" @click.stop="emit('delete', app.id!)">
            <i class="bi bi-trash"></i>
          </button>
        </span>
      </li>
    </ul>

    <!-- Create/Edit Application Modal -->
    <dialog class="modal fade" :class="{ show: showEditModal }" :style="showEditModal ? 'display: block; background: rgba(0,0,0,0.5);' : 'display: none;'" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ newAppMode ? 'Create Application' : 'Edit Application' }}</h5>
            <button type="button" class="btn-close" @click="showEditModal = false"></button>
          </div>
          <div class="modal-body">
            <input v-model="editAppName" class="form-control" required placeholder="Application Name">
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showEditModal = false">Cancel</button>
            <button type="button" class="btn btn-primary" @click="handleEditSave">Save</button>
          </div>
        </div>
      </div>
    </dialog>
  </div>
</template>