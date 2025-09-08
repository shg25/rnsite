/**
 * PostgreSQL バックアップ cronスケジューラー
 * 
 * 機能:
 * - 環境変数によるcronスケジュール設定
 * - smart-backup.jsのメイン処理を定期実行
 * - グレースフルシャットダウン対応
 * - Railway環境での安定動作
 */

const cron = require('node-cron');
const { main } = require('./smart-backup');

// 環境変数からcronスケジュールを取得
const BACKUP_CRON_SCHEDULE = process.env.BACKUP_CRON_SCHEDULE || '35 1 * * *'; // テスト用: 10:35 JST (01:35 UTC)

console.log('🕐 Smart Backup Cron Service Started');
console.log(`📅 Schedule: ${BACKUP_CRON_SCHEDULE} (${new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' })})`);
console.log('⏳ Waiting for next scheduled backup...');

// cronジョブをスケジュール
cron.schedule(BACKUP_CRON_SCHEDULE, async () => {
  console.log('\n🎯 Scheduled backup triggered!');
  try {
    await main();
  } catch (error) {
    console.error('💥 Scheduled backup failed:', error);
  }
  console.log('⏳ Next backup scheduled...\n');
});

// グレースフルシャットダウンハンドラー
process.on('SIGTERM', () => {
  console.log('👋 Smart Backup Service shutting down...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('👋 Smart Backup Service shutting down...');
  process.exit(0);
});