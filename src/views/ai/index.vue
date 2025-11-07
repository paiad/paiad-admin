<template>
  <div class="ai-chat-page">
    <!-- 顶部配置按钮 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-title">
          <SvgIcon icon="solar:chat-round-dots-bold" class="title-icon" />
          <span class="title-text">{{ $t('page.ai.title') }}</span>
        </div>
        <ElButton
          text
          circle
          class="config-toggle-btn"
          @click="openConfig"
        >
          <SvgIcon :icon="showConfig ? 'solar:settings-bold' : 'solar:settings-bold-duotone'" class="config-icon" />
        </ElButton>
      </div>
    </div>

    <ElDialog
      v-model="showConfig"
      width="480px"
      class="ai-config-dialog"
      :close-on-click-modal="false"
      :show-close="false"
      destroy-on-close
      append-to-body
    >
      <template #header>
        <div class="dialog-header">
          <div class="dialog-title">
            <SvgIcon icon="solar:settings-bold-duotone" class="dialog-title-icon" />
            <span>{{ $t('page.ai.config.title') }}</span>
          </div>
        </div>
      </template>

      <div class="config-content">
        <div class="config-section">
          <div class="section-header">
            <SvgIcon icon="solar:server-path-bold" class="section-icon" />
            <span class="section-title">{{ $t('page.ai.config.provider') }}</span>
          </div>
          <ElSelect
            v-model="configForm.provider"
            class="apple-select"
            @change="handleProviderChange"
          >
            <ElOption
              v-for="provider in availableProviders"
              :key="provider.value"
              :label="provider.label"
              :value="provider.value"
            />
          </ElSelect>
        </div>

        <div class="config-section">
          <div class="section-header">
            <SvgIcon icon="solar:key-bold" class="section-icon" />
            <span class="section-title">{{ $t('page.ai.config.apiKey') }}</span>
          </div>
          <ElInput
            v-model="configForm.apiKey"
            type="password"
            :placeholder="$t('page.ai.config.apiKeyPlaceholder')"
            show-password
            clearable
            class="apple-input"
          />
        </div>

        <div class="config-section">
          <div class="section-header">
            <SvgIcon icon="solar:link-bold" class="section-icon" />
            <span class="section-title">{{ $t('page.ai.config.baseUrl') }}</span>
          </div>
          <ElInput
            v-model="configForm.baseUrl"
            :placeholder="$t('page.ai.config.baseUrlPlaceholder')"
            clearable
            class="apple-input"
          />
        </div>

        <div class="config-section">
          <div class="section-header">
            <SvgIcon icon="solar:cpu-bolt-bold" class="section-icon" />
            <span class="section-title">{{ $t('page.ai.config.model') }}</span>
          </div>
          <ElSelect v-model="configForm.model" class="apple-select">
            <ElOption
              v-for="model in availableModels"
              :key="model.value"
              :label="model.label"
              :value="model.value"
            />
          </ElSelect>
        </div>
      </div>

      <template #footer>
        <div class="dialog-actions">
          <ElButton class="apple-button ghost" @click="handleConfigCancel">
            <SvgIcon icon="solar:logout-3-linear" class="btn-icon" />
            {{ $t('page.ai.config.exit') }}
          </ElButton>
          <ElButton class="apple-button primary" @click="handleConfigSave">
            <SvgIcon icon="solar:check-circle-linear" class="btn-icon" />
            {{ $t('page.ai.config.save') }}
          </ElButton>
        </div>
      </template>
    </ElDialog>

    <!-- 对话区域 -->
    <div class="chat-container">
      <!-- 消息列表 -->
      <div ref="messagesContainer" class="messages-container">
        <div v-if="messages.length === 0" class="empty-messages">
          <div class="empty-icon-wrapper">
            <div class="empty-icon">
              <SvgIcon icon="solar:chat-round-call-bold-duotone" class="icon-large" />
            </div>
          </div>
          <div class="empty-text">{{ $t('page.ai.chat.empty') }}</div>
          <div class="empty-hint">{{ $t('page.ai.chat.hint') }}</div>
        </div>
          <div
            v-for="(message, index) in messages"
            :key="index"
            class="message-item"
            :class="{ 'message-user': message.role === 'user', 'message-assistant': message.role === 'assistant' }"
          >
            <div class="message-avatar">
              <div v-if="message.role === 'user'" class="avatar-user">
                <SvgIcon icon="solar:user-bold" />
              </div>
              <div v-else class="avatar-assistant">
                <SvgIcon icon="solar:robot-bold" />
              </div>
            </div>
            <div class="message-content-wrapper">
              <div class="message-content" :class="{ 'content-user': message.role === 'user', 'content-assistant': message.role === 'assistant' }">
                <div class="message-text" v-html="formatMessage(message.content)"></div>
                <div class="message-time">{{ formatTime(message.timestamp) }}</div>
              </div>
            </div>
          </div>
          <div v-if="loading" class="message-item message-assistant">
            <div class="message-avatar">
              <div class="avatar-assistant">
                <SvgIcon icon="solar:robot-bold" />
              </div>
            </div>
            <div class="message-content-wrapper">
              <div class="message-content content-assistant">
                <div class="message-text typing">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        </div>

      <!-- 输入区域 -->
      <div class="input-container">
        <div class="input-wrapper">
          <ElInput
            v-model="inputMessage"
            type="textarea"
            :rows="1"
            :placeholder="$t('page.ai.chat.inputPlaceholder')"
            :disabled="loading || !isConfigValid"
            @keydown.enter.exact.prevent="handleSend"
            @keydown.enter.shift.exact="handleShiftEnter"
            class="apple-textarea"
            resize="none"
          />
          <div class="input-actions">
            <ElButton
              circle
              class="action-btn send-btn"
              :loading="loading"
              :disabled="!inputMessage.trim() || !isConfigValid"
              @click="handleSend"
            >
              <SvgIcon v-if="!loading" icon="solar:plain-bold" class="send-icon" />
            </ElButton>
          </div>
        </div>
        <div v-if="!isConfigValid" class="config-hint">
          <SvgIcon icon="solar:info-circle-bold" class="hint-icon" />
          <span>{{ $t('page.ai.chat.configHint') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { $t } from '@/locales';
import { localStg } from '@/utils/storage';

defineOptions({ name: 'AiChat' });

// 配置相关
const showConfig = ref(false);
const configForm = ref({
  provider: 'openai',
  apiKey: '',
  baseUrl: 'https://api.openai.com/v1',
  model: 'gpt-3.5-turbo'
});

// 服务提供商配置
const providerConfigs = {
  openai: {
    label: 'OpenAI',
    baseUrl: 'https://api.openai.com/v1',
    models: [
      { label: 'GPT-3.5 Turbo', value: 'gpt-3.5-turbo' },
      { label: 'GPT-4', value: 'gpt-4' },
      { label: 'GPT-4 Turbo', value: 'gpt-4-turbo-preview' },
      { label: 'GPT-4o', value: 'gpt-4o' },
      { label: 'GPT-4o Mini', value: 'gpt-4o-mini' }
    ]
  },
  deepseek: {
    label: 'DeepSeek',
    baseUrl: 'https://api.deepseek.com/v1',
    models: [
      { label: 'DeepSeek Chat', value: 'deepseek-chat' },
      { label: 'DeepSeek Coder', value: 'deepseek-coder' },
      { label: 'DeepSeek Recharge', value: 'deepseek-recharge' }
    ]
  },
  claude: {
    label: 'Claude (Anthropic)',
    baseUrl: 'https://api.anthropic.com/v1',
    models: [
      { label: 'Claude 3 Opus', value: 'claude-3-opus-20240229' },
      { label: 'Claude 3 Sonnet', value: 'claude-3-sonnet-20240229' },
      { label: 'Claude 3 Haiku', value: 'claude-3-haiku-20240307' },
      { label: 'Claude 3.5 Sonnet', value: 'claude-3-5-sonnet-20240620' }
    ]
  },
  gemini: {
    label: 'Google Gemini',
    baseUrl: 'https://generativelanguage.googleapis.com/v1',
    models: [
      { label: 'Gemini Pro', value: 'gemini-pro' },
      { label: 'Gemini Pro Vision', value: 'gemini-pro-vision' }
    ]
  },
  moonshot: {
    label: 'Moonshot AI',
    baseUrl: 'https://api.moonshot.cn/v1',
    models: [
      { label: 'Moonshot-v1-8k', value: 'moonshot-v1-8k' },
      { label: 'Moonshot-v1-32k', value: 'moonshot-v1-32k' },
      { label: 'Moonshot-v1-128k', value: 'moonshot-v1-128k' }
    ]
  },
  custom: {
    label: '自定义',
    baseUrl: '',
    models: [
      { label: '自定义模型', value: 'custom' }
    ]
  }
};

const availableProviders = Object.entries(providerConfigs).map(([value, config]) => ({
  value,
  label: config.label
}));

const availableModels = computed(() => {
  const provider = configForm.value.provider;
  return providerConfigs[provider as keyof typeof providerConfigs]?.models || [];
});

// 处理服务提供商切换
function handleProviderChange(provider: string) {
  const config = providerConfigs[provider as keyof typeof providerConfigs];
  if (config) {
    configForm.value.baseUrl = config.baseUrl;
    if (config.models.length > 0) {
      configForm.value.model = config.models[0].value;
    }
  }
}

const isConfigValid = computed(() => {
  return configForm.value.apiKey.trim().length > 0;
});

// 消息相关
interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

const messages = ref<Message[]>([]);
const inputMessage = ref('');
const loading = ref(false);
const messagesContainer = ref<HTMLElement | null>(null);

// 加载配置
function loadConfig() {
  const saved = localStg.get('ai-config');
  if (saved) {
    const savedProvider = saved.provider || 'openai';
    configForm.value = { ...configForm.value, ...saved };
    // 如果provider变化，需要更新模型列表
    if (savedProvider !== configForm.value.provider) {
      configForm.value.provider = savedProvider;
      handleProviderChange(savedProvider);
    }
  }
}

function openConfig() {
  loadConfig();
  showConfig.value = true;
}

function handleConfigSave() {
  if (saveConfig()) {
    showConfig.value = false;
  }
}

function handleConfigCancel() {
  showConfig.value = false;
  loadConfig();
}

// 保存配置
function saveConfig() {
  if (!configForm.value.apiKey.trim()) {
    ElMessage.warning($t('page.ai.config.errors.apiKeyRequired'));
    return false;
  }
  localStg.set('ai-config', configForm.value);
  ElMessage.success($t('page.ai.config.saveSuccess'));
  return true;
}

// 格式化消息内容（支持Markdown）
function formatMessage(content: string) {
  // 简单的Markdown转HTML
  return content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>');
}

// 格式化时间
function formatTime(timestamp: number) {
  const date = new Date(timestamp);
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const messageDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

  if (messageDate.getTime() === today.getTime()) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  } else {
    return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
  }
}

// 滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
}

