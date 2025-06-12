<script setup lang="ts">
import { computed, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { House, Menu, Plus, Search, ShoppingCart, User, VideoCamera } from '@element-plus/icons-vue';

// Core state: Current active tab
const activeTab = ref('home');

// Search query for filtering products
const searchQuery = ref('');

// Cart items
const cartItems = ref<any[]>([]);

// Mock data: Categories
const categories = ref([
  { name: '电脑', icon: 'https://api.iconify.design/ic:round-computer.svg?color=white', color: '#409EFF' },
  { name: '鞋子', icon: 'https://api.iconify.design/hugeicons:running-shoes.svg?color=white', color: '#67C23A' },
  { name: '服装', icon: 'https://api.iconify.design/ion:shirt-outline.svg?color=white', color: '#E6A23C' },
  { name: '手机', icon: 'https://api.iconify.design/ic:round-smartphone.svg?color=white', color: '#F56C6C' },
  {
    name: '美妆',
    icon: 'https://api.iconify.design/icon-park-outline:foundation-makeup.svg?color=white',
    color: '#E11D48'
  }
]);

// Mock data: Products
const products = ref([
  {
    id: 1,
    name: 'Apple iPad 10.2英寸平板电脑',
    price: 2422,
    imageUrl: 'https://cdn.jsdelivr.net/gh/paiad/picture-bed@main/img/ce6.png'
  },
  {
    id: 2,
    name: 'Apple iPad mini 6',
    price: 3749,
    imageUrl: 'https://cdn.jsdelivr.net/gh/paiad/picture-bed@main/img/ae6.png'
  },
  {
    id: 3,
    name: '轻薄透气速干运动T恤',
    price: 99,
    imageUrl: 'https://cdn.jsdelivr.net/gh/paiad/picture-bed@main/img/pe3.png'
  },
  {
    id: 4,
    name: '复古潮流老爹鞋运动鞋',
    price: 199,
    imageUrl: 'https://cdn.jsdelivr.net/gh/paiad/picture-bed@main/img/ae4.png'
  },
  {
    id: 5,
    name: '新款游戏机械键盘',
    price: 399,
    imageUrl: 'https://cdn.jsdelivr.net/gh/paiad/picture-bed@main/img/ae5.png'
  },
  {
    id: 6,
    name: '高清降噪头戴式耳机',
    price: 459,
    imageUrl: 'https://cdn.jsdelivr.net/gh/paiad/picture-bed@main/img/ae3.png'
  }
]);

// Mock data: Videos
const videos = ref([
  {
    id: 1,
    title: '新款iPad使用教程',
    thumbnail: 'https://cdn.jsdelivr.net/gh/paiad/picture-bed@main/img/ae6.png',
    views: '1.2万'
  },
  {
    id: 2,
    title: '潮流老爹鞋穿搭指南',
    thumbnail: 'https://cdn.jsdelivr.net/gh/paiad/picture-bed@main/img/ae4.png',
    views: '3.5万'
  },
  {
    id: 3,
    title: '机械键盘选购推荐',
    thumbnail: 'https://cdn.jsdelivr.net/gh/paiad/picture-bed@main/img/ae5.png',
    views: '2.1万'
  }
]);

// Mock data: Profile options
const profileOptions = ref([
  { label: '我的订单', icon: 'i-ic:round-shopping-bag text-blue-500', action: 'viewOrders' },
  { label: '我的收藏', icon: 'i-ic:round-favorite text-red-500', action: 'viewFavorites' },
  { label: '设置', icon: 'i-ic:round-settings text-gray-500', action: 'viewSettings' },
  { label: '帮助中心', icon: 'i-ic:round-help text-green-500', action: 'viewHelp' }
]);

// Computed: Filtered products based on search query
const filteredProducts = computed(() => {
  if (!searchQuery.value) return products.value;
  return products.value.filter(product => product.name.toLowerCase().includes(searchQuery.value.toLowerCase()));
});

// Computed: Total cart price
const totalCartPrice = computed(() => {
  return cartItems.value.reduce((total, item) => total + item.price, 0);
});

// Tab switching function
const changeTab = (tabName: string) => {
  activeTab.value = tabName;
};

// Add to cart function with feedback
const addToCart = (product: any) => {
  if (!cartItems.value.find(item => item.id === product.id)) {
    cartItems.value.push({ ...product });
    ElMessage.success(`${product.name} 已添加到购物车！`);
  } else {
    ElMessage.warning('此商品已在购物车中！');
  }
};

// Remove from cart function with feedback
const removeFromCart = (productId: number) => {
  const product = cartItems.value.find(item => item.id === productId);
  cartItems.value = cartItems.value.filter(item => item.id !== productId);
  ElMessage.success(`${product?.name} 已从购物车移除！`);
};

// Toggle menu (placeholder for sidebar or menu)
const toggleMenu = () => {
  ElMessage.info('菜单功能待实现！');
};

// Special tab action (placeholder)
const toggleSpecialAction = () => {
  ElMessage.info('发布功能待实现！');
};

// Handle profile option clicks
const handleProfileOption = (action: string) => {
  ElMessage.info(`点击了 ${action}，功能待实现！`);
};
</script>

<template>
  <div
    class="mobile-app-container box-border flex items-center justify-center from-gray-100 to-gray-200 bg-gradient-to-b p-5"
  >
    <div
      class="phone-screen relative h-[760px] w-[400px] flex flex-col overflow-hidden border-8 border-gray-900 rounded-3xl bg-white shadow-2xl"
    >
      <!-- Header -->
      <header
        class="app-header absolute left-0 right-0 top-0 z-20 h-14 flex items-center gap-4 from-blue-500 to-blue-600 bg-gradient-to-r px-4 shadow-md"
      >
        <ElIcon
          class="header-icon cursor-pointer text-2xl text-white transition-all hover:scale-110 hover:text-blue-200"
          @click="toggleMenu"
        >
          <Menu />
        </ElIcon>
        <div
          class="search-bar h-10 flex flex-1 items-center rounded-full bg-white/90 px-4 shadow-sm transition-all"
          :class="{ 'ring-2 ring-blue-300': searchQuery }"
        >
          <ElIcon class="search-icon mr-2 text-lg text-gray-500"><Search /></ElIcon>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索商品..."
            class="w-full border-none bg-transparent text-sm text-gray-800 outline-none"
            @input="filterProducts"
          />
        </div>
        <ElIcon
          class="user-icon cursor-pointer text-2xl text-white transition-all hover:scale-110 hover:text-blue-200"
          @click="changeTab('profile')"
        >
          <User />
        </ElIcon>
      </header>

      <!-- Main Content with Transition -->
      <Transition name="fade-slide" mode="out-in">
        <main :key="activeTab" class="app-content flex-1 overflow-y-auto bg-gray-100 pb-20 pt-14">
          <!-- Home Page -->
          <div v-if="activeTab === 'home'" class="page-content">
            <img
              src="https://cdn.jsdelivr.net/gh/paiad/picture-bed@main/img/ae2.png"
              alt="Banner"
              class="promo-banner block w-full transform rounded-b-lg shadow-md transition-transform duration-300 hover:scale-[1.02]"
            />

            <div class="category-grid mb-2.5 flex justify-around rounded-lg bg-white p-4 shadow-sm">
              <div
                v-for="cat in categories"
                :key="cat.name"
                class="category-item flex flex-col items-center gap-2 text-xs text-gray-700 font-medium"
              >
                <div
                  class="category-icon-wrapper h-14 w-14 flex items-center justify-center rounded-full transition-transform hover:rotate-6 hover:scale-110"
                  :style="{ backgroundColor: cat.color }"
                >
                  <img :src="cat.icon" class="category-icon h-8 w-8" />
                </div>
                <span>{{ cat.name }}</span>
              </div>
            </div>

            <div class="section-title flex items-center gap-2 px-4 py-3 text-lg text-gray-800 font-bold">
              <i class="i-ic:round-favorite animate-pulse text-xl text-red-500" />
              猜你喜欢
            </div>

            <div class="product-grid grid grid-cols-2 gap-3 px-3 pb-3">
              <div
                v-for="product in filteredProducts"
                :key="product.id"
                class="product-card overflow-hidden rounded-lg bg-white shadow-md transition-all duration-300 hover:shadow-xl hover:-translate-y-1"
              >
                <img
                  :src="product.imageUrl"
                  :alt="product.name"
                  class="product-image block aspect-square w-full object-cover"
                />
                <div class="product-card-body p-3">
                  <p class="product-name line-clamp-2 h-10 text-sm text-gray-800 font-medium">{{ product.name }}</p>
                  <div class="product-price mt-2 flex items-center text-lg text-red-500 font-bold">
                    <span class="text-xs">¥</span>
                    {{ product.price }}
                  </div>
                  <button
                    class="mt-2 w-full flex items-center justify-center rounded-full bg-blue-500 py-1.5 text-sm text-white transition-all duration-200 hover:scale-105 hover:bg-blue-600"
                    @click="addToCart(product)"
                  >
                    <ElIcon class="mr-1"><ShoppingCart /></ElIcon>
                    添加到购物车
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Video Page -->
          <div v-if="activeTab === 'video'" class="video-page min-h-full bg-white p-4">
            <div class="section-title flex items-center gap-2 px-2 py-3 text-lg text-gray-800 font-bold">
              <i class="i-ic:round-videocam animate-bounce text-xl text-blue-500" />
              热门视频
            </div>
            <div class="video-grid grid grid-cols-1 gap-4">
              <div
                v-for="video in videos"
                :key="video.id"
                class="video-card overflow-hidden rounded-lg bg-gray-50 shadow-sm transition-all duration-300 hover:scale-[1.02] hover:shadow-md"
              >
                <img :src="video.thumbnail" :alt="video.title" class="aspect-video w-full object-cover" />
                <div class="p-3">
                  <p class="line-clamp-2 text-sm text-gray-800 font-medium">{{ video.title }}</p>
                  <div class="mt-2 flex items-center gap-2 text-xs text-gray-600">
                    <i class="i-ic:round-play-arrow text-blue-500" />
                    {{ video.views }} 次观看
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Cart Page -->
          <div v-if="activeTab === 'cart'" class="cart-page min-h-full bg-white p-4">
            <div class="section-title flex items-center gap-2 px-2 py-3 text-lg text-gray-800 font-bold">
              <i class="i-ic:round-shopping-cart animate-bounce text-xl text-green-500" />
              购物车
            </div>
            <div v-if="cartItems.length === 0" class="h-full flex flex-col items-center justify-center text-gray-500">
              <i class="i-ic:round-shopping-cart mb-2 animate-pulse text-4xl text-gray-400" />
              <p class="text-lg">您的购物车是空的</p>
              <button
                class="mt-4 rounded-full bg-blue-500 px-4 py-2 text-white transition-all duration-200 hover:scale-105 hover:bg-blue-600"
                @click="changeTab('home')"
              >
                去购物
              </button>
            </div>
            <div v-else class="cart-items">
              <TransitionGroup name="cart-item">
                <div
                  v-for="item in cartItems"
                  :key="item.id"
                  class="cart-item mb-2 flex items-center gap-3 rounded-lg bg-gray-50 p-3 shadow-sm transition-colors duration-200 hover:bg-gray-100"
                >
                  <img :src="item.imageUrl" :alt="item.name" class="h-16 w-16 rounded object-cover" />
                  <div class="flex-1">
                    <p class="line-clamp-1 text-sm text-gray-800 font-medium">{{ item.name }}</p>
                    <p class="text-red-500 font-bold">¥{{ item.price }}</p>
                  </div>
                  <button
                    class="text-red-500 transition-all duration-200 hover:scale-110 hover:text-red-700"
                    @click="removeFromCart(item.id)"
                  >
                    <i class="i-ic:round-delete text-xl" />
                  </button>
                </div>
              </TransitionGroup>
              <div class="mt-4 flex items-center justify-between rounded-lg bg-white p-3 shadow-sm">
                <p class="text-lg text-gray-800 font-bold">总计: ¥{{ totalCartPrice }}</p>
                <button
                  class="rounded-full bg-red-500 px-4 py-2 text-white transition-all duration-200 hover:scale-105 hover:bg-red-600"
                >
                  结算
                </button>
              </div>
            </div>
          </div>

          <!-- Profile Page -->
          <div v-if="activeTab === 'profile'" class="profile-page min-h-full bg-white p-4">
            <div class="section-title flex items-center gap-2 px-2 py-3 text-lg text-gray-800 font-bold">
              <i class="i-ic:round-person animate-pulse text-xl text-purple-500" />
              个人中心
            </div>
            <div
              class="profile-info mb-4 rounded-lg bg-gray-50 p-4 shadow-sm transition-shadow duration-300 hover:shadow-md"
            >
              <div class="flex items-center gap-3">
                <i class="i-ic:round-person animate-bounce text-4xl text-purple-500" />
                <div>
                  <p class="text-lg text-gray-800 font-medium">用户名称</p>
                  <p class="text-sm text-gray-600">ID: 12345678</p>
                </div>
              </div>
            </div>
            <div class="profile-options grid grid-cols-2 gap-3">
              <button
                v-for="option in profileOptions"
                :key="option.label"
                class="flex items-center gap-2 rounded-lg bg-white p-3 shadow-sm transition-all duration-200 hover:scale-105 hover:bg-gray-100"
                @click="handleProfileOption(option.action)"
              >
                <i :class="option.icon" class="text-lg" />
                {{ option.label }}
              </button>
            </div>
          </div>
        </main>
      </Transition>

      <!-- Tab Bar -->
      <nav
        class="app-tab-bar absolute bottom-0 left-0 right-0 z-20 h-16 flex items-center justify-around border-t border-gray-200 bg-white shadow-md"
      >
        <div
          class="tab-item flex flex-col cursor-pointer items-center gap-1 text-sm text-gray-600 transition-all duration-200 hover:scale-105 hover:text-blue-500"
          :class="{ 'text-blue-500': activeTab === 'home' }"
          @click="changeTab('home')"
        >
          <ElIcon class="text-3xl" :class="{ 'text-blue-500': activeTab === 'home' }"><House /></ElIcon>
          <span>首页</span>
        </div>
        <div
          class="tab-item flex flex-col cursor-pointer items-center gap-1 text-sm text-gray-600 transition-all duration-200 hover:scale-105 hover:text-blue-500"
          :class="{ 'text-blue-500': activeTab === 'video' }"
          @click="changeTab('video')"
        >
          <ElIcon class="text-3xl" :class="{ 'text-blue-500': activeTab === 'video' }"><VideoCamera /></ElIcon>
          <span>视频</span>
        </div>
        <div
          class="tab-item special-tab h-14 w-14 flex items-center justify-center border-4 border-white rounded-full from-red-500 to-pink-500 bg-gradient-to-r shadow-lg transition-transform duration-300 -mt-6 hover:scale-110"
          @click="toggleSpecialAction"
        >
          <ElIcon class="text-4xl text-white"><Plus /></ElIcon>
        </div>
        <div
          class="tab-item flex flex-col cursor-pointer items-center gap-1 text-sm text-gray-600 transition-all duration-200 hover:scale-105 hover:text-blue-500"
          :class="{ 'text-blue-500': activeTab === 'cart' }"
          @click="changeTab('cart')"
        >
          <ElIcon class="text-3xl" :class="{ 'text-blue-500': activeTab === 'cart' }"><ShoppingCart /></ElIcon>
          <span>购物车</span>
        </div>
        <div
          class="tab-item flex flex-col cursor-pointer items-center gap-1 text-sm text-gray-600 transition-all duration-200 hover:scale-105 hover:text-blue-500"
          :class="{ 'text-blue-500': activeTab === 'profile' }"
          @click="changeTab('profile')"
        >
          <ElIcon class="text-3xl" :class="{ 'text-blue-500': activeTab === 'profile' }"><User /></ElIcon>
          <span>我的</span>
        </div>
      </nav>
    </div>
  </div>
</template>

<style lang="scss" scoped>
/* Minimal scoped styles since UnoCSS handles most styling */
:deep(.el-icon) {
  width: 1em;
  height: 1em;
}

/* Transition styles for page switching */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* Transition styles for cart items */
.cart-item-enter-active,
.cart-item-leave-active {
  transition: all 0.3s ease;
}
.cart-item-enter-from,
.cart-item-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>
