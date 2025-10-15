<script setup lang="ts">
import {ref, computed, onMounted, watch} from 'vue';
import type {UploadFile, UploadInstance} from 'element-plus';
import {ElMessage} from 'element-plus';
import {$t} from '@/locales';

// 后端 YOLO 服务地址（开发通过前端代理，生产使用直连）
const YOLO_BASE_URL = import.meta.env.DEV ? '/proxy-yolo' : (import.meta.env.VITE_YOLO_BASE_URL ?? 'http://localhost:5000');

// UI 状态
const uploading = ref(false);
const uploadRef = ref<UploadInstance | null>(null);
const selectedFile = ref<UploadFile | null>(null);
const previewUrl = ref<string | null>(null);
const fileList = ref<UploadFile[]>([]);
const taskId = ref<string | null>(null);
const resultImage = ref<string | null>(null);
const detections = ref<Array<{ class: string; confidence: number; bbox: number[] }>>([]);

// 新增：模型选择与置信度阈值
const availableModels = [
  {label: 'yolo11n.pt', value: 'yolo11n.pt'},
  {label: 'yolo11s.pt', value: 'yolo11s.pt'},
  {label: 'yolo11m.pt', value: 'yolo11m.pt'},
  {label: 'yolo11l.pt', value: 'yolo11l.pt'},
  {label: 'yolo11x.pt', value: 'yolo11x.pt'},
];
const selectedModel = ref<string>(availableModels[0].value);
const confidence = ref<number>(0.65);

// 历史记录相关状态与方法
interface HistoryItem {
  file_id: string;
  file_name: string;
  upload_time?: string;
  width?: number;
  height?: number;
  file_type?: string;
  url: string;
  file_details?: Array<{ class: string; confidence: number; bbox: number[] }>;
}

const historyList = ref<HistoryItem[]>([]);
const historyLoading = ref(false);
const historyPage = ref(1);
const historyPageSize = ref(5);
const historyTotal = computed(() => historyList.value.length);
const sortOrder = ref<'asc' | 'desc'>('desc');
const sortedHistory = computed(() => {
  const list = [...historyList.value];
  list.sort((a, b) => {
    const atRaw = a.upload_time ? Date.parse(a.upload_time) : 0;
    const btRaw = b.upload_time ? Date.parse(b.upload_time) : 0;
    const at = Number.isNaN(atRaw) ? 0 : atRaw;
    const bt = Number.isNaN(btRaw) ? 0 : btRaw;
    return sortOrder.value === 'desc' ? bt - at : at - bt;
  });
  return list;
});
const pagedHistory = computed(() => {
  const start = (historyPage.value - 1) * historyPageSize.value;
  const end = start + historyPageSize.value;
  return sortedHistory.value.slice(start, end);
});
watch(sortOrder, () => {
  historyPage.value = 1;
});

const previewVisible = ref(false);
const previewItem = ref<HistoryItem | null>(null);

function openPreview(item: HistoryItem) {
  previewItem.value = item;
  previewVisible.value = true;
}

function formatTime(t?: string) {
  try {
    return t ? new Date(t).toLocaleString() : '';
  } catch {
    return t ?? '';
  }
}

async function fetchHistory() {
  historyLoading.value = true;
  try {
    const resp = await fetch(`${YOLO_BASE_URL}/yolo/history`);
    const data = await resp.json();
    if (resp.ok && data?.code === 200) {
      historyList.value = Array.isArray(data.data) ? data.data : [];
      const pageCount = Math.max(1, Math.ceil(historyTotal.value / historyPageSize.value));
      if (historyPage.value > pageCount) historyPage.value = pageCount;
    } else {
      throw new Error(data?.msg || $t('page.yolo.errors.fetchHistoryFail'));
    }
  } catch (error: any) {
    ElMessage.error(error.message || $t('page.yolo.errors.fetchHistoryFail'));
  } finally {
    historyLoading.value = false;
  }
}