// 发送消息
async function handleSend() {
  if (!inputMessage.value.trim() || loading.value || !isConfigValid.value) {
    return;
  }

  const userMessage = inputMessage.value.trim();
  inputMessage.value = '';

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: userMessage,
    timestamp: Date.now()
  });

  scrollToBottom();
  loading.value = true;

  try {
    // 根据服务提供商构建不同的请求
    const provider = configForm.value.provider;
    let apiUrl = '';
    let headers: Record<string, string> = {
      'Content-Type': 'application/json'
    };
    let requestBody: any = {};

    if (provider === 'claude') {
      // Claude API 格式
      apiUrl = `${configForm.value.baseUrl}/messages`;
      headers['x-api-key'] = configForm.value.apiKey;
      headers['anthropic-version'] = '2023-06-01';
      requestBody = {
        model: configForm.value.model,
        max_tokens: 4096,
        messages: messages.value.map(msg => ({
          role: msg.role === 'assistant' ? 'assistant' : 'user',
          content: msg.content
        }))
      };
    } else if (provider === 'gemini') {
      // Gemini API 格式（需要特殊处理）
      apiUrl = `${configForm.value.baseUrl}/${configForm.value.model}:generateContent?key=${configForm.value.apiKey}`;
      requestBody = {
        contents: messages.value.map(msg => ({
          parts: [{ text: msg.content }],
          role: msg.role === 'assistant' ? 'model' : 'user'
        }))
      };
    } else {
      // OpenAI 兼容格式（OpenAI, DeepSeek, Moonshot 等）
      apiUrl = `${configForm.value.baseUrl}/chat/completions`;
      headers['Authorization'] = `Bearer ${configForm.value.apiKey}`;
      requestBody = {
        model: configForm.value.model,
        messages: messages.value.map(msg => ({
          role: msg.role,
          content: msg.content
        })),
        stream: false
      };
    }

    const response = await fetch(apiUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: { message: 'Unknown error' } }));
      throw new Error(error.error?.message || error.message || `HTTP ${response.status}`);
    }

    const data = await response.json();
    let assistantMessage = '';

    // 根据不同服务提供商解析响应
    if (provider === 'claude') {
      assistantMessage = data.content?.[0]?.text || $t('page.ai.chat.errors.noResponse');
    } else if (provider === 'gemini') {
      assistantMessage = data.candidates?.[0]?.content?.parts?.[0]?.text || $t('page.ai.chat.errors.noResponse');
    } else {
      // OpenAI 兼容格式
      assistantMessage = data.choices?.[0]?.message?.content || $t('page.ai.chat.errors.noResponse');
    }

    // 添加AI回复
    if (assistantMessage) {
      messages.value.push({
        role: 'assistant',
        content: assistantMessage,
        timestamp: Date.now()
      });
    } else {
      throw new Error($t('page.ai.chat.errors.noResponse'));
    }

    scrollToBottom();
  } catch (error: any) {
    ElMessage.error(error.message || $t('page.ai.chat.errors.sendFail'));
    // 添加错误消息
    messages.value.push({
      role: 'assistant',
      content: $t('page.ai.chat.errors.sendFail') + ': ' + (error.message || 'Unknown error'),
      timestamp: Date.now()
    });
  } finally {
    loading.value = false;
    scrollToBottom();
  }
}

