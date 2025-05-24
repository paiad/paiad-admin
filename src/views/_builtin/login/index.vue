<script setup lang="ts">
import { computed } from 'vue';
import type { Component } from 'vue';
import { loginModuleRecord } from '@/constants/app';
import { useAppStore } from '@/store/modules/app';
import { useThemeStore } from '@/store/modules/theme';
import PwdLogin from './modules/pwd-login.vue';
import CodeLogin from './modules/code-login.vue';
import Register from './modules/register.vue';
import ResetPwd from './modules/reset-pwd.vue';
import BindWechat from './modules/bind-wechat.vue';
import {$t} from "../../../locales";

defineOptions({ name: 'LoginPage' });

interface Props {
  /** The login module */
  module?: UnionKey.LoginModule;
}

const props = defineProps<Props>();

const appStore = useAppStore();
const themeStore = useThemeStore();

interface LoginModule {
  label: string;
  component: Component;
}

const moduleMap: Record<UnionKey.LoginModule, LoginModule> = {
  'pwd-login': { label: loginModuleRecord['pwd-login'], component: PwdLogin },
  'code-login': { label: loginModuleRecord['code-login'], component: CodeLogin },
  register: { label: loginModuleRecord.register, component: Register },
  'reset-pwd': { label: loginModuleRecord['reset-pwd'], component: ResetPwd },
  'bind-wechat': { label: loginModuleRecord['bind-wechat'], component: BindWechat }
};

const activeModule = computed(() => moduleMap[props.module || 'pwd-login']);
</script>

<template>
  <div class="relative size-full flex-center overflow-hidden">
    <ParticlesBg
      class="particles-bg absolute inset-0 -z-[-1]"
      :quantity="appStore.isMobile ? 0 : 314"
      :color="themeStore.darkMode ? '#6ec5ff' : '#41b291'"
      :staticity="10"
      refresh
    />
    <!--    <WaveBg :theme-color="bgThemeColor" />-->
    <ElCard class="relative z-4 w-auto rd-26px backdrop-blur-md -mt-60px">
      <div class="w-345px lt-sm:w-300px">
        <header class="w-full flex items-center justify-between pt-5 pb-3">
          <div class="w-1/10"></div>
          <SystemLogo class="text-40px text-primary lt-sm:text-48px" />
          <h2 class="select-none text-2xl font-extrabold tracking-wide">{{ $t('page.login.common.welcomeLogin') }}</h2>
          <div class="i-flex-row">
            <LangSwitch
              v-if="themeStore.header.multilingual.visible"
              :lang="appStore.locale"
              :lang-options="appStore.localeOptions"
              :show-tooltip="false"
              @change-lang="appStore.changeLocale"
            />
            <ThemeSchemaSwitch
              :theme-schema="themeStore.themeScheme"
              :show-tooltip="false"
              class="text-20px lt-sm:text-18px"
              @switch="themeStore.toggleThemeScheme"
            />
          </div>
        </header>
        <main class="pt-12px">
          <div class="pt-12px">
            <Transition :name="themeStore.page.animateMode" mode="out-in" appear>
              <component :is="activeModule.component" />
            </Transition>
          </div>
        </main>
      </div>
    </ElCard>
  </div>
</template>

<style scoped></style>
