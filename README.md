# AWS Lambda テナント分離モード サンプル

AWS Lambda のテナント分離モード（Tenant Isolation Mode）を使用したマルチテナントアプリケーションのサンプルです。  
Amazon API Gateway REST API と統合し、クライアントからテナント ID を指定して Lambda 関数を呼び出します。

## 概要

テナント分離モードを有効にすると、Lambda は各テナントの呼び出しを個別の実行環境で処理します。  
これにより、テナント間でメモリや `/tmp` ディレクトリのデータが共有されることがなくなり、厳格な分離が実現されます。

## フォルダ構成

```
.
├── README.md           # このファイル
├── template.yaml       # SAM / CloudFormation テンプレート
└── functions/
    └── app.py          # Lambda 関数コード（Python 3.13）
```

## アーキテクチャ

```
クライアント
  │
  │  POST /process
  │  Header: x-tenant-id: <テナントID>
  ▼
API Gateway (REST API)
  │
  │  x-tenant-id → X-Amz-Tenant-Id にマッピング
  ▼
Lambda 関数（テナント分離モード有効）
  │
  │  テナントごとに独立した実行環境で処理
  ▼
レスポンス返却
```

## 前提条件

- AWS CLI がインストール・設定済みであること
- AWS SAM CLI がインストール済みであること
- Python 3.13以降 がインストール済みであること
- 適切な AWS 権限を持つプロファイルが設定されていること

## デプロイ手順

### 1. ビルド

```bash
sam build
```

### 2. デプロイ

```bash
sam deploy --guided
```

初回は `--guided` オプションで対話的に設定を行います。2回目以降は `sam deploy` のみで実行できます。

## 使い方

### curl によるリクエスト例

デプロイ後に出力される API エンドポイント URL を使用します。

#### テナント A としてリクエスト

```bash
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/prod/process \
  -H "Content-Type: application/json" \
  -H "x-tenant-id: tenant-A" \
  -d '{"action": "process"}'
```

#### テナント B としてリクエスト

```bash
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/prod/process \
  -H "Content-Type: application/json" \
  -H "x-tenant-id: tenant-B" \
  -d '{"action": "process"}'
```

### レスポンス例

テナント A の初回リクエスト：

```json
{
  "statusCode": 200,
  "body": {
    "message": "File contents for tenant-A (isolated per tenant)",
    "file_data": {
      "tenant_id": "tenant-A",
      "request_count": 1,
      "first_request": "2026-04-30T12:00:00.000000",
      "requests": [
        {
          "request_number": 1,
          "timestamp": "2026-04-30T12:00:00.000000"
        }
      ]
    }
  }
}
```

テナント A の2回目のリクエストでは `request_count` が 2 に増加します。  
テナント B でリクエストすると、別の実行環境が使用されるため `request_count` は 1 から始まります。

### テナント ID なしでリクエストした場合

```bash
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/prod/process \
  -H "Content-Type: application/json" \
  -d '{"action": "process"}'
```

テナント分離モードが有効な関数では、テナント ID が必須です。  
指定しない場合は以下のエラーが返されます：

```
{"message": "The invoked function is enabled with tenancy configuration. Add a valid tenant ID in your request and try again."}
```

## 注意事項

- テナント分離モードは関数作成時にのみ設定可能です。既存の関数に対して後から有効化することはできません。
- テナントごとに新しい実行環境が作成されるため、コールドスタートが増加する可能性があります。
- すべてのテナントは同じ実行ロールを共有します。テナントごとの細かい権限制御が必要な場合は、上流でテナントスコープの認証情報を伝播させてください。
- API Gateway の HTTP API ではヘッダーオーバーライドができないため、REST API を使用しています。
- テナント分離実行環境の作成時に追加料金が発生します。詳細は [AWS Lambda の料金](https://aws.amazon.com/lambda/pricing/) を参照してください。

## 参考リンク

- [AWS Lambda テナント分離 開発者ガイド](https://docs.aws.amazon.com/lambda/latest/dg/tenant-isolation.html)
- [テナント分離での Lambda 関数の呼び出し](https://docs.aws.amazon.com/lambda/latest/dg/tenant-isolation-invoke.html)
- [AWS Lambda のテナント分離モードによるマルチテナントアプリケーション開発の効率化（ブログ）](https://aws.amazon.com/jp/blogs/news/streamlined-multi-tenant-application-development-with-tenant-isolation-mode-in-aws-lambda/)

## クリーンアップ

デプロイしたリソースを削除するには：

```bash
sam delete --no-prompts
```