// Shift+Enter换行
function handleShiftEnter() {
  // 默认行为，允许换行
}

// 清空消息
function clearMessages() {
  messages.value = [];
}

// 监听消息变化，自动滚动
watch(
  () => messages.value.length,
  () => {
    scrollToBottom();
  }
);

onMounted(() => {
  loadConfig();
});
</script>

<style scoped lang="scss">
.ai-chat-page {
  padding: 20px;
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color-page);
}

// 页面头部
.page-header {
  margin-bottom: 20px;

  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 24px;
    background: var(--el-bg-color);
    border-radius: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
  }

  .header-title {
    display: flex;
    align-items: center;
    gap: 12px;

    .title-icon {
      font-size: 24px;
      color: rgb(var(--primary-color));
    }

    .title-text {
      font-size: 20px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      letter-spacing: -0.3px;
    }
  }

  .config-toggle-btn {
    width: 40px;
    height: 40px;
    padding: 0;
    border-radius: 50%;
    transition: all 0.2s ease;

    .config-icon {
      font-size: 20px;
      color: var(--el-text-color-primary);
    }

    &:hover {
      background: var(--el-fill-color-light);
      transform: scale(1.05);
    }
  }
}

// 配置弹窗
.ai-config-dialog {
  :deep(.el-dialog) {
    border-radius: 20px;
    background: var(--el-bg-color);
    box-shadow: 0 12px 40px rgba(15, 23, 42, 0.18);
    padding: 0;
  }

  :deep(.el-dialog__header) {
    margin: 0;
    padding: 24px 24px 12px;
    border-bottom: none;
  }

  :deep(.el-dialog__body) {
    padding: 0 24px 24px;
  }

  :deep(.el-dialog__footer) {
    padding: 16px 24px 24px;
    border-top: none;
  }
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.dialog-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);

  .dialog-title-icon {
    font-size: 22px;
    color: rgb(var(--primary-color));
  }
}

