<template>
  <CustomDrawer
    width="825px"
    :visible="visible"
    :bodyStyle="{ height: '100vh', padding: '0px' }"
    :hasTitle="false"
    destroyOnClose
    @close="handleClose"
  >
    <div class="rack-detail">
      <div class="rack-header">
        <div class="rack-header-left">
          <div class="rack-header-name">
            <span class="rack-header-name-label">
              {{ $t('cmdb.dcim.rack') }}
            </span>
            <a-tooltip :title="rackData.name">
              <span class="rack-header-name-value">
                {{ rackData.name }}
              </span>
            </a-tooltip>
          </div>
          <ops-icon
            type="veops-edit"
            class="rack-header-edit"
            @click="clickEdit"
          />
          <ops-icon
            type="veops-delete"
            class="rack-header-delete"
            @click="clickDelete"
          />
        </div>

        <div class="rack-header-right">
          <div
            v-for="(item, index) in countList"
            :key="index"
            class="rack-header-count"
          >
            <span class="rack-header-count-name">{{ $t(item.name) }}:</span>
            <span class="rack-header-count-value">{{ item.value }}</span>
          </div>
        </div>
      </div>

      <a-tabs
        class="rack-detail-tabs"
        v-model="tabActive"
      >
        <a-tab-pane
          key="rackView"
          :tab="$t('cmdb.dcim.rackView')"
        >
          <RackView
            :CITypeRelations="CITypeRelations"
            :rackData="rackData"
            :deviceList="deviceList"
            :rackList="rackList"
            :networkInterfaceData="networkInterfaceData"
          />
        </a-tab-pane>

        <a-tab-pane
          key="rackDetail"
          :tab="$t('cmdb.dcim.rackDetail')"
        >
          <RackGroupAttr
            :ci="rackData"
            :rackCITYpeId="rackCITYpe.id"
          />
        </a-tab-pane>

        <a-tab-pane
          key="deviceList"
          :tab="$t('cmdb.dcim.deviceList')"
        >
          <DeviceList
            :allDeviceList="deviceList"
            :CITypeRelations="CITypeRelations"
          />
        </a-tab-pane>

        <a-tab-pane
          key="operationLog"
          :tab="$t('cmdb.dcim.operationLog')"
        >
          <OperationLog
            v-if="tabActive === 'operationLog'"
            :rackId="rackId"
          />
        </a-tab-pane>
        <a-tab-pane
          key="rackImages"
          :tab="$t('cmdb.dcim.rackImages')"
        >
          <RackImages
            v-if="tabActive === 'rackImages'"
            :rackId="rackId"
          />
        </a-tab-pane>
      </a-tabs>
    </div>
  </CustomDrawer>
</template>

<script>
import { DCIM_TYPE } from '../../constants.js'
import { deleteDCIM } from '@/modules/cmdb/api/dcim.js'
import { getCITypeChildren } from '@/modules/cmdb/api/CITypeRelation'
import { searchCIRelation } from '@/modules/cmdb/api/CIRelation'
import { searchCI2 } from '@/modules/cmdb/api/ci'

import RackView from './rackView/index.vue'
import RackGroupAttr from './rackGroupAttr/index.vue'
import DeviceList from './deviceList/index.vue'
import OperationLog from './operationLog/index.vue'
import RackImages from './rackImages/index.vue'

