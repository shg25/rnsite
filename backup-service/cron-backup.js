const cron = require('node-cron');
const { main } = require('./smart-backup');

// 環境変数からcronスケジュールを取得
const BACKUP_CRON_SCHEDULE = process.env.BACKUP_CRON_SCHEDULE || '0 5 * * 0'; // デフォルト: 毎週日曜 5AM UTC

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