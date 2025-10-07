<template>
  <div class="rack-grid" :style="containerStyle">
    <div class="rack-grid-toolbar">
      <a-button
        type="primary"
        @click="saveLayoutData"
        :loading="isLoading"
        :disabled="!hasUnsavedChanges"
      >
        <a-icon type="save" />保存布局</a-button>
    </div>
    <!-- 加载状态 -->
    <div v-if="isWaitingLayout" class="rack-grid-loading">
      <a-spin size="large" />
      <div class="loading-text">正在加载布局...</div>
    </div>
    <template v-else-if="rackList.length">
      <vue-draggable-resizable
        v-for="(item, index) in rackList"
        :key="`rack-${index}-${item.id || item.name}`"
        :x="getItemPosition(item, index).x"
        :y="getItemPosition(item, index).y"
        :w="100"
        :h="120"
        :snap="true"
        :snap-tolerance="10"
        :grid="[10, 10]"
        :handles="[]"
        :resizable="false"
        class="rack-draggable-wrapper"
        @dragging="(x, y) => onDragging(x, y, index)"
        @dragstop="(x, y) => onDragStop(x, y, index)"
      >
        <div class="rack-grid-item">
          <div
            v-if="item.u_slot_abnormal"
            class="rack-grid-item-warning"
          >
            <a-icon
              type="warning"
              theme="filled"
              class="rack-grid-item-warning-icon"
            />
            <span class="rack-grid-item-warning-text">
              {{ $t('cmdb.dcim.unitAbnormal') }}
            </span>
          </div>

          <div class="rack-grid-item-header">
            <a-tooltip :title="item.name">
              <div class="rack-grid-item-name">
                {{ item.name }}
              </div>
            </a-tooltip>
            <div class="rack-grid-item-store">
              {{ `${item.u_count || 0}U` }}
            </div>
          </div>

          <img
            class="rack-grid-item-img"
            :src="require(`@/modules/cmdb/assets/dcim/rack.png`)"
          />

          <div class="rack-grid-item-data">
            <ops-icon
              type="a-veops-device2"
              class="rack-grid-item-data-icon"
            />
            <span class="rack-grid-item-data-value">
              {{ item.u_used_count }}/{{ item.u_count }}
            </span>

            <div class="rack-grid-item-data-progress">
              <div
                class="rack-grid-item-data-progress-line"
                :style="{
                  width: item.u_used_ratio + '%'
                }"
              ></div>
              <div
                class="rack-grid-item-data-progress-end"
                :style="{
                  left: item.u_used_ratio + '%'
                }"
              ></div>
            </div>
          </div>

          <a
            class="rack-grid-item-btn"
            @click="openRackDetail(item)"
          >
            <span class="rack-grid-item-btn-text">{{ $t('cmdb.dcim.viewDetail') }}</span>
            <a-icon type="right" class="rack-grid-item-btn-icon" />
          </a>
        </div>
      </vue-draggable-resizable>
    </template>

    <div v-else class="rack-grid-null">
      <img class="rack-grid-null-img" :src="require(`@/assets/data_empty.png`)">
      <div class="rack-grid-null-text">{{ $t('noData') }}</div>
    </div>
  </div>
</template>

<script>
import VueDraggableResizable from 'vue-draggable-resizable'
import { message } from 'ant-design-vue'
import { saveLayout, loadLayout } from '@/modules/cmdb/api/dcim'

