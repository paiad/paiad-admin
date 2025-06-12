<script setup lang="ts">
defineOptions({ name: 'GlobalLogo' });

interface Props {
  /** Whether to show the title */
  showTitle?: boolean;
}

withDefaults(defineProps<Props>(), {
  showTitle: true
});
</script>

<template>
  <RouterLink to="/" class="w-full flex-center nowrap-hidden">
    <SystemLogo class="text-30px text-primary" />
    <span class="text-2xl font-bold text-blue-4 hover:text-primary transition-colors pl-5">华杉科技</span>
  </RouterLink>
</template>

<style scoped></style>