export default {
  name: 'RackDetail',
  components: {
    RackView,
    RackGroupAttr,
    DeviceList,
    OperationLog,
    RackImages
  },
  props: {
    roomId: {
      type: String,
      default: ''
    },
    rackCITYpe: {
      type: Object,
      default: () => {}
    },
    rackList: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      visible: false,
      rackId: 0,
      tabActive: 'rackView',

      CITypeRelations: [],
      deviceList: [],
      networkInterfaceData: {},
      peerDevCache: {}
    }
  },
  computed: {
    rackData() {
      return this.rackList.find((item) => item._id === this.rackId) || {}
    },
    countList() {
      const {
        u_count = 0,
        u_used_ratio = 0,
        u_slot_abnormal = false
      } = this.rackData

      return [
        {
          name: 'cmdb.dcim.deviceCount',
          value: this.deviceList?.length || 0
        },
        {
          name: 'cmdb.dcim.unitCount',
          value: u_count
        },
        {
          name: 'cmdb.dcim.unitAbnormal',
          value: u_slot_abnormal ? this.$t('yes') : this.$t('no')
        },
        {
          name: 'cmdb.dcim.utilizationRation',
          value: `${u_used_ratio}%`
        }
      ]
    }
  },
  inject: [
    'getTreeData',
    'getRackList'
  ],
  provide() {
    return {
      getDeviceList: this.getDeviceList
    }
  },
  methods: {
    async open(rackId) {
      this.rackId = rackId
      this.visible = true

      if (!this.CITypeRelations.length) {
        const res = await getCITypeChildren(this.rackCITYpe.id)
        this.CITypeRelations = res?.children || []
      }

      await this.getDeviceList()
      await this.getNetworkInterfaces()
    },

    async getDeviceList() {
      if (!this.rackId) {
        return
      }

      const res = await searchCIRelation(`root_id=${this.rackId}&level=1&count=10000`)
      const deviceList = res?.result || []
      deviceList.sort((a, b) => a.u_start - b.u_start)
      this.deviceList = deviceList
    },

    async getNetworkInterfaces() {
      // 遍历每台设备，调用 ci_relations/s 查询下游关系
      const PEER_DEV_CI_TYPE = 28

      if (!this.deviceList.length) {
        this.networkInterfaceData = {}
        return
      }

      const result = {}
      const requests = this.deviceList.map(async (device) => {
        try {
          const res = await searchCIRelation(`root_id=${device._id}&level=1&count=10000`)
          const children = res?.result || []
          const interfaces = children.filter(
            (ci) => ci.ci_type === 'physical_interface'
          )
          if (interfaces.length) {
            result[String(device._id)] = {
              device_name: device.hostname || device.name || String(device._id),
              interfaces: interfaces.map((iface) => {
                const peerDevVal = iface.peer_dev
                const isNumeric = peerDevVal && /^\d+$/.test(String(peerDevVal))
                return {
                  _id: iface._id,
                  peer_dev: peerDevVal || '',
                  peer_dev_id: isNumeric ? Number(peerDevVal) : null,
                  peer_dev_type: isNumeric ? PEER_DEV_CI_TYPE : null,
                  peer_dev_port: iface.peer_dev_port || '',
                  local_dev_port: iface.local_dev_port || '',
                  mac_address: iface.mac_address || '',
                  IP_ADDR: iface.IP_ADDR || '',
                  interface_usage: iface.interface_usage || '',
                  hd_speed: iface.hd_speed || '',
                  other_info: iface.other_info || '',
                  peer_netdev_name: '',
                  peer_description: ''
                }
              })
            }
          }
        } catch (error) {
          console.error(`Failed to load interfaces for device ${device._id}:`, error)
        }
      })

      await Promise.all(requests)

      await this.loadPeerDevInfo(result)

      this.networkInterfaceData = result
    },

    async loadPeerDevInfo(result) {
      // 收集所有数字类型的 peer_dev_id 并去重
      const peerDevIds = new Set()
      Object.values(result).forEach((deviceData) => {
        (deviceData.interfaces || []).forEach((iface) => {
          if (iface.peer_dev_id) {
            peerDevIds.add(iface.peer_dev_id)
          }
        })
      })

      if (!peerDevIds.size) {
        return
      }

      // 只批量查询缓存中缺失的上游交换机
      const missIds = Array.from(peerDevIds).filter((id) => !this.peerDevCache[id])

      if (missIds.length) {
        try {
          const res = await searchCI2(`q=_id:(${missIds.join(';')})&count=10000`)
          const cis = res?.result || []
          cis.forEach((ci) => {
            this.peerDevCache[ci._id] = {
              netdev_name: ci.netdev_name || '',
              description: ci.description || ''
            }
          })
        } catch (error) {
          console.error('Failed to load peer device info:', error)
        }
      }

      // 回填 netdev_name / description
      Object.values(result).forEach((deviceData) => {
        (deviceData.interfaces || []).forEach((iface) => {
          const cache = iface.peer_dev_id ? this.peerDevCache[iface.peer_dev_id] : null
          if (cache) {
            iface.peer_netdev_name = cache.netdev_name || ''
            iface.peer_description = cache.description || ''
          }
        })
      })
    },

    handleClose() {
      this.rackId = 0
      this.tabActive = 'rackView'
      this.visible = false
    },

    clickEdit() {
      this.$emit('openForm', {
        dcimType: DCIM_TYPE.RACK,
        parentId: this.roomId,
        nodeId: this.rackId
      })
      this.handleClose()
    },

    clickDelete() {
      const reqData = { roomId: this.roomId, rackName: this.rackData.name }
      this.$confirm({
        title: this.$t('warning'),
        content: this.$t('confirmDelete'),
        onOk: () => {
          deleteDCIM(DCIM_TYPE.RACK, this.rackId, reqData).then(() => {
            this.$message.success(this.$t('deleteSuccess'))
            this.handleClose()
            this.getRackList()
            this.getTreeData()
          })
        },
      })
    },

    refreshRackList() {
      this.$emit('refreshRackList')
    }
  }
}
</script>

<style lang="less" scoped>
.rack-detail {
  .rack-header {
    height: 44px;
    padding: 0px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: #F7F8FA;

    &-left {
      display: flex;
      align-items: center;
      width: 100%;
      overflow: hidden;
    }

    &-name {
      display: flex;
      align-items: center;
      font-size: 16px;
      font-weight: 900;
      color: #1D2129;
      max-width: calc(100% - 48px);

      &-label {
        flex-shrink: 0;
      }

      &-value {
        color: #2F54EB;
        margin-left: 2px;

        overflow: hidden;
        text-overflow: ellipsis;
        text-wrap: nowrap;
      }
    }

    &-edit {
      margin-left: 8px;
      font-size: 12px;
    }

    &-delete {
      margin-left: 12px;
      font-size: 12px;
      color: #FD4C6A;
    }

    &-right {
      display: flex;
      align-items: center;
      column-gap: 30px;
      flex-shrink: 0;
      margin-left: 12px;
    }

    &-count {
      display: flex;
      align-items: center;

      &-name {
        font-size: 12px;
        font-weight: 400;
        color: #4E5969;
      }

      &-value {
        font-size: 14px;
        font-weight: 700;
        color: #1D2129;
        margin-left: 5px;
      }
    }
  }

  &-tabs {
    margin-left: 19px;
    margin-right: 19px;

    /deep/ .ant-tabs-bar {
      display: inline-block;
    }
  }
}
</style>
