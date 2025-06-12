<template>
  <div class="product-list-container">
    <div class="toolbar">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="商品名称">
          <el-input v-model="searchForm.name" placeholder="请输入商品名称" clearable></el-input>
        </el-form-item>
        <el-form-item label="商品编码">
          <el-input v-model="searchForm.sku" placeholder="请输入SKU编码" clearable></el-input>
        </el-form-item>
        <el-form-item label="所属类目">
          <el-select v-model="searchForm.categoryId" placeholder="请选择类目" style="width: 200px;" clearable>
            <el-option
              v-for="item in categoryOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      <el-button type="success" :icon="Plus" @click="handleAdd">添加商品</el-button>
    </div>

    <el-table :data="tableData" v-loading="loading" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" align="center" fixed></el-table-column>
      <el-table-column label="商品信息" min-width="280" fixed>
        <template #default="scope">
          <div class="product-info">
            <el-image
              class="product-image"
              :src="scope.row.imageUrl"
              :preview-src-list="[scope.row.imageUrl]"
              fit="cover"
              preview-teleported
            ></el-image>
            <div class="product-details">
              <div class="product-name">{{ scope.row.name }}</div>
              <div class="product-sku">SKU: {{ scope.row.sku }}</div>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="价格" width="120" align="right">
        <template #default="scope">
          {{ formatCurrency(scope.row.price) }}
        </template>
      </el-table-column>
      <el-table-column prop="stock" label="库存" width="100" align="center">
        <template #default="scope">
          <span :class="{'low-stock': scope.row.stock < 50}">{{ scope.row.stock }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="sales" label="销量" width="100" align="center"></el-table-column>
      <el-table-column label="所属类目" width="150">
        <template #default="scope">
          {{ getCategoryName(scope.row.categoryId) }}
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100" align="center">
        <template #default="scope">
          <el-tag :type="scope.row.status === 1 ? 'success' : 'info'">
            {{ scope.row.status === 1 ? '在售' : '下架' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="180">
        <template #default="scope">
          {{ new Date(scope.row.createdAt).toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column label="操作" fixed="right" width="150" align="center">
        <template #default="scope">
          <el-button type="primary" link :icon="Edit" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button type="danger" link :icon="Delete" @click="handleDelete(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      class="pagination"
      :current-page="pagination.currentPage"
      :page-size="pagination.pageSize"
      :total="pagination.total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    ></el-pagination>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" @close="resetForm" top="5vh">
      <el-form ref="productFormRef" :model="productForm" :rules="productFormRules" label-width="100px">
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="productForm.name" placeholder="请输入商品名称"></el-input>
        </el-form-item>
        <el-form-item label="商品编码" prop="sku">
          <el-input v-model="productForm.sku" placeholder="请输入SKU编码"></el-input>
        </el-form-item>
        <el-form-item label="所属类目" prop="categoryId">
          <el-select v-model="productForm.categoryId" placeholder="请选择类目">
            <el-option
              v-for="item in categoryOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number v-model="productForm.price" :precision="2" :step="10" :min="0" />
        </el-form-item>
        <el-form-item label="库存" prop="stock">
          <el-input-number v-model="productForm.stock" :min="0" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="productForm.status">
            <el-radio :label="1">在售</el-radio>
            <el-radio :label="0">下架</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="商品主图" prop="imageUrl">
          <el-input v-model="productForm.imageUrl" placeholder="请输入图片URL"></el-input>
          <p class="tip">提示：实际项目中应使用 el-upload 组件上传图片。</p>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox, FormInstance, FormRules } from 'element-plus';
import { Search, Refresh, Plus, Edit, Delete } from '@element-plus/icons-vue';

// --- 数据模型定义 ---
interface Product {
  id: number;
  name: string;
  sku: string;
  imageUrl: string;
  price: number;
  stock: number;
  sales: number;
  categoryId: number;
  status: 0 | 1; // 0:下架, 1:在售
  createdAt: string;
}

// --- 模拟类目数据 (用于筛选和显示) ---
const categoryOptions = ref([
  { id: 1, name: '潮流服饰' },
  { id: 2, name: '数码家电' },
  { id: 3, name: '男士T恤' },
  { id: 4, name: '智能手机' },
  { id: 5, name: '女士裙装' },
  { id: 6, name: '笔记本电脑' },
]);

// --- 模拟后端商品数据库 ---
const allProducts = ref<Product[]>([
  { id: 101, name: '超薄全面屏智能手机', sku: 'PH-001', imageUrl: 'https://cdn.jsdelivr.net/gh/paiad/picture-bed@main/img/pe1.png', price: 2999, stock: 999, sales: 1502, categoryId: 4, status: 1, createdAt: '2025-05-20T10:00:00Z' },
  { id: 102, name: '高性能游戏笔记本', sku: 'LP-001', imageUrl: 'https://cdn.jsdelivr.net/gh/paiad/picture-bed@main/img/pe2.png', price: 6999, stock: 45, sales: 320, categoryId: 6, status: 1, createdAt: '2025-05-15T11:30:00Z' },
  { id: 103, name: '纯棉透气男士T恤', sku: 'TS-001', imageUrl: 'https://cdn.jsdelivr.net/gh/paiad/picture-bed@main/img/pe3.png', price: 89, stock: 2500, sales: 8540, categoryId: 3, status: 1, createdAt: '2025-04-10T14:00:00Z' },
  { id: 104, name: '夏季雪纺连衣裙', sku: 'DS-001', imageUrl: 'https://cdn.jsdelivr.net/gh/paiad/picture-bed@main/img/pe4.png', price: 249, stock: 0, sales: 1200, categoryId: 5, status: 0, createdAt: '2025-04-01T09:00:00Z' },
  { id: 105, name: '降噪蓝牙耳机', sku: 'HP-002', imageUrl: 'https://cdn.jsdelivr.net/gh/paiad/picture-bed@main/img/pe5.png', price: 599, stock: 800, sales: 3500, categoryId: 2, status: 1, createdAt: '2025-06-01T18:00:00Z' },
]);

// --- 响应式状态 ---
const loading = ref(false);
const tableData = ref<Product[]>([]);
const searchForm = reactive({ name: '', sku: '', categoryId: '' });
const pagination = reactive({ currentPage: 1, pageSize: 10, total: 0 });

// --- 弹窗与表单 ---
const dialogVisible = ref(false);
const dialogTitle = ref('');
const productFormRef = ref<FormInstance>();
const productForm = reactive({
  id: 0, name: '', sku: '', imageUrl: '', price: 0, stock: 100, sales: 0, categoryId: '', status: 1, createdAt: ''
});
const productFormRules = reactive<FormRules>({
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  sku: [{ required: true, message: '请输入商品编码', trigger: 'blur' }],
  categoryId: [{ required: true, message: '请选择所属类目', trigger: 'change' }],
  price: [{ required: true, type: 'number', message: '请输入价格', trigger: 'blur' }],
  stock: [{ required: true, type: 'number', message: '请输入库存', trigger: 'blur' }],
});


// --- 方法 ---

// 格式化货币
const formatCurrency = (value: number) => `¥${value.toFixed(2)}`;

// 根据ID获取类目名称
const getCategoryName = (categoryId: number) => {
  return categoryOptions.value.find(cat => cat.id === categoryId)?.name || '未知类目';
};

// 模拟API获取数据
const fetchData = () => {
  loading.value = true;
  setTimeout(() => {
    let filteredData = allProducts.value;

    // 搜索过滤
    if (searchForm.name) {
      filteredData = filteredData.filter(item => item.name.includes(searchForm.name));
    }
    if (searchForm.sku) {
      filteredData = filteredData.filter(item => item.sku.includes(searchForm.sku));
    }
    if (searchForm.categoryId) {
      filteredData = filteredData.filter(item => item.categoryId === searchForm.categoryId);
    }

    // 分页
    pagination.total = filteredData.length;
    tableData.value = filteredData.slice(
      (pagination.currentPage - 1) * pagination.pageSize,
      pagination.currentPage * pagination.pageSize
    );

    loading.value = false;
  }, 500);
};

onMounted(fetchData);

const handleSearch = () => { pagination.currentPage = 1; fetchData(); };
const handleReset = () => {
  searchForm.name = ''; searchForm.sku = ''; searchForm.categoryId = '';
  handleSearch();
};
const handleSizeChange = (val: number) => { pagination.pageSize = val; fetchData(); };
const handleCurrentChange = (val: number) => { pagination.currentPage = val; fetchData(); };

const resetForm = () => {
  productFormRef.value?.resetFields();
  Object.assign(productForm, {
    id: 0, name: '', sku: '', imageUrl: '', price: 0, stock: 100, sales: 0, categoryId: '', status: 1, createdAt: ''
  });
};

const handleAdd = () => {
  resetForm();
  dialogTitle.value = '添加新商品';
  dialogVisible.value = true;
};

const handleEdit = (row: Product) => {
  resetForm();
  Object.assign(productForm, row);
  dialogTitle.value = `编辑商品 - ${row.name}`;
  dialogVisible.value = true;
};

const handleDelete = (id: number) => {
  ElMessageBox.confirm('您确定要删除此商品吗?', '警告', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning',
  }).then(() => {
    const index = allProducts.value.findIndex(item => item.id === id);
    if (index !== -1) {
      allProducts.value.splice(index, 1);
      ElMessage.success('删除成功');
      fetchData();
    }
  }).catch(() => ElMessage.info('已取消删除'));
};

const submitForm = () => {
  productFormRef.value?.validate((valid) => {
    if (valid) {
      if (productForm.id === 0) { // 新增
        allProducts.value.unshift({
          ...productForm,
          id: Math.max(...allProducts.value.map(p => p.id), 0) + 1,
          createdAt: new Date().toISOString(),
        });
        ElMessage.success('添加成功');
      } else { // 编辑
        const index = allProducts.value.findIndex(item => item.id === productForm.id);
        if (index !== -1) {
          allProducts.value[index] = { ...productForm };
          ElMessage.success('编辑成功');
        }
      }
      dialogVisible.value = false;
      fetchData();
    } else {
      ElMessage.error('请检查表单输入');
    }
  });
};
</script>

<style lang="scss" scoped>
.product-list-container {
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.product-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.product-image {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  flex-shrink: 0;
}

.product-details {
  display: flex;
  flex-direction: column;
}

.product-name {
  font-weight: 500;
  color: #333;
}

.product-sku {
  font-size: 12px;
  color: #999;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.tip {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.low-stock {
  color: #f56c6c;
  font-weight: bold;
}
</style>
