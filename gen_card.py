#!/usr/bin/env python3
"""
AI视频名片Pro - 一键生成器
============================
使用方式: python gen_card.py

根据模板生成每位客户的独立名片HTML页面。
只需要填写客户信息，脚本自动完成全部渲染。
"""

import json
import os
import re
import sys
from datetime import datetime

# ============================================================
# 配置区
# ============================================================
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
TEMPLATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nfc-card.html")
CUSTOMERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "customers.json")

# ============================================================
# 客户数据结构
# ============================================================
CUSTOMER_SCHEMA = {
    "name": "客户姓名（必填）",
    "title": "职业/头衔（必填）",
    "tagline": "一句话介绍（必填）\n例如：专注解决企业合同纠纷 · 累计帮客户挽回损失超5000万",
    "avatar": "头像图片URL（可选，留空用默认图标）",
    "videoUrl": "AI数字人视频链接（可选）",
    "cases": [
        {
            "tag": "案例标签（如：合同纠纷）",
            "title": "案例标题",
            "desc": "案例描述，最好有数据"
        }
    ],
    "phone": "手机号（可选）",
    "qq": "QQ号（可选）",
    "wechat": "微信号（可选）"
}


def load_customers():
    """加载客户数据"""
    if not os.path.exists(CUSTOMERS_FILE):
        # 创建示例配置文件
        example = {
            "_说明": "复制这个模板，每位客户一个对象。name为必填。",
            "customers": [
                {
                    "name": "张三",
                    "title": "资深企业法律顾问",
                    "tagline": "专注解决企业合同纠纷 · 累计帮客户挽回损失超5000万 · 服务200+企业客户",
                    "avatar": "",
                    "videoUrl": "",
                    "cases": [
                        {
                            "tag": "合同纠纷",
                            "title": "某科技公司300万合同纠纷案",
                            "desc": "通过细致的证据梳理和谈判策略，仅用2个月为客户追回全部欠款，节省诉讼费20万+"
                        },
                        {
                            "tag": "股权设计",
                            "title": "某创业公司股权架构设计",
                            "desc": "为创始团队设计4层股权架构，既保证控制权又预留员工期权池，获A轮融资2000万"
                        }
                    ],
                    "phone": "13800138000",
                    "qq": "123456789",
                    "wechat": "zhangsan_lawyer"
                }
            ]
        }
        os.makedirs(os.path.dirname(CUSTOMERS_FILE), exist_ok=True)
        with open(CUSTOMERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(example, f, ensure_ascii=False, indent=2)
        print(f"📄 已创建客户数据文件: {CUSTOMERS_FILE}")
        print(f"   请编辑此文件，填写客户信息后重新运行")
        sys.exit(0)

    with open(CUSTOMERS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("customers", [])


def safe_json_value(val):
    """将值转为安全的JS字符串"""
    if val is None:
        return "''"
    return json.dumps(str(val), ensure_ascii=False)


def generate_card(customer, template):
    """为单个客户生成名片HTML"""
    name = customer.get("name", "未命名")
    safe_name = re.sub(r'[\\/:*?"<>|]', '_', name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_name}_{timestamp}.html"
    filepath = os.path.join(OUTPUT_DIR, filename)

    # 构建客户数据的JS对象
    cases_json = json.dumps(customer.get("cases", []), ensure_ascii=False)

    replace_map = {
        "'__DATA_NAME__'": safe_json_value(customer.get("name", "")),
        "'__DATA_TITLE__'": safe_json_value(customer.get("title", "")),
        "'__DATA_TAGLINE__'": safe_json_value(customer.get("tagline", "")),
        "'__DATA_AVATAR__'": safe_json_value(customer.get("avatar", "")),
        "'__DATA_VIDEO__'": safe_json_value(customer.get("videoUrl", "")),
        "'__DATA_CASES__'": cases_json,
        "'__DATA_PHONE__'": safe_json_value(customer.get("phone", "")),
        "'__DATA_QQ__'": safe_json_value(customer.get("qq", "")),
        "'__DATA_WECHAT__'": safe_json_value(customer.get("wechat", "")),
    }

    # 替换模板中的占位符
    output = template
    for placeholder, value in replace_map.items():
        # template literal 中的占位符
        output = output.replace(placeholder, value)

    # 改为替换 CARD_DATA 对象的默认值
    # 找到 CARD_DATA = { ... } 块并整体替换
    card_data_pattern = re.compile(
        r'const CARD_DATA\s*=\s*\{.*?\};',
        re.DOTALL
    )

    new_card_data = f"""const CARD_DATA = {{
      name: {safe_json_value(customer.get("name", ""))},
      title: {safe_json_value(customer.get("title", ""))},
      tagline: {safe_json_value(customer.get("tagline", ""))},
      avatar: {safe_json_value(customer.get("avatar", ""))},
      videoUrl: {safe_json_value(customer.get("videoUrl", ""))},
      cases: {cases_json},
      phone: {safe_json_value(customer.get("phone", ""))},
      qq: {safe_json_value(customer.get("qq", ""))},
      wechat: {safe_json_value(customer.get("wechat", ""))}
    }};"""

    output = card_data_pattern.sub(new_card_data, output)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(output)

    return filepath, name


def generate_qr_link(filepath):
    """生成二维码链接提示"""
    # 注意：实际部署时需要替换为真实的URL前缀
    filename = os.path.basename(filepath)
    print(f"   部署后链接: https://你的域名.com/vcard/{filename}")
    print(f"   二维码工具: https://cli.im/ (粘贴链接生成二维码)")


def main():
    print("=" * 50)
    print("  AI视频名片Pro - 一键生成器")
    print("=" * 50)

    # 读取模板
    if not os.path.exists(TEMPLATE_FILE):
        print(f"❌ 模板文件不存在: {TEMPLATE_FILE}")
        sys.exit(1)

    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()

    # 加载客户数据
    customers = load_customers()
    if not customers:
        print("⚠️ 没有找到客户数据")
        sys.exit(0)

    print(f"\n📋 共找到 {len(customers)} 位客户\n")

    for i, c in enumerate(customers, 1):
        name = c.get("name", f"客户{i}")
        print(f"  [{i}/{len(customers)}] 正在生成: {name}...", end=" ")

        try:
            filepath, safe_name = generate_card(c, template)
            filesize = os.path.getsize(filepath)
            print(f"✅ 完成 ({filesize/1024:.1f}KB)")
            print(f"   输出: {filepath}")
            generate_qr_link(filepath)
        except Exception as e:
            print(f"❌ 失败: {e}")

    print(f"\n{'=' * 50}")
    print(f"  ✅ 全部生成完毕！")
    print(f"  输出目录: {OUTPUT_DIR}")
    print(f"  📌 下一步:")
    print(f"    1. 将 output/ 目录上传到你的服务器")
    print(f"    2. 将每页的链接写入NFC卡片")
    print(f"    3. 把二维码/链接发给客户")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
