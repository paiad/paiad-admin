<script setup lang="ts">
import { computed, useAttrs } from 'vue';
import { Icon } from '@iconify/vue';

defineOptions({ name: 'SvgIcon', inheritAttrs: false });

interface Props {
  /** Iconify 图标名称，如 'mdi:home' */
  icon?: string;
  /** 本地图标名称（来自 symbol sprite） */
  localIcon?: string;
  /** 远程图标 URL */
  iconUrl?: string;
}

const props = defineProps<Props>();

const attrs = useAttrs();

const bindAttrs = computed<{ class: string; style: string }>(() => ({
  class: (attrs.class as string) || '',
  style: (attrs.style as string) || ''
}));

// 本地图标 symbol ID 构造
const symbolId = computed(() => {
  const { VITE_ICON_LOCAL_PREFIX: prefix } = import.meta.env;
  const defaultLocalIcon = 'no-icon';
  const icon = props.localIcon || defaultLocalIcon;
  return `#${prefix}-${icon}`;
});

// 渲染优先级判断
const isRenderLocal = computed(() => !!props.localIcon);
const isRenderUrl = computed(() => !!props.iconUrl && !props.localIcon);
const isRenderIconify = computed(() => !!props.icon && !props.localIcon && !props.iconUrl);
</script>

<template>
  <!-- 本地 SVG 图标 -->
  <svg v-if="isRenderLocal" aria-hidden="true" width="1em" height="1em" v-bind="bindAttrs">
    <use :xlink:href="symbolId" fill="currentColor" />
  </svg>

  <!-- 远程 URL 图标 -->
  <img v-else-if="isRenderUrl" :src="props.iconUrl" alt="icon" v-bind="bindAttrs" />

  <!-- Iconify 图标 -->
  <Icon v-else-if="isRenderIconify" :icon="props.icon" v-bind="bindAttrs" />
</template>

<style scoped></style>
