<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  modelValue: boolean | null
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean | null): void
}>();

const btnClass = computed(() => {
  if (props.modelValue === null) return 'btn-warning';
  if (props.modelValue === true) return 'btn-success';
  return 'btn-danger';
});

const cycleState = () => {
  let next: boolean | null;
  if (props.modelValue === null) next = true;
  else if (props.modelValue === true) next = false;
  else next = null;
  emit('update:modelValue', next);
};
</script>

<template>
  <span style="display: inline-block; min-width: 70px;">
    <button type="button" class="btn btn-outline-secondary btn-sm" @click="cycleState" :class="btnClass">
      <span v-if="modelValue === null">Any visibility</span>
      <span v-else-if="modelValue === true">must be visible</span>
      <span v-else-if="modelValue === false">must not be visible</span>
    </button>
  </span>
</template>