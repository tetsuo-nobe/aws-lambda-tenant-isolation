import json
import os
from datetime import datetime


def lambda_handler(event, context):
    """テナント分離モードが有効なLambda関数のハンドラー"""
    tenant_id = context.tenant_id
    file_path = '/tmp/tenant_data.json'

    # 既存データの読み取りまたは初期化
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
    else:
        data = {
            'tenant_id': tenant_id,
            'request_count': 0,
            'first_request': datetime.utcnow().isoformat(),
            'requests': []
        }

    # カウンターをインクリメントしてリクエスト情報を追加
    data['request_count'] += 1
    data['requests'].append({
        'request_number': data['request_count'],
        'timestamp': datetime.utcnow().isoformat()
    })

    # 更新されたデータをファイルに書き戻す
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

    # ログ
    print(f"tenant_id: {tenant_id}, request_count: {data['request_count']}")

    # 分離を示すためにファイルの内容を返す
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'File contents for {tenant_id} (isolated per tenant)',
            'file_data': data
        })
    }
