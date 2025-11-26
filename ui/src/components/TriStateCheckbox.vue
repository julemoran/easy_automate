<script setup lang="ts">
// ...existing code...

const props = defineProps<{
  modelValue: boolean | null
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean | null): void
}>();

const updateValue = (value: boolean | null) => {
  emit('update:modelValue', value);
};
</script>

<template>
  <span style="display: block; min-width: 150px;">
    <label style="margin-right: 10px;">
      <input type="radio" name="tri-state" :checked="modelValue === null" @change="updateValue(null)" /> Any visibility
    </label>
    <label style="margin-right: 10px;">
      <input type="radio" name="tri-state" :checked="modelValue === true" @change="updateValue(true)" /> must be visible
    </label>
    <label>
      <input type="radio" name="tri-state" :checked="modelValue === false" @change="updateValue(false)" /> must not be visible
    </label>
  </span>
</template>