.config-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-top: 8px;
}

.config-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;

  .section-icon {
    font-size: 18px;
    color: rgb(var(--primary-color));
  }

  .section-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    letter-spacing: -0.2px;
  }
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;

  .apple-button {
    flex: none;
    min-width: unset;
    padding: 0 18px;
    height: 40px;
  }
}

// Apple 风格输入框和选择器
.apple-input,
.apple-select {
  width: 100%;

  :deep(.el-input__wrapper) {
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
    transition: all 0.2s ease;
    padding: 12px 16px;

    &:hover {
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    }

    &.is-focus {
      box-shadow: 0 0 0 3px rgba(var(--primary-color), 0.1);
    }
  }
}

.apple-select {
  :deep(.el-select__wrapper) {
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
    transition: all 0.2s ease;

    &:hover {
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    }
  }
}

.apple-button {
  flex: 1;
  height: 44px;
  border-radius: 12px;
  font-weight: 500;
  letter-spacing: -0.2px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  .btn-icon {
    font-size: 18px;
  }

  &.primary {
    background: rgb(var(--primary-color));
    color: white;
    border: none;
    box-shadow: 0 2px 8px rgba(var(--primary-color), 0.3);

    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(var(--primary-color), 0.4);
    }

    &:active {
      transform: translateY(0);
    }
  }

  &:not(.primary):not(.ghost) {
    background: var(--el-fill-color-light);
    color: var(--el-text-color-primary);
    border: 1px solid var(--el-border-color-lighter);

    &:hover {
      background: var(--el-fill-color);
      transform: translateY(-1px);
    }
  }

  &.ghost {
    background: transparent;
    color: var(--el-text-color-primary);
    border: 1px solid var(--el-border-color-lighter);

    &:hover {
      background: var(--el-fill-color-light);
      transform: translateY(-1px);
    }
  }
}