export default {
  name: 'RackGrid',
  components: {
    VueDraggableResizable
  },
  props: {
    roomId: {
      type: String,
      default: ''
    },
    rackList: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      itemsPerRow: 8, // 默认每行显示的机架数量
      rackPositions: {}, // 用于每次拖拽结束后，暂存坐标
      hasUnsavedChanges: false,
      isLoading: false,
      roomIdChange: false,
      isWaitingLayout: true
    }
  },
  watch: {
    roomId: {
      deep: true,
      handler(newid, oldid) {
        if (oldid && oldid !== newid) {
          this.rackPositions = {}
          this.hasUnsavedChanges = false
          this.roomIdChange = true
          this.isWaitingLayout = true
        }
      }
    },
    rackList: {
      deep: true,
      handler(newValue) {
        if (this.roomIdChange) {
          // 2. 加载新机房的布局数据
          this.initializePositions()
          // 3. 重新渲染
          this.$nextTick(() => {
            this.$forceUpdate()
          })
          this.roomIdChange = false
        }
      }
    }
  },

  computed: {
    containerStyle() {
      if (!this.rackList.length) {
        return {
          minHeight: '400px',
          width: '100%'
        }
      }

      // 计算所有rack的边界
      let maxX = 0
      let maxY = 0

      this.rackList.forEach((item, index) => {
        const position = this.getItemPosition(item, index)
        maxX = Math.max(maxX, position.x + 100)
        maxY = Math.max(maxY, position.y + 120)
      })

      // 如果没有自定义位置，使用默认网格布局计算
      if (maxX === 0 && maxY === 0) {
        const rows = Math.ceil(this.rackList.length / this.itemsPerRow)
        maxX = this.itemsPerRow * 100
        maxY = rows * 120
      }

      // 放大到1.5倍，添加边距
      const containerWidth = Math.max(maxX * 1.5, 800)
      const containerHeight = Math.max(maxY * 1.5, 400)

      return {
        width: `${containerWidth}px`,
        height: `${containerHeight}px`,
        minHeight: '400px',
        position: 'relative',
        overflow: 'hidden'
      }
    }
  },

  mounted() {
    // 初始化位置数据
    this.initializePositions()
    // 监听容器大小变化
    this.$nextTick(() => {
      this.calculateItemsPerRow()
    })
  },

  methods: {
    saveLayoutData() {
      this.isLoading = true
      const layoutData = {
        rackPositions: Object.entries(this.rackPositions).map(([key, item], index) => ({
          rackName: key,
          x: item.x,
          y: item.y
        }))
      }
      saveLayout({ layoutName: this.roomId, layoutData: layoutData }).then(response => {
        if (response.success) {
          this.hasUnsavedChanges = false
          message.success('布局保存成功')
        } else {
          message.error('布局保存失败')
        }
      }).catch(error => {
        console.log(error)
        message.error('布局保存失败')
      }).finally(() => {
        this.isLoading = false
      })
    },

    async initializePositions() {
      try {
        const response = await loadLayout({ layoutName: this.roomId })
        if (response.success && response.layout) {
          const rackPositions = response.layout.layoutData?.rackPositions
          rackPositions.forEach(pos => {
            this.$set(this.rackPositions, pos.rackName, { x: pos.x, y: pos.y })
          })
        } else {
          this.rackList.forEach((item, index) => {
            this.$set(this.rackPositions, item.name, this.getDefaultPosition(index))
          })
        }
      } catch (error) {
        message.error('加载机架布局失败')
      } finally {
        this.hasUnsavedChanges = false
        this.isWaitingLayout = false
      }
    },

    calculateItemsPerRow() {
      const containerWidth = this.$el?.clientWidth || 1000
      this.itemsPerRow = Math.floor(containerWidth / 100) || 8
    },

    getDefaultPosition(index) {
      const x = (index % this.itemsPerRow) * 100
      const y = Math.floor(index / this.itemsPerRow) * 120
      return { x, y }
    },

    getItemPosition(item, index) {
      let position
      // 获取位置
      if (item.position) {
        position = item.position
      } else if (this.rackPositions[item.name]) {
        position = this.rackPositions[item.name]
      } else {
        position = this.getDefaultPosition(index)
      }
      // 确保位置总是对齐到网格
      return {
        x: Math.round(position.x / 10) * 10,
        y: Math.round(position.y / 10) * 10
      }
    },

    onDragging(x, y, index) {
      // 实时更新位置缓存
      // this.$set(this.rackPositions, this.rackList[index].name, { x, y })
    },

    onDragStop(x, y, index) {
      // 拖拽结束时强制对齐到网格
      const alignedX = Math.round(x / 10) * 10
      const alignedY = Math.round(y / 10) * 10
      // 更新rack的位置数据
      const item = this.rackList[index]
      // this.$set(item, 'position', { x: alignedX, y: alignedY })
      this.$set(this.rackPositions, item.name, { x: alignedX, y: alignedY })
      this.hasUnsavedChanges = true
      // 如果坐标有调整，需要强制更新vue-draggable-resizable的位置
      if (alignedX !== x || alignedY !== y) {
        this.$nextTick(() => {
          // 触发组件重新渲染，确保视觉位置与数据一致
          this.$forceUpdate()
        })
      }
    },

    openRackDetail(data) {
      this.$emit('openRackDetail', data)
    }
  },

  beforeRouteLeave(to, from, next) {
      if (this.hasUnsavedChanges) {
      this.$confirm({
        title: '未保存的更改',
        content: '您有未保存的布局更改，是否要保存？',
        okText: '保存',
        cancelText: '不保存',
        onOk: async () => {
          this.saveLayoutData()
          next()
        },
        onCancel: () => {
          this.hasUnsavedChanges = false
          next()
        }
      })
    } else {
      next()
    }
  }
}
</script>

<style lang="less" scoped>
// 导入vue-draggable-resizable的CSS
@import '~vue-draggable-resizable/dist/VueDraggableResizable.css';

.rack-grid-toolbar {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 12px;
}

.unsaved-indicator {
  font-size: 12px;
  color: #ff4d4f;
}

