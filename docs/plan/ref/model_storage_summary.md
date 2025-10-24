# deepmultilingualpunctuation 模型存放位置指定与离线使用

## 1. 问题背景

用户询问 `deepmultilingualpunctuation` 库中使用的模型是否会在首次使用时自动下载，其下载位置在哪里，以及是否可以指定存放位置或提前下载以支持离线使用。

## 2. 模型下载机制与默认缓存

*   **自动下载**: `deepmultilingualpunctuation` 库底层依赖 Hugging Face `transformers` 库。当首次初始化 `PunctuationModel()` 且未指定本地模型路径时，它会自动从 Hugging Face Hub 下载预训练模型。
*   **默认模型**: 库默认使用的模型是 `oliverguhr/fullstop-punctuation-multilang-large`。
*   **默认缓存位置**: 下载的模型文件会缓存到 Hugging Face 的默认缓存目录中：
    *   **Windows**: 通常是 `C:\Users\您的用户名\.cache\huggingface\transformers`
    *   **Linux/macOS**: 通常是 `~/.cache/huggingface/transformers`

## 3. 指定本地模型路径与提前下载

为了实现离线使用或更好地管理模型文件，可以采取以下步骤：

### 步骤一：提前下载模型文件

1.  **创建模型存放目录**: 在项目根目录下创建或选择一个目录用于存放模型文件。例如，我们创建了 `models` 目录。
    ```bash
    mkdir models
    ```
2.  **克隆模型仓库**: 在您选择的模型存放目录（例如 `c:\Downloads\gemini\models`）中，使用 `git clone` 命令从 Hugging Face Hub 下载完整的模型仓库：
    ```bash
    git clone https://huggingface.co/oliverguhr/fullstop-punctuation-multilang-large
    ```
    这将在 `models` 目录下创建一个名为 `fullstop-punctuation-multilang-large` 的子文件夹，其中包含所有模型文件。

### 步骤二：修改 `process_texts.py` 以加载本地模型

修改 `process_texts.py` 文件中 `PunctuationModel` 的初始化代码，将其 `model` 参数指向您本地下载的模型路径。

**修改前代码示例**:

```python
# 3. Initialize the model
print("Loading punctuation model... (This may take a moment)")
model = PunctuationModel()
print("Model loaded.")
```

**修改后代码示例**:

```python
# 3. Initialize the model
# Define the path to the local model.
# This model should be downloaded beforehand to enable offline use.
local_model_path = "models/fullstop-punctuation-multilang-large"
print(f"Loading punctuation model from '{local_model_path}'... (This may take a moment)")
model = PunctuationModel(model=local_model_path)
print("Model loaded.")
```

通过以上步骤，`process_texts.py` 脚本将不再需要从网络下载模型，而是直接加载本地的模型文件，从而支持在离线环境下运行。