// 动画
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-down-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.chat-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  background: var(--el-bg-color);
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: var(--el-bg-color-page);

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: var(--el-border-color);
    border-radius: 3px;
    transition: background 0.2s;

    &:hover {
      background: var(--el-border-color-darker);
    }
  }
}

.empty-messages {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 60px 20px;

  .empty-icon-wrapper {
    margin-bottom: 24px;

    .empty-icon {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      background: linear-gradient(135deg, rgba(var(--primary-color), 0.1) 0%, rgba(var(--primary-color), 0.05) 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      animation: float 3s ease-in-out infinite;

      .icon-large {
        font-size: 40px;
        color: rgb(var(--primary-color));
      }
    }
  }

  .empty-text {
    font-size: 18px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin-bottom: 8px;
    letter-spacing: -0.3px;
  }

  .empty-hint {
    font-size: 14px;
    color: var(--el-text-color-secondary);
    text-align: center;
    max-width: 400px;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.message-item {
  display: flex;
  gap: 12px;
  animation: messageSlideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);

  &.message-user {
    flex-direction: row-reverse;

    .message-content-wrapper {
      align-items: flex-end;
    }
  }

  &.message-assistant {
    .message-content-wrapper {
      align-items: flex-start;
    }
  }
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.message-avatar {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  transition: transform 0.2s ease;

  &:hover {
    transform: scale(1.05);
  }

  .avatar-user {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background: linear-gradient(135deg, rgb(var(--primary-color)) 0%, rgba(var(--primary-color), 0.8) 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(var(--primary-color), 0.3);
  }

  .avatar-assistant {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--el-fill-color-light) 0%, var(--el-fill-color) 100%);
    color: rgb(var(--primary-color));
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  }
}

.message-content-wrapper {
  display: flex;
  flex-direction: column;
  max-width: 75%;
  min-width: 0;
}

.message-content {
  padding: 14px 18px;
  border-radius: 18px;
  position: relative;
  word-wrap: break-word;
  word-break: break-word;
  transition: all 0.2s ease;

  &.content-user {
    background: rgb(var(--primary-color));
    color: white;
    border-bottom-right-radius: 4px;
    box-shadow: 0 2px 8px rgba(var(--primary-color), 0.25);

    .message-time {
      color: rgba(255, 255, 255, 0.75);
    }
  }

  &.content-assistant {
    background: var(--el-bg-color);
    color: var(--el-text-color-primary);
    border: 1px solid var(--el-border-color-lighter);
    border-bottom-left-radius: 4px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);

    .message-time {
      color: var(--el-text-color-secondary);
    }
  }
}

.message-text {
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 4px;

  :deep(code) {
    background: rgba(0, 0, 0, 0.1);
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
  }

  :deep(strong) {
    font-weight: 600;
  }

  :deep(em) {
    font-style: italic;
  }
}

.message-time {
  font-size: 11px;
  margin-top: 4px;
  opacity: 0.7;
}

.typing {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 8px 0;

  span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--el-text-color-secondary);
    animation: typing 1.4s infinite;

    &:nth-child(2) {
      animation-delay: 0.2s;
    }

    &:nth-child(3) {
      animation-delay: 0.4s;
    }
  }
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.7;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