async function deleteHistory(item: HistoryItem) {
  try {
    const resp = await fetch(`${YOLO_BASE_URL}/yolo/history/${item.file_id}`, {method: 'DELETE'});
    const data = await resp.json();
    if (resp.ok && data?.code === 200) {
      historyList.value = historyList.value.filter(h => h.file_id !== item.file_id);
      ElMessage.success($t('common.deleteSuccess'));
      const pageCount = Math.max(1, Math.ceil(historyTotal.value / historyPageSize.value));
      if (historyPage.value > pageCount) historyPage.value = pageCount;
    } else {
      throw new Error(data?.msg || $t('page.yolo.errors.deleteFail'));
    }
  } catch (error: any) {
    ElMessage.error(error.message || $t('page.yolo.errors.deleteFail'));
  }
}

onMounted(() => {
  fetchHistory();
});

// 选择文件后生成本地预览
function handleFileChange(file: UploadFile) {
  // 清理上一次预览
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
  selectedFile.value = file;
  fileList.value = [file];
  if (file?.raw) previewUrl.value = URL.createObjectURL(file.raw);
  // 清空上一次的检测结果
  taskId.value = null;
  resultImage.value = null;
  detections.value = [];
}

function handleFileRemove() {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
  previewUrl.value = null;
  selectedFile.value = null;
  fileList.value = [];
  taskId.value = null;
  resultImage.value = null;
  detections.value = [];
}

// 超出限制时，替换为新选择的文件
function handleExceed(files: File[]) {
  uploadRef.value?.clearFiles();
  fileList.value = [];
  const file = files?.[0];
  (uploadRef.value as any)?.handleStart?.(file);
}

// 手动点击“开始检测”时触发上传（后端接收即开始检测）
async function startDetect() {
  if (!selectedFile.value?.raw) {
    ElMessage.warning($t('page.yolo.errors.noFileSelected'));
    return;
  }
  uploading.value = true;
  try {
    const fd = new FormData();
    fd.append('image', selectedFile.value.raw);
    // 将模型名称与置信度作为查询参数传递
    const query = new URLSearchParams({
      model_name: selectedModel.value,
      conf: confidence.value.toString(),
    }).toString();
    const resp = await fetch(`${YOLO_BASE_URL}/yolo/upload?${query}`, {
      method: 'POST',
      body: fd,
    });
    const data = await resp.json();
    if (!resp.ok || data?.code !== 200 || !data?.data) {
      throw new Error(data?.msg || $t('page.yolo.errors.uploadFail'));
    }
    const info = data.data;
    taskId.value = info.file_id || null;
    resultImage.value = info.url || null;
    detections.value = Array.isArray(info.file_details) ? info.file_details : [];
    await fetchHistory();
  } catch (error: any) {
    ElMessage.error(error.message || $t('page.yolo.errors.detectFail'));
  } finally {
    uploading.value = false;
  }
}

// 上传成功后，后端返回 { code: 200, data: file_info }
async function handleUploadSuccess(response: any, file: UploadFile) {
  try {
    if (response?.code !== 200 || !response?.data) {
      throw new Error($t('page.yolo.errors.uploadDataInvalid'));
    }
    const info = response.data;
    taskId.value = info.file_id || null;
    resultImage.value = info.url || null;
    detections.value = Array.isArray(info.file_details) ? info.file_details : [];
    await fetchHistory();
  } catch (error: any) {
    ElMessage.error(error.message || $t('page.yolo.errors.parseUploadResultFail'));
  } finally {
    uploading.value = false;
  }
}

function handleUploadError() {
  uploading.value = false;
  ElMessage.error($t('page.yolo.errors.uploadFail'));
}

function handleBeforeUpload() {
  // 清空上一次的检测结果
  taskId.value = null;
  resultImage.value = null;
  detections.value = [];
  return true;
}

// 获取检测结果
async function fetchResults(tid: string) {
  try {
    const resp = await fetch(`${YOLO_BASE_URL}/yolo/results/${tid}`);
    const data = await resp.json();
    if (resp.ok && data?.code === 200) {
      const result = data.data;
      resultImage.value = result.url || null;
      detections.value = Array.isArray(result.file_details) ? result.file_details : [];
      await fetchHistory();
    } else {
      const msg = data?.msg || $t('page.yolo.errors.fetchResultFail');
      throw new Error(msg);
    }
  } catch (error: any) {
    ElMessage.error(error.message || $t('page.yolo.errors.fetchResultFail'));
  }
}

