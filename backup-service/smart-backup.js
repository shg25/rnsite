#!/usr/bin/env node

/**
 * 高機能PostgreSQLバックアップスクリプト
 * - 週1回自動実行
 * - データサイズ比較による異常検知
 * - 前回バックアップファイルの自動削除
 * - Slack通知機能
 */

const { exec } = require('child_process');
const AWS = require('aws-sdk');
const fs = require('fs').promises;
const path = require('path');

// 環境変数
const {
  DATABASE_URL,
  AWS_ACCESS_KEY_ID,
  AWS_SECRET_ACCESS_KEY,
  AWS_S3_BUCKET,
  AWS_S3_REGION = 'ap-northeast-1',
  BACKUP_SIZE_THRESHOLD = 50, // 50%の変化でアラート
  SLACK_WEBHOOK_URL,
  BACKUP_PREFIX = 'weekly-backup'
} = process.env;

// AWS S3設定
const s3 = new AWS.S3({
  accessKeyId: AWS_ACCESS_KEY_ID,
  secretAccessKey: AWS_SECRET_ACCESS_KEY,
  region: AWS_S3_REGION
});

/**
 * PostgreSQL dump実行
 */
async function createDump() {
  const timestamp = new Date().toISOString().split('T')[0];
  const filename = `${BACKUP_PREFIX}-${timestamp}.sql`;
  
  console.log(`📦 Creating database dump: ${filename}`);
  
  return new Promise((resolve, reject) => {
    // PostgreSQL v17対応: 複数のpg_dumpオプションを試行
    const dumpCommands = [
      `pg_dump "${DATABASE_URL}" --no-password --compress=0 --verbose > ${filename}`,
      `pg_dump "${DATABASE_URL}" --compress=0 > ${filename}`,
      `pg_dump "${DATABASE_URL}" > ${filename}`,
      `PGPASSWORD="${DATABASE_URL.split(':')[3].split('@')[0]}" pg_dump -h ${DATABASE_URL.split('@')[1].split(':')[0]} -p ${DATABASE_URL.split(':')[4].split('/')[0]} -U ${DATABASE_URL.split('://')[1].split(':')[0]} -d ${DATABASE_URL.split('/').pop()} > ${filename}`
    ];
    
    const tryDumpCommand = (commandIndex) => {
      if (commandIndex >= dumpCommands.length) {
        reject(new Error('All pg_dump methods failed'));
        return;
      }
      
      exec(dumpCommands[commandIndex], async (error, stdout, stderr) => {
        if (error) {
          console.log(`⚠️ Command ${commandIndex + 1} failed, trying next...`);
          tryDumpCommand(commandIndex + 1);
          return;
        }
      
      try {
        const stats = await fs.stat(filename);
        const sizeInMB = (stats.size / (1024 * 1024)).toFixed(2);
        console.log(`✅ Dump completed: ${sizeInMB}MB`);
        
        resolve({
          filename,
          size: stats.size,
          sizeInMB: parseFloat(sizeInMB)
        });
      } catch (statError) {
        reject(statError);
      }
      });
    };
    
    tryDumpCommand(0);
  });
}

/**
 * 前回バックアップサイズを取得
 */
async function getPreviousBackupSize() {
  try {
    const objects = await s3.listObjectsV2({
      Bucket: AWS_S3_BUCKET,
      Prefix: BACKUP_PREFIX
    }).promise();
    
    if (objects.Contents.length === 0) {
      console.log('📝 No previous backup found');
      return null;
    }
    
    // 最新のファイルを取得
    const latest = objects.Contents
      .sort((a, b) => b.LastModified - a.LastModified)[0];
    
    console.log(`📊 Previous backup: ${(latest.Size / (1024 * 1024)).toFixed(2)}MB`);
    return {
      size: latest.Size,
      key: latest.Key
    };
  } catch (error) {
    console.error('⚠️ Failed to get previous backup size:', error);
    return null;
  }
}

/**
 * サイズ変化をチェック
 */
function checkSizeChange(currentSize, previousSize) {
  if (!previousSize) {
    return { isNormal: true, changePercent: 0 };
  }
  
  const changePercent = Math.abs((currentSize - previousSize.size) / previousSize.size * 100);
  const isNormal = changePercent <= BACKUP_SIZE_THRESHOLD;
  
  console.log(`📈 Size change: ${changePercent.toFixed(1)}% (threshold: ${BACKUP_SIZE_THRESHOLD}%)`);
  
  return { isNormal, changePercent };
}

