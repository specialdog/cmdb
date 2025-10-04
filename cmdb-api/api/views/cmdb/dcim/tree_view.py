# -*- coding:utf-8 -*-

from api.lib.cmdb.dcim.tree_view import TreeViewManager
from api.lib.common_setting.decorator import perms_role_required
from api.lib.common_setting.role_perm_base import CMDBApp
from api.resource import APIView

app_cli = CMDBApp()


class DCIMTreeView(APIView):
    url_prefix = "/dcim/tree_view"

    def get(self):
        result, type2name = TreeViewManager.get()

        return self.jsonify(result=result, type2name=type2name)