.rack-grid {
  display: block;
  position: relative;
  overflow: auto;
  padding: 20px;
  background: #f5f5f5;
  transform: scale(0.75);
  transform-origin: top left;

  // 添加网格背景辅助线
  background-image:
    linear-gradient(rgba(0,0,0,.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,0,0,.1) 1px, transparent 1px);
  background-size: 20px 20px;

  .rack-draggable-wrapper {
    // 确保拖拽元素有合适的层级
    z-index: 1;

    &:hover {
      z-index: 10;
    }

    // 拖拽时的样式
    &.dragging {
      z-index: 1000;

      .rack-grid-item {
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
      }
    }
  }

  &-item {
    width: 102.5px;  // 原尺寸的一半
    height: 109.5px;  // 原尺寸的一半
    flex-shrink: 0;
    background-color: #F9FBFF;
    border-radius: 4px;
    border: 1px solid #888888;
    border-top: 2px solid #aaaaaa;
    border-left: 2px solid #aaaaaa;
    border-right: 2px solid #666666;
    border-bottom: 2px solid #666666;
    overflow: hidden;
    position: relative;
    cursor: move;  // 改为移动光标
    text-align: center;
    transition: all 0.2s ease;
    box-sizing: border-box;

    &-warning {
      display: flex;
      align-items: center;
      padding: 1px 3px;  // 缩小padding
      background-color: #FFDEBF;
      border-radius: 2px;
      width: max-content;
      font-size: 10px;  // 缩小字体

      position: absolute;
      top: 15px;  // 调整位置
      left: 50%;
      transform: translateX(-50%);

      &-icon {
        font-size: 10px;  // 缩小图标
        color: #FF7D00;
        margin-right: 1px;
      }

      &-text {
        font-size: 10px;  // 缩小字体
        font-weight: 400;
        color: #FF7D00;
      }

      &::after {
        content: '';
        position: absolute;
        bottom: -3px;  // 调整箭头位置
        left: 50%;
        margin-left: -3px;

        width: 0;
        height: 0;
        border-left: 3px solid transparent;
        border-right: 3px solid transparent;
        border-top: 3px solid #FFDEBF;
      }
    }

    &-header {
      width: 100%;
      height: 12px;  // 缩小高度
      background-color: #8FB9F712;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    &-name {
      height: 12px;  // 缩小高度
      line-height: 12px;
      border-bottom-right-radius: 12px;
      padding-left: 4px;  // 缩小padding
      padding-right: 8px;
      background-color: #4E5969;

      font-size: 10px;  // 缩小字体
      font-weight: 700;
      color: #FFFFFF;
      overflow: hidden;
      text-overflow: ellipsis;
      text-wrap: nowrap;
    }

    &-store {
      padding-right: 5px;  // 缩小padding
      font-size: 10px;  // 缩小字体
      font-weight: 400;
      color: #2F54EB;
      margin-left: 6px;
    }

    &-img {
      height: 56px;  // 缩小图片
      margin-top: 8px;
      transition: all 0.2s;
    }

    &-data {
      margin-top: 8px;  // 缩小间距
      display: flex;
      align-items: center;
      justify-content: center;

      &-icon {
        font-size: 12px;  // 缩小图标
      }

      &-value {
        margin-left: 3px;
        font-size: 10px;  // 缩小字体
        font-weight: 400;
        color: #4E5969;
      }

      &-progress {
        margin-left: 3px;
        width: 48px;  // 缩小进度条
        height: 2px;
        border-radius: 2px;
        background-color: #C3D0EB;
        position: relative;

        &-line {
          height: 2px;
          border-radius: 2px;
          background-color: #7F97FA;
        }

        &-end {
          position: absolute;
          top: 50%;
          margin-top: -6px;
          margin-left: -6px;
          height: 12px;  // 缩小圆点
          width: 12px;
          border-radius: 12px;
          background-color: #3044F112;

          &::after {
            content: '';
            position: absolute;
            z-index: 2;
            top: 50%;
            left: 50%;
            margin-top: -2px;
            margin-left: -2px;
            background-color: #2F54EB;
            width: 4px;  // 缩小内圆
            height: 4px;
            border-radius: 4px;
          }
        }
      }
    }

    &-btn {
      position: absolute;
      right: 8px;  // 调整位置
      bottom: 5px;
      align-items: center;
      display: none;

      &-text {
        margin-right: 1px;
        font-size: 9px;  // 缩小字体
        font-weight: 400;
        color: #2F54EB;
      }

      &-icon {
        font-size: 9px;  // 缩小图标
        color: #2F54EB;
      }
    }

    &:hover {
      background-color: #FFFFFF;
      box-shadow: ~'0px 11px 16px 0px @{primary-color}15';  // 缩小阴影
      z-index: 5;
      border-color: #2F54EB;  // hover时边框变色

      .rack-grid-item-name {
        background-color: #2F54EB;
      }

      .rack-grid-item-img {
        margin-top: 4px;
        height: 64px;  // 缩小hover图片
      }

      .rack-grid-item-data {
        margin-top: 5px;

        &-icon {
          display: none;
        }

        &-progress {
          width: 56px;  // 缩小hover进度条
        }
      }

      .rack-grid-item-btn {
        display: flex;
      }
    }
  }

  &-null {
    padding-top: 150px;
    text-align: center;
    width: 100%;

    &-img {
      width: 150px;
    }

    &-text {
      margin-top: 12px;
    }
  }

  .vdr {
    border: none !important;
  }
}
</style>
