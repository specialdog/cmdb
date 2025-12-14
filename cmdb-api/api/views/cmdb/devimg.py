import os
import subprocess
from flask import request, abort, current_app
from werkzeug.utils import secure_filename
from api.resource import APIView
from api.lib.cmdb.cache import CITypeCache
from api.lib.cmdb.resp_format import ErrFormat

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
DEV_BASE_IMAGE_PATH = '/data/img/devImg'
RACK_BASE_IMAGE_PATH = '/data/img/rackImg'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def ensure_directory_exists(path):
    """确保目录存在，不存在则创建"""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path


class DeviceImageView(APIView):
    url_prefix = (
        "/citypes/<int:ci_type_id>/devimg",
        "/dcim/<int:rack_id>/rackimg"
    )

    def get(self, ci_type_id=None, rack_id=None):
        if 'citypes' in request.path:
            # 验证CI类型存在
            if ci_type_id:
                ci_type = CITypeCache.get(ci_type_id)
            else:
                return abort(400, "CI类型ID是必需的")
            if not ci_type:
                return abort(404, ErrFormat.ci_type_not_found)

            server_id = request.args.get('server_id')

            if not server_id:
                return abort(400, "server_id 参数是必需的")

            image_dir = os.path.join(DEV_BASE_IMAGE_PATH, str(ci_type_id), server_id)
            img_info = self.get_img_info(image_dir)
        else:
            if not rack_id:
                return abort(400, "rack ID是必需的")
            image_dir = os.path.join(RACK_BASE_IMAGE_PATH, str(rack_id))
            img_info = self.get_img_info(image_dir)

        return img_info


    def get_img_info(self, image_dir):
        """
        参数:
            image_dir: 图片路径
            find_all: 是否要根据图片的上一级路径，全局查找
        返回:
            list [图片信息]
        """

        try:
            # 获取目录下所有图片文件
            images = []
            for filename in os.listdir(image_dir):
                if allowed_file(filename):
                    file_path = os.path.join(image_dir, filename)
                    file_stat = os.stat(file_path)
                    file_base64 = self.trans_img_to_base64(file_path, filename)
                    images.append({
                        'filename': filename,
                        'size': file_stat.st_size,
                        'created_time': file_stat.st_ctime,
                        'modified_time': file_stat.st_mtime,
                        'base64': file_base64
                    })

            return self.jsonify(images=images, count=len(images))
        except Exception as e:
            current_app.logger.error(f"获取图片列表失败: {e}")
            return abort(500, f"获取图片列表失败: {str(e)}")


    def find_folders_with_partial_name(self, partial_name, base_path):
        """
        使用系统find命令在指定目录下查找名称包含部分字符串的文件夹

        参数:
            parent_dir (str): 要搜索的父目录路径
            partial_name (str): 不完整的文件夹名称（部分字符串）
            case_sensitive (bool): 是否区分大小写，默认不区分

        返回:
            tuple: (存在与否, 匹配的文件夹路径列表)
                   第一个元素为bool值，第二个元素为所有匹配的文件夹完整路径列表
        """
        cmd = ['find', base_path, '-type', 'd']
        cmd.extend(['-name', f'*{partial_name}*'])

        try:
            # 执行命令并捕获输出
            result = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # 处理输出结果（按行分割）
            folders = [line.strip() for line in result.stdout.splitlines() if line.strip()]
            return len(folders) > 0, folders

        except subprocess.CalledProcessError:
            # 命令执行出错（如目录不存在）
            return False, []


    def trans_img_to_base64(self, file_path, file_name):
        import base64
        try:
            with open(file_path, 'rb') as f:
                image_data = f.read()
                base64_data = base64.b64encode(image_data).decode('utf-8')

            # 获取文件扩展名确定MIME类型
            ext = file_name.split('.')[-1].lower()
            mime_map = {
                'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                'png': 'image/png', 'gif': 'image/gif',
                'bmp': 'image/bmp', 'webp': 'image/webp'
            }
            mime_type = mime_map.get(ext, 'image/jpeg')

            return f"data:{mime_type};base64,{base64_data}"
        except Exception as e:
            current_app.logger.error(f"读取图片失败: {e}")
            return abort(500, f"读取图片失败: {str(e)}")


    def post(self, ci_type_id=None, rack_id=None):
        # 检查是否有文件上传
        if 'file' not in request.files:
            return abort(400, "没有文件被上传")
        files = request.files.getlist('file')
        if not files or files[0].filename == '':
            return abort(400, "没有选择文件")

        if 'citypes' in request.path:
            if ci_type_id:
                ci_type = CITypeCache.get(ci_type_id)
            else:
                return abort(400, "CI类型ID或名称是必需的")

            if not ci_type:
                return abort(404, ErrFormat.ci_type_not_found)

            # 获取请求参数
            params = request.get_json() if request.is_json else request.form.to_dict()
            server_id = params.get('server_id')
            if not server_id:
                return abort(400, "server_id 参数是必需的")
            # 构建存储目录路径
            image_dir = os.path.join(DEV_BASE_IMAGE_PATH, str(ci_type_id), server_id)
        else:
            image_dir = os.path.join(RACK_BASE_IMAGE_PATH, str(rack_id))

        return self.save_img_info(files, image_dir)


    def save_img_info(self, files, image_dir):
        ensure_directory_exists(image_dir)
        uploaded_files = []
        errors = []
        try:
            for file in files:
                if file and allowed_file(file.filename):
                    # 安全的文件名处理
                    filename = secure_filename(file.filename)
                    if not filename:
                        filename = f"image_{len(uploaded_files)}.jpg"

                    # 避免文件名冲突
                    file_path = os.path.join(image_dir, filename)
                    counter = 1
                    base_name, ext = os.path.splitext(filename)
                    while os.path.exists(file_path):
                        filename = f"{base_name}_{counter}{ext}"
                        file_path = os.path.join(image_dir, filename)
                        counter += 1

                    # 保存文件
                    file.save(file_path)
                    uploaded_files.append({
                        'filename': filename,
                        'size': os.path.getsize(file_path)
                    })
                else:
                    errors.append(f"文件 {file.filename} 格式不支持")

            if uploaded_files:
                return self.jsonify(
                    message=f"成功上传 {len(uploaded_files)} 个文件",
                    uploaded_files=uploaded_files,
                    errors=errors if errors else None
                )
            else:
                return abort(400, f"没有有效的图片文件被上传。错误: {'; '.join(errors)}")

        except Exception as e:
            current_app.logger.error(f"文件上传失败: {e}")
            return abort(500, f"文件上传失败: {str(e)}")


    def delete(self, ci_type_id=None, rack_id=None):
        """删除指定图片文件"""
        if 'citypes' in request.path:
            # 验证CI类型
            ci_type = CITypeCache.get(ci_type_id)
            if not ci_type:
                return abort(404, ErrFormat.ci_type_not_found)
            # 获取请求参数
            params = request.get_json() if request.is_json else request.form.to_dict()
            server_id = params.get('server_id')
            filename = params.get('filename')
            file_path = os.path.join(DEV_BASE_IMAGE_PATH, str(ci_type_id), str(server_id), filename)

        else:
            params = request.get_json() if request.is_json else request.form.to_dict()
            filename = params.get('filename')
            file_path = os.path.join(RACK_BASE_IMAGE_PATH, str(rack_id), filename)
        return self.delete_img_info(file_path, filename)


    def delete_img_info(self, file_path, filename):
        if not os.path.exists(file_path):
            return abort(404, "图片文件不存在")
        try:
            os.remove(file_path)
            return self.jsonify(message=f"文件 {filename} 删除成功")
        except Exception as e:
            current_app.logger.error(f"删除文件失败: {e}")
            return abort(500, f"删除文件失败: {str(e)}")