// 分类颜色样式函数
function categoryColorClass(name: string) {
  if (!name) return 'border border-transparent bg-[#FFE6E6] text-[#B35C5C] border-[#FFCCCC]';
  let sum = 0;
  for (const ch of name) sum = (sum + ch.charCodeAt(0)) % 1000;
  const idx = sum % 8; // 8 种马卡龙配色
  const colorClasses = [
    'border bg-[#FFE6E6] text-[#B35C5C] border-[#FFCCCC]', // 草莓奶昔粉
    'border bg-[#FFF4E6] text-[#B38B5C] border-[#FFE0B3]', // 香草奶油黄
    'border bg-[#E6F7FF] text-[#5C7BB3] border-[#B3E0FF]', // 薄荷海盐蓝
    'border bg-[#E8F8F5] text-[#4FA39F] border-[#BEEDEA]', // 抹茶牛油果绿
    'border bg-[#F6E8FF] text-[#7A5CA3] border-[#E5CCFF]', // 蓝莓薰衣草紫
    'border bg-[#FFF0F6] text-[#A35C8A] border-[#FFCCE0]', // 覆盆子蜜桃粉
    'border bg-[#E8FFF3] text-[#5CA377] border-[#CCFFE0]', // 开心果青
    'border bg-[#FFF9E6] text-[#A38A5C] border-[#FFEEB3]'  // 焦糖牛奶米黄
  ];
  return colorClasses[idx];
}


</script>

