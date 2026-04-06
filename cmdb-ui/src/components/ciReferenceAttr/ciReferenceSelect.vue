<template>
  <div class="ci-reference-select">
    <!-- 搜索框 -->
    <a-input-search
      :placeholder="$t(`请搜索${this.alias}ID`)"
      @search="handleSearch"
    />

    <!-- 单选模式 -->
    <a-radio-group
      v-if="!isList && CIList.length"
      :value="currentSelect"
      class="ci-reference-select-group"
      @change="handleCIChange"
    >
      <a-radio
        v-for="item in CIList"
        :key="item.key"
        :value="item.key"
        class="ci-reference-select-item"
      >
        <a-tooltip :title="item.title" placement="topLeft">
          {{ item.title }}
        </a-tooltip>
      </a-radio>
    </a-radio-group>

    <!-- 多选模式 -->
    <a-checkbox-group
      v-else-if="isList && CIList.length"
      v-model="localSelectedValues"
      class="ci-reference-select-group"
    >
      <a-checkbox
        v-for="item in CIList"
        :key="item.key"
        :value="item.key"
        class="ci-reference-select-item"
      >
        <a-tooltip :title="item.title" placement="topLeft">
          {{ item.title }}
        </a-tooltip>
      </a-checkbox>
    </a-checkbox-group>

    <!-- 空数据 -->
    <div v-else class="ci-reference-select-null">
      <img class="ci-reference-select-null-img" :src="require('@/assets/data_empty.png')" />
      <div class="ci-reference-select-null-text">{{ $t('noData') }}</div>
    </div>

    <!-- 分页 -->
    <div class="ci-reference-select-pagination">
      <a-pagination
        :current="page"
        :total="totalNumber"
        :page-size="pageSize"
        :page-size-options="['20', '50', '100']"
        size="small"
        show-quick-jumper
        show-size-changer
        @change="handleChangePage"
        @showSizeChange="onShowSizeChange"
      />
    </div>

    <!-- 多选模式的操作按钮 -->
    <div v-if="isList" class="ci-reference-select-actions">
      <a-button size="small" @click="handleCancel">
        {{ $t('cancel') }}
      </a-button>
      <a-button type="primary" size="small" @click="handleConfirm">
        {{ $t('confirm') }}
      </a-button>
    </div>
  </div>
</template>

<script>
import { searchCI, getCIType } from '@/api/cmdb'

export default {
  name: 'CIReferenceSelect',
  props: {
    value: {
      type: [Number, String, Array],
      default: () => null
    },
    isList: {
      type: Boolean,
      default: false
    },
    referenceShowAttrName: {
      type: String,
      default: ''
    },
    referenceTypeId: {
      type: [String, Number],
      default: ''
    }
  },
  data() {
    return {
      page: 1,
      pageSize: 20,
      totalNumber: 0,
      CIList: [],
      searchValue: '',
      innerReferenceShowAttrName: '',
      unique_name: '',
      alias: '',
      localSelectedValues: [] // 多选模式的本地临时选中值
    }
  },
  computed: {
    currentSelect() {
      if (this.isList) {
        return this.value || []
      }
      return this.value ? Number(this.value) : undefined
    }
  },
  watch: {
    referenceTypeId: {
      immediate: true,
      handler(newVal) {
        this.page = 1
        this.searchValue = ''
        if (newVal) {
          this.init()
        } else {
          this.CIList = []
          this.totalNumber = 0
        }
      }
    },
    value: {
      immediate: true,
      handler(val) {
        // 初始化多选模式的本地值
        if (this.isList) {
          this.localSelectedValues = val || []
        }
      }
    }
  },
  methods: {
    async init() {
      if (!this.referenceShowAttrName) {
        const res = await getCIType(this.referenceTypeId)
        const ciType = res?.ci_types?.[0]
        this.innerReferenceShowAttrName = ciType?.show_name || ciType?.unique_name || ''
        this.unique_name = ciType?.unique_name || ''
        this.alias = ciType?.alias || ''
      }
      await this.getCIList()
    },

    async getCIList() {
      const attrName = this.referenceShowAttrName || this.innerReferenceShowAttrName || ''
      if (!attrName) return

      let searchValue = ''
      if (this.searchValue) {
        if (typeof this.searchValue === 'object') {
          const [key, value] = Object.entries(this.searchValue)[0]
          searchValue = `,${key}:${value}`
        } else {
          searchValue = `,*${this.searchValue}*`
        }
      }
      const res = await searchCI({
        q: `_type:${this.referenceTypeId}${searchValue}`,
        fl: attrName,
        count: this.pageSize,
        page: this.page
      })

      this.CIList = res?.result?.map(item => ({
        key: item._id,
        title: String(item?.[attrName] ?? '')
      })) || []

      this.totalNumber = res?.numfound || 0
    },

    handleSearch(value) {
      this.searchValue = this.unique_name ? { [this.unique_name]: value } : { value }
      this.page = 1
      this.getCIList()
    },

    handleChangePage(page) {
      this.page = page
      this.getCIList()
    },

    onShowSizeChange(_, pageSize) {
      this.page = 1
      this.pageSize = pageSize
      this.getCIList()
    },

    // 单选模式：立即触发变更并关闭
    handleCIChange(e) {
      const value = e.target.value
      const findCI = this.CIList.find((item) => item.key === value)

      // 传递完整的选中项信息
      this.$emit('change', {
        value: findCI.key,
        title: findCI.title,
        // 添加其他需要的字段
      })
    },

    // 多选模式：确认按钮
    handleConfirm() {
      // 获取所有选中项的完整信息
      const selectedItems = this.CIList.filter(item =>
        this.localSelectedValues.includes(item.key)
      )
      this.$emit('change', {
        values: this.localSelectedValues,
        items: selectedItems, // 传递完整的选中项信息
      })
    },

    // 多选模式：取消按钮
    handleCancel() {
      this.$emit('cancel')
    }
  }
}
</script>

<style lang="less" scoped>
.ci-reference-select {
  width: 650px;

  &-group {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    row-gap: 20px;
    margin: 12px 0;
    max-height: 40vh;
    overflow-y: auto;
  }

  &-item {
    width: 48%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &-null {
    margin: 30px 0;
    text-align: center;

    &-img {
      width: 130px;
    }

    &-text {
      margin-top: 12px;
    }
  }

  &-pagination {
    text-align: right;
    margin-top: 4px;
  }

  &-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #f0f0f0;
  }
}
</style>
