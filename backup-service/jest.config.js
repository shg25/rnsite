/**
 * Jest テスト設定
 */
module.exports = {
  // テスト環境
  testEnvironment: 'node',
  
  // テストファイルのパターン
  testMatch: [
    '**/__tests__/**/*.js',
    '**/?(*.)+(spec|test).js'
  ],
  
  // カバレッジ対象ファイル
  collectCoverageFrom: [
    'smart-backup.js',
    'cron-backup.js',
    '!node_modules/**'
  ],
  
  // カバレッジレポート形式
  coverageReporters: [
    'text',
    'html',
    'lcov'
  ],
  
  // カバレッジしきい値（基本的なレベル）
  coverageThreshold: {
    global: {
      branches: 60,
      functions: 70,
      lines: 70,
      statements: 70
    }
  },
  
  // モック設定
  clearMocks: true,
  resetMocks: true,
  restoreMocks: true,
  
  // テスト実行時の詳細表示
  verbose: true
};