.input-container {
  padding: 20px;
  border-top: 1px solid var(--el-border-color-lighter);
  background: var(--el-bg-color);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: center;
}

.apple-textarea {
  flex: 1;

  :deep(.el-textarea__inner) {
    resize: none;
    font-size: 15px;
    line-height: 1.5;
    padding: 12px 18px;
    min-height: 44px;
    border-radius: 20px;
    border: 1px solid var(--el-border-color-lighter);
    background: var(--el-fill-color-light);
    transition: all 0.2s ease;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);

    &:focus {
      border-color: rgb(var(--primary-color));
      box-shadow: 0 0 0 3px rgba(var(--primary-color), 0.1);
      background: var(--el-bg-color);
    }

    &::placeholder {
      color: var(--el-text-color-placeholder);
    }
  }
}

.input-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.action-btn {
  padding: 0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  border: none;
  flex-shrink: 0;

  .svg-icon {
    font-size: 28px;
  }

  &.clear-btn {
    background: var(--el-fill-color-light);
    color: var(--el-text-color-secondary);

    &:hover:not(:disabled) {
      background: var(--el-fill-color);
      transform: scale(1.05);
    }

    &:disabled {
      opacity: 0.4;
    }
  }

  &.send-btn {
    background: transparent;
    color: rgb(var(--primary-color));
    box-shadow: none;
    border: none;
    min-width: 40px;
    min-height: 40px;

    &:hover:not(:disabled) {
      background: rgba(var(--primary-color), 0.1);
      transform: scale(1.1);
    }

    &:active:not(:disabled) {
      transform: scale(1);
    }

    &:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }

    .send-icon {
      font-size: 36px !important;
      color: rgb(var(--primary-color));
      width: 36px;
      height: 36px;
    }
  }
}

.config-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--el-color-warning-light-9);
  border-radius: 12px;
  font-size: 13px;
  color: var(--el-color-warning-dark-2);

  .hint-icon {
    font-size: 16px;
    color: var(--el-color-warning);
  }
}

// 暗色模式适配
html.dark {
  .message-content.content-assistant {
    background: var(--el-bg-color-page);
    border-color: var(--el-border-color);
  }

  .avatar-assistant {
    background: var(--el-color-info-dark-2);
    color: var(--el-color-info-light-3);
  }

  .message-content.content-user .message-text :deep(code) {
    background: rgba(255, 255, 255, 0.2);
  }

  .message-content.content-assistant .message-text :deep(code) {
    background: rgba(255, 255, 255, 0.1);
  }
}
</style>
