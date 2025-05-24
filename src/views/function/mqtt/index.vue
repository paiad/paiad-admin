<template>
  <div
    class="flex flex-col w-full max-w-760px h-85vh mx-auto my-20px bg-white rounded-16px shadow-xl overflow-hidden font-sans">
    <div
      class="flex justify-between items-center px-25px py-15px bg-gradient-to-r from-blue-400 to-purple-300 text-white border-b border-white/20 flex-shrink-0 shadow-md">
      <span class="text-1.6em font-bold text-white tracking-0.5px">MQTT Chat</span>
      <div class="header-actions">
        <el-button
          :type="clientInitData.connected ? 'danger' : 'success'"
          :icon="clientInitData.connected ? CircleClose : CircleCheck"
          @click="clientInitData.connected ? closeConnection() : openConnectionDialog()"
          size="small"
          class="ml-12px rounded-20px font-semibold transition-all duration-300 hover:translate-y--1px hover:shadow-lg"
        >
          {{ clientInitData.connected ? '断开' : '连接' }}
        </el-button>
        <el-button
          :type="subscriptionInitData.subscription ? 'warning' : 'primary'"
          :icon="subscriptionInitData.subscription ? Minus : Plus"
          @click="subscriptionInitData.subscription ? unSubscriptionTopicHandler() : openSubscriptionDialog()"
          size="small"
          :disabled="!clientInitData.connected"
          class="ml-12px rounded-20px font-semibold transition-all duration-300 hover:translate-y--1px hover:shadow-lg"
        >
          {{ subscriptionInitData.subscription ? '取消订阅' : '订阅' }}
        </el-button>
      </div>
    </div>

    <div class="flex-grow p-25px bg-gray-100 overflow-y-auto flex flex-col gap-15px">
      <el-scrollbar ref="chatScrollbar" class="flex-grow">
        <div v-for="(msg, index) in chatMessages" :key="index"
             :class="['message-item', msg.sender, 'flex max-w-full items-end', msg.sender === 'me' ? 'justify-end' : 'justify-start']">
          <div
            :class="['message-content', 'flex flex-col-reverse gap-4px', msg.sender === 'me' ? 'items-end' : 'items-start']">
            <div class="message-meta text-0.8em text-gray-400 flex items-center gap-8px order-2 px-4px"
                 :class="msg.sender === 'me' ? 'justify-end' : ''"
            >
              <span class="font-semibold" :class="msg.sender === 'me' ? 'text-green-500' : 'text-indigo-600'">{{
                  msg.sender === 'me' ? 'Me' : 'Subscribe Theme'
                }}</span>
              <span class="italic text-0.85em text-blue-4">@ {{ msg.topic }}</span>
              <span class="text-0.8em text-gray-400">{{ formatTime(msg.timestamp) }}</span>
            </div>
            <div class="message-bubble p-12px px-18px rounded-22px break-words leading-1.6 shadow-md relative order-1"
                 :class="msg.sender === 'me' ? 'bg-blue-400 text-white rounded-br-8px' : 'bg-gray-200 text-gray-800 rounded-bl-8px'">
              {{ msg.message }}
            </div>
          </div>
        </div>
      </el-scrollbar>
    </div>

    <div class="relative flex-shrink-0 border-t border-gray-200 bg-white p-18px px-25px">
      <div class="mx-0 mb-6px border border-gray-300 rounded-8px bg-gray-50 px-12px py-8px shadow-sm">
        <el-form :inline="true" :model="publishInfo" class="flex justify-between items-center w-full mb-0">
          <el-form-item label="发布主题" class="mb-0 flex-grow flex items-center">
            <el-input v-model="publishInfo.topic" placeholder="e.g., my/chat/message" size="small" class="w-full"/>
          </el-form-item>
          <el-form-item label="QoS" class="mb-0 flex-grow-0">
            <el-select v-model="publishInfo.qos" placeholder="QoS" size="small" class="w-100px">
              <el-option v-for="q in qosList" :key="q" :label="'QoS ' + q" :value="q as number"/>
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      <el-input
        v-model="publishInfo.payload"
        placeholder="输入要发送的消息..."
        @keyup.enter.native="handleEnterToSend"
      >
        <template #append>
          <el-button
            type="primary"
            @click="doPublish"
            :disabled="!clientInitData.connected || !publishInfo.payload"
            class="bg-black text-white"
          >
            <span class="text-blue">发送</span>
            <el-icon class="el-icon--right text-blue">
              <Right/>
            </el-icon>
          </el-button>
        </template>
      </el-input>
    </div>

    <el-dialog
      v-model="connectionDialogVisible"
      title="连接设置"
      width="400px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form :model="connectionInfo" label-width="80px">
        <el-form-item label="协议">
          <el-input v-model="connectionInfo.protocol" placeholder="ws"/>
        </el-form-item>
        <el-form-item label="主机">
          <el-input v-model="connectionInfo.host" placeholder="localhost"/>
        </el-form-item>
        <el-form-item label="端口">
          <el-input v-model="connectionInfo.port" placeholder="8083"/>
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="connectionInfo.username" placeholder="admin"/>
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="connectionInfo.password" type="password" show-password placeholder="********"/>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="connectionDialogVisible = false">取消</el-button>
          <el-button type="success" @click="createConnection">连接</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog
      v-model="subscriptionDialogVisible"
      title="订阅主题"
      width="400px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form :model="subscriptionInfo" label-width="80px">
        <el-form-item label="主题">
          <el-input v-model="subscriptionInfo.topic" placeholder="e.g., my/chat/#"/>
        </el-form-item>
        <el-form-item label="QoS">
          <el-select v-model="subscriptionInfo.qos" placeholder="选择 QoS">
            <el-option v-for="q in qosList" :key="q" :label="'QoS ' + q" :value="q as number"/>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="subscriptionDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="subscriptionTopicHandler">订阅</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import {nextTick, onMounted, onUnmounted, ref} from 'vue';
