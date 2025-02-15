print("✅ chat.py 読み込み開始")

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel  #LoRA適用のため追加
import torch
from database import get_custom_response, save_chat
from config import MODEL_PATH, LORA_PATH
from accelerate import infer_auto_device_map, dispatch_model

print("✅ transformers, torch, config のインポート完了")

# トークナイザーのロード
print("✅ トークナイザーのロード開始")
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH,
    local_files_only=True,
    use_fast=True
)
print("✅ トークナイザーのロード完了")

# `pad_token_id` を設定（ない場合は `eos_token_id` に設定）
if tokenizer.pad_token_id is None:
    tokenizer.pad_token_id = tokenizer.eos_token_id

# モデルをロード
print("✅ モデルロード開始...")
max_memory = {0: "5GiB", "cpu": "10GiB"}  # VRAM の使用を制限

# **1. ベースモデルをロード**
base_model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH, 
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto",
    offload_state_dict=True,
    max_memory=max_memory,
    local_files_only=True
)

# **2. LoRA モデルを適用**
print("✅ LoRAモデルを適用...")
model = PeftModel.from_pretrained(base_model, LORA_PATH)  # LoRAを適用
print("✅ LoRAモデル適用完了")

# `device_map` を推論
print("✅ device_map 推論開始")
device_map = infer_auto_device_map(model, max_memory=max_memory)
print("✅ device_map 推論完了")

# モデルを適切なデバイスに配置
print("✅ モデルを適切なデバイスに配置")
model = dispatch_model(model, device_map=device_map, offload_dir="offload", offload_buffers=True)
print("✅ モデルの準備完了")

# チャット関数
def chat_with_ai(user_input):
    print(f"✅ 入力受信: {user_input}")

    # カスタム応答がある場合はそれを返す
    custom_response = get_custom_response(user_input)
    if custom_response:
        return f"(カスタム応答) {custom_response}"

    # 会話のテンプレートを適用
    chat_history = [
        {"role": "system", "content": "あなたはユーザーに寄り添うフレンドリーな AI アシスタントです。"},
        {"role": "user", "content": user_input}
    ]
    
    input_ids = tokenizer.apply_chat_template(
        chat_history,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(device=model.device)

    # `attention_mask` を適切に設定
    attention_mask = input_ids.ne(tokenizer.pad_token_id).long()

    # AI の応答を生成
    output = model.generate(
        input_ids,
        attention_mask=attention_mask,
        max_new_tokens=2048,  # **2048トークンまで生成**
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
        temperature=0.7,  # 生成のランダム性
        top_p=0.9,       # 高確率の単語を選択する閾値
        do_sample=True,
        repetition_penalty=1.1  # 繰り返し抑制
    )

    # 出力のデコード（クリーンな応答を抽出）
    response = tokenizer.decode(output[0], skip_special_tokens=True)

    # 余分な「システムプロンプト」「USER」「ASSISTANT」部分を削除
    response = response.replace("あなたはユーザーに寄り添うフレンドリーな AI アシスタントです。", "").strip()
    response = response.replace("USER:", "").replace("ASSISTANT:", "").strip()

    # ループ防止（ユーザー入力と被る部分を削除）
    response = response.replace(user_input, "").strip()

    save_chat(user_input, response)
    print(f"✅ AI 応答: {response}")
    return response
