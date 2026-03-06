<template>
  <div class="reference-attr-select-wrap">
    <!-- 弹窗模式 -->
    <template>
      <a-popover
        v-model="popoverVisible"
        trigger="click"
        placement="bottom"
        overlayClassName="ci-reference-popover"
        :getPopupContainer="trigger => trigger.parentElement"
      >
        <div slot="content" @click.stop @mousedown.stop>
          <CIReferenceSelect
            slot="content"
            :value="selectCIIds"
            :isList="isList"
            :referenceShowAttrName="referenceShowAttrName"
            :referenceTypeId="referenceTypeId"
            @change="handleModalChange"
            @cancel="handleModalCancel"/>
        </div>

        <div class="reference-attr-modal-trigger">
          <span v-if="displayText" class="reference-attr-modal-text">
            {{ displayText }}
          </span>
          <span v-else class="reference-attr-modal-placeholder">
            {{ $t('placeholder2') }}
          </span>
          <a-icon
            v-if="allowClear && selectCIIds && (isList ? selectCIIds.length : true)"
            type="close-circle"
            class="reference-attr-modal-clear"
            @click.stop="handleClear"
          />
        </div>
      </a-popover>
    </template>
  </div>
</template>

<script>
import { searchCI, getCIType } from '@/api/cmdb'
import CIReferenceSelect from './ciReferenceSelect.vue'

export default {
  name: 'CIReferenceAttr',
  components: {
    CIReferenceSelect
  },
  props: {
    value: {
      type: [Number, String, Array],
      default: () => '',
    },
    isList: {
      type: Boolean,
      default: false,
    },
    referenceShowAttrName: {
      type: String,
      default: ''
    },
    referenceTypeId: {
      type: [String, Number],
      default: ''
    },
    initSelectOption: {
      type: Array,
      default: () => []
    },
    allowClear: {
      type: Boolean,
      default: true
    }
  },
  model: {
    prop: 'value',
    event: 'change',
  },
  data() {
    return {
      isInit: false,
      options: [],
      innerReferenceShowAttrName: '',
      popoverVisible: false,
      // 用于弹窗模式的显示名称映射 { id: name }
      selectedItemsMap: {}
    }
  },
  computed: {
    selectCIIds: {
      get() {
        if (this.isList) {
          return this.value || []
        } else {
          return this.value ? Number(this.value) : ''
        }
      },
      set(val) {
        this.$emit('change', val ?? (this.isList ? [] : null))
        return val
      },
    },
    // 弹窗触发器显示文本
    displayText() {
      if (this.isList) {
        const ids = this.selectCIIds || []
        if (!ids.length) return ''

        // 显示前2个 + 剩余数量
        const names = ids.slice(0, 2).map(id => this.selectedItemsMap[id] || id)
        const text = names.join(', ')
        return ids.length > 2 ? `${text} +${ids.length - 2}` : text
      }
      return this.selectedItemsMap[this.selectCIIds] || ''
    }
  },
  watch: {
    selectCIIds: {
      immediate: true,
      handler(val) {
        if (val) {
          this.loadDisplayNames()
        }
      }
    }
  },
  methods: {
    // 弹窗模式的变更处理
    handleModalChange(data) {
      if (this.isList) {
        // 多选模式
        const { values, items } = data

        // 更新显示名称映射
        items.forEach(item => {
          this.selectedItemsMap[item.key] = item.title
        })

        // 触发变更
        this.$emit('change', values || [])

        // 关闭弹窗
        this.popoverVisible = false
      } else {
        // 单选模式
        const { value, title } = data

        // 更新显示名称映射
        this.selectedItemsMap[value] = title

        // 触发变更
        this.$emit('change', value)

        // 关闭弹窗
        this.popoverVisible = false
      }
    },

    // 取消弹窗
    handleModalCancel() {
      this.popoverVisible = false
    },

    // 清空选择
    handleClear() {
      this.$emit('change', this.isList ? [] : null)
      this.selectedItemsMap = {}
    },

    // 加载显示名称（用于弹窗触发器显示）
    async loadDisplayNames() {
      if (!this.selectCIIds || (Array.isArray(this.selectCIIds) && !this.selectCIIds.length)) {
        this.selectedItemsMap = {}
        return
      }

      // 如果已经有映射，跳过加载
      const ids = Array.isArray(this.selectCIIds) ? this.selectCIIds : [this.selectCIIds]
      const needLoad = ids.filter(id => !this.selectedItemsMap[id])

      if (!needLoad.length) return

      const attrName = this.referenceShowAttrName || this.innerReferenceShowAttrName

      if (!attrName) {
        // 如果还没有属性名，先获取
        const res = await getCIType(this.referenceTypeId)
        const ciType = res?.ci_types?.[0]
        this.innerReferenceShowAttrName = ciType?.show_name || ciType?.unique_name || ''
      }

      const finalAttrName = this.referenceShowAttrName || this.innerReferenceShowAttrName
      if (!finalAttrName) return

      const res = await searchCI({
        q: `_id:(${needLoad.join(',')})`,
        fl: finalAttrName,
        count: needLoad.length
      })

      res.result.forEach(item => {
        this.selectedItemsMap[item._id] = String(item?.[finalAttrName] ?? '')
      })
    }
  }
}
</script>

<style lang="less" scoped>
.reference-attr-select-wrap {
  width: 100%;

  .reference-attr-select {
    width: 100%;

    /deep/ .ant-select-dropdown {
      z-index: 15;
    }
  }

  .reference-attr-modal-trigger {
    border: 1px solid #d9d9d9;
    border-radius: 2px;
    line-height: 30px;
    min-height: 32px;
    padding: 0 11px;
    cursor: pointer;
    position: relative;
    transition: all 0.3s;

    &:hover {
      border-color: #40a9ff;
    }

    .reference-attr-modal-text {
      color: rgba(0, 0, 0, 0.65);
    }

    .reference-attr-modal-placeholder {
      color: #bfbfbf;
    }

    .reference-attr-modal-clear {
      position: absolute;
      right: 11px;
      top: 50%;
      transform: translateY(-50%);
      color: rgba(0, 0, 0, 0.25);
      font-size: 12px;

      &:hover {
        color: rgba(0, 0, 0, 0.45);
      }
    }
  }
}

/deep/ .ci-reference-popover {
  .ant-popover-inner-content {
    padding: 12px;
  }
}
</style>