/**
 * Slack通知送信
 */
async function sendSlackNotification(message) {
  if (!SLACK_WEBHOOK_URL || SLACK_WEBHOOK_URL === 'https://hooks.slack.com/your/webhook/url') {
    console.log('📢 Slack notification skipped (no valid webhook URL)');
    return;
  }
  
  try {
    const https = require('https');
    const data = JSON.stringify({
      text: `🛡️ Database Backup Alert: ${message}`,
      username: 'Railway Backup Bot',
      icon_emoji: ':floppy_disk:'
    });
    
    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length
      }
    };
    
    return new Promise((resolve, reject) => {
      const req = https.request(SLACK_WEBHOOK_URL, options, (res) => {
        if (res.statusCode === 200) {
          console.log('📱 Slack notification sent');
          resolve();
        } else {
          reject(new Error(`Slack API returned ${res.statusCode}`));
        }
      });
      
      req.on('error', reject);
      req.write(data);
      req.end();
    });
  } catch (error) {
    console.error('📱 Failed to send Slack notification:', error);
  }
}

/**
 * S3にファイルアップロード
 */
async function uploadToS3(filename, filesize) {
  try {
    const fileBuffer = await fs.readFile(filename);
    
    const uploadParams = {
      Bucket: AWS_S3_BUCKET,
      Key: filename,
      Body: fileBuffer,
      ServerSideEncryption: 'AES256',
      Metadata: {
        'backup-size': filesize.toString(),
        'backup-date': new Date().toISOString()
      }
    };
    
    console.log(`☁️ Uploading to S3: ${filename}`);
    await s3.upload(uploadParams).promise();
    console.log('✅ Upload completed');
    
    return true;
  } catch (error) {
    console.error('❌ S3 upload failed:', error);
    throw error;
  }
}

/**
 * 前回バックアップファイルを削除
 */
async function deletePreviousBackup(previousBackup) {
  if (!previousBackup) {
    console.log('🗑️ No previous backup to delete');
    return;
  }
  
  try {
    await s3.deleteObject({
      Bucket: AWS_S3_BUCKET,
      Key: previousBackup.key
    }).promise();
    
    console.log(`🗑️ Deleted previous backup: ${previousBackup.key}`);
  } catch (error) {
    console.error('⚠️ Failed to delete previous backup:', error);
  }
}

/**
 * ローカルファイル削除
 */
async function cleanupLocalFile(filename) {
  try {
    await fs.unlink(filename);
    console.log(`🧹 Cleaned up local file: ${filename}`);
  } catch (error) {
    console.error('⚠️ Failed to cleanup local file:', error);
  }
}

/**
 * メイン処理
 */
async function main() {
  console.log('🚀 Starting smart backup process...');
  console.log(`📅 ${new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' })}`);
  
  try {
    // 1. 前回バックアップサイズ取得
    const previousBackup = await getPreviousBackupSize();
    
    // 2. データベースダンプ
    const dumpResult = await createDump();
    
    // 3. サイズチェック
    const sizeCheck = checkSizeChange(dumpResult.size, previousBackup);
    
    // 4. 異常検知時の通知
    if (!sizeCheck.isNormal) {
      const message = `Database size changed by ${sizeCheck.changePercent.toFixed(1)}% (${dumpResult.sizeInMB}MB)`;
      await sendSlackNotification(message);
      console.log('⚠️ Size change detected, but backup continues...');
    }
    
    // 5. S3アップロード
    await uploadToS3(dumpResult.filename, dumpResult.size);
    
    // 6. 前回ファイル削除
    await deletePreviousBackup(previousBackup);
    
    // 7. ローカルファイルクリーンアップ
    await cleanupLocalFile(dumpResult.filename);
    
    console.log('🎉 Smart backup completed successfully!');
    
    // 8. 成功通知（異常検知がなかった場合のみ）
    if (sizeCheck.isNormal) {
      console.log(`✅ Weekly backup: ${dumpResult.sizeInMB}MB (${sizeCheck.changePercent.toFixed(1)}% change)`);
    }
    
  } catch (error) {
    console.error('💥 Backup failed:', error);
    
    // エラー通知
    try {
      await sendSlackNotification(`Backup failed: ${error.message}`);
    } catch (slackError) {
      console.error('📱 Failed to send Slack error notification:', slackError.message);
    }
    process.exit(1);
  }
}

// 実行
if (require.main === module) {
  main();
}

module.exports = { main };