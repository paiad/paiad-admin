<script setup>
import { Icon } from '@iconify/vue';

defineProps({
  modelValue: String,
  prop: String,
  placeholder: String,
  icon: String,
  type: {
    type: String,
    default: 'text'
  },
  showPassword: {
    type: Boolean,
    default: false
  },
  inputClass: {
    type: String,
    default: 'rounded-2xl'
  }
});

defineEmits(['update:modelValue']);
</script>

<template>
  <ElFormItem :prop="prop">
    <ElInput
      :model-value="modelValue"
      :type="type"
      :placeholder="placeholder"
      :show-password="showPassword"
      :class="inputClass"
      @update:model-value="$emit('update:modelValue', $event)"
    >
      <template v-if="icon" #prefix>
        <Icon :icon="icon" class="text-16px text-gray-500" />
      </template>
    </ElInput>
  </ElFormItem>
</template>