import { ElMessage, ElNotification, ElScrollbar } from 'element-plus';
import type { ClientSubscribeCallback, IClientOptions, IClientPublishOptions, IClientSubscribeOptions, MqttClient } from 'mqtt';
import mqtt from 'mqtt';
import { CircleCheck, CircleClose, Minus, Plus, Right } from '@element-plus/icons-vue';

// Define a type for QoS based on MQTT standard
type QoS = 0 | 1 | 2;

// Define message interface
interface ChatMessage {
  sender: 'me' | 'other';
  topic: string;
  message: string;
  timestamp: number;
}

// Define connection info interface
interface ConnectionInfo {
  protocol: string;
  host: string;
  port: string;
  clientId?: string;
  username?: string;
  password?: string;
}

// --- Constants ---
const qosList: QoS[] = [0, 1, 2];

// --- Reactive State ---
const connectionInfo = ref<ConnectionInfo>({
  protocol: 'ws',
  host: 'localhost',
  port: '8083',
  clientId: `emqx_vue_client_${Math.random().toString().substring(2, 8)}`,
  username: 'admin',
  password: '123456',
});

const clientInitData = ref({connected: false});
const subscriptionInitData = ref({subscription: false});

const client = ref<MqttClient | null>(null);
const chatMessages = ref<ChatMessage[]>([]);
const chatScrollbar = ref<InstanceType<typeof ElScrollbar> | null>(null);

const subscriptionInfo = ref<{ topic: string; qos: QoS }>({topic: 'emqx/subscribe', qos: 0});
const publishInfo = ref<{ topic: string; qos: QoS; payload: string }>({topic: 'emqx/publish', qos: 0, payload: ''});

const connectionDialogVisible = ref(false);
const subscriptionDialogVisible = ref(false);

// --- Lifecycle Hooks ---
onMounted(() => {
  // createConnection();
});

onUnmounted(() => {
  if (client.value) {
    client.value.end(true);
  }
});

// --- Utility Functions ---
const formatTime = (timestamp: number): string => {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  return date.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', second: '2-digit'});
};

const scrollToBottom = () => {
  nextTick(() => {
    if (chatScrollbar.value && chatScrollbar.value.wrapRef) {
      chatScrollbar.value.setScrollTop(chatScrollbar.value.wrapRef.scrollHeight);
    }
  });
};

const handleEnterToSend = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    doPublish();
  }
};

// --- Connection Logic ---
const openConnectionDialog = () => {
  console.log('Attempting to open connection dialog...');
  connectionDialogVisible.value = true;
  console.log('connectionDialogVisible set to:', connectionDialogVisible.value);
};

