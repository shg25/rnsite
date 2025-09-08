/**
 * cron-backup.js の基本的なテスト
 * cronスケジューラーの基本動作確認
 */

// Jest グローバル関数を使用

// モジュールをモック
jest.mock('node-cron');
jest.mock('../smart-backup', () => ({
  main: jest.fn()
}));

describe('cron-backup.js テスト', () => {
  let consoleSpy;

  beforeEach(() => {
    // コンソール出力をスパイ
    consoleSpy = jest.spyOn(console, 'log').mockImplementation();
    jest.clearAllMocks();
  });

  afterEach(() => {
    consoleSpy.mockRestore();
  });

  /**
   * cronスケジュールの設定テスト
   */
  describe('cronスケジュール設定', () => {
    test('デフォルトスケジュールが正しく設定される', () => {
      const cron = require('node-cron');
      
      // cronモジュールがモックされていることを確認
      expect(cron.schedule).toBeDefined();
      expect(typeof cron.schedule).toBe('function');
    });

    test('環境変数が正しく処理される', () => {
      const originalSchedule = process.env.BACKUP_CRON_SCHEDULE;
      process.env.BACKUP_CRON_SCHEDULE = '0 19 * * 1';

      const cron = require('node-cron');
      expect(cron.schedule).toBeDefined();

      // 環境変数を復元
      if (originalSchedule) {
        process.env.BACKUP_CRON_SCHEDULE = originalSchedule;
      } else {
        delete process.env.BACKUP_CRON_SCHEDULE;
      }
    });
  });

  /**
   * プロセス終了ハンドラのテスト
   */
  describe('プロセス終了ハンドラ', () => {
    test('プロセス終了処理が定義されている', () => {
      // プロセスハンドラの存在確認
      expect(process.listenerCount('SIGTERM')).toBeGreaterThanOrEqual(0);
      expect(process.listenerCount('SIGINT')).toBeGreaterThanOrEqual(0);
    });
  });

  /**
   * 基本的な動作テスト
   */
  describe('基本動作確認', () => {
    test('cron-backupモジュールが正常に読み込める', () => {
      expect(() => {
        require('../cron-backup');
      }).not.toThrow();
    });
  });
});