<template>
  <div class="p-24px">
    <ElCard class="min-h-[560px]">
      <template #header>
        <div class="flex items-center gap-8px">
          <div class="text-20px font-700">{{ $t('page.yolo.title') }}</div>
          <div class="text-14px color-gray-6">{{ $t('page.yolo.subtitle') }}</div>
        </div>
      </template>

      <ElRow :gutter="16">
        <!-- 左侧：上传与预览区 -->
        <ElCol :span="10">
          <ElCard shadow="never" class="h-full">
            <div class="text-16px font-600 mb-12px">{{ $t('page.yolo.upload.title') }}</div>
            <!-- 新增：参数设置（模型与置信度） -->
            <div class="mb-12px flex items-center gap-12px">
              <div class="flex items-center gap-6px">
                <span class="text-12px color-gray-6">{{ $t('page.yolo.settings.model') }}</span>
                <ElSelect v-model="selectedModel" size="small" class="w-[110px]">
                  <ElOption v-for="m in availableModels" :key="m.value" :label="m.label" :value="m.value"/>
                </ElSelect>
              </div>
              <div class="flex items-center gap-6px flex-1">
                <span class="text-12px color-gray-6 whitespace-nowrap">
                  {{ $t('page.yolo.settings.confidence') }}
                </span>
                <ElSlider v-model="confidence" :min="0" :max="1" :step="0.01" show-input size="small"/>
              </div>

            </div>

            <ElUpload
              ref="uploadRef"
              class="w-full"
              drag
              :action="`${YOLO_BASE_URL}/yolo/upload`"
              name="image"
              :auto-upload="false"
              :limit="1"
              :file-list="fileList"
              :multiple="false"
              accept="image/*"
              :show-file-list="false"
              :on-success="handleUploadSuccess"
              :on-error="handleUploadError"
              :before-upload="handleBeforeUpload"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :on-exceed="handleExceed"
            >
              <div class="py-8px">
                <template v-if="previewUrl">
                  <div class="w-full aspect-[4/3] bg-[#f5f7fa] border border-dashed border-[var(--el-border-color)] rounded-8px flex items-center justify-center overflow-hidden max-h-[360px] h-[200px]">
                    <ElImage :src="previewUrl" fit="contain" class="w-[94%] h-[94%]"/>
                  </div>
                  <div class="text-12px color-gray-6 mt-6px">{{ $t('page.yolo.upload.selectedTips') }}</div>
                </template>
                <template v-else>
                  <div class="w-full aspect-[4/3] bg-[#f5f7fa] border border-dashed border-[var(--el-border-color)] rounded-8px flex items-center justify-center overflow-hidden max-h-[360px]">
                    <div class="text-center text-[#909399]">
                      <div class="text-16px">{{ $t('page.yolo.upload.dropTips') }}</div>
                      <div class="text-12px color-gray-6 mt-6px">{{ $t('page.yolo.upload.singleOnly') }}</div>
                    </div>
                  </div>
                </template>
              </div>
            </ElUpload>

            <div class="mt-16px flex items-center gap-8px">
              <ElButton type="primary" :disabled="!selectedFile || uploading" @click="startDetect">
                {{ uploading ? $t('page.yolo.buttons.detecting') : $t('page.yolo.buttons.startDetect') }}
              </ElButton>
              <ElButton :disabled="uploading" @click="handleFileRemove">{{ $t('common.reset') }}</ElButton>
            </div>
          </ElCard>
        </ElCol>

        <!-- 右侧：检测结果（仅显示图片） -->
        <ElCol :span="14">
          <ElCard shadow="never" class="h-full">
            <div class="text-16px font-600 mb-12px">{{ $t('page.yolo.result.title') }}</div>
            <div v-if="!resultImage" class="color-gray-6">{{ $t('page.yolo.result.emptyTips') }}</div>
            <div v-else class="result-area">
              <div class="w-full aspect-[4/3] bg-[#f5f7fa] border border-dashed border-[var(--el-border-color)] rounded-8px flex items-center justify-center overflow-hidden max-h-[360px]">
                <ElImage :src="resultImage" fit="contain" class="w-[94%] h-[94%]"/>
              </div>
            </div>
          </ElCard>
        </ElCol>
      </ElRow>

      <!-- 底部全宽：检测详情 -->
      <div class="mt-16px">
        <ElCard shadow="never">
          <div class="text-16px font-600 mb-12px">{{ $t('page.yolo.detail.title') }}</div>
          <ElTable :data="detections" size="small" border stripe v-if="detections.length">
            <ElTableColumn prop="class" :label="$t('page.yolo.detail.columns.class')" width="160">
              <template #default="{ row }">
                <ElTag size="small" :class="categoryColorClass(row.class)">{{ row.class }}</ElTag>
              </template>
            </ElTableColumn>
            <ElTableColumn prop="confidence" :label="$t('page.yolo.detail.columns.confidence')" width="160">
              <template #default="{ row }">
                <ElTag :type="row.confidence >= 0.8 ? 'success' : row.confidence >= 0.5 ? 'warning' : 'danger'">
                  {{ (row.confidence * 100).toFixed(1) }}%
                </ElTag>
              </template>
            </ElTableColumn>
            <ElTableColumn prop="bbox" :label="$t('page.yolo.detail.columns.bbox')">
              <template #default="{ row }">
                <span class="text-12px">{{ Array.isArray(row.bbox) ? row.bbox.join(', ') : row.bbox }}</span>
              </template>
            </ElTableColumn>
          </ElTable>
          <div v-else class="text-13px color-gray-6">{{ $t('common.noData') }}</div>
        </ElCard>
      </div>

      <!-- 历史检测记录 -->
      <div class="mt-16px">
        <ElCard shadow="never">
          <div class="flex items-center justify-between mb-12px">
            <div class="text-16px font-600">{{ $t('page.yolo.history.title') }}</div>
            <div class="flex items-center gap-8px">
              <ElButton size="small" :loading="historyLoading" @click="fetchHistory">{{
                  $t('common.refresh')
                }}
              </ElButton>
              <div class="flex items-center gap-6px">
                <span class="text-12px color-gray-6">{{ $t('page.yolo.sortByTime.label') }}</span>
                <ElButtonGroup>
                  <ElButton size="small" :type="sortOrder === 'desc' ? 'primary' : 'default'"
                            @click="sortOrder = 'desc'">{{ $t('page.yolo.sortByTime.latestFirst') }}
                  </ElButton>
                  <ElButton size="small" :type="sortOrder === 'asc' ? 'primary' : 'default'" @click="sortOrder = 'asc'">
                    {{ $t('page.yolo.sortByTime.oldestFirst') }}
                  </ElButton>
                </ElButtonGroup>
              </div>
            </div>
          </div>
          <div v-if="historyLoading" class="text-13px color-gray-6">{{ $t('page.yolo.loading') }}</div>
          <template v-else>
              <div v-if="historyList.length" class="flex flex-col gap-12px">
              <div v-for="item in pagedHistory" :key="item.file_id" class="grid grid-cols-[120px_1fr_auto] items-center gap-12px border border-[var(--el-border-color)] rounded-6px p-8px">
                <div class="w-[120px] h-[90px] bg-[var(--el-fill-color-light)] rounded-4px overflow-hidden cursor-zoom-in">
                  <ElImage
                    :src="item.url"
                    fit="cover"
                    class="w-full h-full object-cover"
                    :preview-src-list="[item.url]"
                    :initial-index="0"
                    :preview-teleported="true"
                    :z-index="3000"
                  />
                </div>
                <div class="min-w-0">
                  <div class="text-13px text-[var(--el-text-color-primary)] flex items-center min-w-0 mb-8px">
                    <ElTag type="info" class="max-w-full inline-block overflow-hidden text-ellipsis whitespace-nowrap pt-4.7px">{{ item.file_name }}</ElTag>
                  </div>
                  <div class="text-12px color-gray-6">
                    <span v-if="item.width && item.height">{{ $t('page.yolo.meta.resolution') }} {{
                        item.width
                      }} x {{ item.height }}</span>
                    <span v-if="item.file_type" class="ml-8px">
                    {{ $t('page.yolo.meta.type') }} {{ item.file_type }}
                  </span>
                    <span v-if="item.upload_time" class="ml-8px">{{
                        $t('page.yolo.meta.upload')
                      }} {{ formatTime(item.upload_time) }}</span>
                  </div>
                  <div class="text-12px mt-6px">
                    <template v-if="Array.isArray(item.file_details) && item.file_details.length">
                      <div class="flex flex-wrap gap-6px">
                        <ElTag v-for="(d, idx) in item.file_details.slice(0, 6)" :key="idx" size="small"
                               :class="categoryColorClass(d.class)">
                          {{ d.class }} {{ (d.confidence * 100).toFixed(0) }}%
                        </ElTag>
                        <span v-if="item.file_details.length > 6"
                              class="color-gray-6">+{{ item.file_details.length - 6 }}</span>
                      </div>
                    </template>
                    <template v-else>
                      <span class="color-gray-6">{{ $t('common.noData') }}</span>
                    </template>
                  </div>
                </div>
                <div class="flex items-center gap-8px">
                  <ElButton size="small" @click="openPreview(item)">{{ $t('page.yolo.actions.preview') }}</ElButton>
                  <ElPopconfirm :title="$t('page.yolo.confirm.deleteHistory')" @confirm="deleteHistory(item)">
                    <template #reference>
                      <ElButton size="small" type="danger" plain>{{ $t('common.delete') }}</ElButton>
                    </template>
                  </ElPopconfirm>
                </div>
              </div>
            </div>
            <div v-else class="text-13px color-gray-6">{{ $t('page.yolo.history.empty') }}</div>
            <div class="mt-12px flex justify-end" v-if="historyList.length">
              <ElPagination
                layout="prev, pager, next, jumper, sizes"
                :total="historyTotal"
                :page-size="historyPageSize"
                :current-page="historyPage"
                :page-sizes="[5, 10, 15, 20]"
                @size-change="val => historyPageSize = val"
                @current-change="val => historyPage = val"
              />
            </div>
          </template>
        </ElCard>
      </div>

      <!-- 预览弹窗 -->
      <ElDialog v-model="previewVisible" width="40%" :title="$t('page.yolo.previewDialog.title')">
        <div v-if="previewItem">
          <div class="w-full aspect-[4/3] bg-[#f5f7fa] border border-dashed border-[var(--el-border-color)] rounded-8px flex items-center justify-center overflow-hidden h-[240px] max-h-[240px]">
            <ElImage :src="previewItem.url" fit="contain" class="w-[94%] h-[94%]"/>
          </div>
          <div class="mt-12px text-13px color-gray-7">
            <div>{{ $t('page.yolo.previewDialog.fileName') }} {{ previewItem.file_name }}</div>
            <div>{{ $t('page.yolo.previewDialog.resolution') }} {{ previewItem.width }} x {{ previewItem.height }}</div>
            <div>{{ $t('page.yolo.previewDialog.type') }} {{ previewItem.file_type }}</div>
            <div>{{ $t('page.yolo.previewDialog.uploadTime') }} {{ formatTime(previewItem.upload_time) }}</div>
            <div>{{ $t('page.yolo.previewDialog.url') }} {{ previewItem.url }}</div>
          </div>
        </div>
        <template #footer>
          <ElButton @click="previewVisible=false">{{ $t('common.close') }}</ElButton>
        </template>
      </ElDialog>

    </ElCard>
  </div>
</template>