const createConnection = () => {
  console.log('--- createConnection called ---');
  console.log('Current connectionInfo:', JSON.parse(JSON.stringify(connectionInfo.value)));
  const {protocol, host, port, ...options} = connectionInfo.value;

  if (!protocol || !host || !port) {
    ElMessage.error('连接信息不完整：协议、主机和端口都不能为空。');
    console.error('Connection info missing:', {protocol, host, port});
    return;
  }

  const url = `${protocol}://${host}:${port}/mqtt`;
  console.log('Constructing URL:', url);

  if (client.value && client.value.connected) {
    console.log('Existing client connected, attempting to end it.');
    client.value.end(true);
  }

  try {
    // Convert port to number and create proper options
    const clientOptions: IClientOptions = {
      ...options,
      port: parseInt(port, 10)
    };

    client.value = mqtt.connect(url, clientOptions);
    console.log('MQTT client initiated.');

    client.value.on('connect', () => {
      clientInitData.value.connected = true;
      connectionDialogVisible.value = false;
      ElNotification({type: 'success', title: '连接成功', message: `已连接到 ${url}`, position: 'top-right'});
      console.log('MQTT client connected successfully!');
    });

    client.value.on('error', (err: Error) => {
      ElNotification({type: 'error', title: '连接失败', message: err.message, position: 'top-right'});
      clientInitData.value.connected = false;
      console.error('MQTT connection error:', err);
    });

    client.value.on('close', () => {
      if (clientInitData.value.connected) {
        ElNotification({type: 'info', title: '连接关闭', message: 'MQTT 连接已断开', position: 'top-right'});
      }
      clientInitData.value.connected = false;
      subscriptionInitData.value.subscription = false;
      console.log('MQTT connection closed.');
    });

    client.value.on('message', (recvTopic: string, message: Buffer) => {
      console.log(`Received message on topic "${recvTopic}":`, message.toString());
      chatMessages.value.push({
        sender: 'other',
        topic: recvTopic,
        message: message.toString(),
        timestamp: Date.now()
      });
      scrollToBottom();
    });
  } catch (e: any) {
    ElMessage.error(`无法初始化 MQTT 客户端: ${e.message}`);
    console.error('Error initializing MQTT client:', e);
  }
};

const closeConnection = () => {
  if (client.value) {
    console.log('Attempting to close connection.');
    client.value.end(false, () => {
      clientInitData.value.connected = false;
      subscriptionInitData.value.subscription = false;
      ElNotification({type: 'info', title: '断开连接', message: '已断开 MQTT 连接', position: 'top-right'});
      console.log('MQTT connection gracefully ended.');
    });
  }
};

// --- Subscription Logic ---
const openSubscriptionDialog = () => {
  if (!clientInitData.value.connected) {
    ElMessage.warning('请先连接到 MQTT 服务器');
    return;
  }
  subscriptionDialogVisible.value = true;
};

const subscriptionTopicHandler = () => {
  if (!client.value || !clientInitData.value.connected) {
    ElMessage.warning('请先连接到 MQTT 服务器');
    return;
  }
  const {topic, qos} = subscriptionInfo.value;
  if (!topic) {
    ElMessage.warning('请输入订阅主题');
    return;
  }

  const subscribeOptions: IClientSubscribeOptions = { qos };
  const callback: ClientSubscribeCallback = (err: Error | null) => {
    if (err) {
      ElNotification({ type: 'error', title: '订阅失败', message: err.message, position: 'top-right' });
      return;
    }
    subscriptionInitData.value.subscription = true;
    subscriptionDialogVisible.value = false;
    ElNotification({type: 'success', title: '订阅成功', message: `已订阅主题: ${topic}`, position: 'top-right'});
  };

  client.value.subscribe(topic, subscribeOptions, callback);
};

const unSubscriptionTopicHandler = () => {
  if (!client.value || !clientInitData.value.connected) {
    ElMessage.warning('请先连接到 MQTT 服务器');
    return;
  }
  const {topic} = subscriptionInfo.value;
  if (!topic) {
    ElMessage.warning('请输入要取消订阅的主题');
    return;
  }

  client.value.unsubscribe(topic, (err: Error | null) => {
    if (err) {
      ElNotification({type: 'error', title: '取消订阅失败', message: err.message, position: 'top-right'});
      return;
    }
    subscriptionInitData.value.subscription = false;
    ElNotification({type: 'info', title: '已取消订阅', message: `已取消订阅主题: ${topic}`, position: 'top-right'});
  });
};

// --- Publish Logic ---
const doPublish = () => {
  if (!client.value || !clientInitData.value.connected) {
    ElMessage.warning('请先连接到 MQTT 服务器');
    return;
  }
  const {topic, qos, payload} = publishInfo.value;
  if (!topic || !payload.trim()) {
    ElMessage.warning('主题和消息不能为空');
    return;
  }

  const publishOptions: IClientPublishOptions = { qos };

  client.value.publish(topic, payload, publishOptions, (err?: Error) => {
    if (err) {
      ElNotification({type: 'error', title: '发送失败', message: err.message, position: 'top-right'});
      return;
    }
    chatMessages.value.push({sender: 'me', topic, message: payload, timestamp: Date.now()});
    publishInfo.value.payload = '';
    scrollToBottom();
  });
};
</script>
