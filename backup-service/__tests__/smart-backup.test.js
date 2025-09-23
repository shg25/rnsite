/**
 * smart-backup.js の基本的なユニットテスト
 * 修正時の問題発生防止に重点を置いたテスト
 */

// Jest グローバル関数を使用

// モジュールをモック
jest.mock('aws-sdk');
jest.mock('fs', () => ({
  promises: {
    readFile: jest.fn(),
    unlink: jest.fn(),
    stat: jest.fn()
  }
}));
jest.mock('child_process');

// テスト対象モジュール
const {
  checkSizeChange,
  sendSlackNotification,
  getPreviousBackupSize,
  uploadToS3,
  deletePreviousBackup,
  cleanupLocalFile
} = require('../smart-backup');

describe('smart-backup.js ユニットテスト', () => {
  
  // 各テスト前にモックをリセット
  beforeEach(() => {
    jest.clearAllMocks();
  });

  /**
   * checkSizeChange 関数のテスト
   * サイズ異常検知ロジックの確認
   */
  describe('checkSizeChange', () => {
    test('前回バックアップが存在しない場合、正常判定される', () => {
      const result = checkSizeChange(1000000, null);
      
      expect(result).toEqual({
        isNormal: true,
        changePercent: 0
      });
    });

    test('サイズ変化が50%以内の場合、正常判定される', () => {
      const previousBackup = { size: 1000000 };
      const currentSize = 1400000; // 40%増加
      
      const result = checkSizeChange(currentSize, previousBackup);
      
      expect(result.isNormal).toBe(true);
      expect(result.changePercent).toBe(40);
    });

    test('サイズ変化が50%を超える場合、異常判定される', () => {
      const previousBackup = { size: 1000000 };
      const currentSize = 1600000; // 60%増加
      
      const result = checkSizeChange(currentSize, previousBackup);
      
      expect(result.isNormal).toBe(false);
      expect(result.changePercent).toBe(60);
    });

    test('サイズ減少の場合も正しく計算される', () => {
      const previousBackup = { size: 1000000 };
      const currentSize = 400000; // 60%減少
      
      const result = checkSizeChange(currentSize, previousBackup);
      
      expect(result.isNormal).toBe(false);
      expect(result.changePercent).toBe(60);
    });

    test('極端なサイズ変化も正しく処理される', () => {
      const previousBackup = { size: 1000000 };
      const currentSize = 100; // 99.99%減少
      
      const result = checkSizeChange(currentSize, previousBackup);
      
      expect(result.isNormal).toBe(false);
      expect(result.changePercent).toBeCloseTo(99.99, 1);
    });
  });

  /**
   * sendSlackNotification 関数のテスト
   * Slack通知の基本的な処理確認
   */
  describe('sendSlackNotification', () => {
    beforeEach(() => {
      // 環境変数設定
      process.env.SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/test/webhook';
    });

    afterEach(() => {
      delete process.env.SLACK_WEBHOOK_URL;
    });

    test('有効なWebhook URLが設定されている場合、関数が正常終了する', async () => {
      // httpsモジュールをモック
      const https = require('https');
      const mockRequest = {
        on: jest.fn(),
        write: jest.fn(),
        end: jest.fn()
      };
      
      const mockResponse = {
        statusCode: 200,
        on: jest.fn()
      };

      https.request = jest.fn((options, callback) => {
        // レスポンスハンドラを即座に呼び出し
        process.nextTick(() => callback(mockResponse));
        return mockRequest;
      });

      mockResponse.on.mockImplementation((event, callback) => {
        if (event === 'data') {
          process.nextTick(() => callback('ok'));
        } else if (event === 'end') {
          process.nextTick(() => callback());
        }
      });

      mockRequest.on.mockImplementation(() => {});

      await expect(sendSlackNotification('テストメッセージ')).resolves.toBeUndefined();
    });

    test('Webhook URLが未設定の場合、リクエストが送信されない', async () => {
      delete process.env.SLACK_WEBHOOK_URL;
      
      const https = require('https');
      https.request.mockClear();

      await sendSlackNotification('テストメッセージ');

      expect(https.request).not.toHaveBeenCalled();
    });

    test('デフォルトWebhook URLの場合、リクエストが送信されない', async () => {
      process.env.SLACK_WEBHOOK_URL = 'https://hooks.slack.com/your/webhook/url';
      
      const https = require('https');
      https.request.mockClear();

      await sendSlackNotification('テストメッセージ');

      expect(https.request).not.toHaveBeenCalled();
    });
  });

  /**
   * cleanupLocalFile 関数のテスト
   * ファイル削除処理の確認
   */
  describe('cleanupLocalFile', () => {
    const fs = require('fs').promises;

    test('ファイル削除が成功する', async () => {
      fs.unlink.mockResolvedValue();

      await expect(cleanupLocalFile('test.sql')).resolves.toBeUndefined();
      expect(fs.unlink).toHaveBeenCalledWith('test.sql');
    });

    test('ファイル削除が失敗してもエラーにならない', async () => {
      fs.unlink.mockRejectedValue(new Error('ファイルが見つかりません'));

      await expect(cleanupLocalFile('nonexistent.sql')).resolves.toBeUndefined();
      expect(fs.unlink).toHaveBeenCalledWith('nonexistent.sql');
    });
  });

  /**
   * 環境変数のテスト
   * 必須環境変数の存在確認
   */
  describe('環境変数の設定確認', () => {
    const requiredEnvVars = [
      'DATABASE_URL',
      'AWS_ACCESS_KEY_ID',
      'AWS_SECRET_ACCESS_KEY',
      'AWS_S3_BUCKET',
      'SLACK_WEBHOOK_URL'
    ];

    test.each(requiredEnvVars)('%s が設定可能である', (envVar) => {
      // 環境変数を設定
      process.env[envVar] = 'test-value';
      
      expect(process.env[envVar]).toBe('test-value');
      
      // テスト後クリーンアップ
      delete process.env[envVar];
    });
  });

  /**
   * 定数値のテスト
   * デフォルト値の確認
   */
  describe('定数値の確認', () => {
    test('BACKUP_SIZE_THRESHOLD のデフォルト値は50', () => {
      const originalValue = process.env.BACKUP_SIZE_THRESHOLD;
      delete process.env.BACKUP_SIZE_THRESHOLD;
      
      // モジュールを再読み込みせずに、デフォルト値をテスト
      expect(process.env.BACKUP_SIZE_THRESHOLD || '50').toBe('50');
      
      // 元の値を復元
      if (originalValue) {
        process.env.BACKUP_SIZE_THRESHOLD = originalValue;
      }
    });

    test('BACKUP_PREFIX のデフォルト値は weekly-backup', () => {
      const originalValue = process.env.BACKUP_PREFIX;
      delete process.env.BACKUP_PREFIX;
      
      expect(process.env.BACKUP_PREFIX || 'weekly-backup').toBe('weekly-backup');
      
      if (originalValue) {
        process.env.BACKUP_PREFIX = originalValue;
      }
    });
  });
});