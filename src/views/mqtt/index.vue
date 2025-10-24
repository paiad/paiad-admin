<template>
  <div class="mqtt-page">
    <ElCard class="block-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>{{ $t('page.mqtt.title') }}</span>
          <span class="subtitle">{{ $t('page.mqtt.subtitle') }}</span>
        </div>
      </template>

      <ElRow :gutter="16">
        <ElCol :xs="24" :md="12">
          <ElCard class="inner-card" shadow="never">
            <template #header>
              <div class="card-header">
                <span>{{ $t('page.mqtt.publish.title') }}</span>
              </div>
            </template>

            <ElForm label-width="88px" :model="publishForm" class="form-block">
              <ElFormItem :label="$t('page.mqtt.common.topic')">
                <ElInput v-model="publishForm.topic" :placeholder="$t('page.mqtt.placeholders.topic')" clearable />
              </ElFormItem>
              <ElFormItem :label="$t('page.mqtt.common.qos')">
                <ElSelect v-model="publishForm.qos" class="qos-select">
                  <ElOption :label="$t('page.mqtt.common.qos0')" :value="0" />
                  <ElOption :label="$t('page.mqtt.common.qos1')" :value="1" />
                  <ElOption :label="$t('page.mqtt.common.qos2')" :value="2" />
                </ElSelect>
              </ElFormItem>
              <ElFormItem :label="$t('page.mqtt.publish.msg')">
                <ElInput type="textarea" v-model="publishForm.msg" :rows="4" :placeholder="$t('page.mqtt.placeholders.msg')" />
              </ElFormItem>

              <div class="actions">
                <ElButton type="primary" :loading="publishing" @click="handlePublish">
                  {{ $t('page.mqtt.publish.submit') }}
                </ElButton>
                <ElButton @click="resetPublish">{{ $t('common.reset') }}</ElButton>
              </div>
            </ElForm>
          </ElCard>
        </ElCol>

        <ElCol :xs="24" :md="12">
          <ElCard class="inner-card" shadow="never">
            <template #header>
              <div class="card-header">
                <span>{{ $t('page.mqtt.subscribe.title') }}</span>
              </div>
            </template>

            <ElForm label-width="88px" :model="subscribeForm" class="form-block">
              <ElFormItem :label="$t('page.mqtt.common.topic')">
                <ElInput v-model="subscribeForm.topic" :placeholder="$t('page.mqtt.placeholders.topic')" clearable />
              </ElFormItem>
              <ElFormItem :label="$t('page.mqtt.common.qos')">
                <ElSelect v-model="subscribeForm.qos" class="qos-select">
                  <ElOption :label="$t('page.mqtt.common.qos0')" :value="0" />
                  <ElOption :label="$t('page.mqtt.common.qos1')" :value="1" />
                  <ElOption :label="$t('page.mqtt.common.qos2')" :value="2" />
                </ElSelect>
              </ElFormItem>

              <div class="actions">
                <ElButton type="primary" :loading="subscribing" @click="handleSubscribe">
                  {{ $t('page.mqtt.subscribe.submit') }}
                </ElButton>
                <ElButton @click="resetSubscribe">{{ $t('common.reset') }}</ElButton>
              </div>
            </ElForm>
          </ElCard>
        </ElCol>
      </ElRow>
    </ElCard>

    <ElCard class="inner-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>{{ $t('page.mqtt.logs.title') }}</span>
        </div>
      </template>
      <ElTable :data="logs" size="small" style="width: 100%">
        <ElTableColumn prop="time" :label="$t('page.mqtt.logs.columns.time')" min-width="140" />
        <ElTableColumn prop="topic" :label="$t('page.mqtt.logs.columns.topic')" min-width="160" />
        <ElTableColumn prop="qos" :label="$t('page.mqtt.logs.columns.qos')" min-width="80" />
        <ElTableColumn prop="msg" :label="$t('page.mqtt.logs.columns.msg')">
          <template #default="{ row }">
            <span>{{ row.msg }}</span>
          </template>
        </ElTableColumn>
        <template #empty>
          <div class="empty-block">{{ $t('page.mqtt.logs.empty') }}</div>
        </template>
      </ElTable>
    </ElCard>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { request } from '@/service/request';

const publishing = ref(false);
const subscribing = ref(false);

type MqttLog = { time: string; type: 'publish' | 'subscribe'; topic: string; qos: number; msg?: string };
const logs = ref<MqttLog[]>([]);

const publishForm = reactive({
  topic: 'emqx/publish',
  qos: 1,
  msg: ''
});

const subscribeForm = reactive({
  // 注意：后端控制器默认示例为 emqx/subsribe（少了一个 c），这里保持一致
  topic: 'emqx/subsribe',
  qos: 1
});

function resetPublish() {
  publishForm.topic = 'emqx/publish';
  publishForm.qos = 1;
  publishForm.msg = '';
}

function resetSubscribe() {
  subscribeForm.topic = 'emqx/subsribe';
  subscribeForm.qos = 1;
}

async function handlePublish() {
  if (!publishForm.topic.trim()) {
    ElMessage.warning(window.$t('page.mqtt.errors.topicRequired'));
    return;
  }
  if (!publishForm.msg.trim()) {
    ElMessage.warning(window.$t('page.mqtt.errors.msgRequired'));
    return;
  }
  publishing.value = true;
  const { error } = await request({
    url: '/mqtt/publish',
    method: 'post',
    params: {
      topic: publishForm.topic,
      msg: publishForm.msg,
      qos: publishForm.qos
    }
  });
  publishing.value = false;
  if (!error) {
    logs.value.unshift({
      time: new Date().toLocaleString(),
      type: 'publish',
      topic: publishForm.topic,
      qos: publishForm.qos,
      msg: publishForm.msg
    });
    ElMessage.success(`${window.$t('page.mqtt.publish.success')} - ${window.$t('page.mqtt.common.topic')}: ${publishForm.topic}`);
  }
}

async function handleSubscribe() {
  if (!subscribeForm.topic.trim()) {
    ElMessage.warning(window.$t('page.mqtt.errors.topicRequired'));
    return;
  }
  subscribing.value = true;
  const { error } = await request({
    url: '/mqtt/subscriber',
    method: 'post',
    params: {
      topic: subscribeForm.topic,
      qos: subscribeForm.qos
    }
  });
  subscribing.value = false;
  if (!error) {
    logs.value.unshift({
      time: new Date().toLocaleString(),
      type: 'subscribe',
      topic: subscribeForm.topic,
      qos: subscribeForm.qos
    });
    ElMessage.success(`${window.$t('page.mqtt.subscribe.success')} - ${window.$t('page.mqtt.common.topic')}: ${subscribeForm.topic}`);
  }
}
</script>

<style scoped>
.mqtt-page {
  padding: 12px;
}
.block-card :deep(.el-card__header) {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}
.subtitle {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
.inner-card {
  margin-bottom: 12px;
}
.form-block {
  padding-top: 8px;
}
.qos-select {
  width: 160px;
}
.actions {
  display: flex;
  gap: 12px;
}
</style>
