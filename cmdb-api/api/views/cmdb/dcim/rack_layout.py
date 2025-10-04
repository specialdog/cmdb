from flask import request, current_app, abort

from api.models.dcim import DcimRackLayout
from api.resource import APIView


class RackLayoutView(APIView):
    url_prefix = "/dcim/layout"

    def post(self):
        try:
            data = request.get_json()
            if not data:
                return abort(400, "请求数据不能为空")
            layout_name = data.get('layoutName', '')
            layout_data = data.get('layoutData', {})
            layout = DcimRackLayout.get_by(layout_name=layout_name, first=True, to_dict=False)
            if not layout:
                DcimRackLayout.create(layout_name=layout_name, layout_data=layout_data)
            else:
                layout.update(layout_name=layout_name, layout_data=layout_data)
            return self.jsonify({
                "success": True,
                "message": "布局保存成功"
            })
        except Exception as e:
            current_app.logger.error(f"保存布局失败: {str(e)}")
            return abort(500, "保存布局失败")


    def get(self):
        try:
            layout_name = request.args.get('layoutName')
            if layout_name:
                # 加载指定布局
                layout = DcimRackLayout.get_by(layout_name=layout_name, first=True, to_dict=False)
            else:
                return abort(400, "请求数据不能为空")

            if layout:
                return self.jsonify({
                    "success": True,
                    "layout": {
                        "layoutId": layout.id,
                        "layoutName": layout.layout_name,
                        "layoutData": layout.layout_data
                    }
                })
            else:
                return self.jsonify({
                    "success": True,
                    "layout": None,
                    "message": "暂无布局数据"
                })
        except Exception as e:
            current_app.logger.error(f"加载布局失败: {str(e)}")
            return abort(500, "加载失败")
