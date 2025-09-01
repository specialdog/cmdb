export const DCIM_TYPE = {
  REGION: 'region',
  IDC: 'idc',
  SERVER_ROOM: 'server_room',
  RACK: 'rack'
}

export const DCIM_CITYPE_NAME = {
  REGION: 'dcim_region',
  IDC: 'dcim_idc',
  SERVER_ROOM: 'dcim_server_room',
  RACK: 'dcim_rack'
}

export const DEVICE_CITYPE_NAME = {
  SWITCH: 'switch',
  FC_SWITCH: 'fc_switch',
  F5: 'bigip',
  ROUTER: 'router',
  FIRE_WALL: 'firewall',
  SERVER: 'server',
  RAID: 'raid'
}

export const DEVICE_CITYPE_MANUFACTURER = {
  HUAWEI: '华为',
  IBM: 'IBM',
  H3C: '华三',
  DELL: '戴尔',
  HP: '惠普',
  KEDACOM: '科达',
  CISCO: '思科',
  LENOVO: '联想'
}

export const DEVICE_CITYPE_MANUFACTURER2 = {
  '华为': 'huawei',
  'IBM': 'ibm',
  '华三': 'h3c',
  '戴尔': 'dell',
  '惠普': 'hp',
  '科达': 'kedacom',
  '思科': 'cisco',
  '联想': 'lenovo'
}

const createTypeNameMap = (typeObj, typeNameObj) => {
  const map = {}

  Object.keys(typeObj).forEach(key => {
    map[typeObj[key]] = typeNameObj[key]
    map[typeNameObj[key]] = typeObj[key]
  })

  return map
}

export const DCIM_TYPE_NAME_MAP = createTypeNameMap(DCIM_TYPE, DCIM_CITYPE_NAME)
