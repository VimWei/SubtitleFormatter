import os
import subprocess
import sys
from pathlib import Path

import spacy

from ..utils.unified_logger import log_info


class ModelManager:
    """语言模型管理器"""

    @staticmethod
    def get_model(config):
        """获取语言模型实例

        Args:
            config: 配置字典，包含：
                   - language: 语言设置 ('auto'/'en'/'zh')
                   - model_size: 模型大小 ('sm'/'md'/'lg')

        Returns:
            spacy.Language: 加载好的语言模型
        """
        language = config["language"]
        model_size = config["model_size"]

        # 确定模型名称
        if language == "auto" or language == "en":
            model_name = f"en_core_web_{model_size}"
        else:
            model_name = f"{language}_core_news_{model_size}"

        # 设置本地模型目录
        project_root = Path(__file__).resolve().parents[3]
        models_dir = project_root / "models"
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # 本地模型路径
        local_model_path = models_dir / model_name

        # 加载或下载模型
        try:
            if local_model_path.exists():
                # 从本地路径加载
                nlp = spacy.load(str(local_model_path))
                log_info(f"已从本地加载语言模型: {model_name}")
            else:
                # 尝试从系统默认位置加载
                nlp = spacy.load(model_name)
                log_info(f"已从系统加载语言模型: {model_name}")
                
                # 尝试从系统位置复制模型到本地
                try:
                    import shutil

                    # 获取已加载模型的路径
                    model_path = nlp.meta.get('path', '')
                    if not model_path:
                        # 尝试从模型对象获取路径
                        model_path = str(nlp.path) if hasattr(nlp, 'path') else ''
                    
                    if model_path and Path(model_path).exists():
                        shutil.copytree(model_path, local_model_path)
                        log_info(f"已从系统复制模型到本地: {model_name}")
                    else:
                        log_info(f"无法获取系统模型路径，跳过复制: {model_name}")
                except Exception as copy_error:
                    log_info(f"复制模型到本地失败: {copy_error}")
        except OSError:
            log_info(f"正在下载语言模型到本地: {model_name}")
            try:
                # 设置环境变量，让spaCy知道我们要下载到哪里
                original_data_dir = os.environ.get("SPACY_DATA_DIR")
                os.environ["SPACY_DATA_DIR"] = str(models_dir)
                
                try:
                    # 下载模型
                    spacy.cli.download(model_name)
                    
                    # 检查下载是否成功
                    if local_model_path.exists():
                        nlp = spacy.load(str(local_model_path))
                        log_info(f"语言模型已下载并加载: {model_name}")
                    else:
                        raise FileNotFoundError(f"模型下载后未找到: {local_model_path}")
                        
                finally:
                    # 恢复原始的环境变量
                    if original_data_dir:
                        os.environ["SPACY_DATA_DIR"] = original_data_dir
                    else:
                        os.environ.pop("SPACY_DATA_DIR", None)
                        
            except Exception as e:
                log_info(f"本地下载失败，尝试使用系统默认方式: {e}")
                # 如果下载失败，回退到系统默认方式
                spacy.cli.download(model_name)
                nlp = spacy.load(model_name)
                log_info(f"已从系统下载并加载语言模型: {model_name}")
                
                # 尝试从系统位置复制模型到本地
                try:
                    import shutil

                    # 获取已加载模型的路径
                    model_path = nlp.meta.get('path', '')
                    if not model_path:
                        # 尝试从模型对象获取路径
                        model_path = str(nlp.path) if hasattr(nlp, 'path') else ''
                    
                    if model_path and Path(model_path).exists():
                        shutil.copytree(model_path, local_model_path)
                        log_info(f"已从系统复制模型到本地: {model_name}")
                    else:
                        log_info(f"无法获取系统模型路径，跳过复制: {model_name}")
                except Exception as copy_error:
                    log_info(f"复制模型到本地失败: {copy_error}")

        return nlp
